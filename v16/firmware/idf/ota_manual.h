#pragma once
// Prototype OTA interface, NOT connected to the device GUI.
// Current software does not ship or enable OTA.
#include "esp_err.h"
namespace ghost16 {
struct UpdateRequest {
 const char* release_url; // MUST be obtained from a verified, trusted release catalog
 bool physical_user_approved;
 bool trusted_manifest_and_signature_verified;
 bool device_idle;
 bool stable_power;
};
esp_err_t manual_https_ota(const UpdateRequest& request);
// Invoke only after board-specific display, touch, storage and clock health checks.
// A failed health check requests rollback; NEVER auto-confirm on app startup.
esp_err_t confirm_new_app_after_health(bool all_tests_pass);
}
