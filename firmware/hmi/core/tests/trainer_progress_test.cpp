#include <cassert>
#include <iostream>
#include "../trainer_progress.h"

int main(){
  TrainerProgress p; p.study_exp=350; p.partner_level=12; p.bond=99; p.egg_progress=96; p.total_sessions=4;
  RewardResult r; r.exp_gained=25; r.bond_gained=2; r.egg_progress_gained=8; r.encounter=true; r.pokemon_id=280; r.shiny=true;
  auto out=apply_focus_reward(p,r);
  assert(p.partner_level==13);
  assert(p.study_exp==15);
  assert(p.bond==100);
  assert(p.egg_progress==4);
  assert(out.level_up); assert(out.egg_ready); assert(out.new_catch);
  assert(p.shiny_count==1);
  assert(has_badge(p,BADGE_ROUTINE));
  std::cout<<"PokéDock progression tests passed\n"; return 0;
}
