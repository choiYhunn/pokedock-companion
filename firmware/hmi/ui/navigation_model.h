#pragma once
#include "screen_ids.h"

// V10: the 800x480 persistent bar is HOME | FOCUS | central Poke Ball drawer.
// Drawer is a modal, not a ScreenId. FOCUS uses the study/rest timer;
// TIMER is a separate general-purpose countdown without study rewards.
enum class MenuGroup : unsigned char { DAILY, PLAY, EXTRA };

struct MenuEntry {
  ScreenId screen;
  const char* label;
};

static constexpr MenuEntry kDailyMenu[] = {
  {ScreenId::QUESTS, "To-do / D-day"},
  {ScreenId::TIMER, "General countdown"},
  {ScreenId::ALARM, "Alarm"},
  {ScreenId::OUR_SPACE, "Private couple nook"}
};
static constexpr MenuEntry kPlayMenu[] = {
  {ScreenId::TRAINER, "Party / Trainer"},
  {ScreenId::DEX, "Pokedex"},
  {ScreenId::EGG, "Mystery Egg"},
  {ScreenId::BADGES, "Badges"},
  {ScreenId::STATS, "Record"}
};
static constexpr MenuEntry kExtraMenu[] = {
  {ScreenId::SETTINGS, "Settings"},
  {ScreenId::LIGHT, "Light"},
  {ScreenId::WEATHER, "Weather"},
  {ScreenId::PHONE, "Phone presence"},
  {ScreenId::NFC, "NFC"},
  {ScreenId::STOPWATCH, "Stopwatch"}
};

// The animated partner-select overlay is a modal over the currently active
// screen; it is not a persisted screen nor a fourth permanent navigation tab.
// The native LVGL port MUST implement an explicit previous-screen stack.
