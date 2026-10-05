#pragma once
#include <stdint.h>
#include "reward_engine.h"

enum TrainerBadge : uint16_t {
  BADGE_FOCUS=1u<<0, BADGE_STREAK=1u<<1, BADGE_ROUTINE=1u<<2,
  BADGE_NIGHT=1u<<3, BADGE_DEX=1u<<4, BADGE_WISH=1u<<5
};

struct TrainerProgress {
  uint16_t partner_id=468; uint16_t partner_level=12; uint8_t bond=67;
  uint16_t study_exp=285; uint8_t egg_progress=42;
  uint32_t total_sessions=3; uint16_t streak_days=4;
  uint16_t badge_bits=BADGE_FOCUS|BADGE_STREAK;
  uint16_t caught_ids[32] = {}; uint8_t caught_count=0; uint8_t shiny_count=0;
};

struct ProgressApplyResult { bool level_up=false; bool egg_ready=false; bool new_catch=false; bool new_badge=false; };

bool has_badge(const TrainerProgress& p, TrainerBadge badge);
bool add_badge(TrainerProgress& p, TrainerBadge badge);
bool has_caught(const TrainerProgress& p, uint16_t pokemon_id);
bool add_caught(TrainerProgress& p, uint16_t pokemon_id);
ProgressApplyResult apply_focus_reward(TrainerProgress& p, const RewardResult& reward);
