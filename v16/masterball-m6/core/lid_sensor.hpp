// Lid sensor for the M7 openable ball: reed sensor (Littelfuse 59155) on IO17 (header J1-10) to GND,
// internal pull-up. Lid closed = actuator over the reed = contact closed = level 0.
// Fail-safe by construction: no sensor (M6), a broken wire or a dead reed all read 1 = "open", which
// behaves exactly like firmware without a sensor (screen on, idle timeout as before).
// The clock, alarm and focus timer never depend on this class: it only gates the display.
#pragma once
#include <cstdint>

namespace pokedock {

enum class LidEvent : uint8_t { kNone, kOpened, kClosed };

class LidSensor {
 public:
  static constexpr int64_t kDebounceMs = 120;         // reed bounce < 1 ms; lid rattle / slow closing ~100 ms
  static constexpr int64_t kTouchOverrideMs = 60000;  // a touch while "closed" proves the reading is wrong
  static constexpr int kStuckTouches = 3;             // after 3 such touches the sensor is ignored until it opens

  void set_enabled(bool on) { enabled_ = on; }
  bool enabled() const { return enabled_; }

  // Feed one raw sample (true = contact closed). Returns an event when the debounced state changes.
  LidEvent update(bool raw_closed, int64_t now_ms) {
    if (raw_closed != candidate_) {
      candidate_ = raw_closed;
      since_ = now_ms;
    }
    if (candidate_ == closed_ || now_ms - since_ < kDebounceMs) return LidEvent::kNone;
    closed_ = candidate_;
    if (!closed_) {  // a real opening clears every fallback
      ignored_ = false;
      stuck_touches_ = 0;
      override_until_ = 0;
    }
    if (!enabled_ || ignored_) return LidEvent::kNone;
    return closed_ ? LidEvent::kClosed : LidEvent::kOpened;
  }

  bool closed() const { return closed_; }
  bool ignored() const { return ignored_; }

  // Called on every touch. A touch cannot happen through a closed lid, so it overrides the sensor.
  void touched(int64_t now_ms) {
    if (!enabled_ || !closed_ || ignored_) return;
    override_until_ = now_ms + kTouchOverrideMs;
    if (++stuck_touches_ >= kStuckTouches) ignored_ = true;
  }

  // May the display be on? (the caller still applies its own idle timeout and manual screen-off)
  bool screen_allowed(int64_t now_ms) const {
    return !enabled_ || ignored_ || !closed_ || now_ms < override_until_;
  }

 private:
  bool enabled_ = true;
  bool closed_ = false;     // debounced; starts "open" so a missing sensor never blanks the screen
  bool candidate_ = false;
  bool ignored_ = false;
  int64_t since_ = 0;
  int64_t override_until_ = 0;
  int stuck_touches_ = 0;
};

}  // namespace pokedock
