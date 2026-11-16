// M7 sound: DFRobot DFR0534 (Gravity UART MP3 voice module) on header J10 (SH1.0, 4 pins):
//   J10-1 GPIO44 (silk "RXD") -> module R (UART1 TX through the GPIO matrix, 9600 8N1)
//   J10-3 3V3 -> module +,  J10-4 GND -> module -
// J10-2 (GPIO43) carries the ROM boot log and the module's T line is not wired, so the link is
// transmit-only: a missing or dead module just stays silent and nothing here ever waits for it.
#include "board.h"
#include "sdkconfig.h"

#if CONFIG_PD_AUDIO_DFR0534
#include "driver/uart.h"
#include "esp_log.h"

static const char *TAG = "pd_audio";
static bool s_ok;

void board_audio_init(void) {
  const uart_config_t c = {.baud_rate = 9600,
                           .data_bits = UART_DATA_8_BITS,
                           .parity = UART_PARITY_DISABLE,
                           .stop_bits = UART_STOP_BITS_1,
                           .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
                           .source_clk = UART_SCLK_DEFAULT};
  // RX buffer must exceed the 128 B hardware FIFO even though nothing is received
  if (uart_driver_install(PD_AUDIO_UART, 256, 256, 0, NULL, 0) != ESP_OK || uart_param_config(PD_AUDIO_UART, &c) != ESP_OK ||
      uart_set_pin(PD_AUDIO_UART, PD_PIN_AUDIO_TX, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE) != ESP_OK) {
    ESP_LOGE(TAG, "UART%d setup failed: sound off, everything else runs", PD_AUDIO_UART);
    return;
  }
  s_ok = true;
  ESP_LOGI(TAG, "DFR0534 link: UART%d TX on GPIO%d, 9600 8N1, transmit only", PD_AUDIO_UART, PD_PIN_AUDIO_TX);
}

void board_audio_write(const uint8_t *bytes, size_t n) {
  // frames are <= 6 B and the TX ring holds 256 B, so this returns at once in practice
  if (s_ok && n) uart_write_bytes(PD_AUDIO_UART, bytes, n);
}

void board_audio_line_test(bool hold_low) {
  // wiring check (docs/07): an inverted idle level holds J10-1 at 0 V so a multimeter can find it
  if (s_ok) uart_set_line_inverse(PD_AUDIO_UART, hold_low ? UART_SIGNAL_TXD_INV : UART_SIGNAL_INV_DISABLE);
}
#endif
