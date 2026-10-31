// Partner animation director (gift content, firmware m6-0.4.0-gift).
//
// Official pixel sprites only have ONE (idle) animation per Pokémon, so every mood is the idle
// frames (or a per-mood clip if the private pack has one) plus a motion curve and an original
// overlay drawn by the firmware (heart, sparkle, Zzz, !). Everything here is a pure function of
// time and state so the host tests and the browser simulator check exactly what the device runs.
#pragma once
#include <cmath>
#include <cstdint>
#include <cstdlib>

#include "pdk_format.h"

namespace pokedock {

enum class Stage : uint8_t { kHome, kFocus, kAlarm };
enum Overlay : uint8_t { kOvNone = 0, kOvHeart, kOvSparkle, kOvZzz, kOvExclaim };

struct DirectorInput {
  int64_t now_ms = 0;
  int dex = 94;
  bool ringing = false;
  bool focus_active = false;  // running or paused
  bool night = false;         // 23:00-06:59 with a trusted clock
  int64_t last_touch_ms = 0;
};

struct Pose {
  int dx = 0, dy = 0;     // px offset from the stage anchor
  int zoom_pct = 100;     // kept at 100 by every mood: pixel art stays at an exact integer scale
  uint8_t overlay = kOvNone;
  int overlay_dy = 0;     // overlay rise (px, negative = up)
  uint8_t overlay_opa = 0;  // 0..255
};

struct Shot {
  Stage stage = Stage::kHome;
  uint8_t anim = PDK_IDLE;  // which PDK clip to show (the asset loader falls back to idle)
  Pose pose;
  int64_t t_ms = 0;         // time inside the current mood (drives the clip frame too)
};

struct Rect {
  int x, y, w, h;  // centre-relative top-left (px) and size of the scaled frame
  int zoom;        // LVGL zoom units (256 = 1x)
};

// Screen geometry (466 x 466 round panel, origin = panel centre).
static constexpr int kPanelR = 233;
static constexpr int kHomeAnchorY = 30;     // below the 80 px clock, feet clear of the status pill
static constexpr int kHomeTopLimit = -88;   // clock label bottom: the partner never covers digits
static constexpr int kHomeBox = 248;        // largest integer-scaled frame on the home screen
static constexpr int kFocusRestTop = 140;   // focus: partner's top rests just below "분 남음" (bottom ~ +134)
static constexpr int kFocusTopLimit = 136;  // and never rises into it
static constexpr int kFocusRingR = 207;     // and stays inside the 14 px progress ring (inner edge 209)
static constexpr int kAlarmAnchorY = -150;  // takes the title's place on the alarm screen
static constexpr int kSmallMaxH = 64, kSmallMaxW = 96;  // focus / alarm partner box (Gen-V sprites are <= 63 px: exact x1)
static constexpr int kSleepAfterMs = 60 * 1000;

inline bool floats(int dex) { return dex == 94 || dex == 468 || dex == 385; }  // Gengar, Togekiss, Jirachi
inline bool is_gengar(int dex) { return dex == 94; }

// One-shot clips the firmware triggers (tap, appear, celebrate...). Loops (idle, sleep, cheer,
// alarm) come from the state and never need a trigger.
inline int one_shot_ms(uint8_t anim) {
  switch (anim) {
    case PDK_GREET: return 1300;
    case PDK_TOUCH: return 900;
    case PDK_JUMP: return 800;
    case PDK_CELEBRATE: return 1800;
    case PDK_DANCE: return 1800;
    case PDK_EGG: return 2600;
    default: return 0;
  }
}

namespace detail {
static constexpr double kPi = 3.14159265358979323846;
inline double wave(int64_t t, int period_ms) { return std::sin(2.0 * kPi * double(t % period_ms) / period_ms); }
inline int hop(int64_t t, int len_ms, int height) {  // half-sine arc, 0 outside [0, len)
  if (t < 0 || t >= len_ms) return 0;
  return -int(std::lround(height * std::sin(kPi * double(t) / len_ms)));
}
inline double ease_out_back(double x) {
  const double c1 = 1.70158, c3 = c1 + 1.0;
  return 1.0 + c3 * std::pow(x - 1.0, 3) + c1 * std::pow(x - 1.0, 2);
}
inline uint8_t fade(int64_t t, int len_ms) {  // 255 -> 0 over the second half
  if (t < len_ms / 2) return 255;
  if (t >= len_ms) return 0;
  return uint8_t(255 - 255 * (t - len_ms / 2) / (len_ms - len_ms / 2));
}
}  // namespace detail

inline Pose pose_for(uint8_t anim, int64_t t, int dex) {
  using namespace detail;
  Pose p;
  switch (anim) {
    case PDK_IDLE:
      if (floats(dex)) p.dy = int(std::lround(6 * wave(t, 3000)));        // ghosts and fliers hover
      else p.dy = int(std::lround(2 * wave(t, 2400)));                     // ground partners breathe (2 px bob)
      break;
    case PDK_SLEEP:
      p.dy = 8 + int(std::lround(3 * wave(t, 4000)));
      p.overlay = kOvZzz;
      p.overlay_dy = -int((t % 3000) * 36 / 3000);
      p.overlay_opa = uint8_t(t % 3000 < 2400 ? 255 : 255 - (t % 3000 - 2400) * 255 / 600);
      break;
    case PDK_GREET:
      if (is_gengar(dex)) {  // Gengar peeks in from the side, overshoots, then grins in place
        const double x = t < 700 ? double(t) / 700 : 1.0;
        p.dx = int(std::lround(150 * (1.0 - ease_out_back(x))));
        if (t >= 700) p.dx += int(std::lround(4 * wave(t - 700, 300) * (t < 1300 ? (1300 - t) / 600.0 : 0)));
      } else {  // others drop in with a small bounce
        const double x = t < 600 ? double(t) / 600 : 1.0;
        p.dy = int(std::lround(-50 * (1.0 - ease_out_back(x))));
      }
      if (t >= 700) { p.overlay = kOvSparkle; p.overlay_opa = fade(t - 700, 600); p.overlay_dy = -int((t - 700) / 30); }
      break;
    case PDK_TOUCH:
      if (is_gengar(dex)) {  // mischievous giggle: quick side-to-side shake
        const double decay = t < 900 ? (900 - t) / 900.0 : 0;
        p.dx = int(std::lround(8 * wave(t, 160) * decay));
        p.dy = hop(t, 300, 8);
      } else {
        p.dy = hop(t, 450, 20) + (t >= 450 && t < 600 ? 2 : 0);  // hop, then a 2 px landing dip
      }
      p.overlay = kOvHeart;
      p.overlay_dy = -int(t * 40 / 900);
      p.overlay_opa = fade(t, 900);
      break;
    case PDK_JUMP:
      p.dy = hop(t, 800, 30);
      break;
    case PDK_CHEER:  // focus running: calm sway with a tiny bounce every 2 s (the band under the label is narrow)
      p.dx = int(std::lround(5 * wave(t, 4000)));
      p.dy = hop(t % 2000, 300, 4);
      break;
    case PDK_CELEBRATE:
      p.dy = hop(t, 600, 28) + hop(t - 600, 600, 28);
      p.overlay = kOvSparkle;
      p.overlay_dy = -int(t * 30 / 1800);
      p.overlay_opa = fade(t, 1800);
      break;
    case PDK_ALARM:  // wake-up bounce with a blinking "!"
      p.dy = -int(std::lround(8 * std::fabs(wave(t, 500))));
      p.dx = int(std::lround(3 * wave(t, 120)));
      p.overlay = kOvExclaim;
      p.overlay_opa = (t % 500) < 300 ? 255 : 0;
      break;
    case PDK_DANCE:
    case PDK_EGG:
      p.dx = int(std::lround(14 * wave(t, 800)));
      p.dy = -int(std::lround(10 * std::fabs(wave(t, 400))));
      if (anim == PDK_EGG) { p.overlay = kOvHeart; p.overlay_dy = -int((t % 1300) * 40 / 1300); p.overlay_opa = fade(t % 1300, 1300); }
      break;
    default:
      break;
  }
  return p;
}

class Director {
 public:
  // One-shot clips (tap, appear, celebrate, egg...). Ignored while the alarm rings.
  void trigger(uint8_t anim, int64_t now_ms) {
    if (one_shot_ms(anim) <= 0) return;
    if (anim == PDK_TOUCH && now_ms < wake_guard_) return;  // the tap that woke it keeps the wake-up greet
    shot_anim_ = anim;
    shot_start_ = now_ms;
  }
  // Called on every touch: remembers it and, if the partner was asleep, makes it wake up (greet).
  void touched(const DirectorInput &in) {
    const bool was_asleep = sleeping(in);
    last_touch_ = in.now_ms;
    if (was_asleep) {
      trigger(PDK_GREET, in.now_ms);
      wake_guard_ = in.now_ms + 300;
    }
  }
  bool sleeping(const DirectorInput &in) const {
    const int64_t last = in.last_touch_ms > last_touch_ ? in.last_touch_ms : last_touch_;
    return in.night && !in.focus_active && !in.ringing && in.now_ms - last >= kSleepAfterMs;
  }

