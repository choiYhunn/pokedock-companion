// NimBLE GATT peripheral: one owner phone, LE Secure Connections with MITM (passkey shown on the
// ball's screen, DisplayOnly), bonds persisted in NVS. New pairings only inside a pairing window
// opened from the device menu (or automatically while no phone is bonded).
#include "ble_gatt.h"

#include <string.h>

#include "esp_log.h"
#include "esp_random.h"
#include "esp_timer.h"
#include "host/ble_hs.h"
#include "host/ble_store.h"
#include "host/util/util.h"
#include "nimble/nimble_port.h"
#include "nimble/nimble_port_freertos.h"
#include "services/gap/ble_svc_gap.h"
#include "services/gatt/ble_svc_gatt.h"

void ble_store_config_init(void);

static const char *TAG = "pd_ble";
#define PD_UUID(last) BLE_UUID128_INIT(0x71, 0xb7, 0x2a, 0x3d, 0xd9, 0x7b, 0x3e, 0x9a, 0x41, 0x4b, 0x48, 0x81, last, 0x00, 0xc0, 0xed)
static const ble_uuid128_t k_svc = PD_UUID(0x01), k_cmd = PD_UUID(0x02), k_evt = PD_UUID(0x03), k_state = PD_UUID(0x04);
static uint16_t s_evt_handle, s_conn = BLE_HS_CONN_HANDLE_NONE;
static bool s_subscribed;
static uint8_t s_own_addr_type;
static int64_t s_pair_until_us;

static bool link_authenticated(uint16_t conn) {
  struct ble_gap_conn_desc d;
  return ble_gap_conn_find(conn, &d) == 0 && d.sec_state.encrypted && d.sec_state.authenticated && d.sec_state.bonded;
}

static void notify(const char *data, size_t len) {
  if (s_conn == BLE_HS_CONN_HANDLE_NONE || !s_subscribed) return;
  struct os_mbuf *om = ble_hs_mbuf_from_flat(data, len);
  if (om) ble_gatts_notify_custom(s_conn, s_evt_handle, om);
}

void ble_notify_state(void) {
  char buf[200];
  size_t n = pd_app_state_json(buf, sizeof buf);
  if (n) notify(buf, n);
}

static int access_cb(uint16_t conn, uint16_t attr, struct ble_gatt_access_ctxt *ctxt, void *arg) {
  (void)attr;
  (void)arg;
  if (ble_uuid_cmp(ctxt->chr->uuid, &k_cmd.u) == 0 && ctxt->op == BLE_GATT_ACCESS_OP_WRITE_CHR) {
    uint8_t in[181];
    uint16_t len = 0;
    if (OS_MBUF_PKTLEN(ctxt->om) > 180) return BLE_ATT_ERR_INVALID_ATTR_VALUE_LEN;
    if (ble_hs_mbuf_to_flat(ctxt->om, in, sizeof in, &len) != 0) return BLE_ATT_ERR_UNLIKELY;
    char ack[96];
    bool changed = false;
    size_t n = pd_app_handle_command(in, len, link_authenticated(conn), ack, sizeof ack, &changed);
    notify(ack, n);
    if (changed) ble_notify_state();
    return 0;
  }
  if (ble_uuid_cmp(ctxt->chr->uuid, &k_state.u) == 0 && ctxt->op == BLE_GATT_ACCESS_OP_READ_CHR) {
    char buf[200];
    size_t n = pd_app_state_json(buf, sizeof buf);
    return os_mbuf_append(ctxt->om, buf, n) == 0 ? 0 : BLE_ATT_ERR_INSUFFICIENT_RES;
  }
  return BLE_ATT_ERR_UNLIKELY;
}

static const struct ble_gatt_svc_def k_svcs[] = {
    {.type = BLE_GATT_SVC_TYPE_PRIMARY,
     .uuid = &k_svc.u,
     .characteristics = (struct ble_gatt_chr_def[]){
         {.uuid = &k_cmd.u, .access_cb = access_cb,
          .flags = BLE_GATT_CHR_F_WRITE | BLE_GATT_CHR_F_WRITE_ENC | BLE_GATT_CHR_F_WRITE_AUTHEN},
         {.uuid = &k_evt.u, .access_cb = access_cb, .flags = BLE_GATT_CHR_F_NOTIFY, .val_handle = &s_evt_handle},
         {.uuid = &k_state.u, .access_cb = access_cb,
          .flags = BLE_GATT_CHR_F_READ | BLE_GATT_CHR_F_READ_ENC | BLE_GATT_CHR_F_READ_AUTHEN},
         {0}}},
    {0}};

static void advertise(void);

bool ble_pairing_open(void) { return esp_timer_get_time() < s_pair_until_us; }

void ble_open_pairing_window(uint32_t seconds) { s_pair_until_us = esp_timer_get_time() + (int64_t)seconds * 1000000; }

static int bond_count(void) {
  int n = 0;
  ble_store_util_count(BLE_STORE_OBJ_TYPE_PEER_SEC, &n);
  return n;
}

