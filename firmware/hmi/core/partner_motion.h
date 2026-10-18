#pragma once
#include <stdint.h>

// Portable motion policy for the eventual LVGL sprite-sheet renderer.
// Deliberately independent of LCD, FreeRTOS, Wi-Fi, GIF decoders and assets.
enum class PartnerMotion : uint8_t {
  STATIC, HAUNT, PEEK, HOP, WADDLE, GLIDE, STANCE, SWAY, BOB, CELEBRATE
};
struct PartnerMotionCue {
  PartnerMotion motion = PartnerMotion::STATIC;
  uint16_t duration_ms = 0;
  int8_t travel_x_px = 0;
  int8_t travel_y_px = 0;
  uint8_t max_frames = 0;
};
// 'beat' increments only when ready for a new ambient animation (e.g., every 7 seconds).
inline PartnerMotionCue partner_motion_cue(uint16_t pokemon_id, uint32_t beat,
                                           bool focus_active, bool night_mode,
                                           bool reduced_motion) {
  if (focus_active || night_mode || reduced_motion) return {};
  switch (pokemon_id) {
    case 94:  // Gengar — sneak left/right, occasionally peek
      return beat % 3u == 2u
          ? PartnerMotionCue{PartnerMotion::PEEK, 650, 8, -7, 5}
          : PartnerMotionCue{PartnerMotion::HAUNT, 1600, 14, -4, 8};
    case 393: // Piplup — playful hop / waddle
      return beat % 3u == 0u
          ? PartnerMotionCue{PartnerMotion::WADDLE, 1100, 13, 0, 7}
          : PartnerMotionCue{PartnerMotion::HOP, 850, 5, -13, 6};
    case 468: return {PartnerMotion::GLIDE, 2100, 12, -14, 8}; // Togekiss
    case 448: return {PartnerMotion::STANCE, 1200, 6, -3, 6}; // Lucario
    case 195: return {PartnerMotion::SWAY, 1800, 3, 2, 6};   // Quagsire
    default:  return {PartnerMotion::BOB, 1200, 2, -4, 4};
  }
}
inline PartnerMotionCue partner_tap_cue(bool reduced_motion) {
  if (reduced_motion) return {};
  return {PartnerMotion::CELEBRATE, 580, 0, -12, 6};
}
