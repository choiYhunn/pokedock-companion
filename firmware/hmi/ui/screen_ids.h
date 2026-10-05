#pragma once
#include <stdint.h>

enum class ScreenId : uint8_t {
  HOME,
  FOCUS,
  TIMER,
  STOPWATCH,
  TODAY,
  STATS,
  DEX,
  NFC,
  WEATHER,
  ALARM,
  PHONE,
  LIGHT,
  SETTINGS,
  BIRTHDAY,
  NIGHT
};

inline const char* screen_id_name(ScreenId id) {
  switch(id) {
    case ScreenId::HOME: return "home";
    case ScreenId::FOCUS: return "focus";
    case ScreenId::TIMER: return "timer";
    case ScreenId::STOPWATCH: return "stopwatch";
    case ScreenId::TODAY: return "today";
    case ScreenId::STATS: return "stats";
    case ScreenId::DEX: return "dex";
    case ScreenId::NFC: return "nfc";
    case ScreenId::WEATHER: return "weather";
    case ScreenId::ALARM: return "alarm";
    case ScreenId::PHONE: return "phone";
    case ScreenId::LIGHT: return "light";
    case ScreenId::SETTINGS: return "settings";
    case ScreenId::BIRTHDAY: return "birthday";
    case ScreenId::NIGHT: return "night";
  }
  return "unknown";
}
