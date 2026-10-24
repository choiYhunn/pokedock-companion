// Independent regression suite for pokedock_core.hpp (M6).
// Includes the nine 2026-10-24 audit probes (A1..A6, F1..F3) plus a 400-day real-time daily
// alarm simulation and a randomized clock-jump fuzz with invariant checks.
#include "../core/pokedock_core.hpp"

#include <cstdio>
#include <cstdlib>
#include <map>
#include <random>
#include <string>

using namespace pokedock;
static int g_pass = 0, g_fail = 0;
#define CHECK(name, cond)                                         \
  do {                                                            \
    if (cond) {                                                   \
      ++g_pass;                                                   \
    } else {                                                      \
      ++g_fail;                                                   \
      std::printf("FAIL %s (%s:%d)\n", name, __FILE__, __LINE__); \
    }                                                             \
  } while (0)

static int64_t A(int day, int hh, int mm) { return int64_t(day) * kMinutesPerDay + hh * 60 + mm; }

static void audit_probes() {
  {  // A1 reboot inside alarm minute must still ring
    Core c;
    c.set_alarm(7, 0, true, A(99, 20, 0));
    Core rebooted;
    rebooted.restore(c.alarm(), c.persisted());
    rebooted.tick(0, A(100, 7, 0));
    CHECK("A1 reboot in alarm minute rings", rebooted.alarm_ringing());
  }
  {  // A2 23:59 alarm with poll gap over midnight
    Core c;
    c.set_alarm(23, 59, true, A(100, 12, 0));
    c.tick(0, A(100, 23, 58));
    c.tick(120000, A(101, 0, 0));
    CHECK("A2 23:59 over midnight rings", c.alarm_ringing());
  }
  {  // A3 forward time sync over the alarm
    Core c;
    c.set_alarm(7, 0, true, A(99, 22, 0));
    c.tick(0, A(100, 6, 58));
    c.tick(1000, A(100, 7, 1));
    CHECK("A3 forward sync jump rings", c.alarm_ringing());
  }
  {  // A4 snooze while wall clock untrusted
    Core c;
    c.set_alarm(7, 0, true, A(99, 22, 0));
    c.tick(0, A(100, 7, 0));
    c.snooze_alarm(1000);
    c.tick(1000 + 5 * 60000, -1);
    CHECK("A4 snooze fires without trusted clock", c.alarm_ringing());
  }
  {  // A5 ringing auto-stops
    Core c;
    c.set_alarm(7, 0, true, A(99, 22, 0));
    c.tick(0, A(100, 7, 0));
    c.tick(kRingMaxMs, A(100, 7, 2));
    CHECK("A5 ring auto-snoozes after 2 min", !c.alarm_ringing() && c.snooze_pending());
    int64_t t = kRingMaxMs;
    int gave_up = 0, rings = 1;
    for (int i = 0; i < 20000 && !gave_up; ++i) {
      t += 1000;
      uint32_t ev = c.tick(t, -1);
      rings += (ev & kEvAlarmRing) ? 1 : 0;
      gave_up = (ev & kEvAlarmGaveUp) ? 1 : 0;
    }
    CHECK("A5 gives up after 3 auto snoozes", gave_up && rings == 4 && !c.alarm_ringing() && !c.snooze_pending());
  }
  {  // A6 reboot after dismiss must not ring again
    Core c;
    c.set_alarm(7, 0, true, A(99, 22, 0));
    c.tick(0, A(100, 7, 0));
    c.dismiss_alarm();
    CHECK("A6 fire marks persist dirty", c.take_persist_dirty());
    Core rebooted;
    rebooted.restore(c.alarm(), c.persisted());
    rebooted.tick(0, A(100, 7, 1));
    CHECK("A6 no duplicate after reboot", !rebooted.alarm_ringing());
  }
  {  // F1 start while running refused
    Core c;
    c.start_focus(25, 0);
    CHECK("F1 start while running refused", !c.start_focus(15, 600000));
    CHECK("F1 remaining untouched", c.focus_remaining(600000) == 1500000 - 600000);
    c.pause_focus(700000);
    CHECK("F1 start while paused refused", !c.start_focus(15, 800000));
    CHECK("F1 cancel then start", c.cancel_focus() && c.start_focus(15, 800000));
  }
  {  // F2 single completion edge
    Core c;
    c.start_focus(1, 0);
    uint32_t a = c.tick(60000, -1), b = c.tick(61000, -1), d = c.tick(3600000, -1);
    CHECK("F2 completion event once", (a & kEvFocusComplete) && !(b & kEvFocusComplete) && !(d & kEvFocusComplete));
    CHECK("F2 completed count 1", c.focus_completed_count() == 1 && c.focus_phase() == FocusPhase::kDone);
    CHECK("F2 restart after done allowed", c.start_focus(25, 3600000));
  }
  {  // F3 pause/resume exact
    Core c;
    c.start_focus(25, 0);
    int64_t t = 0;
    for (int i = 0; i < 100; ++i) {
      t += 7000;
      c.pause_focus(t);
      t += 3000;
      c.resume_focus(t);
    }
    CHECK("F3 100 pause/resume exact", c.focus_remaining(t) == 1500000 - 700000);
  }
}

