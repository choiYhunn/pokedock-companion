// PokéDock Master Ball M6 firmware: USB-powered desk companion on Waveshare ESP32-S3-Touch-AMOLED-1.43.
// Device is the source of truth (timer, alarm, settings); the phone app only configures it over BLE.
#include <sys/time.h>

#include <atomic>
#include <cstring>
#include <ctime>

#include "assets.h"
#include "ble_gatt.h"
#include "board.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "nvs.h"
#include "nvs_flash.h"
#include "pdk_format.h"
#include "protocol.hpp"
#include "rtc_pcf85063.h"
#include "ui.hpp"

using namespace pokedock;
static const char *TAG = "pokedock";

namespace {

constexpr int kPresets[] = {15, 25, 45, 60};
constexpr int kBrightSteps[] = {20, 40, 70, 100};
constexpr int64_t kScreenOffMs = 10 * 60 * 1000;

SemaphoreHandle_t g_mux;  // guards core, engine, settings (BLE host task + main loop + LVGL task)
struct Lock {
  Lock() { xSemaphoreTakeRecursive(g_mux, portMAX_DELAY); }
  ~Lock() { xSemaphoreGiveRecursive(g_mux); }
};

int64_t mono_ms() { return esp_timer_get_time() / 1000; }

struct Settings {
  int tz_min = 540;
  int64_t last_sync_utc = 0;
  int preset_idx = 1;
} g_set;

std::atomic<bool> g_clock_trusted{false};
std::atomic<uint32_t> g_passkey{0};
std::atomic<bool> g_ble_connected{false};
std::atomic<int> g_vcc_mv{5000};
int64_t g_last_touch_ms = 0;
bool g_screen_on = true;
int g_tap_count = 0;
int64_t g_tap_window_ms = 0;

class Env final : public DeviceEnv {
 public:
  int64_t mono_ms() override { return ::mono_ms(); }
  int64_t local_abs_minute() override {
    if (!g_clock_trusted) return -1;
    return local_abs_minutes(int64_t(time(nullptr)), g_set.tz_min);
  }
  bool set_utc(int64_t t, int tz) override {
    if (!pd_rtc_write_utc(t)) return false;
    timeval tv{static_cast<time_t>(t), 0};
    settimeofday(&tv, nullptr);
    g_set.tz_min = tz;
    g_set.last_sync_utc = t;
    g_clock_trusted = true;
    return true;
  }
  int sync_age_min() override {
    return g_set.last_sync_utc ? int((int64_t(time(nullptr)) - g_set.last_sync_utc) / 60) : -1;
  }
  int usb_mv() override { return g_vcc_mv; }
  void persist() override;
  void reaction() override { pending_reaction = true; }
  bool pending_reaction = false;
};

Core g_core;
Env g_env;
ProtocolEngine g_engine(g_core, g_env);

// ---- NVS persistence ----------------------------------------------------------------------------
void Env::persist() {
  nvs_handle_t h;
  if (nvs_open("pd", NVS_READWRITE, &h) != ESP_OK) return;
  nvs_set_i32(h, "partner", g_core.partner());
  nvs_set_i32(h, "bright", g_core.brightness());
  nvs_set_u8(h, "sound", g_core.sound());
  nvs_set_u8(h, "al_en", g_core.alarm().enabled);
  nvs_set_i32(h, "al_min", g_core.alarm().minute_of_day);
  nvs_set_i32(h, "al_last", g_core.persisted().last_fired_day);
  nvs_set_i64(h, "al_armed", g_core.persisted().armed_after_abs);
  nvs_set_str(h, "msg", g_engine.message().c_str());
  nvs_set_i32(h, "tz", g_set.tz_min);
  nvs_set_i64(h, "sync_s", g_set.last_sync_utc);
  nvs_set_i32(h, "preset", g_set.preset_idx);
  nvs_commit(h);
  nvs_close(h);
}

void load_settings() {
  nvs_handle_t h;
  if (nvs_open("pd", NVS_READONLY, &h) != ESP_OK) return;
  int32_t i = 0;
  uint8_t u = 0;
  int64_t l = 0;
  if (nvs_get_i32(h, "partner", &i) == ESP_OK) g_core.set_partner(i);
  if (nvs_get_i32(h, "bright", &i) == ESP_OK) g_core.set_brightness(i);
  if (nvs_get_u8(h, "sound", &u) == ESP_OK) g_core.set_sound(u);
  AlarmConfig cfg;
  PersistedAlarmState st;
  if (nvs_get_u8(h, "al_en", &u) == ESP_OK) cfg.enabled = u;
  if (nvs_get_i32(h, "al_min", &i) == ESP_OK && i >= 0 && i < kMinutesPerDay) cfg.minute_of_day = i;
  if (nvs_get_i32(h, "al_last", &i) == ESP_OK) st.last_fired_day = i;
  if (nvs_get_i64(h, "al_armed", &l) == ESP_OK) st.armed_after_abs = l;
  g_core.restore(cfg, st);
  char msg[kMaxMessageBytes + 1];
  size_t len = sizeof msg;
  if (nvs_get_str(h, "msg", msg, &len) == ESP_OK) g_engine.restore_message(msg);
  if (nvs_get_i32(h, "tz", &i) == ESP_OK) g_set.tz_min = i;
  if (nvs_get_i64(h, "sync_s", &l) == ESP_OK) g_set.last_sync_utc = l;
  if (nvs_get_i32(h, "preset", &i) == ESP_OK && i >= 0 && i < 4) g_set.preset_idx = i;
  nvs_close(h);
}

void after_local_change() {  // user acted on the device: persist and tell the phone
  g_engine.bump();
  g_env.persist();
  ble_notify_state();
}

// ---- touch actions (LVGL task, LVGL lock held) ------------------------------------------------------
bool wake_if_off() {
  g_last_touch_ms = mono_ms();
  if (g_screen_on) return false;
  g_screen_on = true;
  ui::set_screen_on(true);
  return true;  // the waking touch does nothing else
}

void on_tap() {
  if (wake_if_off()) return;
  Lock l;
  if (g_core.alarm_ringing()) {
    g_core.snooze_alarm(mono_ms());
    buzzer_stop();
    after_local_change();
    return;
  }
  if (g_core.focus_phase() == FocusPhase::kDone) {
    g_core.cancel_focus();
    after_local_change();
    return;
  }
  const int64_t now = mono_ms();
  if (now > g_tap_window_ms) {
    g_tap_count = 0;
    g_tap_window_ms = now + 3000;
  }
  if (++g_tap_count == 5) {  // hidden message easter egg
    ui::show_message(g_engine.message());
    ui::react(PDK_EGG);
    g_tap_count = 0;
    return;
  }
  ui::react(g_core.focus_phase() == FocusPhase::kRunning ? PDK_CHEER : PDK_TOUCH);
  if (g_core.sound()) buzzer_play(PD_TUNE_CHIRP);
}

void on_long_press() {
  if (wake_if_off()) return;
  Lock l;
  const int64_t now = mono_ms();
  if (g_core.alarm_ringing()) g_core.dismiss_alarm(), buzzer_stop();
  else if (g_core.focus_phase() == FocusPhase::kRunning) g_core.pause_focus(now);
  else if (g_core.focus_phase() == FocusPhase::kPaused) g_core.resume_focus(now);
  else {
    if (g_core.focus_phase() == FocusPhase::kDone) g_core.cancel_focus();
    g_core.start_focus(kPresets[g_set.preset_idx], now);
  }
  after_local_change();
}

void menu_timer(bool long_press) {
  Lock l;
  const auto ph = g_core.focus_phase();
  if (ph == FocusPhase::kRunning || ph == FocusPhase::kPaused) {
    if (long_press) g_core.cancel_focus(), ui::close_menu();  // cancelling needs a deliberate hold
  } else {
    g_set.preset_idx = (g_set.preset_idx + 1) % 4;
  }
  after_local_change();
}

void menu_alarm() {
  Lock l;
  const auto &a = g_core.alarm();
  g_core.set_alarm(a.minute_of_day / 60, a.minute_of_day % 60, !a.enabled, g_env.local_abs_minute());
  after_local_change();
}

void menu_brightness() {
  Lock l;
  int next = kBrightSteps[0];
  for (int b : kBrightSteps)
    if (b > g_core.brightness()) {
      next = b;
      break;
    }
  g_core.set_brightness(next);
  after_local_change();
}

void menu_partner() {
  Lock l;
  size_t i = 0;
  while (i < kPokemonIds.size() && kPokemonIds[i] != g_core.partner()) ++i;
  g_core.set_partner(kPokemonIds[(i + 1) % kPokemonIds.size()]);
  ui::react(PDK_GREET);
  after_local_change();
}

void menu_pairing() {
  ble_open_pairing_window(120);
  if (g_core.sound()) buzzer_play(PD_TUNE_PAIR);
  ui::close_menu();
}

void menu_screen_off() {
  g_screen_on = false;
  ui::set_screen_on(false);
}

// ---- main loop -----------------------------------------------------------------------------------
void main_loop(void *) {
  int64_t last_vcc = -60000;
  int vcc_hist[6] = {5000, 5000, 5000, 5000, 5000, 5000};
  int vcc_i = 0;
  bool usb_low = false;
  for (;;) {
    const int64_t now = mono_ms();
    if (now - last_vcc > 5000) {  // 6 samples x 5 s = 30 s moving average, with hysteresis
      vcc_hist[vcc_i++ % 6] = board_vcc_mv();
      int sum = 0;
      for (int s : vcc_hist) sum += s;
      g_vcc_mv = sum / 6;
      if (vcc_i % 6 == 0) ESP_LOGI(TAG, "VCC avg %d mV (warn < %d, clear > %d)", g_vcc_mv.load(), kUsbLowMv, kUsbOkMv);
      if (g_vcc_mv < kUsbLowMv) usb_low = true;
      else if (g_vcc_mv > kUsbOkMv) usb_low = false;
      last_vcc = now;
    }
    ui::View v;
    uint32_t ev;
    {
      Lock l;
      ev = g_core.tick(now, g_env.local_abs_minute());
      if (g_core.take_persist_dirty()) g_env.persist();
      if (ev) g_engine.bump();
      v.clock_trusted = g_clock_trusted;
      if (v.clock_trusted) {
        const int64_t abs = g_env.local_abs_minute();
        v.hh = abs_minute_of_day(abs) / 60;
        v.mm = abs_minute_of_day(abs) % 60;
      }
      v.phase = g_core.focus_phase();
      v.remaining_s = int((g_core.focus_remaining(now) + 999) / 1000);
      v.total_s = int(g_core.focus_total_ms() / 1000);
      v.ringing = g_core.alarm_ringing();
      v.alarm_h = g_core.alarm().minute_of_day / 60;
      v.alarm_m = g_core.alarm().minute_of_day % 60;
      v.alarm_en = g_core.alarm().enabled;
      v.partner = g_core.partner();
      v.brightness = g_core.brightness();
      v.preset_min = kPresets[g_set.preset_idx];
      v.usb_low = usb_low;
      v.ble_connected = g_ble_connected;
      v.passkey = g_passkey;
    }
    if (ev & kEvAlarmRing) {
      g_screen_on = true;
      if (g_core.sound()) buzzer_play(PD_TUNE_ALARM);
    }
    if (ev & (kEvAlarmAutoSnooze | kEvAlarmGaveUp)) buzzer_stop();
    if ((ev & kEvFocusComplete) && g_core.sound()) buzzer_play(PD_TUNE_DONE);
    if (ev) ble_notify_state();

    const bool busy = v.ringing || v.phase == FocusPhase::kRunning || v.passkey;
    if (g_screen_on && !busy && now - g_last_touch_ms > kScreenOffMs) g_screen_on = false;
    const bool night = v.clock_trusted && (v.hh >= 23 || v.hh < 7);
    if (board_lvgl_lock(100)) {
      if (ev & kEvFocusComplete) ui::react(PDK_CELEBRATE);
      if (ev & kEvAlarmRing) ui::react(PDK_ALARM);
      if (g_env.pending_reaction) ui::react(PDK_DANCE), g_env.pending_reaction = false;
      ui::update(v);
      static bool shown = true;
      if (shown != g_screen_on) ui::set_screen_on(shown = g_screen_on);
      board_display_brightness(uint8_t(night && !v.ringing ? (v.brightness < 15 ? v.brightness : 15) : v.brightness));
      board_lvgl_unlock();
    }
    vTaskDelay(pdMS_TO_TICKS(250));
  }
}

}  // namespace

