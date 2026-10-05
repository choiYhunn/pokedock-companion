#include <cassert>
#include <iostream>
#include "../study_engine.h"
#include "../notification_filter.h"

int main() {
  StudyEngine e;

  e.startFocus(1500, 1000);
  assert(e.tick(601000) == StudyEvent::TICK);
  assert(e.snapshot().elapsed_s == 600);
  assert(e.snapshot().remaining_s == 900);

  e.pause(601000);
  e.resume(901000); // 300 s pause
  assert(e.tick(1501000) == StudyEvent::TICK);
  assert(e.snapshot().elapsed_s == 1200);
  assert(e.snapshot().remaining_s == 300);

  assert(e.tick(1801000) == StudyEvent::FOCUS_COMPLETE);
  assert(e.snapshot().today_focus_s == 1500);
  assert(e.snapshot().today_sessions == 1);

  e.startStopwatch(5000);
  assert(e.tick(65000) == StudyEvent::TICK);
  assert(e.snapshot().elapsed_s == 60);
  assert(e.lap(70000) == StudyEvent::LAP);
  assert(e.snapshot().lap_count == 1);

  NotificationPolicy policy;
  assert(notification_allowed(NoticeClass::CALL, policy));
  assert(notification_allowed(NoticeClass::CALENDAR, policy));
  assert(!notification_allowed(NoticeClass::SYSTEM, policy));

  std::cout << "PokéDock core tests passed\n";
  return 0;
}
