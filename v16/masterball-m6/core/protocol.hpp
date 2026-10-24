// PokéDock BLE application protocol v2 (device side). Transport-agnostic and host-testable:
// the firmware feeds GATT writes in and sends the returned ACK / state as notifications.
//
// Command  {"v":2,"s":<session u32>,"q":<seq u32>,"c":"<cmd>", ...args}   (<= 180 bytes UTF-8)
// ACK      {"q":<seq>,"ok":1,"r":<state_rev>}  |  {"q":<seq>,"ok":0,"e":"<code>"}
// State    {"r":rev,"p":partner,"b":bright,"snd":0|1,"f":[phase,rem_s,total_s],
//           "a":[en,h,m,ringing],"clk":[trusted,sync_age_min],"pwr":[usb_mv,ok],"msg":len,"fw":"..."}
//
// Rules: writes are refused unless the link is encrypted + authenticated (bonded owner);
// an exact (session, seq) repeat returns the cached ACK without executing again (retries are
// safe); state_rev increases on every applied change so the app can resync after reconnect.
#pragma once
#include <array>
#include <cstdint>
#include <string>

#include "mini_json.hpp"
#include "pokedock_core.hpp"

namespace pokedock {

static constexpr size_t kMaxCommandBytes = 180;
static constexpr size_t kMaxMessageBytes = 90;  // ~30 Hangul syllables
static constexpr const char *kFirmwareVersion = "m6-0.1.0";

class DeviceEnv {
 public:
  virtual ~DeviceEnv() = default;
  virtual int64_t mono_ms() = 0;
  virtual int64_t local_abs_minute() = 0;               // -1 if the wall clock is untrusted
  virtual bool set_utc(int64_t epoch_s, int tz_min) = 0;  // writes RTC, marks clock trusted
  virtual int sync_age_min() = 0;                       // minutes since last phone sync, -1 never
  virtual int usb_mv() = 0;
  virtual void persist() = 0;                           // settings / alarm / message to NVS
  virtual void reaction() = 0;                          // partner happy animation + chirp
};

class ProtocolEngine {
 public:
  ProtocolEngine(Core &core, DeviceEnv &env) : core_(core), env_(env) {}

  const std::string &message() const { return message_; }
  void restore_message(const std::string &m) { message_ = m; }
  uint32_t rev() const { return rev_; }
  void bump() { ++rev_; }

  // Returns the ACK JSON. `authenticated` = LE link encrypted with an authenticated bond.
  std::string handle(const std::string &in, bool authenticated) {
    if (in.size() > kMaxCommandBytes) return nack(0, "size");
    JsonObject o;
    if (!JsonReader::parse(in, o)) return nack(0, "json");
    int64_t seq = geti(o, "q", -1), session = geti(o, "s", -1);
    if (seq < 1 || seq > 0xFFFFFFFFLL || session < 0 || session > 0xFFFFFFFFLL) return nack(0, "seq");
    if (geti(o, "v", 0) != 2) return nack(seq, "ver");
    if (!authenticated) return nack(seq, "auth");
    for (const auto &c : cache_)
      if (c.valid && c.session == uint32_t(session) && c.seq == uint32_t(seq)) return c.ack;
    std::string ack = execute(o, seq);
    auto &slot = cache_[cache_next_++ % cache_.size()];
    slot = {true, uint32_t(session), uint32_t(seq), ack};
    return ack;
  }

  std::string state_json() {
    const int64_t now = env_.mono_ms();
    const auto ph = core_.focus_phase();
    std::string f = "[" + std::to_string(int(ph)) + "," + std::to_string((core_.focus_remaining(now) + 999) / 1000) + "," +
                    std::to_string(core_.focus_total_ms() / 1000) + "]";
    const auto &al = core_.alarm();
    std::string a = "[" + std::to_string(al.enabled ? 1 : 0) + "," + std::to_string(al.minute_of_day / 60) + "," +
                    std::to_string(al.minute_of_day % 60) + "," + std::to_string(core_.alarm_ringing() ? 1 : 0) + "]";
    std::string clk = "[" + std::to_string(env_.local_abs_minute() >= 0 ? 1 : 0) + "," + std::to_string(env_.sync_age_min()) + "]";
    int mv = env_.usb_mv();
    std::string pwr = "[" + std::to_string(mv) + "," + std::to_string(mv >= 4400 ? 1 : 0) + "]";
    return JsonWriter()
        .kv("r", rev_).kv("p", core_.partner()).kv("b", core_.brightness()).kv("snd", core_.sound() ? 1 : 0)
        .raw("f", f).raw("a", a).raw("clk", clk).raw("pwr", pwr).kv("msg", int64_t(message_.size()))
        .kv("fw", std::string(kFirmwareVersion))
        .str();
  }

 private:
  struct CacheSlot {
    bool valid = false;
    uint32_t session = 0, seq = 0;
    std::string ack;
  };

