#pragma once
#include "phone_bridge.h"

struct NotificationPolicy {
  bool allow_calls = true;
  bool allow_calendar = true;
  bool allow_priority_contacts = true;
  bool allow_system = false;
  bool show_message_body = false; // should remain false in V1
};

inline bool notification_allowed(NoticeClass c, const NotificationPolicy& p) {
  switch (c) {
    case NoticeClass::CALL: return p.allow_calls;
    case NoticeClass::CALENDAR: return p.allow_calendar;
    case NoticeClass::PRIORITY_CONTACT: return p.allow_priority_contacts;
    case NoticeClass::SYSTEM: return p.allow_system;
  }
  return false;
}
