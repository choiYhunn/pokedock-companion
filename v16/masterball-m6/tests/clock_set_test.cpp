// Host tests for on-device clock setting (core/clock_set.hpp + Core::wall_clock_set).
// The timer/alarm regression suite (core_regression_test.cpp) is unchanged and still runs.
#include "../core/clock_set.hpp"

#include <cstdio>
#include <ctime>

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

static bool same(const LocalDateTime &a, const LocalDateTime &b) {
  return a.year == b.year && a.month == b.month && a.day == b.day && a.hour == b.hour && a.minute == b.minute;
}

static void calendar() {
  CHECK("leap 2028", is_leap_year(2028) && days_in_month(2028, 2) == 29);
  CHECK("2100 not leap", !is_leap_year(2100));
  CHECK("2026-02 has 28", days_in_month(2026, 2) == 28);
  // 2026-10-31 07:30 KST == 2026-10-30 22:30 UTC == 1793399400
  const LocalDateTime t{2026, 10, 31, 7, 30};
  CHECK("KST to UTC", local_to_utc(t, 540) == 1793399400LL);
  CHECK("UTC back to KST", same(local_from_utc(1793399400LL, 540), t));
  // the BLE time_sync window starts at 2026-01-01 00:00 UTC; the editor's minimum is inside it
  CHECK("editor minimum accepted by time_sync range", local_to_utc(LocalDateTime{2026, 1, 1, 9, 0}, 540) >= 1767225600LL);
  CHECK("editor maximum accepted", local_to_utc(LocalDateTime{2099, 12, 31, 23, 59}, 540) <= 4102444800LL);
  // exhaustive round trip over every minute of 2026..2099 sampled daily at a moving minute
  int bad = 0;
  for (int64_t d = days_from_civil(2026, 1, 1); d < days_from_civil(2100, 1, 1); ++d) {
    LocalDateTime x;
    civil_from_days(d, x.year, x.month, x.day);
    x.hour = int(d % 24);
    x.minute = int(d % 60);
    if (!valid_local(x) || !same(local_from_utc(local_to_utc(x, 540), 540), x)) ++bad;
  }
  CHECK("daily round trip 2026-2099", bad == 0);
  // cross-check with the C library for a UTC offset of 0
  const int64_t u = local_to_utc(LocalDateTime{2031, 3, 15, 12, 34}, 0);
  std::time_t tt = static_cast<std::time_t>(u);
  std::tm *g = std::gmtime(&tt);
  CHECK("matches gmtime", g && g->tm_year + 1900 == 2031 && g->tm_mon + 1 == 3 && g->tm_mday == 15 && g->tm_hour == 12 &&
                              g->tm_min == 34);
}

static void stepping() {
  LocalDateTime t{2026, 1, 31, 23, 59};
  CHECK("minute wraps without touching hour", same(step_field(t, ClockField::kMinute, 1), LocalDateTime{2026, 1, 31, 23, 0}));
  CHECK("hour wraps without touching day", same(step_field(t, ClockField::kHour, 1), LocalDateTime{2026, 1, 31, 0, 59}));
  CHECK("Jan 31 -> Feb clamps day to 28", same(step_field(t, ClockField::kMonth, 1), LocalDateTime{2026, 2, 28, 23, 59}));
  CHECK("day wraps inside month", step_field(t, ClockField::kDay, 1).day == 1);
  CHECK("minute down from 0", step_field(LocalDateTime{2026, 5, 5, 5, 0}, ClockField::kMinute, -1).minute == 59);
  CHECK("year wraps to max", step_field(LocalDateTime{2026, 5, 5, 5, 0}, ClockField::kYear, -1).year == kClockMaxYear);
  CHECK("Feb 29 leap -> non-leap year clamps", same(step_field(LocalDateTime{2028, 2, 29, 8, 0}, ClockField::kYear, 1),
                                                   LocalDateTime{2029, 2, 28, 8, 0}));
  CHECK("long press of 75 minutes", step_field(LocalDateTime{2026, 5, 5, 5, 10}, ClockField::kMinute, 75).minute == 25);
  // every value reachable from any start produces a valid date
  int bad = 0;
  LocalDateTime x{2026, 1, 1, 0, 0};
  for (int i = 0; i < 20000; ++i) {
    x = step_field(x, ClockField(i % 5), (i * 7919) % 13 - 6);
    if (!valid_local(x)) ++bad;
  }
  CHECK("random stepping stays valid", bad == 0);
  CHECK("field_value", field_value(LocalDateTime{2027, 4, 9, 6, 45}, ClockField::kDay) == 9);
}

static void suggestions() {
  const int64_t build = local_to_utc(LocalDateTime{2026, 10, 31, 0, 0}, 540);
  CHECK("never synced -> build date", same(suggest_clock_start(0, build, 540), LocalDateTime{2026, 10, 31, 0, 0}));
  const int64_t synced = local_to_utc(LocalDateTime{2026, 12, 24, 21, 15}, 540);
  CHECK("last sync wins when newer", same(suggest_clock_start(synced, build, 540), LocalDateTime{2026, 12, 24, 21, 15}));
}

static int64_t A(int day, int hh, int mm) { return int64_t(day) * kMinutesPerDay + hh * 60 + mm; }

static void alarm_after_manual_set() {
  {  // alarm already fired today, user re-sets the clock the same day: no second ring
    Core c;
    c.set_alarm(7, 0, true, A(99, 20, 0));
    c.tick(0, A(100, 7, 0));
    c.dismiss_alarm();
    c.wall_clock_set(A(100, 7, 3));
    c.tick(1000, A(100, 7, 3));
    CHECK("same-day reset does not re-ring", !c.alarm_ringing());
  }
  {  // a wrong future date had recorded day 120 as fired; the corrected clock (day 100) must ring
    Core c;
    c.set_alarm(7, 0, true, A(119, 20, 0));
    c.tick(0, A(120, 7, 0));
    c.dismiss_alarm();
    Core b;  // reboot after power cut (no RTC cell): NVS kept the bookkeeping
    b.restore(c.alarm(), c.persisted());
    b.wall_clock_set(A(100, 6, 0));
    CHECK("bookkeeping repaired is persisted", b.take_persist_dirty());
    b.tick(1000, A(100, 6, 59));
    CHECK("not early", !b.alarm_ringing());
    b.tick(2000, A(100, 7, 0));
    CHECK("corrected clock rings today", b.alarm_ringing());
  }
  {  // alarm armed under a future clock would stay silent until that moment: re-armed at "now"
    Core c;
    c.set_alarm(7, 0, true, A(200, 9, 0));
    c.wall_clock_set(A(150, 6, 0));
    c.tick(0, A(150, 7, 0));
    CHECK("re-armed alarm rings", c.alarm_ringing());
  }
  {  // setting the clock just after the alarm minute does not create a surprise ring for a past target
    Core c;
    c.set_alarm(7, 0, true, A(99, 20, 0));
    c.wall_clock_set(A(100, 12, 0));
    c.tick(0, A(100, 12, 0));
    CHECK("no stale ring", !c.alarm_ringing());
  }
  {  // untrusted clock is ignored
    Core c;
    c.set_alarm(7, 0, true, A(99, 20, 0));
    c.wall_clock_set(-1);
    CHECK("untrusted ignored", c.persisted().armed_after_abs == A(99, 20, 0));
  }
}

int main() {
  calendar();
  stepping();
  suggestions();
  alarm_after_manual_set();
  std::printf("%s: %d passed, %d failed\n", g_fail ? "FAIL" : "PASS", g_pass, g_fail);
  return g_fail ? 1 : 0;
}