static void timer_spec() {
  Core c;
  CHECK("T 25:00 at start", c.start_focus(25, 1000) && c.focus_remaining(1000) == 1500000);
  CHECK("T 24:59 after 1s", c.focus_remaining(2000) == 1499000);
  c.pause_focus(5000);
  CHECK("T paused frozen", c.focus_remaining(5000) == c.focus_remaining(99999999));
  c.resume_focus(10000);
  CHECK("T resume continues", c.focus_remaining(11000) == 1495000);
  CHECK("T reset clears", c.cancel_focus() && c.focus_remaining(12000) == 0 && c.focus_phase() == FocusPhase::kIdle);
  uint32_t ev = c.tick(99999999, -1);
  CHECK("T no stale completion after reset", !(ev & kEvFocusComplete) && c.focus_completed_count() == 0);
  for (int m : {15, 25, 45, 60}) {
    Core p;
    CHECK("T presets valid", p.start_focus(m, 0) && p.focus_remaining(0) == int64_t(m) * 60000);
  }
  CHECK("T bounds", !c.start_focus(0, 0) && !c.start_focus(121, 0));
}

static void alarm_spec() {
  {  // setting an alarm whose minute already passed today must not fire now, but tomorrow
    Core c;
    c.set_alarm(7, 0, true, A(100, 7, 3));
    c.tick(0, A(100, 7, 3));
    CHECK("S set-in-past does not fire now", !c.alarm_ringing());
    c.tick(1000, A(101, 7, 0));
    CHECK("S fires next day", c.alarm_ringing());
  }
  {  // stale alarm after long outage
    Core c;
    c.set_alarm(7, 0, true, A(99, 20, 0));
    c.tick(0, A(100, 7, 0) + kAlarmGraceMin + 1);
    CHECK("S stale (grace+1) never fires", !c.alarm_ringing());
  }
  {  // backward correction after firing must not duplicate
    Core c;
    c.set_alarm(7, 0, true, A(99, 20, 0));
    c.tick(0, A(100, 7, 0));
    c.dismiss_alarm();
    c.tick(1000, A(100, 6, 50));
    c.tick(600000, A(100, 7, 0));
    CHECK("S backward jump no duplicate", !c.alarm_ringing());
  }
  {  // disabled alarm
    Core c;
    c.set_alarm(7, 0, false, A(99, 20, 0));
    c.tick(0, A(100, 7, 0));
    CHECK("S disabled silent", !c.alarm_ringing());
  }
  {  // 00:00 alarm
    Core c;
    c.set_alarm(0, 0, true, A(99, 20, 0));
    c.tick(0, A(99, 23, 59));
    CHECK("S 00:00 not early", !c.alarm_ringing());
    c.tick(60000, A(100, 0, 0));
    CHECK("S 00:00 fires", c.alarm_ringing());
  }
  {  // untrusted clock never fires schedule
    Core c;
    c.set_alarm(7, 0, true, -1);
    c.tick(0, -1);
    CHECK("S untrusted clock silent", !c.alarm_ringing());
  }
  {  // local time conversion: 2026-10-24 22:30 UTC = 2026-10-25 07:30 KST
    int64_t abs = local_abs_minutes(1792881000LL, 540);
    CHECK("S KST conversion minute", abs_minute_of_day(abs) == 7 * 60 + 30);
    CHECK("S KST conversion day", abs_day(abs) == abs_day(local_abs_minutes(1792881000LL - 22 * 3600 - 1800, 540)) + 1);
  }
  {  // settings validation
    Core c;
    CHECK("S partner valid", c.set_partner(385) && !c.set_partner(900) && c.partner() == 385);
    CHECK("S brightness range", !c.set_brightness(0) && !c.set_brightness(101) && c.set_brightness(100));
    CHECK("S alarm ranges", !c.set_alarm(24, 0, true, -1) && !c.set_alarm(7, 60, true, -1) && !c.set_alarm(-1, 0, true, -1));
  }
}

