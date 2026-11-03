// M7 sound: DFRobot DFR0534 (Gravity UART MP3 voice module, 8 MB flash, MP3/WAV) driven over a
// TX-only UART. Host-testable: this file only builds byte frames and decides what to play; the
// firmware writes the bytes to UART1 (board_audio_write) and never waits for an answer.
//
// Link (M7 harness, docs/04): board J10 pin 1 (GPIO44, silk "RXD") -> module R, J10 pin 3 (3V3) ->
// module +, J10 pin 4 (GND) -> module -. The module's T and J10 pin 2 (GPIO43, ROM boot log) stay
// unconnected, so a missing, unpowered or dead module only means silence: nothing here blocks.
//
// Frame (DFRobot wiki DFR0534 "Reference"): AA <cmd> <len> <data...> <sum>, sum = low byte of the
// sum of all preceding bytes; 9600 8N1. Track numbers count files in copy order on the module drive
// (tools/audio/copy_sounds_windows.ps1 copies them one by one in kCueTracks order).
//
// Every sound is bounded by a firmware timer (max_ms) and ended with an explicit Stop, so the result
// does not depend on the module's loop mode; the alarm repeats by re-sending Play.
#pragma once
#include <array>
#include <cstddef>
#include <cstdint>

namespace pokedock {

enum class Cue : uint8_t { kBoot, kLidOpen, kLidClose, kTap, kConfirm, kPair, kTimerDone, kAlarm, kCry, kCount };

struct CueSpec {
  uint16_t track;    // first track (kCry: + partner index)
  uint8_t priority;  // a playing cue is only interrupted by a cue of equal or higher priority
  uint16_t max_ms;   // the sound is stopped at this time (files longer than this are cut)
  bool loop;         // re-sent every max_ms until stop()
};

// track 1..8 = cues in this order, 9..16 = partner cries in kPokemonIds order (pokedock_core.hpp)
static constexpr std::array<CueSpec, size_t(Cue::kCount)> kCueTracks{{
    {1, 1, 2500, false},  // kBoot
    {2, 1, 1500, false},  // kLidOpen
    {3, 2, 1500, false},  // kLidClose (a closing lid cuts the partner cry short)
    {4, 0, 600, false},   // kTap
    {5, 1, 1000, false},  // kConfirm
    {6, 2, 1500, false},  // kPair
    {7, 3, 4000, false},  // kTimerDone
    {8, 4, 3000, true},   // kAlarm
    {9, 2, 3000, false},  // kCry
}};
static constexpr int kCryTracks = 8;
static constexpr uint16_t kTrackCount = 8 + kCryTracks;

namespace dfr0534 {
constexpr uint8_t kStart = 0xAA;
constexpr uint8_t kCmdPlay = 0x02, kCmdStop = 0x04, kCmdTrack = 0x07, kCmdVolume = 0x13;
constexpr int kVolumeMax = 30;  // module range 0..30
constexpr int kBaud = 9600;

// Writes one frame to out (needs 4 + n bytes) and returns its length.
inline size_t frame(uint8_t cmd, const uint8_t *data, uint8_t n, uint8_t *out) {
  out[0] = kStart;
  out[1] = cmd;
  out[2] = n;
  uint8_t sum = uint8_t(kStart + cmd + n);
  for (uint8_t i = 0; i < n; ++i) {
    out[3 + i] = data[i];
    sum = uint8_t(sum + data[i]);
  }
  out[3 + n] = sum;
  return 4u + n;
}
}  // namespace dfr0534

class AudioDirector {
 public:
  static constexpr int64_t kModuleBootMs = 800;  // module powers up with the board 3V3; first frame after this
  static constexpr int kDefaultVolume = 20;

  // enabled = Core::sound(); volume 0..30 (0 = mute); cap = highest volume allowed by the build
  void configure(bool enabled, int volume, bool close_sound, int cap) {
    cap_ = clamp(cap, 0, dfr0534::kVolumeMax);
    const int v = clamp(volume, 0, dfr0534::kVolumeMax);
    const int eff = v < cap_ ? v : cap_;
    if (eff != volume_ || !volume_sent_) {
      volume_ = eff;
      volume_sent_ = false;
    }
    close_sound_ = close_sound;
    if (enabled_ && !enabled) stop_all();
    enabled_ = enabled;
    if (volume_ == 0) stop_all();
  }
  int volume() const { return volume_; }
  bool enabled() const { return enabled_ && volume_ > 0; }

  void begin(int64_t now_ms) {
    ready_at_ = now_ms + kModuleBootMs;
    begun_ = true;
    volume_sent_ = false;
    stop_pending_ = true;  // silence whatever the module may have started on its own at power-up
  }

