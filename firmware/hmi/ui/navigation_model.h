#pragma once
#include "screen_ids.h"

enum class MenuGroup : unsigned char {
  TRAIN,
  JOURNEY,
  DESK,
  LINK
};

struct MenuEntry {
  ScreenId screen;
  const char* label;
};

static constexpr MenuEntry kTrainMenu[] = {
  {ScreenId::FOCUS, "Focus"},
  {ScreenId::TIMER, "Timer"},
  {ScreenId::STOPWATCH, "Stopwatch"}
};

static constexpr MenuEntry kJourneyMenu[] = {
  {ScreenId::QUESTS, "Quest"},
  {ScreenId::TRAINER, "Trainer"},
  {ScreenId::EGG, "Egg"},
  {ScreenId::BADGES, "Badges"},
  {ScreenId::STATS, "Record"}
};

static constexpr MenuEntry kDeskMenu[] = {
  {ScreenId::WEATHER, "Weather"},
  {ScreenId::ALARM, "Alarm"},
  {ScreenId::LIGHT, "Light"}
};

static constexpr MenuEntry kLinkMenu[] = {
  {ScreenId::PHONE, "Phone"},
  {ScreenId::NFC, "NFC"},
  {ScreenId::SETTINGS, "Settings"}
};

// Persistent device-level navigation is intentionally minimal:
// HOME | POKE BALL MENU | DEX
// Birthday is event-driven and not part of the everyday menu.