static int gap_cb(struct ble_gap_event *ev, void *arg) {
  (void)arg;
  switch (ev->type) {
    case BLE_GAP_EVENT_CONNECT:
      if (ev->connect.status != 0) {
        advertise();
        return 0;
      }
      s_conn = ev->connect.conn_handle;
      s_subscribed = false;
      ble_gap_security_initiate(s_conn);  // bonded phones re-encrypt silently; new ones must pair
      pd_app_link_changed(true);
      return 0;
    case BLE_GAP_EVENT_DISCONNECT:
      s_conn = BLE_HS_CONN_HANDLE_NONE;
      s_subscribed = false;
      pd_app_show_passkey(0);
      pd_app_link_changed(false);
      advertise();
      return 0;
    case BLE_GAP_EVENT_SUBSCRIBE:
      if (ev->subscribe.attr_handle == s_evt_handle) s_subscribed = ev->subscribe.cur_notify;
      return 0;
    case BLE_GAP_EVENT_PASSKEY_ACTION: {
      if (ev->passkey.params.action != BLE_SM_IOACT_DISP || !ble_pairing_open()) {
        ESP_LOGW(TAG, "pairing refused (window closed or unsupported IO action)");
        ble_gap_terminate(ev->passkey.conn_handle, BLE_ERR_AUTH_FAIL);
        return 0;
      }
      struct ble_sm_io io = {.action = BLE_SM_IOACT_DISP, .passkey = esp_random() % 1000000};
      pd_app_show_passkey(io.passkey ? io.passkey : 1);
      ble_sm_inject_io(ev->passkey.conn_handle, &io);
      return 0;
    }
    case BLE_GAP_EVENT_ENC_CHANGE:
      pd_app_show_passkey(0);
      if (ev->enc_change.status == 0 && link_authenticated(ev->enc_change.conn_handle)) s_pair_until_us = 0;
      return 0;
    case BLE_GAP_EVENT_REPEAT_PAIRING: {
      if (!ble_pairing_open()) return BLE_GAP_REPEAT_PAIRING_IGNORE;
      struct ble_gap_conn_desc d;
      if (ble_gap_conn_find(ev->repeat_pairing.conn_handle, &d) == 0) ble_store_util_delete_peer(&d.peer_id_addr);
      return BLE_GAP_REPEAT_PAIRING_RETRY;
    }
    case BLE_GAP_EVENT_MTU:
      ESP_LOGI(TAG, "MTU %d", ev->mtu.value);
      return 0;
    default:
      return 0;
  }
}

static void advertise(void) {
  struct ble_hs_adv_fields f = {0};
  f.flags = BLE_HS_ADV_F_DISC_GEN | BLE_HS_ADV_F_BREDR_UNSUP;
  f.uuids128 = (ble_uuid128_t *)&k_svc;
  f.num_uuids128 = 1;
  f.uuids128_is_complete = 1;
  ble_gap_adv_set_fields(&f);
  struct ble_hs_adv_fields r = {0};
  const char *name = ble_svc_gap_device_name();
  r.name = (const uint8_t *)name;
  r.name_len = (uint8_t)strlen(name);
  r.name_is_complete = 1;
  ble_gap_adv_rsp_set_fields(&r);
  struct ble_gap_adv_params p = {.conn_mode = BLE_GAP_CONN_MODE_UND, .disc_mode = BLE_GAP_DISC_MODE_GEN,
                                 .itvl_min = 320, .itvl_max = 480};  // 200-300 ms: low power, still quick to find
  int rc = ble_gap_adv_start(s_own_addr_type, NULL, BLE_HS_FOREVER, &p, gap_cb, NULL);
  if (rc && rc != BLE_HS_EALREADY) ESP_LOGE(TAG, "adv start rc=%d", rc);
}

static void on_sync(void) {
  ble_hs_util_ensure_addr(0);
  ble_hs_id_infer_auto(0, &s_own_addr_type);
  if (bond_count() == 0) ble_open_pairing_window(600);  // first setup: no owner yet
  advertise();
}

static void on_reset(int reason) { ESP_LOGW(TAG, "host reset %d", reason); }

static void host_task(void *param) {
  (void)param;
  nimble_port_run();
  nimble_port_freertos_deinit();
}

void ble_start(void) {
  ESP_ERROR_CHECK(nimble_port_init());
  ble_hs_cfg.sync_cb = on_sync;
  ble_hs_cfg.reset_cb = on_reset;
  ble_hs_cfg.store_status_cb = ble_store_util_status_rr;
  ble_hs_cfg.sm_io_cap = BLE_SM_IO_CAP_DISP_ONLY;
  ble_hs_cfg.sm_bonding = 1;
  ble_hs_cfg.sm_mitm = 1;
  ble_hs_cfg.sm_sc = 1;
  ble_hs_cfg.sm_our_key_dist = BLE_SM_PAIR_KEY_DIST_ENC | BLE_SM_PAIR_KEY_DIST_ID;
  ble_hs_cfg.sm_their_key_dist = BLE_SM_PAIR_KEY_DIST_ENC | BLE_SM_PAIR_KEY_DIST_ID;
  ble_svc_gap_init();
  ble_svc_gatt_init();
  ESP_ERROR_CHECK(ble_gatts_count_cfg(k_svcs));
  ESP_ERROR_CHECK(ble_gatts_add_svcs(k_svcs));
  ble_svc_gap_device_name_set("PokeDock-MB");
  ble_att_set_preferred_mtu(247);
  ble_store_config_init();
  nimble_port_freertos_init(host_task);
}
