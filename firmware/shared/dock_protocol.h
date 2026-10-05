#pragma once
#include <stdint.h>

static constexpr uint32_t POKEDOCK_DOCK_MAGIC = 0x504F4B45; // POKE

enum DockFlags : uint16_t {
  DOCK_PHONE_PARKED = 1u << 0,
  DOCK_NFC_PRESENT  = 1u << 1,
  DOCK_DARK         = 1u << 2,
  DOCK_NODE_OK      = 1u << 3
};

struct __attribute__((packed)) DockToHmiPacket {
  uint32_t magic = POKEDOCK_DOCK_MAGIC;
  uint32_t seq = 0;
  uint16_t flags = 0;
  uint16_t lux_x10 = 0;
  uint16_t phone_distance_mm = 0;
  uint16_t pokemon_id = 0;
  uint32_t nfc_uid_hash = 0;
};

struct __attribute__((packed)) HmiToDockPacket {
  uint32_t magic = POKEDOCK_DOCK_MAGIC;
  uint32_t seq = 0;
  uint16_t theme_id = 0;
  uint8_t brightness = 32;
  uint8_t focus_mode = 0;
};
