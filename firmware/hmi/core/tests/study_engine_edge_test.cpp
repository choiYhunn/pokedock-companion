#include <cassert>
#include <iostream>
#include "../study_engine.h"
int main(){
  StudyEngine e;
  e.startFocus(0,1000);
  assert(e.snapshot().mode==RunMode::IDLE);
  assert(e.tick(2000)==StudyEvent::NONE);
  e.startFocus(60,1000);
  assert(e.snapshot().mode==RunMode::IDLE); // no demo cheat credit
  e.startCountdown(0,1000);
  assert(e.snapshot().mode==RunMode::IDLE);
  e.startFocus(900,1000); // 15min
  assert(e.tick(11000)==StudyEvent::TICK);
  e.pause(14000);
  assert(e.snapshot().elapsed_s==13);
  assert(e.snapshot().remaining_s==887); // freeze() must update on pause
  e.resume(13000); // invalid clock rollback: remain paused
  assert(e.snapshot().paused);
  assert(e.tick(910000)==StudyEvent::NONE);
  e.resume(14000);
  assert(!e.snapshot().paused);
  assert(e.tick(901000)==StudyEvent::FOCUS_COMPLETE);
  assert(e.tick(902000)==StudyEvent::NONE); // exactly one completion event
  assert(e.snapshot().today_sessions==1);
  e.startCountdown(180,1000000);
  assert(e.tick(1180000)==StudyEvent::COUNTDOWN_COMPLETE);
  assert(e.snapshot().today_sessions==1); // no credit from plain timer
  e.startFocus(1500,2000000);
  e.stop(2010000);
  assert(e.tick(4000000)==StudyEvent::NONE);
  assert(e.snapshot().today_sessions==1); // abort gives nothing
  std::cout<<"StudyEngine edge cases/invalid presets/rollback/duplicate PASS\n";
}
