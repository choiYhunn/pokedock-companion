#pragma once
#include <stdint.h>

// PokéDock V11 — deterministic, offline, device-independent progression.
// This is an opt-in POLICY for a future firmware/UI bridge, NOT yet integrated.
// Units: fully completed verified focus minutes (not wall time while paused).
// Session IDs MUST be monotonically increasing and persisted atomically.
enum StudyUnlock : uint8_t {
  UNLOCK_NONE      = 0,
  UNLOCK_GENGAR    = 1u << 0, // 60 min  : first personal reaction
  UNLOCK_POSTCARD  = 1u << 1, // 120 min : Piplup postcard/encounter token
  UNLOCK_EGG       = 1u << 2, // 300 min : egg hatch scene
  UNLOCK_BADGE     = 1u << 3, // 600 min : study badge
  UNLOCK_ROOM      = 1u << 4  // 1200 min: decoration theme (20h)
};
struct StudyBondProgress {
  uint32_t credited_minutes = 0;
  uint32_t total_stars = 0;
  uint32_t total_focus_sessions = 0;
  uint32_t last_day_key = 0;     // local YYYYMMDD after validated RTC/NTP
  uint64_t last_session_id = 0;  // durable, unique, increasing
  uint8_t day_bond_awards = 0;  // max two per calendar day
  uint16_t bond = 0;
  uint8_t unlock_bits = 0;
};
struct StudyBondResult {
  bool accepted = false;
  uint16_t minutes_credited = 0;
  uint8_t new_stars = 0;
  uint8_t new_unlocks = 0;
  uint8_t bond_gained = 0;
};
// Commit only after a completed Focus timer, never from a generic timer,
// a pause, a session reset, or the 5-min rest phase.
// Presets are fixed to 15/25/45min to prevent accidental custom over-awards.
inline bool verified_local_day_key(uint32_t k) {
  const uint32_t year=k/10000u;
  const uint32_t month=(k/100u)%100u;
  const uint32_t day=k%100u;
  if(year<2020u||year>2099u||month<1u||month>12u||day<1u)return false;
  const bool leap=(year%4u==0u && (year%100u!=0u||year%400u==0u));
  const uint8_t days[]={31,static_cast<uint8_t>(leap?29:28),31,30,31,30,31,31,30,31,30,31};
  return day<=days[month-1u];
}
inline StudyBondResult commit_verified_focus(StudyBondProgress& p, uint64_t id,
                                             uint16_t duration_minutes,
                                             uint32_t local_day_key) {
  StudyBondResult out{};
  if (id == 0 || id <= p.last_session_id) return out;
  if (duration_minutes != 15 && duration_minutes != 25 && duration_minutes != 45) return out;
  // Reject absent/not-yet-synchronized dates for time-bound daily bond.
  // Focus itself may still run offline, but date-dependent rewards need trust.
  if (!verified_local_day_key(local_day_key)) return out;
  if (p.last_day_key != 0u && local_day_key < p.last_day_key) return out;
  if (p.total_focus_sessions == UINT32_MAX) return out;
  if (p.credited_minutes > UINT32_MAX - duration_minutes) return out;
  const uint32_t prev = p.credited_minutes;
  const uint32_t next = prev + duration_minutes;
  p.credited_minutes = next;
  p.total_focus_sessions++;
  p.last_session_id = id;
  const uint32_t stars = next/60u - prev/60u;
  p.total_stars += stars;
  out.accepted = true;
  out.minutes_credited = duration_minutes;
  out.new_stars = static_cast<uint8_t>(stars);

  constexpr struct{ uint32_t threshold; uint8_t mask; } milestones[] = {
    {60u,UNLOCK_GENGAR},{120u,UNLOCK_POSTCARD},{300u,UNLOCK_EGG},
    {600u,UNLOCK_BADGE},{1200u,UNLOCK_ROOM}
  };
  for (const auto& m:milestones) {
    if (prev < m.threshold && next >= m.threshold && !(p.unlock_bits & m.mask)) {
      p.unlock_bits |= m.mask;
      out.new_unlocks |= m.mask;
    }
  }
  // Warm feedback at most twice per day — no coercive grind.
  if (p.last_day_key != local_day_key) {
    p.last_day_key = local_day_key;
    p.day_bond_awards = 0;
  }
  if (p.day_bond_awards < 2 && p.bond < 100) {
    p.bond++;
    p.day_bond_awards++;
    out.bond_gained = 1;
  }
  return out;
}
