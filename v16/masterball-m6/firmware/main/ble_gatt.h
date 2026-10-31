#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// Implemented in app_main.cpp: run one command, write the ACK into ack (<= ack_cap bytes),
// return its length. *state_changed tells the GATT layer to also notify the new state.
size_t pd_app_handle_command(const uint8_t *in, size_t len, bool authenticated, char *ack, size_t ack_cap,
                             bool *state_changed);
size_t pd_app_state_json(char *out, size_t cap);
void pd_app_show_passkey(uint32_t passkey);  // UI overlay, 0 = hide
void pd_app_link_changed(bool connected);

void ble_start(void);
void ble_open_pairing_window(uint32_t seconds);  // only during this window may a new phone bond
bool ble_pairing_open(void);
void ble_notify_state(void);                     // push state to the subscribed owner (if any)

#ifdef __cplusplus
}
#endif
