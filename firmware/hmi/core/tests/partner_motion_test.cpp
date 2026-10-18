#include <cassert>
#include <iostream>
#include "../partner_motion.h"

int main() {
  const auto ghost = partner_motion_cue(94, 0, false, false, false);
  assert(ghost.motion == PartnerMotion::HAUNT);
  assert(ghost.max_frames <= 8);
  const auto peek = partner_motion_cue(94, 2, false, false, false);
  assert(peek.motion == PartnerMotion::PEEK);
  assert(partner_motion_cue(393, 1, false, false, false).motion == PartnerMotion::HOP);
  assert(partner_motion_cue(393, 3, false, false, false).motion == PartnerMotion::WADDLE);
  assert(partner_motion_cue(468, 0, false, false, false).motion == PartnerMotion::GLIDE);
  assert(partner_motion_cue(448, 0, false, false, false).motion == PartnerMotion::STANCE);
  assert(partner_motion_cue(195, 0, false, false, false).motion == PartnerMotion::SWAY);
  assert(partner_motion_cue(94, 0, true, false, false).motion == PartnerMotion::STATIC);
  assert(partner_motion_cue(94, 0, false, true, false).motion == PartnerMotion::STATIC);
  assert(partner_motion_cue(94, 0, false, false, true).motion == PartnerMotion::STATIC);
  assert(partner_tap_cue(false).motion == PartnerMotion::CELEBRATE);
  assert(partner_tap_cue(true).motion == PartnerMotion::STATIC);
  std::cout << "Partner animation policy tests passed\n";
}
