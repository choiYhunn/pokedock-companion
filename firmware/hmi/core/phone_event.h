#pragma once
#include <stdint.h>

enum class PhoneEventType : uint8_t {
  NONE = 0, CALL = 1, CALENDAR = 2, PRIORITY_CONTACT = 3, CONNECTION = 4
};

struct PhoneEvent {
  PhoneEventType type = PhoneEventType::NONE;
  uint8_t flags = 0;
  uint16_t ttl_s = 10;
  char source[24] = {};
  char title[48] = {};
};

// Privacy: short summaries only; never persist notification bodies to SD.
