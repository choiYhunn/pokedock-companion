#include <cassert>
#include <iostream>
#include "../reward_engine.h"

int main() {
  RewardEngine e;

  auto too_short = e.onFocusComplete(9 * 60, 0, 123);
  assert(too_short.exp_gained == 0);
  assert(!too_short.encounter);

  auto normal = e.onFocusComplete(25 * 60, 4, 12345);
  assert(normal.exp_gained == 25);
  if (normal.encounter) assert(normal.pokemon_id != 0);

  auto capped = e.onFocusComplete(200 * 60, 20, 777);
  assert(capped.exp_gained == 120);

  std::cout << "PokéDock reward tests passed\n";
  return 0;
}
