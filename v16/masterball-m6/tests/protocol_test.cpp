// Host unit tests for core/protocol.hpp + mini_json.hpp (device side of BLE protocol v2).
#include "../core/protocol.hpp"

#include <cstdio>

using namespace pokedock;
static int g_pass = 0, g_fail = 0;
#define CHECK(name, cond)                                         \
  do {                                                            \
    if (cond) ++g_pass;                                           \
    else {                                                        \
      ++g_fail;                                                   \
      std::printf("FAIL %s (%s:%d)\n", name, __FILE__, __LINE__); \
    }                                                             \
  } while (0)

struct MockEnv : DeviceEnv {
  int64_t mono = 0, abs_min = -1, synced_utc = 0;
  int tz = 0, persists = 0, reactions = 0;
  int64_t mono_ms() override { return mono; }
  int64_t local_abs_minute() override { return abs_min; }
  bool set_utc(int64_t t, int tz_min) override {
    synced_utc = t;
    tz = tz_min;
    abs_min = local_abs_minutes(t, tz_min);
    return true;
  }
  int sync_age_min() override { return synced_utc ? 0 : -1; }
  int usb_mv() override { return 4850; }
  void persist() override { ++persists; }
  void reaction() override { ++reactions; }
};

static bool has(const std::string &s, const char *frag) { return s.find(frag) != std::string::npos; }

int main() {
  Core core;
  MockEnv env;
  ProtocolEngine pe(core, env);
  auto cmd = [&](const std::string &body, int q, bool auth = true, int s = 77) {
    return pe.handle("{\"v\":2,\"s\":" + std::to_string(s) + ",\"q\":" + std::to_string(q) + "," + body + "}", auth);
  };
  CHECK("unauthenticated write refused", has(cmd("\"c\":\"partner\",\"id\":393", 1, false), "\"e\":\"auth\"") && core.partner() == 94);
  CHECK("partner ok", has(cmd("\"c\":\"partner\",\"id\":393", 2), "\"ok\":1") && core.partner() == 393);
  CHECK("partner range", has(cmd("\"c\":\"partner\",\"id\":999", 3), "\"e\":\"range\""));
  CHECK("unknown field rejected", has(cmd("\"c\":\"partner\",\"id\":94,\"x\":1", 4), "\"e\":\"args\"") && core.partner() == 393);
  CHECK("wrong type rejected", has(cmd("\"c\":\"brightness\",\"val\":\"40\"", 5), "\"e\":\"range\""));
  CHECK("float rejected", has(pe.handle("{\"v\":2,\"s\":1,\"q\":6,\"c\":\"brightness\",\"val\":4.5}", true), "\"e\":\"json\""));
  CHECK("bad version", has(pe.handle("{\"v\":1,\"s\":1,\"q\":7,\"c\":\"get_state\"}", true), "\"e\":\"ver\""));
  CHECK("duplicate key rejected", has(pe.handle("{\"v\":2,\"v\":2,\"s\":1,\"q\":8,\"c\":\"get_state\"}", true), "\"e\":\"json\""));
  CHECK("oversize rejected", has(pe.handle(std::string(181, ' '), true), "\"e\":\"size\""));
  CHECK("seq 0 rejected", has(cmd("\"c\":\"get_state\"", 0), "\"e\":\"seq\""));
  // duplicate (retry after lost ACK) must not execute twice
  CHECK("focus start", has(cmd("\"c\":\"focus_start\",\"min\":25", 10), "\"ok\":1"));
  env.mono = 60000;
  uint32_t rev = pe.rev();
  std::string again = cmd("\"c\":\"focus_start\",\"min\":25", 10);
  CHECK("retry returns cached ACK", has(again, "\"ok\":1") && pe.rev() == rev && core.focus_remaining(env.mono) == 1440000);
  CHECK("new start while running refused", has(cmd("\"c\":\"focus_start\",\"min\":15", 11), "\"e\":\"busy\""));
  CHECK("pause", has(cmd("\"c\":\"focus_pause\"", 12), "\"ok\":1"));
  CHECK("pause twice -> state", has(cmd("\"c\":\"focus_pause\"", 13), "\"e\":\"state\""));
  CHECK("cancel", has(cmd("\"c\":\"focus_cancel\"", 14), "\"ok\":1") && core.focus_phase() == FocusPhase::kIdle);
  // same seq, different session (app restarted) executes
  CHECK("new session same seq executes", has(cmd("\"c\":\"focus_start\",\"min\":15", 10, true, 78), "\"ok\":1") &&
                                             core.focus_total_ms() == 900000);
  // time sync + alarm
  CHECK("time sync range", has(cmd("\"c\":\"time_sync\",\"t\":1000,\"tz\":540", 20), "\"e\":\"range\""));
  CHECK("time sync ok", has(cmd("\"c\":\"time_sync\",\"t\":1792881000,\"tz\":540", 21), "\"ok\":1") &&
                            abs_minute_of_day(env.abs_min) == 7 * 60 + 30);
  CHECK("alarm set", has(cmd("\"c\":\"alarm_set\",\"h\":7,\"m\":31,\"en\":true", 22), "\"ok\":1"));
  env.abs_min += 1;
  core.tick(env.mono, env.abs_min);
  CHECK("alarm rings at 07:31", core.alarm_ringing());
  CHECK("snooze from app", has(cmd("\"c\":\"alarm_snooze\"", 23), "\"ok\":1") && !core.alarm_ringing());
  CHECK("dismiss from app", has(cmd("\"c\":\"alarm_dismiss\"", 24), "\"ok\":1") && !core.snooze_pending());
  CHECK("alarm bad bool", has(cmd("\"c\":\"alarm_set\",\"h\":7,\"m\":0,\"en\":1", 25), "\"e\":\"args\""));
  // message: Korean UTF-8, length bound, escapes
  CHECK("message korean", has(cmd("\"c\":\"message\",\"txt\":\"사랑해 \\\"팬텀\\\"\"", 30), "\"ok\":1") && pe.message() == "사랑해 \"팬텀\"");
  std::string long_txt(91, 'a');
  CHECK("message too long", has(cmd("\"c\":\"message\",\"txt\":\"" + long_txt + "\"", 31), "\"e\":\"range\""));
  CHECK("invalid utf8 rejected", has(cmd("\"c\":\"message\",\"txt\":\"\xC3\x28\"", 32), "\"e\":\"json\""));
  CHECK("sound bool", has(cmd("\"c\":\"sound\",\"on\":false", 33), "\"ok\":1") && !core.sound());
  CHECK("reaction", has(cmd("\"c\":\"reaction\"", 34), "\"ok\":1") && env.reactions == 1);
  std::string st = pe.state_json();
  CHECK("state compact for MTU 185", st.size() <= 182);
  CHECK("state fields", has(st, "\"p\":393") && has(st, "\"snd\":0") && has(st, "\"clk\":[1,0]") && has(st, "\"pwr\":[4850,1]"));
  JsonObject parsed;
  CHECK("ack is valid json", JsonReader::parse(cmd("\"c\":\"get_state\"", 40), parsed) && parsed["ok"].i == 1);
  CHECK("persist called on changes", env.persists >= 8);
  std::printf("state=%s (%zu bytes)\n", st.c_str(), st.size());
  std::printf("%s: %d passed, %d failed\n", g_fail ? "FAIL" : "PASS", g_pass, g_fail);
  return g_fail ? 1 : 0;
}
