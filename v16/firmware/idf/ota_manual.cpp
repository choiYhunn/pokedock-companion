#include "ota_manual.h"
#include <cstring>
#include "esp_log.h"
#include "esp_ota_ops.h"
#include "esp_system.h"
#if CONFIG_GHOST_V16_ENABLE_OTA
#include "esp_https_ota.h"
#include "esp_http_client.h"
#include "esp_crt_bundle.h"
#endif
namespace ghost16 {
static const char* TAG = "ghost16-ota";
esp_err_t manual_https_ota(const UpdateRequest& r){
#if !CONFIG_GHOST_V16_ENABLE_OTA
 (void)r;ESP_LOGW(TAG,"Manual OTA DISABLED; board/bootloader/signing not validated");
 return ESP_ERR_NOT_SUPPORTED;
#else
 // This only verifies caller claims; the caller MUST perform real cryptographic
 // release catalog verification, board/schema/version checks and power tests.
 // DO NOT ENABLE while those integrations are absent.
 const char* root=CONFIG_GHOST_V16_UPDATE_BASE;
 if(!r.physical_user_approved||!r.trusted_manifest_and_signature_verified||
    !r.device_idle||!r.stable_power||!r.release_url||!root||root[0]=='\0')
    return ESP_ERR_INVALID_STATE;
 const size_t n=std::strlen(root);
 if(std::strncmp(root,"https://",8)!=0||root[n-1]!='/'||
    std::strncmp(r.release_url,root,n)!=0) return ESP_ERR_INVALID_ARG;
 esp_http_client_config_t http={};
 http.url=r.release_url;
 http.timeout_ms=20000;
 http.crt_bundle_attach=esp_crt_bundle_attach;
 http.disable_auto_redirect=true;
 esp_https_ota_config_t cfg={};
 cfg.http_config=&http;
 const esp_err_t err=esp_https_ota(&cfg);
 if(err==ESP_OK){ESP_LOGI(TAG,"New image staged. Rebooting to pending-health app");
  esp_restart();}
 ESP_LOGE(TAG,"Update failed: %s",esp_err_to_name(err));
 return err;
#endif
}
esp_err_t confirm_new_app_after_health(bool all_tests_pass){
 // Only called after verified application health.
 const esp_partition_t* running=esp_ota_get_running_partition();
 if(!running)return ESP_ERR_INVALID_STATE;
 esp_ota_img_states_t state;
 const esp_err_t err=esp_ota_get_state_partition(running,&state);
 if(err!=ESP_OK)return err;
 if(state!=ESP_OTA_IMG_PENDING_VERIFY)return ESP_OK;
 if(all_tests_pass)return esp_ota_mark_app_valid_cancel_rollback();
 ESP_LOGE(TAG,"New image failed postboot hardware health; rolling back");
 return esp_ota_mark_app_invalid_rollback_and_reboot();
}
} // namespace ghost16
