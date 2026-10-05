#pragma once
#include <stdint.h>

constexpr int POKEDOCK_MAX_TODOS = 5;

struct TodoItem {
  bool done = false;
  char title[64] = {};
  char due_label[24] = {};
};

struct DailyStudyStats {
  uint32_t focus_seconds = 0;
  uint16_t sessions = 0;
  uint16_t streak_days = 0;
};

struct WeatherSnapshot {
  bool valid = false;
  int16_t temp_c_x10 = 0;
  uint16_t weather_code = 0;
  uint32_t fetched_epoch = 0;
};
