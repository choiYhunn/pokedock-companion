#include "assets.h"

#include <string.h>

#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_partition.h"
#include "pdk_format.h"

static const char *TAG = "pd_assets";
static const uint8_t *s_base;
static size_t s_len;
static int s_count = -1;
static esp_partition_mmap_handle_t s_map;
static uint8_t *s_idx;       // decoded palette indices (largest frame)
static uint8_t *s_px[2];     // double-buffered LV_IMG_CF_TRUE_COLOR_ALPHA
static lv_img_dsc_t s_dsc[2];
static int s_flip;
#define PDK_MAX_W 128

bool assets_init(void) {
  const esp_partition_t *p = esp_partition_find_first(ESP_PARTITION_TYPE_DATA, 0x40, "assets");
  if (!p) return false;
  const void *ptr;
  if (esp_partition_mmap(p, 0, p->size, ESP_PARTITION_MMAP_DATA, &ptr, &s_map) != ESP_OK) return false;
  s_base = (const uint8_t *)ptr;
  s_len = p->size;
  s_count = pdk_header(s_base, s_len);
  if (s_count <= 0) {
    ESP_LOGW(TAG, "no PDK1 sprite pack flashed - showing neutral placeholder (not Pokémon art)");
    return false;
  }
  s_idx = heap_caps_malloc(PDK_MAX_W * PDK_MAX_W, MALLOC_CAP_SPIRAM);
  for (int i = 0; i < 2; i++) s_px[i] = heap_caps_malloc(PDK_MAX_W * PDK_MAX_W * 3, MALLOC_CAP_SPIRAM);
  ESP_LOGI(TAG, "sprite pack: %d animations", s_count);
  return s_idx && s_px[0] && s_px[1];
}

bool assets_available(void) { return s_count > 0; }

static bool find(uint16_t dex, uint8_t anim, pdk_entry_t *e) {
  for (int i = 0; i < s_count; i++) {
    pdk_entry(s_base, i, e);
    if (e->dex == dex && e->anim == anim) return true;
  }
  return false;
}

const lv_img_dsc_t *assets_frame(uint16_t dex, uint8_t anim, uint32_t idx, uint16_t *frame_ms, uint8_t *frames) {
  if (s_count <= 0) return NULL;
  pdk_entry_t e;
  if (!find(dex, anim, &e) && !find(dex, PDK_IDLE, &e)) return NULL;
  if (e.w > PDK_MAX_W || e.h > PDK_MAX_W || !e.frames || e.frames_off >= s_len) return NULL;
  idx %= e.frames;
  const uint8_t *f = s_base + e.frames_off;
  for (uint32_t k = 0; k < idx; k++) f += 4 + pdk_u32(f);
  const uint32_t rle_len = pdk_u32(f);
  if ((size_t)(f + 4 + rle_len - s_base) > s_len) return NULL;
  const size_t npx = (size_t)e.w * e.h;
  if (!pdk_rle_decode(f + 4, rle_len, s_idx, npx)) return NULL;
  const uint8_t *pal = s_base + e.palette_off;
  uint8_t *out = s_px[s_flip];
  for (size_t i = 0; i < npx; i++) {
    const uint8_t *c = pal + 3 * (s_idx[i] < e.palette_n ? s_idx[i] : 0);
    lv_color_t col;
    col.full = pdk_u16(c);
#if LV_COLOR_16_SWAP
    col.full = (uint16_t)((col.full >> 8) | (col.full << 8));
#endif
    memcpy(out + 3 * i, &col.full, 2);
    out[3 * i + 2] = c[2];
  }
  lv_img_dsc_t *d = &s_dsc[s_flip];
  d->header.cf = LV_IMG_CF_TRUE_COLOR_ALPHA;
  d->header.always_zero = 0;
  d->header.w = e.w;
  d->header.h = e.h;
  d->data_size = (uint32_t)(npx * 3);
  d->data = out;
  s_flip ^= 1;
  if (frame_ms) *frame_ms = e.frame_ms ? e.frame_ms : 100;
  if (frames) *frames = e.frames;
  return d;
}
