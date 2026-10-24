// Round 466x466 device UI (LVGL 8). Layouts follow the 2026-10-24 legibility audit:
// home = partner first (x3 integer sprite, 80 px clock), focus = minutes hero (210 px) and
// MM:SS (140 px) for the last 10 minutes, no text smaller than 34 px except the private message.
#pragma once
#include <cstdint>
#include <string>

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
  void (*menu_alarm)();
  void (*menu_brightness)();
  void (*menu_partner)();
  void (*menu_pairing)();
  void (*menu_screen_off)();
};

void init(const Actions &a);
void update(const View &v);            // call with the LVGL lock held
void show_message(const std::string &m);
void react(uint8_t anim);              // play a one-shot partner animation (pdk_anim)
void set_screen_on(bool on);
bool menu_open();
void close_menu();

}  // namespace ui
