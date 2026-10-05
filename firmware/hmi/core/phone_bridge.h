#pragma once
#include <stdint.h>

enum class PhonePlatform : uint8_t {
  NONE,
  ANDROID_HELPER,
  IOS_ANCS,
  GENERIC_LAN
};

enum class NoticeClass : uint8_t {
  CALL,
  CALENDAR,
  PRIORITY_CONTACT,
  SYSTEM
};

struct PriorityNotice {
  NoticeClass type = NoticeClass::SYSTEM;
  char title[48] = {};
  char source[32] = {};
  uint32_t ttl_s = 10;
};

struct PhoneBridgeStatus {
  PhonePlatform platform = PhonePlatform::NONE;
  bool connected = false;
  bool phone_parked = false;
  bool charging_hint = false;
};

class PhoneBridge {
 public:
  virtual ~PhoneBridge() = default;
  virtual void begin() = 0;
  virtual void poll() = 0;
  virtual PhoneBridgeStatus status() const = 0;
  virtual bool popPriorityNotice(PriorityNotice& out) = 0;
};

// Privacy contract:
// - message body is never required;
// - implementation should forward only allowlisted categories;
// - notification text must not be persisted to SD.
