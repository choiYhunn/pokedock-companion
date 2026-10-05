#include "reward_engine.h"

static constexpr uint16_t kEncounterPool[] = {
  25, 37, 39, 54, 133, 143, 196, 197,
  258, 280, 447, 492, 570, 700, 702, 778
};

uint32_t RewardEngine::xorshift32(uint32_t x) {
  if (x == 0) x = 0x9E3779B9u;
  x ^= x << 13; x ^= x >> 17; x ^= x << 5; return x;
}

RewardResult RewardEngine::onFocusComplete(uint32_t duration_s, uint16_t streak_days, uint32_t entropy_seed) const {
  RewardResult out{};
  const uint32_t minutes = duration_s / 60u;
  if (minutes < 10u) return out;
  out.exp_gained = static_cast<uint16_t>(minutes > 120u ? 120u : minutes);
  out.bond_gained = static_cast<uint8_t>(minutes >= 25u ? 2u : 1u);
  out.egg_progress_gained = static_cast<uint8_t>(minutes >= 25u ? 8u : 3u);
  uint32_t chance = 20u + (minutes >= 25u ? 10u : 0u) + (streak_days > 10u ? 20u : streak_days * 2u);
  if (chance > 60u) chance = 60u;
  const uint32_t r = xorshift32(entropy_seed ^ duration_s ^ (static_cast<uint32_t>(streak_days) << 16));
  out.encounter = (r % 100u) < chance;
  if (out.encounter) {
    out.pokemon_id = kEncounterPool[(r >> 8) % (sizeof(kEncounterPool) / sizeof(kEncounterPool[0]))];
    out.shiny = ((r >> 16) % 128u) == 0u;
  }
  return out;
}
