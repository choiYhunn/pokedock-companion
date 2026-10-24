// Host stand-in for the ESP32 GATT server: runs the real ProtocolEngine + Core behind a line
// protocol on stdin/stdout so the JS BLE client can be tested end to end without a radio.
//   W <auth 0|1> <hex payload>  -> "N <hex ack>" then "S <hex state>" when state_rev changed
//   R                           -> "S <hex state>"        (characteristic read)
//   T <mono_ms>                 -> advance monotonic clock, tick core, "E <events>" if any
//   X                           -> "X <rev>" (introspection for tests)
//   P                           -> power cut + reboot WITHOUT an RTC backup cell: RAM state lost,
//                                  NVS snapshot restored, wall clock untrusted (PCF85063 OS flag)
#include <cstdio>
#include <iostream>
#include <sstream>
#include <string>

#include "../core/protocol.hpp"

using namespace pokedock;

struct Nvs {  // what the firmware persists (app_main.cpp Env::persist)
  bool valid = false;
  int partner = 94, brightness = 40;
  bool sound = true;
  AlarmConfig alarm;
  PersistedAlarmState alarm_state;
  std::string message;
};

struct BridgeEnv : DeviceEnv {
  int64_t mono = 0, abs_min = -1, synced_mono = -1;
  Core *core = nullptr;
  ProtocolEngine *engine = nullptr;
  Nvs nvs;
  int64_t mono_ms() override { return mono; }
  int64_t local_abs_minute() override { return abs_min; }
  bool set_utc(int64_t t, int tz) override {
    abs_min = local_abs_minutes(t, tz);
    synced_mono = mono;
    return true;
  }
  int sync_age_min() override { return synced_mono < 0 ? -1 : int((mono - synced_mono) / 60000); }
  int usb_mv() override { return 4870; }
  void persist() override {
    nvs = {true, core->partner(), core->brightness(), core->sound(), core->alarm(), core->persisted(), engine->message()};
  }
  void reaction() override {}
};

static std::string hex(const std::string &s) {
  static const char *d = "0123456789abcdef";
  std::string o;
  for (unsigned char c : s) {
    o += d[c >> 4];
    o += d[c & 15];
  }
  return o;
}
static std::string unhex(const std::string &h) {
  std::string o;
  for (size_t i = 0; i + 1 < h.size(); i += 2) o += char(std::stoi(h.substr(i, 2), nullptr, 16));
  return o;
}

int main() {
  Core core;
  BridgeEnv env;
  ProtocolEngine pe(core, env);
  env.core = &core;
  env.engine = &pe;
  std::string line;
  std::cout << "READY " << kFirmwareVersion << std::endl;
  while (std::getline(std::cin, line)) {
    std::istringstream is(line);
    std::string op;
    is >> op;
    if (op == "W") {
      int auth = 0;
      std::string h;
      is >> auth >> h;
      uint32_t before = pe.rev();
      std::cout << "N " << hex(pe.handle(unhex(h), auth == 1)) << "\n";
      if (pe.rev() != before) std::cout << "S " << hex(pe.state_json()) << "\n";
      std::cout << std::flush;
    } else if (op == "R") {
      std::cout << "S " << hex(pe.state_json()) << std::endl;
    } else if (op == "T") {
      int64_t t = 0;
      is >> t;
      if (env.abs_min >= 0) env.abs_min += (t - env.mono) / 60000;
      env.mono = t;
      uint32_t ev = core.tick(env.mono, env.abs_min);
      if (ev) {
        pe.bump();
        std::cout << "E " << ev << "\nS " << hex(pe.state_json()) << "\n";
      }
      std::cout << "K" << std::endl;
    } else if (op == "P") {
      int64_t wall_before = env.abs_min;  // the real world keeps going; the device forgets
      core = Core();
      if (env.nvs.valid) {
        core.set_partner(env.nvs.partner);
        core.set_brightness(env.nvs.brightness);
        core.set_sound(env.nvs.sound);
        core.restore(env.nvs.alarm, env.nvs.alarm_state);
        pe.restore_message(env.nvs.message);
      }
      pe.forget_sessions();
      env.abs_min = -1;
      env.synced_mono = -1;
      env.mono = 0;
      pe.bump();
      std::cout << "B " << wall_before << std::endl;
    } else if (op == "X") {
      std::cout << "X " << pe.rev() << std::endl;
    }
  }
  return 0;
}
