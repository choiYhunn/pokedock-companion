// Console bring-up only; NOT a native PokéDock LVGL/HOME/Focus UI.
// This source does not toggle board-specific GPIO or drive an LCD.
// Reuse StudyEngine as a standalone host-tested timing class before BSP integration.
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "study_engine.h"

static const char *TAG = "PokéDock-M0";

extern "C" void app_main(void) {
    StudyEngine engine;
    ESP_LOGW(TAG, "M0 skeleton only — no display, touch, RTC, SD, NVS or OTA");
    ESP_LOGI(TAG, "esp_timer time in milliseconds: %llu",
             static_cast<unsigned long long>(esp_timer_get_time()/1000));
    // No automatic study credit, and no timer started on boot.
    for (;;) {
        const uint64_t now_ms = static_cast<uint64_t>(esp_timer_get_time()/1000);
        (void)engine.tick(now_ms);
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
