#pragma once
#include <stdint.h>
#include <string.h>
#include "phone_event.h"

static constexpr uint16_t POKEDOCK_PHONE_MAGIC = 0x5042;
static constexpr uint8_t POKEDOCK_PHONE_VERSION = 1;

struct __attribute__((packed)) PhoneWireHeader {
  uint16_t magic = POKEDOCK_PHONE_MAGIC;
  uint8_t version = POKEDOCK_PHONE_VERSION;
  uint8_t type = 0;
  uint8_t flags = 0;
  uint8_t source_len = 0;
  uint8_t title_len = 0;
  uint8_t ttl_s = 10;
};

class PhoneFrameDecoder {
 public:
  static constexpr uint16_t kMaxFrame = sizeof(PhoneWireHeader) + 23 + 47;
  void reset() { used_ = 0; expected_ = 0; }

  bool feed(const uint8_t* data, uint16_t len, PhoneEvent& out) {
    if (!data || !len) return false;
    if (used_ + len > kMaxFrame) { reset(); return false; }
    for (uint16_t i = 0; i < len; ++i) buf_[used_++] = data[i];

    if (used_ >= sizeof(PhoneWireHeader) && expected_ == 0) {
      PhoneWireHeader h{};
      memcpy(&h, buf_, sizeof(h));
      if (h.magic != POKEDOCK_PHONE_MAGIC || h.version != POKEDOCK_PHONE_VERSION) { reset(); return false; }
      if (h.source_len >= sizeof(out.source) || h.title_len >= sizeof(out.title)) { reset(); return false; }
      expected_ = static_cast<uint16_t>(sizeof(PhoneWireHeader) + h.source_len + h.title_len);
    }

    if (expected_ == 0 || used_ < expected_) return false;
    if (used_ != expected_) { reset(); return false; }

    PhoneWireHeader h{};
    memcpy(&h, buf_, sizeof(h));
    out = {};
    out.type = static_cast<PhoneEventType>(h.type);
    out.flags = h.flags;
    out.ttl_s = h.ttl_s;

    const uint8_t* p = buf_ + sizeof(PhoneWireHeader);
    if (h.source_len) memcpy(out.source, p, h.source_len);
    out.source[h.source_len] = 0;
    p += h.source_len;
    if (h.title_len) memcpy(out.title, p, h.title_len);
    out.title[h.title_len] = 0;

    reset();
    return true;
  }

 private:
  uint8_t buf_[kMaxFrame] = {};
  uint16_t used_ = 0;
  uint16_t expected_ = 0;
};
