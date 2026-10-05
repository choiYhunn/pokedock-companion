#pragma once
#include <stdint.h>
#include "screen_ids.h"

struct PartnerVm {
  uint16_t pokemon_id = 468; uint16_t level = 12; uint8_t bond = 67;
  uint16_t study_exp = 285; uint8_t egg_progress = 42;
  char name[24] = "Togekiss"; char role[16] = "CALM"; char quote[96] = {};
};

struct TrainerVm {
  char rank[24] = "ACE SCHOLAR"; uint32_t total_focus_s = 0;
  uint32_t total_sessions = 0; uint16_t streak_days = 0;
  uint16_t caught_count = 0; uint8_t badge_count = 0; uint8_t shiny_count = 0;
};

struct QuestItemVm { char category[12] = {}; char title[56] = {}; char progress[20] = {}; bool complete = false; };
struct TimerVm { bool running=false; bool paused=false; uint32_t elapsed_s=0; uint32_t remaining_s=0; };
struct PhoneVm { bool connected=false; bool parked=false; bool charging_hint=false; bool has_priority_notice=false; char priority_title[48] = {}; };

struct UiViewModel {
  ScreenId screen = ScreenId::HOME; PartnerVm partner{}; TrainerVm trainer{};
  QuestItemVm quests[4]{}; TimerVm focus{}; TimerVm countdown{};
  uint32_t stopwatch_s=0; uint16_t stopwatch_laps=0; PhoneVm phone{};
  bool dark=false; bool dock_online=true; bool wifi_online=false;
};
