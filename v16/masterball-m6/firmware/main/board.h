// PokéDock M6 board layer for Waveshare ESP32-S3-Touch-AMOLED-1.43 (standard, SKU 30106).
// Pin map verified against the official schematic (2024) and the vendor ESP-IDF demo V3.
#pragma once
#include <stdbool.h>
#include <stdint.h>

#include "driver/i2c_master.h"
#include "lvgl.h"

#ifdef __cplusplus
extern "C" {
#endif

// QSPI AMOLED (SH8601 or CO5300 depending on production batch; detected at boot via RDID 0xDA)
#define PD_PIN_LCD_CS 9
#define PD_PIN_LCD_CLK 10
#define PD_PIN_LCD_D0 11
#define PD_PIN_LCD_D1 12
#define PD_PIN_LCD_D2 13
#define PD_PIN_LCD_D3 14
#define PD_PIN_LCD_RST 21
// shared I2C: FT3168 touch 0x38, PCF85063 RTC 0x51, QMI8658 IMU 0x6B
#define PD_PIN_I2C_SDA 47
#define PD_PIN_I2C_SCL 48
#define PD_PIN_RTC_INT 15
#define PD_PIN_VCC_ADC 4   // ADC1_CH3, 200k/100k divider from VCC (post power-path, NOT the battery)
// M6 harness on header J1 (1.27 mm 2x7): pin 8 = IO16 -> 470R -> 2N3904 -> passive buzzer (Soberton WT-1205) on USB_5V
#define PD_PIN_BUZZER 16

#define PD_LCD_RES 466

typedef enum { PD_PANEL_SH8601 = 0x86, PD_PANEL_CO5300 = 0xFF } pd_panel_t;

i2c_master_bus_handle_t board_i2c(void);
void board_i2c_init(void);

// display + LVGL; returns detected panel id
pd_panel_t board_display_init(lv_disp_t **out_disp);
void board_display_brightness(uint8_t percent);  // 0..100 via DCS 0x51
void board_display_power(bool on);
bool board_lvgl_lock(int timeout_ms);
void board_lvgl_unlock(void);

void board_touch_init(void);
bool board_touch_read(uint16_t *x, uint16_t *y);
uint8_t board_touch_chip(void);  // FocalTech chip ID (reg 0xA3), logged at boot for G1

int board_vcc_mv(void);  // VCC = USB 5 V - cable - PTC - MBR230: ~4.0-4.8 V when healthy

void buzzer_init(void);
typedef enum { PD_TUNE_CHIRP, PD_TUNE_ALARM, PD_TUNE_DONE, PD_TUNE_PAIR } pd_tune_t;
void buzzer_play(pd_tune_t tune);
void buzzer_stop(void);

#ifdef __cplusplus
}
#endif
