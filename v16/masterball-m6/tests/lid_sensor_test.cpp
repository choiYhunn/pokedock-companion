// Host test of core/lid_sensor.hpp (M7 lid reed sensor): debounce, events, fail-safe, touch override.
// build: g++ -std=c++17 -O1 -Wall -Wextra -Werror -I. tests/lid_sensor_test.cpp -o build/lid_sensor_test
#include <cstdio>

#include "core/lid_sensor.hpp"

using pokedock::LidEvent;
using pokedock::LidSensor;

static int g_fail = 0, g_n = 0;
static void check(const char *name, bool ok) {
  ++g_n;
  std::printf("%s %s\n", ok ? "PASS" : "FAIL", name);
  if (!ok) ++g_fail;
}

// feed `level` every 250 ms (the firmware main loop period) from t0 to t1, return the events seen
static int feed(LidSensor &s, bool closed, int64_t t0, int64_t t1, LidEvent *last, int64_t step = 250) {
  int n = 0;
  for (int64_t t = t0; t <= t1; t += step) {
    LidEvent e = s.update(closed, t);
    if (e != LidEvent::kNone) {
      ++n;
      *last = e;
    }
  }
  return n;
}

int main() {
  LidEvent e = LidEvent::kNone;
  {
    LidSensor s;
    check("starts open: screen allowed with no sensor reading yet", s.screen_allowed(0) && !s.closed());
    check("no sensor (pull-up = open) for 10 min: no event, screen allowed",
          feed(s, false, 0, 600000, &e) == 0 && s.screen_allowed(600000));
  }
  {
    LidSensor s;
    check("lid closes: exactly one kClosed after debounce", feed(s, true, 0, 2000, &e) == 1 && e == LidEvent::kClosed);
    check("closed: screen not allowed", !s.screen_allowed(2000));
    check("lid opens: exactly one kOpened", feed(s, false, 2250, 4000, &e) == 1 && e == LidEvent::kOpened);
    check("open: screen allowed", s.screen_allowed(4000));
  }
  {
    LidSensor s;
    // contact chatter shorter than the debounce never produces an event
    int n = 0;
    for (int64_t t = 0; t < 5000; t += 50) {
      if (s.update((t / 50) % 2 == 0, t) != LidEvent::kNone) ++n;
    }
    check("chatter faster than 120 ms: no event", n == 0 && !s.closed());
    check("one 1 ms sample loop at 10 ms: closes after >= 120 ms", [&] {
      LidSensor q;
      int64_t when = -1;
      for (int64_t t = 0; t < 1000; t += 10)
        if (q.update(true, t) == LidEvent::kClosed) { when = t; break; }
      return when >= 120 && when <= 130;
    }());
  }
  {
    LidSensor s;
    feed(s, true, 0, 1000, &e);
    s.touched(1000);
    check("touch while 'closed': screen on for 60 s", s.screen_allowed(1000) && s.screen_allowed(60999) && !s.screen_allowed(61000));
    s.touched(70000);
    s.touched(80000);
    check("3 touches while 'closed': sensor ignored (stuck closed / wrong magnet)", s.ignored() && s.screen_allowed(10000000));
    check("ignored sensor: closing again gives no event", feed(s, true, 80250, 90000, &e) == 0);
    feed(s, false, 90250, 91000, &e);
    check("a real opening re-arms the sensor", !s.ignored());
    check("re-armed: next close is reported", feed(s, true, 91250, 92000, &e) == 1 && e == LidEvent::kClosed);
  }
  {
    LidSensor s;
    s.set_enabled(false);
    check("disabled (setting off): closing gives no event and screen stays allowed",
          feed(s, true, 0, 5000, &e) == 0 && s.screen_allowed(5000));
  }
  std::printf("%s: %d/%d lid sensor checks\n", g_fail ? "FAIL" : "PASS", g_n - g_fail, g_n);
  return g_fail ? 1 : 0;
}
