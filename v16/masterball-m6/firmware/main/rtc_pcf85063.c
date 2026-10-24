// PCF85063A RTC (I2C 0x51). Stores UTC. The OS (oscillator-stop) flag in register 0x04 bit 7
// marks the time as untrusted after power loss without a backup cell.
#include "rtc_pcf85063.h"

#include "board.h"
#include "esp_log.h"

static const char *TAG = "pd_rtc";
static i2c_master_dev_handle_t s_dev;

static uint8_t bcd2bin(uint8_t v) { return (uint8_t)((v >> 4) * 10 + (v & 0x0F)); }
static uint8_t bin2bcd(int v) { return (uint8_t)(((v / 10) << 4) | (v % 10)); }

// days since 1970-01-01 for a civil date (Howard Hinnant's algorithm)
static int64_t days_from_civil(int y, unsigned m, unsigned d) {
  y -= m <= 2;
  const int64_t era = (y >= 0 ? y : y - 399) / 400;
  const unsigned yoe = (unsigned)(y - era * 400);
  const unsigned doy = (153 * (m > 2 ? m - 3 : m + 9) + 2) / 5 + d - 1;
  const unsigned doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
  return era * 146097 + (int64_t)doe - 719468;
}
static void civil_from_days(int64_t z, int *y, unsigned *m, unsigned *d) {
  z += 719468;
  const int64_t era = (z >= 0 ? z : z - 146096) / 146097;
  const unsigned doe = (unsigned)(z - era * 146097);
  const unsigned yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
  const unsigned doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
  const unsigned mp = (5 * doy + 2) / 153;
  *d = doy - (153 * mp + 2) / 5 + 1;
  *m = mp < 10 ? mp + 3 : mp - 9;
  *y = (int)(yoe + era * 400 + (*m <= 2));
}

bool pd_rtc_init(void) {
  const i2c_device_config_t dev = {.dev_addr_length = I2C_ADDR_BIT_LEN_7, .device_address = 0x51, .scl_speed_hz = 400000};
  if (i2c_master_bus_add_device(board_i2c(), &dev, &s_dev) != ESP_OK) return false;
  uint8_t ctrl[2] = {0x00, 0x00};  // Control_1: normal mode, 12.5 pF load as per board crystal
  return i2c_master_transmit(s_dev, ctrl, 2, 50) == ESP_OK;
}

bool pd_rtc_read_utc(int64_t *epoch_s, bool *trusted) {
  uint8_t reg = 0x04, r[7];
  if (i2c_master_transmit_receive(s_dev, &reg, 1, r, 7, 50) != ESP_OK) return false;
  *trusted = (r[0] & 0x80) == 0;
  const int sec = bcd2bin(r[0] & 0x7F), min = bcd2bin(r[1] & 0x7F), hour = bcd2bin(r[2] & 0x3F);
  const unsigned day = bcd2bin(r[3] & 0x3F), mon = bcd2bin(r[5] & 0x1F);
  const int year = 2000 + bcd2bin(r[6]);
  if (mon < 1 || mon > 12 || day < 1 || day > 31 || year < 2026) *trusted = false;
  *epoch_s = days_from_civil(year, mon ? mon : 1, day ? day : 1) * 86400 + hour * 3600 + min * 60 + sec;
  return true;
}

bool pd_rtc_write_utc(int64_t epoch_s) {
  int64_t days = epoch_s / 86400, rem = epoch_s % 86400;
  int y;
  unsigned m, d;
  civil_from_days(days, &y, &m, &d);
  const int wday = (int)((days + 4) % 7);  // 1970-01-01 was Thursday
  uint8_t w[8] = {0x04, bin2bcd((int)(rem % 60)) /* clears OS */, bin2bcd((int)(rem / 60 % 60)), bin2bcd((int)(rem / 3600)),
                  bin2bcd((int)d), (uint8_t)wday, bin2bcd((int)m), bin2bcd(y - 2000)};
  const bool ok = i2c_master_transmit(s_dev, w, sizeof w, 50) == ESP_OK;
  if (!ok) ESP_LOGE(TAG, "RTC write failed");
  return ok;
}