// ---- BLE glue (C ABI, called from the NimBLE host task) ------------------------------------------------
extern "C" size_t pd_app_handle_command(const uint8_t *in, size_t len, bool auth, char *ack, size_t cap, bool *changed) {
  Lock l;
  const uint32_t before = g_engine.rev();
  std::string a = g_engine.handle(std::string(reinterpret_cast<const char *>(in), len), auth);
  *changed = g_engine.rev() != before;
  const size_t n = a.size() < cap ? a.size() : cap;
  memcpy(ack, a.data(), n);
  return n;
}

extern "C" size_t pd_app_state_json(char *out, size_t cap) {
  Lock l;
  std::string s = g_engine.state_json();
  const size_t n = s.size() < cap ? s.size() : cap;
  memcpy(out, s.data(), n);
  return n;
}

extern "C" void pd_app_show_passkey(uint32_t passkey) {
  g_passkey = passkey;
  if (passkey) g_screen_on = true;
}

extern "C" void pd_app_link_changed(bool connected) { g_ble_connected = connected; }

extern "C" void app_main(void) {
  esp_err_t err = nvs_flash_init();
  if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
    ESP_ERROR_CHECK(nvs_flash_erase());
    err = nvs_flash_init();
  }
  ESP_ERROR_CHECK(err);
  g_mux = xSemaphoreCreateRecursiveMutex();
  load_settings();

  board_i2c_init();
  board_touch_init();
  buzzer_init();
  const pd_panel_t panel = board_display_init(nullptr);
  ESP_LOGI(TAG, "PokeDock %s panel=%s", kFirmwareVersion, panel == PD_PANEL_SH8601 ? "SH8601" : "CO5300");

  int64_t utc = 0;
  bool trusted = false;
  if (pd_rtc_init() && pd_rtc_read_utc(&utc, &trusted) && trusted) {
    timeval tv{static_cast<time_t>(utc), 0};
    settimeofday(&tv, nullptr);
  }
  g_clock_trusted = trusted;
  ESP_LOGI(TAG, "RTC %s", trusted ? "trusted" : "NOT set (oscillator stopped / never synced)");
  assets_init();

  const ui::Actions actions{on_tap, on_long_press, menu_timer, menu_alarm, menu_brightness, menu_partner, menu_pairing,
                            menu_screen_off};
  if (board_lvgl_lock(-1)) {
    ui::init(actions);
    board_lvgl_unlock();
  }
  g_last_touch_ms = mono_ms();
  ble_start();
  xTaskCreatePinnedToCore(main_loop, "pd_main", 6144, nullptr, 4, nullptr, 0);
}
