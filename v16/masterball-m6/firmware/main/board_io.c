// I2C bus, FT3168 touch, VCC monitor (ADC) and passive buzzer (LEDC) for the 1.43 board.
#include "board.h"
#include "driver/gpio.h"
#include "driver/ledc.h"
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_log.h"
#include "esp_timer.h"

static const char *TAG = "pd_io";
static i2c_master_bus_handle_t s_bus;
static i2c_master_dev_handle_t s_touch;

void board_i2c_init(void) {
  const i2c_master_bus_config_t cfg = {
      .i2c_port = I2C_NUM_0,
      .sda_io_num = PD_PIN_I2C_SDA,
      .scl_io_num = PD_PIN_I2C_SCL,
      .clk_source = I2C_CLK_SRC_DEFAULT,
      .glitch_ignore_cnt = 7,
      .flags = {.enable_internal_pullup = 1},
  };
  ESP_ERROR_CHECK(i2c_new_master_bus(&cfg, &s_bus));
}

i2c_master_bus_handle_t board_i2c(void) { return s_bus; }

void board_touch_init(void) {
  const i2c_device_config_t dev = {.dev_addr_length = I2C_ADDR_BIT_LEN_7, .device_address = 0x38, .scl_speed_hz = 400000};
  ESP_ERROR_CHECK(i2c_master_bus_add_device(s_bus, &dev, &s_touch));
  uint8_t normal_mode[2] = {0x00, 0x00};
  if (i2c_master_transmit(s_touch, normal_mode, 2, 50) != ESP_OK) ESP_LOGW(TAG, "FT3168 did not ACK");
}

bool board_touch_read(uint16_t *x, uint16_t *y) {
  uint8_t reg = 0x02, n = 0, buf[4];
  if (i2c_master_transmit_receive(s_touch, &reg, 1, &n, 1, 20) != ESP_OK || (n & 0x0F) == 0) return false;
  reg = 0x03;
  if (i2c_master_transmit_receive(s_touch, &reg, 1, buf, 4, 20) != ESP_OK) return false;
  uint16_t tx = (uint16_t)(((buf[0] & 0x0F) << 8) | buf[1]), ty = (uint16_t)(((buf[2] & 0x0F) << 8) | buf[3]);
  *x = tx >= PD_LCD_RES ? PD_LCD_RES - 1 : tx;
  *y = ty >= PD_LCD_RES ? PD_LCD_RES - 1 : ty;
#if CONFIG_PD_SCREEN_ROTATION_180
  *x = PD_LCD_RES - 1 - *x;
  *y = PD_LCD_RES - 1 - *y;
#endif
  return true;
}

// ---- VCC monitor ------------------------------------------------------------------------------
static adc_oneshot_unit_handle_t s_adc;
static adc_cali_handle_t s_cali;

int board_vcc_mv(void) {
  if (!s_adc) {
    const adc_oneshot_unit_init_cfg_t u = {.unit_id = ADC_UNIT_1};
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&u, &s_adc));
    const adc_oneshot_chan_cfg_t c = {.atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_DEFAULT};
    ESP_ERROR_CHECK(adc_oneshot_config_channel(s_adc, ADC_CHANNEL_3, &c));
    const adc_cali_curve_fitting_config_t cc = {.unit_id = ADC_UNIT_1, .chan = ADC_CHANNEL_3, .atten = ADC_ATTEN_DB_12,
                                                .bitwidth = ADC_BITWIDTH_DEFAULT};
    if (adc_cali_create_scheme_curve_fitting(&cc, &s_cali) != ESP_OK) s_cali = NULL;
  }
  int raw = 0, mv = 0, acc = 0;
  for (int i = 0; i < 8; i++) {
    adc_oneshot_read(s_adc, ADC_CHANNEL_3, &raw);
    if (s_cali) adc_cali_raw_to_voltage(s_cali, raw, &mv);
    else mv = raw * 3300 / 4095;
    acc += mv;
  }
  return acc / 8 * 3;  // R12 200k / R17 100k divider
}

// ---- buzzer: passive transducer, NPN low-side switch, LEDC square wave ----------------------------
typedef struct {
  uint16_t hz, ms;
} note_t;
static const note_t k_chirp[] = {{2093, 60}, {0, 30}, {2637, 80}, {0, 0}};
static const note_t k_done[] = {{1568, 120}, {2093, 120}, {2637, 120}, {3136, 260}, {0, 0}};
static const note_t k_alarm[] = {{2637, 140}, {0, 80}, {2637, 140}, {0, 80}, {3136, 220}, {0, 600}, {0, 0}};
static const note_t k_pair[] = {{1760, 80}, {0, 40}, {1760, 80}, {0, 0}};
static const note_t *s_tune;
static int s_idx;
static bool s_loop;
static esp_timer_handle_t s_timer;

static void tone(uint16_t hz) {
  if (!hz) {
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, 0);
  } else {
    ledc_set_freq(LEDC_LOW_SPEED_MODE, LEDC_TIMER_0, hz);
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, 512);  // 50 % of 10-bit
  }
  ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
}

static void step(void *arg) {
  (void)arg;
  if (!s_tune) return;
  const note_t *n = &s_tune[s_idx];
  if (n->ms == 0) {
    if (!s_loop) {
      tone(0);
      s_tune = NULL;
      return;
    }
    s_idx = 0;
    n = &s_tune[0];
  }
  tone(n->hz);
  s_idx++;
  esp_timer_start_once(s_timer, (uint64_t)n->ms * 1000);
}

void buzzer_init(void) {
  // Hold the NPN base low before LEDC takes the pin (external 100k pull-down also fitted).
  gpio_set_direction(PD_PIN_BUZZER, GPIO_MODE_OUTPUT);
  gpio_set_level(PD_PIN_BUZZER, 0);
  const ledc_timer_config_t t = {.speed_mode = LEDC_LOW_SPEED_MODE, .duty_resolution = LEDC_TIMER_10_BIT,
                                 .timer_num = LEDC_TIMER_0, .freq_hz = 2000, .clk_cfg = LEDC_AUTO_CLK};
  ESP_ERROR_CHECK(ledc_timer_config(&t));
  const ledc_channel_config_t c = {.gpio_num = PD_PIN_BUZZER, .speed_mode = LEDC_LOW_SPEED_MODE, .channel = LEDC_CHANNEL_0,
                                   .timer_sel = LEDC_TIMER_0, .duty = 0, .hpoint = 0};
  ESP_ERROR_CHECK(ledc_channel_config(&c));
  const esp_timer_create_args_t a = {.callback = step, .name = "buzz"};
  ESP_ERROR_CHECK(esp_timer_create(&a, &s_timer));
}

void buzzer_play(pd_tune_t tune) {
  esp_timer_stop(s_timer);
  s_tune = tune == PD_TUNE_ALARM ? k_alarm : tune == PD_TUNE_DONE ? k_done : tune == PD_TUNE_PAIR ? k_pair : k_chirp;
  s_loop = tune == PD_TUNE_ALARM;
  s_idx = 0;
  step(NULL);
}

void buzzer_stop(void) {
  esp_timer_stop(s_timer);
  s_tune = NULL;
  tone(0);
}
