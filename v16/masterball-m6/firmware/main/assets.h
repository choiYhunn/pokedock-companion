#pragma once
#include <stdbool.h>
#include <stdint.h>

#include "lvgl.h"

#ifdef __cplusplus
extern "C" {
#endif

// Maps the "assets" flash partition (PDK1). Returns false when no private pack is flashed.
bool assets_init(void);
bool assets_available(void);
// Decodes frame `idx` of (dex, anim) into an LVGL true-colour+alpha image owned by the module.
// Falls back to the idle animation when that animation is missing. Returns NULL if nothing exists.
const lv_img_dsc_t *assets_frame(uint16_t dex, uint8_t anim, uint32_t idx, uint16_t *frame_ms, uint8_t *frames);

#ifdef __cplusplus
}
#endif
