// PokéDock M6 device core: focus timer + daily alarm + snooze, platform independent.
// Shared verbatim by the ESP-IDF firmware and the host regression tests.
//
// Time model
//  - Focus and snooze use a monotonic millisecond clock (esp_timer / steady_clock).
//  - The daily alarm uses local wall-clock "absolute minutes" (days since epoch * 1440 +
//    minute of day) supplied by the caller from the RTC, only while the wall clock is trusted.
//  - An alarm fires once per local day, at most ALARM_GRACE_MIN minutes late (reboot during
//    the alarm minute, RTC corrected forward by BLE sync, missed polls over midnight).
//    Targets older than the grace window never fire (no stale alarms after long power loss).
//  - last_fired_day / armed_after_abs must be persisted by the caller whenever
//    take_persist_dirty() returns true, so a reboot never re-fires a dismissed alarm.
#pragma once
#include <algorithm>
#include <array>
#include <cstdint>

namespace pokedock {

static constexpr std::array<int, 8> kPokemonIds{{94, 393, 468, 448, 195, 175, 417, 385}};
inline bool valid_partner(int id) {
  return std::find(kPokemonIds.begin(), kPokemonIds.end(), id) != kPokemonIds.end();
}

static constexpr int kMinutesPerDay = 1440;
static constexpr int kAlarmGraceMin = 10;
static constexpr int64_t kRingMaxMs = 2 * 60 * 1000;   // auto-snooze after ringing 2 min
static constexpr int kMaxAutoSnoozes = 3;               // then give up for the day
static constexpr int kSnoozeMin = 5;

// Converts UTC epoch seconds + fixed offset (minutes, Korea = +540) to local absolute minutes.
inline int64_t local_abs_minutes(int64_t utc_epoch_s, int tz_offset_min) {
  int64_t local_s = utc_epoch_s + int64_t(tz_offset_min) * 60;
  int64_t m = local_s / 60;
  if (local_s < 0 && local_s % 60) --m;  // floor for pre-1970 (defensive)
  return m;
}
inline int abs_day(int64_t abs_min) {
  return int((abs_min >= 0 ? abs_min : abs_min - (kMinutesPerDay - 1)) / kMinutesPerDay);
}
inline int abs_minute_of_day(int64_t abs_min) {
  return int(((abs_min % kMinutesPerDay) + kMinutesPerDay) % kMinutesPerDay);
}

enum Event : uint32_t {
  kEvNone = 0,
  kEvFocusComplete = 1u << 0,
  kEvAlarmRing = 1u << 1,       // alarm started ringing (scheduled or snooze)
  kEvAlarmAutoSnooze = 1u << 2, // nobody touched it for kRingMaxMs
  kEvAlarmGaveUp = 1u << 3,     // stopped after kMaxAutoSnoozes
};

struct AlarmConfig {
  bool enabled = false;
  int minute_of_day = 7 * 60;
};

struct PersistedAlarmState {  // what the firmware stores in NVS
  int last_fired_day = -1;
  int64_t armed_after_abs = -1;  // targets <= this absolute minute are never fired
};

enum class FocusPhase : uint8_t { kIdle, kRunning, kPaused, kDone };

class Core {
 public:
  // ---- settings -------------------------------------------------------------------------
  bool set_partner(int id) {
    if (!valid_partner(id)) return false;
    partner_ = id;
    return true;
  }
  int partner() const { return partner_; }
  bool set_brightness(int v) {
    if (v < 1 || v > 100) return false;
    brightness_ = v;
    return true;
  }
  int brightness() const { return brightness_; }
  bool set_sound(bool on) {
    sound_ = on;
    return true;
  }
  bool sound() const { return sound_; }

  // ---- focus timer ----------------------------------------------------------------------
  // Starting while a session runs or is paused is refused; the UI must cancel explicitly.
  bool start_focus(int minutes, int64_t mono_ms) {
    if (minutes < 1 || minutes > 120) return false;
    if (phase_ == FocusPhase::kRunning || phase_ == FocusPhase::kPaused) return false;
    focus_total_ms_ = int64_t(minutes) * 60000;
    focus_remaining_ms_ = focus_total_ms_;
    focus_end_ms_ = mono_ms + focus_remaining_ms_;
    phase_ = FocusPhase::kRunning;
    return true;
  }
  bool pause_focus(int64_t mono_ms) {
    if (phase_ != FocusPhase::kRunning) return false;
    focus_remaining_ms_ = std::max<int64_t>(0, focus_end_ms_ - mono_ms);
    phase_ = FocusPhase::kPaused;
    return true;
  }
  bool resume_focus(int64_t mono_ms) {
    if (phase_ != FocusPhase::kPaused) return false;
    focus_end_ms_ = mono_ms + focus_remaining_ms_;
    phase_ = FocusPhase::kRunning;
    return true;
  }
  bool cancel_focus() {
    if (phase_ == FocusPhase::kIdle) return false;
    phase_ = FocusPhase::kIdle;
    focus_remaining_ms_ = 0;
    return true;
  }
  FocusPhase focus_phase() const { return phase_; }
  int64_t focus_total_ms() const { return focus_total_ms_; }
  int64_t focus_remaining(int64_t mono_ms) const {
    switch (phase_) {
      case FocusPhase::kRunning: return std::max<int64_t>(0, focus_end_ms_ - mono_ms);
      case FocusPhase::kPaused: return focus_remaining_ms_;
      default: return 0;
    }
  }
  int focus_completed_count() const { return focus_completed_; }

