#pragma once
#include <stdint.h>

enum class RunMode : uint8_t {
  IDLE,
  FOCUS,
  COUNTDOWN,
  STOPWATCH
};

struct StudySnapshot {
  RunMode mode = RunMode::IDLE;
  bool paused = false;
  uint32_t elapsed_s = 0;
  uint32_t remaining_s = 0;
  uint32_t today_focus_s = 0;
  uint16_t today_sessions = 0;
  uint16_t lap_count = 0;
};

enum class StudyEvent : uint8_t {
  NONE,
  TICK,
  FOCUS_COMPLETE,
  COUNTDOWN_COMPLETE,
  STOPPED,
  LAP
};

class StudyEngine {
 public:
  void startFocus(uint32_t duration_s, uint64_t now_ms);
  void startCountdown(uint32_t duration_s, uint64_t now_ms);
  void startStopwatch(uint64_t now_ms);
  void pause(uint64_t now_ms);
  void resume(uint64_t now_ms);
  void stop(uint64_t now_ms);
  StudyEvent lap(uint64_t now_ms);
  StudyEvent tick(uint64_t now_ms);

  const StudySnapshot& snapshot() const { return snap_; }
  uint32_t currentElapsed(uint64_t now_ms) const;

 private:
  void startCommon(RunMode mode, uint32_t duration_s, uint64_t now_ms);
  void freeze(uint64_t now_ms);

  StudySnapshot snap_{};
  uint64_t started_ms_ = 0;
  uint64_t paused_at_ms_ = 0;
  uint64_t accumulated_pause_ms_ = 0;
  uint32_t target_s_ = 0;
};
