// Round 466x466 device UI (LVGL 8). Layouts follow the 2026-10-24 legibility audit:
// home = partner first (x3 integer sprite, 80 px clock), focus = minutes hero (210 px) and
// MM:SS (140 px) for the last 10 minutes, no text smaller than 34 px except the private message.
#pragma once
#include <cstdint>
#include <string>

#include "clock_set.hpp"
#include "pokedock_core.hpp"

namespace ui {

struct View {
  bool clock_trusted = false;
  int hh = 0, mm = 0;
  pokedock::FocusPhase phase = pokedock::FocusPhase::kIdle;
  int remaining_s = 0, total_s = 0;
  bool ringing = false;
  int alarm_h = 7, alarm_m = 0;
  bool alarm_en = false;
  int partner = 94;
  bool night = false;  // 23:00-06:59 with a trusted clock: the partner may fall asleep
  int brightness = 40;
  int preset_min = 25;
  bool usb_low = false;
  bool ble_connected = false;
  uint32_t passkey = 0;  // 0 = hidden
};

struct Actions {  // called from the LVGL task with the LVGL lock held
  void (*tap)();
  void (*long_press)();
  void (*menu_timer)(bool long_press);
  void (*menu_alarm)(bool long_press);  // short: on/off, long: open the alarm time editor
  void (*menu_brightness)();
  void (*menu_partner)();
  void (*menu_pairing)();
  void (*menu_screen_off)();
  void (*menu_time)();                                        // open the clock editor
  void (*clock_saved)(const pokedock::LocalDateTime &local);  // user confirmed date + time
  void (*alarm_time_saved)(int hour, int minute);             // user confirmed the alarm time
};

void init(const Actions &a);
void update(const View &v);            // call with the LVGL lock held
void show_message(const std::string &m);
void react(uint8_t anim);              // one-shot partner mood (pdk_anim); loops follow the state
void set_screen_on(bool on);
bool menu_open();
void close_menu();
// Touch editors (no phone needed): one field per page, large -/+ buttons, 이전/다음, 저장.
void open_clock_editor(const pokedock::LocalDateTime &start);
void open_alarm_editor(int hour, int minute);
bool editor_open();
void close_editor();

}  // namespace ui