  // Ask for a cue. partner_index selects the cry (0..7). delay_ms > 0 puts it in the single
  // pending slot (e.g. the cry that follows the lid-open sound); a newer delayed cue replaces it.
  bool play(Cue c, int64_t now_ms, int partner_index = 0, int64_t delay_ms = 0) {
    if (!enabled() || c == Cue::kCount) return false;
    if (c == Cue::kLidClose && !close_sound_) return false;
    if (delay_ms > 0) {
      pending_ = c;
      pending_partner_ = partner_index;
      pending_at_ = now_ms + delay_ms;
      return true;
    }
    return start(c, now_ms, partner_index);
  }

  // Stop the given cue if it is the one playing (and drop it from the pending slot).
  void stop(Cue c) {
    if (pending_ == c) pending_ = Cue::kCount;
    if (current_ == c) {
      current_ = Cue::kCount;
      stop_pending_ = true;
    }
  }
  void stop_all() {
    pending_ = Cue::kCount;
    if (current_ != Cue::kCount) stop_pending_ = true;
    current_ = Cue::kCount;
  }

  Cue current() const { return current_; }
  bool busy(int64_t now_ms) const { return current_ != Cue::kCount && now_ms < until_; }

  // Call regularly (main loop, 250 ms): ends finished cues, repeats the alarm, fires the pending cue.
  void tick(int64_t now_ms) {
    if (current_ != Cue::kCount && now_ms >= until_) {
      const CueSpec &s = spec(current_);
      if (s.loop) {
        emit_track(current_track_);
        until_ = now_ms + s.max_ms;
      } else {
        current_ = Cue::kCount;
        stop_pending_ = true;
      }
    }
    if (pending_ != Cue::kCount && now_ms >= pending_at_) {
      const Cue c = pending_;
      pending_ = Cue::kCount;
      start(c, now_ms, pending_partner_);
    }
  }

  // Bytes to send now (frames are held until the module has booted). Returns the count written.
  size_t drain(int64_t now_ms, uint8_t *buf, size_t cap) {
    if (!begun_ || now_ms < ready_at_) return 0;
    size_t n = 0;
    uint8_t f[8];
    if (!volume_sent_) {
      const uint8_t v = uint8_t(volume_);
      const size_t k = dfr0534::frame(dfr0534::kCmdVolume, &v, 1, f);
      if (n + k > cap) return n;
      copy(f, k, buf + n);
      n += k;
      volume_sent_ = true;
    }
    if (stop_pending_ && !track_pending_) {
      const size_t k = dfr0534::frame(dfr0534::kCmdStop, nullptr, 0, f);
      if (n + k > cap) return n;
      copy(f, k, buf + n);
      n += k;
      stop_pending_ = false;
    }
    if (track_pending_) {
      const uint8_t d[2] = {uint8_t(track_ >> 8), uint8_t(track_ & 0xFF)};
      const size_t k = dfr0534::frame(dfr0534::kCmdTrack, d, 2, f);
      if (n + k > cap) return n;
      copy(f, k, buf + n);
      n += k;
      track_pending_ = false;
      stop_pending_ = false;  // the new track replaces whatever played
    }
    return n;
  }

  static const CueSpec &spec(Cue c) { return kCueTracks[size_t(c)]; }
  static uint16_t track_of(Cue c, int partner_index) {
    if (c != Cue::kCry) return spec(c).track;
    return uint16_t(spec(c).track + clamp(partner_index, 0, kCryTracks - 1));
  }

 private:
  static int clamp(int v, int lo, int hi) { return v < lo ? lo : v > hi ? hi : v; }
  static void copy(const uint8_t *s, size_t n, uint8_t *d) {
    for (size_t i = 0; i < n; ++i) d[i] = s[i];
  }

  bool start(Cue c, int64_t now_ms, int partner_index) {
    if (!enabled()) return false;
    const CueSpec &s = spec(c);
    if (busy(now_ms) && s.priority < spec(current_).priority) return false;
    current_ = c;
    current_track_ = track_of(c, partner_index);
    until_ = now_ms + s.max_ms;
    emit_track(current_track_);
    return true;
  }
  void emit_track(uint16_t t) {
    track_ = t;
    track_pending_ = true;
  }

  bool enabled_ = true, close_sound_ = true, begun_ = false;
  int volume_ = kDefaultVolume, cap_ = dfr0534::kVolumeMax;
  bool volume_sent_ = false, stop_pending_ = false, track_pending_ = false;
  int64_t ready_at_ = 0, until_ = 0, pending_at_ = 0;
  Cue current_ = Cue::kCount, pending_ = Cue::kCount;
  int pending_partner_ = 0;
  uint16_t current_track_ = 0, track_ = 0;
};

}  // namespace pokedock
