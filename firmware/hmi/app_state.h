#pragma once
#include <stdint.h>

enum class PrimaryMode : uint8_t {
  HOME,
  FOCUS,
  COUNTDOWN,
  STOPWATCH,
  TODAY,
  NIGHT,
  BIRTHDAY,
  NFC_OVERRIDE,
  ALARM
};

enum OverlayFlags : uint16_t {
  OVERLAY_NONE              = 0,
  OVERLAY_PHONE_PARKED      = 1u << 0,
  OVERLAY_PRIORITY_NOTICE   = 1u << 1,
  OVERLAY_WIFI_OFFLINE      = 1u << 2,
  OVERLAY_DOCK_OFFLINE      = 1u << 3,
  OVERLAY_WEATHER_STALE     = 1u << 4
};

struct AppInputs {
  bool alarm = false;
  bool birthday = false;
  bool nfc_override = false;
  bool focus_active = false;
  bool countdown_active = false;
  bool stopwatch_active = false;
  bool night = false;

  bool phone_parked = false;
  bool priority_notice = false;
  bool wifi_online = false;
  bool dock_online = true;
  bool weather_stale = false;

  uint16_t nfc_pokemon_id = 0;
};

struct UiDecision {
  PrimaryMode mode = PrimaryMode::HOME;
  uint16_t pokemon_id = 468; // calm default
  uint16_t overlays = OVERLAY_NONE;
};

inline UiDecision resolve_ui(const AppInputs& in) {
  UiDecision out{};

  if (in.alarm) {
    out.mode = PrimaryMode::ALARM;
    out.pokemon_id = 175;
  } else if (in.birthday) {
    out.mode = PrimaryMode::BIRTHDAY;
    out.pokemon_id = 385;
  } else if (in.nfc_override) {
    out.mode = PrimaryMode::NFC_OVERRIDE;
    out.pokemon_id = in.nfc_pokemon_id;
  } else if (in.focus_active) {
    out.mode = PrimaryMode::FOCUS;
    out.pokemon_id = 448;
  } else if (in.countdown_active) {
    out.mode = PrimaryMode::COUNTDOWN;
    out.pokemon_id = 175;
  } else if (in.stopwatch_active) {
    out.mode = PrimaryMode::STOPWATCH;
    out.pokemon_id = 448;
  } else if (in.night) {
    out.mode = PrimaryMode::NIGHT;
    out.pokemon_id = 94;
  } else {
    out.mode = PrimaryMode::HOME;
    out.pokemon_id = 468;
  }

  if (in.phone_parked) out.overlays |= OVERLAY_PHONE_PARKED;
  if (in.priority_notice) out.overlays |= OVERLAY_PRIORITY_NOTICE;
  if (!in.wifi_online) out.overlays |= OVERLAY_WIFI_OFFLINE;
  if (!in.dock_online) out.overlays |= OVERLAY_DOCK_OFFLINE;
  if (in.weather_stale) out.overlays |= OVERLAY_WEATHER_STALE;

  return out;
}
