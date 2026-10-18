#include <cassert>
#include <iostream>
#include "../study_bond_policy.h"

int main() {
  StudyBondProgress p{};
  auto a=commit_verified_focus(p,1,15,20261018);
  assert(a.accepted && a.minutes_credited==15 && a.new_stars==0);
  assert(p.credited_minutes==15 && p.bond==1);
  auto dup=commit_verified_focus(p,1,15,20261018);
  assert(!dup.accepted && p.credited_minutes==15);
  auto bad=commit_verified_focus(p,2,5,20261018);
  assert(!bad.accepted && p.last_session_id==1);
  a=commit_verified_focus(p,2,45,20261018);
  assert(a.accepted && p.credited_minutes==60 && a.new_stars==1);
  assert(a.new_unlocks & UNLOCK_GENGAR);
  assert(p.bond==2);
  a=commit_verified_focus(p,3,45,20261018);
  assert(a.accepted && p.bond==2 && p.credited_minutes==105);
  a=commit_verified_focus(p,4,15,20261019);
  assert(a.accepted && (a.new_unlocks & UNLOCK_POSTCARD));
  assert(p.bond==3 && p.credited_minutes==120);
  assert(p.total_stars==2);
  for(uint64_t id=5; id<=16; id++){
    auto r=commit_verified_focus(p,id,15,20261020);
    assert(r.accepted);
  }
  assert(p.credited_minutes==300);
  assert(p.unlock_bits & UNLOCK_EGG);
  for(uint64_t id=17; id<=36; ++id) assert(commit_verified_focus(p,id,15,20261021).accepted);
  assert(p.credited_minutes==600 && (p.unlock_bits & UNLOCK_BADGE));
  for(uint64_t id=37; id<=76; ++id) assert(commit_verified_focus(p,id,15,20261022).accepted);
  assert(p.credited_minutes==1200 && (p.unlock_bits & UNLOCK_ROOM));
  assert(p.total_stars==20);
  assert(p.total_focus_sessions==76);
  assert(!commit_verified_focus(p,76,45,20261022).accepted);
  assert(!commit_verified_focus(p,77,45,0).accepted);
  assert(!commit_verified_focus(p,77,45,20999999).accepted);
  assert(!commit_verified_focus(p,77,45,20260230).accepted);
  assert(!commit_verified_focus(p,77,45,20261021).accepted);
  std::cout << "V11 deterministic Focus progression PASS\n";
}
