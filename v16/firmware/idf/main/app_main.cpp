#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "ghost_core.h"
#include "../ota_manual.h"
static const char *TAG="GhostV16";
extern "C" void app_main(void){
 static ghost16::Core core;
 ESP_LOGW(TAG,"V16 DEVELOPMENT SKELETON. No AMOLED, beam splitter, SSD1327, sensor, speaker, RTC, WiFi or OTA UI");
 ESP_LOGW(TAG,"OTA is OFF unless explicitly configured and cryptographic/update gates are implemented");
 // No network scan, OTA, alarm or focus starts automatically.
 while(true){
  core.tick(static_cast<uint64_t>(esp_timer_get_time()/1000),-1,-1);
  vTaskDelay(pdMS_TO_TICKS(250));
 }
}
