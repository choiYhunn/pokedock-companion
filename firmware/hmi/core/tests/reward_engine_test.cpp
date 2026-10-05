#include <cassert>
#include <iostream>
#include "../reward_engine.h"

int main(){
  RewardEngine e;
  auto short_run=e.onFocusComplete(9*60,0,123);
  assert(short_run.exp_gained==0); assert(short_run.bond_gained==0); assert(short_run.egg_progress_gained==0);
  auto normal=e.onFocusComplete(25*60,4,12345);
  assert(normal.exp_gained==25); assert(normal.bond_gained==2); assert(normal.egg_progress_gained==8);
  if(normal.encounter) assert(normal.pokemon_id!=0);
  auto capped=e.onFocusComplete(200*60,20,777); assert(capped.exp_gained==120);
  std::cout<<"PokéDock reward tests passed\n"; return 0;
}
