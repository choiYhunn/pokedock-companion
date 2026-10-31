// AMOLED (QSPI) + LVGL 8 port. Panel detection and init tables follow the Waveshare 1.43 demo V3:
// SH8601 returns 0x86 on RDID(0xDA); CO5300 returns 0xFF and needs a +6 column offset.
#include <string.h>

#include "board.h"
#include "driver/gpio.h"
#include "driver/spi_master.h"
#include "esp_heap_caps.h"
#include "esp_lcd_panel_io.h"
#include "esp_lcd_panel_ops.h"
#include "esp_lcd_sh8601.h"
#include "esp_log.h"
#include "esp_rom_sys.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"

static const char *TAG = "pd_disp";
static esp_lcd_panel_handle_t s_panel;
static esp_lcd_panel_io_handle_t s_io;
static pd_panel_t s_id = PD_PANEL_SH8601;
static SemaphoreHandle_t s_lvgl_mux;
static lv_disp_drv_t s_drv;

static const sh8601_lcd_init_cmd_t k_sh8601_init[] = {
    {0x11, (uint8_t[]){0x00}, 0, 120}, {0x44, (uint8_t[]){0x01, 0xD1}, 2, 0}, {0x35, (uint8_t[]){0x00}, 1, 0},
    {0x53, (uint8_t[]){0x20}, 1, 10},  {0x51, (uint8_t[]){0x00}, 1, 10},      {0x29, (uint8_t[]){0x00}, 0, 10},
};
static const sh8601_lcd_init_cmd_t k_co5300_init[] = {
    {0x11, (uint8_t[]){0x00}, 0, 80}, {0xC4, (uint8_t[]){0x80}, 1, 0}, {0x53, (uint8_t[]){0x20}, 1, 1},
    {0x63, (uint8_t[]){0xFF}, 1, 1},  {0x51, (uint8_t[]){0x00}, 1, 1}, {0x29, (uint8_t[]){0x00}, 0, 10},
};

// ---- panel ID via 1-line bit-banged SPI read (before the QSPI peripheral owns the pins) ----------
static void bb_out(int pin, int v) { gpio_set_level(pin, v); }
static void bb_send(uint8_t b) {
  for (int i = 0; i < 8; i++, b <<= 1) {
    bb_out(PD_PIN_LCD_D0, (b & 0x80) != 0);
    bb_out(PD_PIN_LCD_CLK, 0);
    bb_out(PD_PIN_LCD_CLK, 1);
  }
}
static uint8_t read_panel_id(void) {
  gpio_config_t out = {.pin_bit_mask = (1ULL << PD_PIN_LCD_CS) | (1ULL << PD_PIN_LCD_CLK) | (1ULL << PD_PIN_LCD_D0) |
                                       (1ULL << PD_PIN_LCD_RST),
                       .mode = GPIO_MODE_OUTPUT, .pull_up_en = GPIO_PULLUP_ENABLE};
  gpio_config(&out);
  bb_out(PD_PIN_LCD_CS, 1);
  bb_out(PD_PIN_LCD_RST, 1);
  vTaskDelay(pdMS_TO_TICKS(20));
  bb_out(PD_PIN_LCD_RST, 0);
  vTaskDelay(pdMS_TO_TICKS(20));
  bb_out(PD_PIN_LCD_RST, 1);
  vTaskDelay(pdMS_TO_TICKS(120));
  bb_out(PD_PIN_LCD_CS, 0);
  bb_send(0x03);  // 1-line read
  bb_send(0x00);
  bb_send(0xDA);  // RDID1
  bb_send(0x00);
  gpio_set_direction(PD_PIN_LCD_D0, GPIO_MODE_INPUT);
  uint8_t v = 0;
  for (int i = 0; i < 8; i++) {
    bb_out(PD_PIN_LCD_CLK, 0);
    esp_rom_delay_us(1);
    v = (uint8_t)((v << 1) | gpio_get_level(PD_PIN_LCD_D0));
    bb_out(PD_PIN_LCD_CLK, 1);
    esp_rom_delay_us(1);
  }
  bb_out(PD_PIN_LCD_CS, 1);
  gpio_reset_pin(PD_PIN_LCD_CS);
  gpio_reset_pin(PD_PIN_LCD_CLK);
  gpio_reset_pin(PD_PIN_LCD_D0);
  return v;
}

static bool on_flush_done(esp_lcd_panel_io_handle_t io, esp_lcd_panel_io_event_data_t *e, void *ctx) {
  (void)io;
  (void)e;
  lv_disp_flush_ready((lv_disp_drv_t *)ctx);
  return false;
}

static void flush_cb(lv_disp_drv_t *drv, const lv_area_t *a, lv_color_t *px) {
  const int off = (s_id == PD_PANEL_CO5300) ? 6 : 0;
  esp_lcd_panel_draw_bitmap((esp_lcd_panel_handle_t)drv->user_data, a->x1 + off, a->y1, a->x2 + off + 1, a->y2 + 1, px);
}

static void rounder_cb(lv_disp_drv_t *drv, lv_area_t *a) {  // controller needs even start / odd end
  (void)drv;
  a->x1 &= ~1;
  a->y1 &= ~1;
  a->x2 |= 1;
  a->y2 |= 1;
}

static void touch_cb(lv_indev_drv_t *drv, lv_indev_data_t *data) {
  (void)drv;
  uint16_t x, y;
  if (board_touch_read(&x, &y)) {
    data->point.x = x;
    data->point.y = y;
    data->state = LV_INDEV_STATE_PRESSED;
  } else {
    data->state = LV_INDEV_STATE_RELEASED;
  }
}