  static int64_t geti(const JsonObject &o, const char *k, int64_t dflt) {
    auto it = o.find(k);
    return (it != o.end() && it->second.kind == JsonValue::kInt) ? it->second.i : dflt;
  }
  static bool getb(const JsonObject &o, const char *k, bool &out) {
    auto it = o.find(k);
    if (it == o.end() || it->second.kind != JsonValue::kBool) return false;
    out = it->second.b;
    return true;
  }
  static bool has_only(const JsonObject &o, std::initializer_list<const char *> extra) {
    for (const auto &kv : o) {
      bool ok = kv.first == "v" || kv.first == "s" || kv.first == "q" || kv.first == "c";
      for (const char *e : extra) ok = ok || kv.first == e;
      if (!ok) return false;
    }
    return true;
  }
  std::string nack(int64_t seq, const char *code) {
    return JsonWriter().kv("q", seq).kv("ok", 0).kv("e", std::string(code)).str();
  }
  std::string ok(int64_t seq, bool changed) {
    if (changed) {
      ++rev_;
      env_.persist();
    }
    return JsonWriter().kv("q", seq).kv("ok", 1).kv("r", rev_).str();
  }

  std::string execute(const JsonObject &o, int64_t seq) {
    auto it = o.find("c");
    if (it == o.end() || it->second.kind != JsonValue::kString) return nack(seq, "json");
    const std::string &c = it->second.s;
    const int64_t now = env_.mono_ms();
    if (c == "get_state") return has_only(o, {}) ? ok(seq, false) : nack(seq, "args");
    if (c == "partner") {
      if (!has_only(o, {"id"})) return nack(seq, "args");
      return core_.set_partner(int(geti(o, "id", -1))) ? ok(seq, true) : nack(seq, "range");
    }
    if (c == "brightness") {
      if (!has_only(o, {"val"})) return nack(seq, "args");
      return core_.set_brightness(int(geti(o, "val", -1))) ? ok(seq, true) : nack(seq, "range");
    }
    if (c == "sound") {
      bool on;
      if (!has_only(o, {"on"}) || !getb(o, "on", on)) return nack(seq, "args");
      core_.set_sound(on);
      return ok(seq, true);
    }
    if (c == "focus_start") {
      if (!has_only(o, {"min"})) return nack(seq, "args");
      int64_t m = geti(o, "min", -1);
      if (m < 1 || m > 120) return nack(seq, "range");
      return core_.start_focus(int(m), now) ? ok(seq, true) : nack(seq, "busy");
    }
    if (c == "focus_pause") return has_only(o, {}) && core_.pause_focus(now) ? ok(seq, true) : nack(seq, "state");
    if (c == "focus_resume") return has_only(o, {}) && core_.resume_focus(now) ? ok(seq, true) : nack(seq, "state");
    if (c == "focus_cancel") return has_only(o, {}) && core_.cancel_focus() ? ok(seq, true) : nack(seq, "state");
    if (c == "alarm_set") {
      bool en;
      if (!has_only(o, {"h", "m", "en"}) || !getb(o, "en", en)) return nack(seq, "args");
      return core_.set_alarm(int(geti(o, "h", -1)), int(geti(o, "m", -1)), en, env_.local_abs_minute()) ? ok(seq, true)
                                                                                                         : nack(seq, "range");
    }
    if (c == "alarm_dismiss") {
      if (!has_only(o, {})) return nack(seq, "args");
      core_.dismiss_alarm();
      return ok(seq, true);
    }
    if (c == "alarm_snooze") return has_only(o, {}) && core_.snooze_alarm(now) ? ok(seq, true) : nack(seq, "state");
    if (c == "time_sync") {
      if (!has_only(o, {"t", "tz"})) return nack(seq, "args");
      int64_t t = geti(o, "t", -1), tz = geti(o, "tz", 9999);
      if (t < 1767225600LL /* 2026-01-01 */ || t > 4102444800LL || tz < -720 || tz > 840) return nack(seq, "range");
      return env_.set_utc(t, int(tz)) ? ok(seq, true) : nack(seq, "rtc");
    }
    if (c == "message") {
      auto m = o.find("txt");
      if (!has_only(o, {"txt"}) || m == o.end() || m->second.kind != JsonValue::kString) return nack(seq, "args");
      if (m->second.s.size() > kMaxMessageBytes || !utf8_valid(m->second.s)) return nack(seq, "range");
      message_ = m->second.s;
      return ok(seq, true);
    }
    if (c == "reaction") {
      if (!has_only(o, {})) return nack(seq, "args");
      env_.reaction();
      return ok(seq, false);
    }
    return nack(seq, "unknown");
  }

  Core &core_;
  DeviceEnv &env_;
  std::string message_ = "오늘도 함께하자";
  uint32_t rev_ = 1;
  std::array<CacheSlot, 8> cache_{};
  size_t cache_next_ = 0;
};

}  // namespace pokedock