// 400 days at 1 s resolution with alarm 07:30: exactly one ring per day, at 07:30.
static void daily_realtime_sim() {
  Core c;
  const int64_t start = A(20000, 12, 0);
  c.set_alarm(7, 30, true, start);
  int rings = 0, wrong_minute = 0;
  int64_t mono = 0;
  for (int64_t s = 0; s < int64_t(400) * 86400; s += 1, mono += 1000) {
    int64_t now = start + s / 60;
    uint32_t ev = c.tick(mono, now);
    if (ev & kEvAlarmRing) {
      ++rings;
      if (abs_minute_of_day(now) != 7 * 60 + 30) ++wrong_minute;
      c.dismiss_alarm();
    }
  }
  CHECK("D 400 days -> 400 rings", rings == 400);
  CHECK("D always at 07:30", wrong_minute == 0);
}

// Random clock jumps, reboots and polling gaps; check invariants.
static void fuzz() {
  std::mt19937_64 rng(20261024);
  int violations = 0, total_rings = 0;
  for (int run = 0; run < 300; ++run) {
    Core c;
    int hh = int(rng() % 24), mm = int(rng() % 60);
    int64_t now = A(30000, int(rng() % 24), int(rng() % 60));
    c.set_alarm(hh, mm, true, now);
    PersistedAlarmState nv = c.persisted();
    std::map<int, int> rings_per_day;
    int64_t mono = 0;
    for (int step = 0; step < 6000; ++step) {
      int r = int(rng() % 1000);
      if (r < 900) now += 1;                         // normal minute
      else if (r < 960) now += 1 + rng() % 30;       // poll gap / forward sync
      else if (r < 985) now -= int64_t(rng() % 20);  // backward sync
      else {                                          // reboot: restore persisted state only
        AlarmConfig cfg = c.alarm();
        c = Core();
        c.restore(cfg, nv);
      }
      mono += 60000;
      uint32_t ev = c.tick(mono, now);
      if (c.take_persist_dirty()) nv = c.persisted();
      if (ev & kEvAlarmRing) {
        if (c.snooze_pending()) continue;
        int day = c.persisted().last_fired_day;
        int64_t target = int64_t(day) * kMinutesPerDay + hh * 60 + mm;
        ++rings_per_day[day];
        ++total_rings;
        if (now < target || now - target > kAlarmGraceMin) ++violations;
        c.dismiss_alarm();
      }
    }
    for (auto &kv : rings_per_day)
      if (kv.second > 1) ++violations;
  }
  CHECK("Z fuzz: once per day, never early, never > grace late", violations == 0);
  CHECK("Z fuzz: alarms actually fire", total_rings > 500);
  std::printf("fuzz rings=%d violations=%d\n", total_rings, violations);
}

int main() {
  audit_probes();
  timer_spec();
  alarm_spec();
  daily_realtime_sim();
  fuzz();
  std::printf("%s: %d passed, %d failed\n", g_fail ? "FAIL" : "PASS", g_pass, g_fail);
  return g_fail ? 1 : 0;
}
