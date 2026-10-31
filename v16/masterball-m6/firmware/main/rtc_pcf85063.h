#pragma once
#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

bool pd_rtc_init(void);
bool pd_rtc_read_utc(int64_t *epoch_s, bool *trusted);  // trusted=false after oscillator stop / unset
bool pd_rtc_write_utc(int64_t epoch_s);

#ifdef __cplusplus
}
#endif
