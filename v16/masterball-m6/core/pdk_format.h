/* PDK1 sprite pack: private Pokémon animation frames flashed to the "assets" partition.
 * The public repository ships only this format + tools; artwork stays on the owner's PC.
 *
 *  0  char[4] "PDK1" | u16 version=1 | u16 entry_count
 *  8  entry[count] (20 B each, little-endian):
 *       u16 dex, u8 anim, u8 frames, u16 w, u16 h, u16 frame_ms, u16 palette_n,
 *       u32 palette_off, u32 frames_off
 *  palette: palette_n x {u16 rgb565, u8 alpha}; index 0 is fully transparent
 *  frames : per frame {u32 rle_len, rle bytes}; RLE = pairs (run 1..255, index)
 */
#ifndef PDK_FORMAT_H
#define PDK_FORMAT_H
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

enum pdk_anim { PDK_IDLE = 0, PDK_SLEEP, PDK_GREET, PDK_JUMP, PDK_DANCE, PDK_TOUCH, PDK_CHEER, PDK_CELEBRATE, PDK_ALARM,
                PDK_EGG, PDK_ANIM_COUNT };

typedef struct {
  uint16_t dex;
  uint8_t anim, frames;
  uint16_t w, h, frame_ms, palette_n;
  uint32_t palette_off, frames_off;
} pdk_entry_t;

static inline uint16_t pdk_u16(const uint8_t *p) { return (uint16_t)(p[0] | (p[1] << 8)); }
static inline uint32_t pdk_u32(const uint8_t *p) {
  return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

/* Validates the header; returns entry count or -1. */
static inline int pdk_header(const uint8_t *buf, size_t len) {
  if (len < 8 || buf[0] != 'P' || buf[1] != 'D' || buf[2] != 'K' || buf[3] != '1' || pdk_u16(buf + 4) != 1) return -1;
  int n = pdk_u16(buf + 6);
  return (size_t)(8 + 20 * n) <= len ? n : -1;
}

static inline void pdk_entry(const uint8_t *buf, int i, pdk_entry_t *e) {
  const uint8_t *p = buf + 8 + 20 * i;
  e->dex = pdk_u16(p);
  e->anim = p[2];
  e->frames = p[3];
  e->w = pdk_u16(p + 4);
  e->h = pdk_u16(p + 6);
  e->frame_ms = pdk_u16(p + 8);
  e->palette_n = pdk_u16(p + 10);
  e->palette_off = pdk_u32(p + 12);
  e->frames_off = pdk_u32(p + 16);
}

/* Decodes one RLE frame into npx palette indices. Rejects overruns and short streams. */
static inline int pdk_rle_decode(const uint8_t *src, size_t len, uint8_t *dst, size_t npx) {
  size_t o = 0;
  if (len % 2) return 0;
  for (size_t i = 0; i < len; i += 2) {
    size_t run = src[i];
    if (!run || o + run > npx) return 0;
    for (size_t k = 0; k < run; k++) dst[o++] = src[i + 1];
  }
  return o == npx;
}

#ifdef __cplusplus
}
#endif
#endif
