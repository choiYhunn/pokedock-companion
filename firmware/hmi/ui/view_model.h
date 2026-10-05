#pragma once
#include <stdint.h>
#include "screen_ids.h"

struct HomeVm {
  char time[6] = "00:00";
  char date[32] = {};
  uint32_t today_focus_s = 0;
  uint32_t daily_target_s = 10800;
  int16_t temperature_c_x10 = 0;
  char weather_label[24] = {};
  char next_todo[64] = {};
  char dday_label[24] = {};
  uint16_t companion_id = 468;
};

struct TimerVm {
  bool running = false;
  bool paused = false;
  uint32_t elapsed_s = 0;
  uint32_t remaining_s = 0;
};

struct PhoneVm {
  bool connected = false;
  bool parked = false;
  bool charging_hint = false;
  bool has_priority_notice = false;
  char priority_title[48] = {};
};

struct UiViewModel {
  ScreenId screen = ScreenId::HOME;
  HomeVm home{};
  TimerVm focus{};
  TimerVm countdown{};
  uint32_t stopwatch_s = 0;
  uint16_t stopwatch_laps = 0;
  PhoneVm phone{};
  bool dark = false;
  bool dock_online = true;
  bool wifi_online = false;
};
