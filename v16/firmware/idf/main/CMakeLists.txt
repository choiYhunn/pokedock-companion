# Board-neutral serial bring-up only. Display and RTC drivers NOT included.
idf_component_register(
 SRCS "app_main.cpp" "../ota_manual.cpp"
 INCLUDE_DIRS "." ".." "../.."
 REQUIRES esp_timer app_update esp_https_ota esp_http_client mbedtls
)