static void tick_cb(void *arg) {
  (void)arg;
  lv_tick_inc(2);
}

static void lvgl_task(void *arg) {
  (void)arg;
  for (;;) {
    uint32_t wait = 10;
    if (board_lvgl_lock(-1)) {
      wait = lv_timer_handler();
      board_lvgl_unlock();
    }
    if (wait > 50) wait = 50;
    if (wait < 2) wait = 2;
    vTaskDelay(pdMS_TO_TICKS(wait));
  }
}

bool board_lvgl_lock(int timeout_ms) {
  return xSemaphoreTakeRecursive(s_lvgl_mux, timeout_ms < 0 ? portMAX_DELAY : pdMS_TO_TICKS(timeout_ms)) == pdTRUE;
}
void board_lvgl_unlock(void) { xSemaphoreGiveRecursive(s_lvgl_mux); }

void board_display_brightness(uint8_t percent) {
  if (percent > 100) percent = 100;
  uint8_t v = (uint8_t)((percent * 255 + 50) / 100);
  esp_lcd_panel_io_tx_param(s_io, 0x51, &v, 1);
}

void board_display_power(bool on) { esp_lcd_panel_disp_on_off(s_panel, on); }

pd_panel_t board_display_init(lv_disp_t **out_disp) {
  uint8_t id = read_panel_id();
  s_id = (id == PD_PANEL_SH8601) ? PD_PANEL_SH8601 : PD_PANEL_CO5300;
  ESP_LOGI(TAG, "panel RDID=0x%02x -> %s", id, s_id == PD_PANEL_SH8601 ? "SH8601" : "CO5300");

  const spi_bus_config_t bus = SH8601_PANEL_BUS_QSPI_CONFIG(PD_PIN_LCD_CLK, PD_PIN_LCD_D0, PD_PIN_LCD_D1, PD_PIN_LCD_D2,
                                                            PD_PIN_LCD_D3, PD_LCD_RES * 80 * sizeof(lv_color_t));
  ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &bus, SPI_DMA_CH_AUTO));
  const esp_lcd_panel_io_spi_config_t io_cfg = SH8601_PANEL_IO_QSPI_CONFIG(PD_PIN_LCD_CS, on_flush_done, &s_drv);
  ESP_ERROR_CHECK(esp_lcd_new_panel_io_spi((esp_lcd_spi_bus_handle_t)SPI2_HOST, &io_cfg, &s_io));
  sh8601_vendor_config_t vendor = {
      .init_cmds = s_id == PD_PANEL_SH8601 ? k_sh8601_init : k_co5300_init,
      .init_cmds_size = s_id == PD_PANEL_SH8601 ? sizeof(k_sh8601_init) / sizeof(k_sh8601_init[0])
                                                : sizeof(k_co5300_init) / sizeof(k_co5300_init[0]),
      .flags = {.use_qspi_interface = 1},
  };
  const esp_lcd_panel_dev_config_t panel_cfg = {
      .reset_gpio_num = PD_PIN_LCD_RST,
      .rgb_ele_order = LCD_RGB_ELEMENT_ORDER_RGB,
      .bits_per_pixel = 16,
      .vendor_config = &vendor,
  };
  ESP_ERROR_CHECK(esp_lcd_new_panel_sh8601(s_io, &panel_cfg, &s_panel));
  ESP_ERROR_CHECK(esp_lcd_panel_reset(s_panel));
  ESP_ERROR_CHECK(esp_lcd_panel_init(s_panel));
  ESP_ERROR_CHECK(esp_lcd_panel_disp_on_off(s_panel, true));

  lv_init();
  static lv_disp_draw_buf_t draw;
  const size_t lines = 58;  // 466 x 58 x 2 B = 54 KB per buffer, internal DMA RAM
  lv_color_t *b1 = heap_caps_malloc(PD_LCD_RES * lines * sizeof(lv_color_t), MALLOC_CAP_DMA | MALLOC_CAP_INTERNAL);
  lv_color_t *b2 = heap_caps_malloc(PD_LCD_RES * lines * sizeof(lv_color_t), MALLOC_CAP_DMA | MALLOC_CAP_INTERNAL);
  assert(b1 && b2);
  lv_disp_draw_buf_init(&draw, b1, b2, PD_LCD_RES * lines);
  lv_disp_drv_init(&s_drv);
  s_drv.hor_res = PD_LCD_RES;
  s_drv.ver_res = PD_LCD_RES;
  s_drv.flush_cb = flush_cb;
  s_drv.rounder_cb = rounder_cb;
  s_drv.draw_buf = &draw;
  s_drv.user_data = s_panel;
#if CONFIG_PD_SCREEN_ROTATION_180
  s_drv.sw_rotate = 1;
  s_drv.rotated = LV_DISP_ROT_180;
#endif
  lv_disp_t *disp = lv_disp_drv_register(&s_drv);

  static lv_indev_drv_t indev;
  lv_indev_drv_init(&indev);
  indev.type = LV_INDEV_TYPE_POINTER;
  indev.disp = disp;
  indev.read_cb = touch_cb;
  lv_indev_drv_register(&indev);

  const esp_timer_create_args_t targs = {.callback = tick_cb, .name = "lv_tick"};
  esp_timer_handle_t t;
  ESP_ERROR_CHECK(esp_timer_create(&targs, &t));
  ESP_ERROR_CHECK(esp_timer_start_periodic(t, 2000));
  s_lvgl_mux = xSemaphoreCreateRecursiveMutex();
  xTaskCreatePinnedToCore(lvgl_task, "lvgl", 8192, NULL, 3, NULL, 1);
  if (out_disp) *out_disp = disp;
  return s_id;
}
