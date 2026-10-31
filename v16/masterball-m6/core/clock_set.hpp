// On-device clock setting without a phone (M6 has no RTC backup cell, and iPhone Safari cannot
// reach the ball over BLE). The ball edits a local date/time one field at a time; this header holds
// the calendar math and field stepping so the host tests cover exactly what the firmware runs.
#pragma once
#include <cstdint>

#include "pokedock_core.hpp"

namespace pokedock {

static constexpr int kClockMinYear = 2026;  // same window the BLE time_sync command accepts
static constexpr int kClockMaxYear = 2099;

struct LocalDateTime {
  int year = kClockMinYear, month = 1, day = 1, hour = 0, minute = 0;
};

enum class ClockField : uint8_t { kYear, kMonth, kDay, kHour, kMinute };

inline bool is_leap_year(int y) { return (y % 4 == 0 && y % 100 != 0) || y % 400 == 0; }
inline int days_in_month(int y, int m) {
  static constexpr int kDays[12] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
  return m == 2 && is_leap_year(y) ? 29 : kDays[(m - 1) % 12];
}

// days since 1970-01-01 (proleptic Gregorian, Howard Hinnant's algorithms)
inline int64_t days_from_civil(int y, int m, int d) {
  y -= m <= 2;
  const int64_t era = (y >= 0 ? y : y - 399) / 400;
  const int64_t yoe = y - era * 400;
  const int64_t doy = (153 * (m > 2 ? m - 3 : m + 9) + 2) / 5 + d - 1;
  const int64_t doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
  return era * 146097 + doe - 719468;
}
inline void civil_from_days(int64_t z, int &y, int &m, int &d) {
  z += 719468;
  const int64_t era = (z >= 0 ? z : z - 146096) / 146097;
  const int64_t doe = z - era * 146097;
  const int64_t yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
  const int64_t doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
  const int64_t mp = (5 * doy + 2) / 153;
  d = int(doy - (153 * mp + 2) / 5 + 1);
  m = int(mp < 10 ? mp + 3 : mp - 9);
  y = int(yoe + era * 400 + (m <= 2));
}

inline bool valid_local(const LocalDateTime &t) {
  return t.year >= kClockMinYear && t.year <= kClockMaxYear && t.month >= 1 && t.month <= 12 && t.day >= 1 &&
         t.day <= days_in_month(t.year, t.month) && t.hour >= 0 && t.hour <= 23 && t.minute >= 0 && t.minute <= 59;
}

// Local wall time + fixed offset (minutes, Korea = +540) -> UTC epoch seconds.
inline int64_t local_to_utc(const LocalDateTime &t, int tz_offset_min) {
  const int64_t local_min = days_from_civil(t.year, t.month, t.day) * kMinutesPerDay + t.hour * 60 + t.minute;
  return (local_min - tz_offset_min) * 60;
}
inline LocalDateTime local_from_utc(int64_t utc_epoch_s, int tz_offset_min) {
  const int64_t abs = local_abs_minutes(utc_epoch_s, tz_offset_min);
  LocalDateTime t;
  civil_from_days(abs_day(abs), t.year, t.month, t.day);
  const int mod = abs_minute_of_day(abs);
  t.hour = mod / 60;
  t.minute = mod % 60;
  return t;
}

inline int wrap(int v, int lo, int hi) {
  const int n = hi - lo + 1;
  return lo + ((v - lo) % n + n) % n;
}

// +/- one field. Every field wraps inside its own range (no carry into the next field, so a
// long press on "minute" never changes the hour); the day is clamped when month/year change.
inline LocalDateTime step_field(LocalDateTime t, ClockField f, int delta) {
  switch (f) {
    case ClockField::kYear: t.year = wrap(t.year + delta, kClockMinYear, kClockMaxYear); break;
    case ClockField::kMonth: t.month = wrap(t.month + delta, 1, 12); break;
    case ClockField::kDay: t.day = wrap(t.day + delta, 1, days_in_month(t.year, t.month)); break;
    case ClockField::kHour: t.hour = wrap(t.hour + delta, 0, 23); break;
    case ClockField::kMinute: t.minute = wrap(t.minute + delta, 0, 59); break;
  }
  if (t.day > days_in_month(t.year, t.month)) t.day = days_in_month(t.year, t.month);
  return t;
}

inline int field_value(const LocalDateTime &t, ClockField f) {
  switch (f) {
    case ClockField::kYear: return t.year;
    case ClockField::kMonth: return t.month;
    case ClockField::kDay: return t.day;
    case ClockField::kHour: return t.hour;
    default: return t.minute;
  }
}

// Where the editor starts after a power cut: the last known date (phone sync or previous manual
// setting), never earlier than the firmware build date, so an untouched "다음, 다음…" still lands on
// a plausible day. The alarm logic only needs the date to be right to the day the user confirms.
inline LocalDateTime suggest_clock_start(int64_t last_known_utc, int64_t build_utc, int tz_offset_min) {
  const int64_t base = last_known_utc > build_utc ? last_known_utc : build_utc;
  LocalDateTime t = local_from_utc(base, tz_offset_min);
  if (t.year < kClockMinYear) t = LocalDateTime{};
  if (t.year > kClockMaxYear) t.year = kClockMaxYear;
  return t;
}

}  // namespace pokedock