  Shot decide(const DirectorInput &in) {
    Shot s;
    s.stage = in.ringing ? Stage::kAlarm : in.focus_active ? Stage::kFocus : Stage::kHome;
    uint8_t loop = PDK_IDLE;
    if (s.stage == Stage::kAlarm) loop = PDK_ALARM;
    else if (s.stage == Stage::kFocus) loop = PDK_CHEER;
    else if (sleeping(in)) loop = PDK_SLEEP;
    if (loop != loop_anim_) { loop_anim_ = loop; loop_start_ = in.now_ms; }
    const bool shot_live = shot_anim_ != PDK_IDLE && s.stage != Stage::kAlarm &&
                           in.now_ms - shot_start_ < one_shot_ms(shot_anim_) && in.now_ms >= shot_start_;
    if (!shot_live) shot_anim_ = PDK_IDLE;
    s.anim = shot_live ? shot_anim_ : loop;
    s.t_ms = shot_live ? in.now_ms - shot_start_ : in.now_ms - loop_start_;
    s.pose = pose_for(s.anim, s.t_ms, in.dex);
    return s;
  }

 private:
  uint8_t shot_anim_ = PDK_IDLE, loop_anim_ = PDK_IDLE;
  int64_t shot_start_ = 0, loop_start_ = 0, last_touch_ = 0, wake_guard_ = 0;
};

// Base LVGL zoom (256 = 1x) for a frame on a stage. Home: largest integer scale (crisp pixels,
// max x3) that fits the 248 px box. Focus/alarm: 1x, shrunk only if a frame is unusually large.
inline int base_zoom(Stage st, int w, int h) {
  if (w <= 0 || h <= 0) return 256;
  if (st == Stage::kHome) {
    const int m = w > h ? w : h;
    int s = kHomeBox / m;
    s = s < 1 ? 1 : s > 3 ? 3 : s;
    return 256 * s;
  }
  int z = 256;
  if (h > kSmallMaxH) z = 256 * kSmallMaxH / h;
  if (w > kSmallMaxW && 256 * kSmallMaxW / w < z) z = 256 * kSmallMaxW / w;
  return z;
}

// Where the scaled frame goes. Keeps every corner inside the circle (4 px margin) and, at home,
// never lets the partner rise into the clock digits; the pose is clamped, not the layout.
inline Rect place(Stage st, int w, int h, const Pose &p) {
  const int zoom = base_zoom(st, w, h) * p.zoom_pct / 100;
  const int sw = (w * zoom + 255) / 256, sh = (h * zoom + 255) / 256;
  const int ay = st == Stage::kHome ? kHomeAnchorY : st == Stage::kFocus ? kFocusRestTop + sh / 2 : kAlarmAnchorY;
  int cx = p.dx, cy = ay + p.dy;
  const int top_limit = st == Stage::kHome ? kHomeTopLimit : st == Stage::kFocus ? kFocusTopLimit : -kPanelR;
  if (cy - sh / 2 < top_limit) cy = top_limit + sh / 2;
  // pull inward until the farthest corner is inside the circle
  const int rmax = st == Stage::kFocus ? kFocusRingR : kPanelR - 4;
  for (int guard = 0; guard < 400; ++guard) {
    const int fx = std::abs(cx) + sw / 2 + 1, fy = std::abs(cy) + sh / 2 + 1;
    if (fx * fx + fy * fy <= rmax * rmax) break;
    if (cx) cx += cx > 0 ? -1 : 1;
    if (std::abs(cy) > 0 && (cy < 0 || cy - sh / 2 > top_limit)) cy += cy > 0 ? -1 : 1;
    else if (!cx) break;
  }
  return {cx - sw / 2, cy - sh / 2, sw, sh, zoom};
}

}  // namespace pokedock
