#pragma once
#include "screen_ids.h"

struct ScreenDescriptor {
  ScreenId id;
  const char* label;
  bool persistent_nav;
  bool suppress_random_events;
  bool allow_priority_overlay;
};

static constexpr ScreenDescriptor kScreenRegistry[] = {
  {ScreenId::HOME,      "HOME",      true,  false, true},
  {ScreenId::FOCUS,     "TRAIN",     false, true,  true},
  {ScreenId::QUESTS,    "QUEST",     false, false, true},
  {ScreenId::TIMER,     "TIMER",     false, true,  true},
  {ScreenId::STOPWATCH, "STOPWATCH", false, true,  true},
  {ScreenId::TODAY,     "TODAY",     false, false, true},
  {ScreenId::STATS,     "RECORD",    false, false, true},
  {ScreenId::TRAINER,   "TRAINER",   false, false, true},
  {ScreenId::BADGES,    "BADGES",    false, false, true},
  {ScreenId::EGG,       "EGG",       false, false, true},
  {ScreenId::DEX,       "DEX",       true,  false, true},
  {ScreenId::NFC,       "NFC",       false, false, true},
  {ScreenId::WEATHER,   "WEATHER",   false, false, true},
  {ScreenId::ALARM,     "ALARM",     false, false, true},
  {ScreenId::PHONE,     "PHONE",     false, false, true},
  {ScreenId::LIGHT,     "LIGHT",     false, false, true},
  {ScreenId::SETTINGS,  "SETTINGS",  false, false, false},
  {ScreenId::BIRTHDAY,  "BIRTHDAY",  false, true,  false},
  {ScreenId::NIGHT,     "NIGHT",     false, true,  true}
};
