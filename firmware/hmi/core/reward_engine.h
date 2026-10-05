#pragma once
#include <stdint.h>

struct RewardResult {
  uint16_t exp_gained = 0;
  bool encounter = false;
  uint16_t pokemon_id = 0;
};

class RewardEngine {
 public:
  RewardResult onFocusComplete(uint32_t duration_s,
                               uint16_t streak_days,
                               uint32_t entropy_seed) const;

 private:
  static uint32_t xorshift32(uint32_t x);
};
