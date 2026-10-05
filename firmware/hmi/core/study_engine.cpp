#include "study_engine.h"

static uint32_t ms_to_s(uint64_t ms) {
  return static_cast<uint32_t>(ms / 1000ULL);
}

void StudyEngine::startCommon(RunMode mode, uint32_t duration_s, uint64_t now_ms) {
  snap_.mode = mode;
  snap_.paused = false;
  snap_.elapsed_s = 0;
  snap_.remaining_s = duration_s;
  snap_.lap_count = 0;
  target_s_ = duration_s;
  started_ms_ = now_ms;
  paused_at_ms_ = 0;
  accumulated_pause_ms_ = 0;
}

void StudyEngine::startFocus(uint32_t duration_s, uint64_t now_ms) {
  startCommon(RunMode::FOCUS, duration_s, now_ms);
}

void StudyEngine::startCountdown(uint32_t duration_s, uint64_t now_ms) {
  startCommon(RunMode::COUNTDOWN, duration_s, now_ms);
}

void StudyEngine::startStopwatch(uint64_t now_ms) {
  startCommon(RunMode::STOPWATCH, 0, now_ms);
}

uint32_t StudyEngine::currentElapsed(uint64_t now_ms) const {
  if (snap_.mode == RunMode::IDLE) return 0;
  const uint64_t end_ms = snap_.paused ? paused_at_ms_ : now_ms;
  if (end_ms <= started_ms_ + accumulated_pause_ms_) return 0;
  return ms_to_s(end_ms - started_ms_ - accumulated_pause_ms_);
}

void StudyEngine::pause(uint64_t now_ms) {
  if (snap_.mode == RunMode::IDLE || snap_.paused) return;
  snap_.elapsed_s = currentElapsed(now_ms);
  snap_.paused = true;
  paused_at_ms_ = now_ms;
}

void StudyEngine::resume(uint64_t now_ms) {
  if (snap_.mode == RunMode::IDLE || !snap_.paused) return;
  accumulated_pause_ms_ += now_ms - paused_at_ms_;
  snap_.paused = false;
  paused_at_ms_ = 0;
}

void StudyEngine::freeze(uint64_t now_ms) {
  snap_.elapsed_s = currentElapsed(now_ms);
  if ((snap_.mode == RunMode::FOCUS || snap_.mode == RunMode::COUNTDOWN) && target_s_ > snap_.elapsed_s) {
    snap_.remaining_s = target_s_ - snap_.elapsed_s;
  } else {
    snap_.remaining_s = 0;
  }
}

void StudyEngine::stop(uint64_t now_ms) {
  freeze(now_ms);
  snap_.mode = RunMode::IDLE;
  snap_.paused = false;
}

StudyEvent StudyEngine::lap(uint64_t now_ms) {
  if (snap_.mode != RunMode::STOPWATCH) return StudyEvent::NONE;
  freeze(now_ms);
  snap_.lap_count++;
  return StudyEvent::LAP;
}

StudyEvent StudyEngine::tick(uint64_t now_ms) {
  if (snap_.mode == RunMode::IDLE || snap_.paused) return StudyEvent::NONE;

  freeze(now_ms);

  if ((snap_.mode == RunMode::FOCUS || snap_.mode == RunMode::COUNTDOWN) &&
      snap_.elapsed_s >= target_s_) {
    const RunMode completed = snap_.mode;
    if (completed == RunMode::FOCUS) {
      snap_.today_focus_s += target_s_;
      snap_.today_sessions++;
    }
    snap_.mode = RunMode::IDLE;
    snap_.remaining_s = 0;
    return completed == RunMode::FOCUS ? StudyEvent::FOCUS_COMPLETE
                                       : StudyEvent::COUNTDOWN_COMPLETE;
  }

  return StudyEvent::TICK;
}