  // ---- alarm ----------------------------------------------------------------------------
  // now_abs: current local absolute minute if the wall clock is trusted, else -1.
  bool set_alarm(int hour, int minute, bool enabled, int64_t now_abs) {
    if (hour < 0 || hour > 23 || minute < 0 || minute > 59) return false;
    alarm_.minute_of_day = hour * 60 + minute;
    alarm_.enabled = enabled;
    // Never fire a target that is already in the past at the moment of setting.
    persisted_.armed_after_abs = now_abs >= 0 ? now_abs : persisted_.armed_after_abs;
    persist_dirty_ = true;
    return true;
  }
  const AlarmConfig &alarm() const { return alarm_; }
  void restore(const AlarmConfig &cfg, const PersistedAlarmState &st) {
    alarm_ = cfg;
    persisted_ = st;
  }
  const PersistedAlarmState &persisted() const { return persisted_; }
  bool take_persist_dirty() {
    bool d = persist_dirty_;
    persist_dirty_ = false;
    return d;
  }
  bool alarm_ringing() const { return ringing_; }
  bool snooze_pending() const { return snooze_until_ms_ >= 0; }

  void dismiss_alarm() {
    ringing_ = false;
    snooze_until_ms_ = -1;
    auto_snoozes_ = 0;
  }
  bool snooze_alarm(int64_t mono_ms, int minutes = kSnoozeMin) {
    if (!ringing_) return false;
    ringing_ = false;
    snooze_until_ms_ = mono_ms + int64_t(minutes) * 60000;
    return true;
  }

  // ---- periodic tick (call >= 1 Hz) -------------------------------------------------------
  uint32_t tick(int64_t mono_ms, int64_t now_abs /* -1 = wall clock untrusted */) {
    uint32_t ev = kEvNone;
    if (phase_ == FocusPhase::kRunning && mono_ms >= focus_end_ms_) {
      phase_ = FocusPhase::kDone;
      focus_remaining_ms_ = 0;
      ++focus_completed_;
      ev |= kEvFocusComplete;
    }
    // Monotonic duties first: they must not depend on wall-clock trust.
    if (snooze_until_ms_ >= 0 && mono_ms >= snooze_until_ms_) {
      snooze_until_ms_ = -1;
      start_ring(mono_ms);
      ev |= kEvAlarmRing;
    }
    if (ringing_ && mono_ms - ring_started_ms_ >= kRingMaxMs) {
      ringing_ = false;
      if (++auto_snoozes_ > kMaxAutoSnoozes) {
        auto_snoozes_ = 0;
        ev |= kEvAlarmGaveUp;
      } else {
        snooze_until_ms_ = mono_ms + int64_t(kSnoozeMin) * 60000;
        ev |= kEvAlarmAutoSnooze;
      }
    }
    if (now_abs >= 0 && alarm_.enabled) {
      const int today = abs_day(now_abs);
      for (int day : {today - 1, today}) {  // yesterday covers 23:5x targets seen after midnight
        const int64_t target = int64_t(day) * kMinutesPerDay + alarm_.minute_of_day;
        if (day <= persisted_.last_fired_day) continue;
        if (target <= persisted_.armed_after_abs) continue;
        if (now_abs < target || now_abs - target > kAlarmGraceMin) continue;
        persisted_.last_fired_day = day;
        persist_dirty_ = true;
        if (!ringing_) {
          snooze_until_ms_ = -1;
          auto_snoozes_ = 0;
          start_ring(mono_ms);
          ev |= kEvAlarmRing;
        }
      }
    }
    return ev;
  }

 private:
  void start_ring(int64_t mono_ms) {
    ringing_ = true;
    ring_started_ms_ = mono_ms;
  }

  int partner_ = 94;
  int brightness_ = 40;
  bool sound_ = true;
  FocusPhase phase_ = FocusPhase::kIdle;
  int64_t focus_total_ms_ = 25 * 60000, focus_end_ms_ = 0, focus_remaining_ms_ = 0;
  int focus_completed_ = 0;
  AlarmConfig alarm_;
  PersistedAlarmState persisted_;
  bool persist_dirty_ = false;
  bool ringing_ = false;
  int64_t ring_started_ms_ = 0;
  int64_t snooze_until_ms_ = -1;
  int auto_snoozes_ = 0;
};

}  // namespace pokedock
