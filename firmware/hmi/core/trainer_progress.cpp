#include "trainer_progress.h"

bool has_badge(const TrainerProgress& p, TrainerBadge badge) {
  return (p.badge_bits & static_cast<uint16_t>(badge)) != 0;
}

bool add_badge(TrainerProgress& p, TrainerBadge badge) {
  const uint16_t bit=static_cast<uint16_t>(badge); const bool fresh=(p.badge_bits & bit)==0; p.badge_bits|=bit; return fresh;
}

bool has_caught(const TrainerProgress& p, uint16_t pokemon_id) {
  for(uint8_t i=0;i<p.caught_count;++i) if(p.caught_ids[i]==pokemon_id) return true;
  return false;
}

bool add_caught(TrainerProgress& p, uint16_t pokemon_id) {
  if(pokemon_id==0 || has_caught(p,pokemon_id) || p.caught_count>=32) return false;
  p.caught_ids[p.caught_count++]=pokemon_id; return true;
}

ProgressApplyResult apply_focus_reward(TrainerProgress& p, const RewardResult& reward) {
  ProgressApplyResult out{}; p.total_sessions++;
  const uint16_t bond_sum=static_cast<uint16_t>(p.bond)+reward.bond_gained;
  p.bond=static_cast<uint8_t>(bond_sum>100u?100u:bond_sum);
  uint16_t egg_sum=static_cast<uint16_t>(p.egg_progress)+reward.egg_progress_gained;
  if(egg_sum>=100u){egg_sum-=100u;out.egg_ready=true;} p.egg_progress=static_cast<uint8_t>(egg_sum);
  p.study_exp=static_cast<uint16_t>(p.study_exp+reward.exp_gained);
  const uint16_t threshold=static_cast<uint16_t>(p.partner_level*30u);
  if(p.study_exp>=threshold){p.study_exp=static_cast<uint16_t>(p.study_exp-threshold);p.partner_level++;out.level_up=true;}
  if(reward.encounter){out.new_catch=add_caught(p,reward.pokemon_id);if(reward.shiny)p.shiny_count++;}
  if(p.total_sessions>=5u) out.new_badge|=add_badge(p,BADGE_ROUTINE);
  if(p.caught_count>=12u) out.new_badge|=add_badge(p,BADGE_DEX);
  return out;
}
