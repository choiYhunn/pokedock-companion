// Host unit tests for core/audio_director.hpp (M7 DFR0534 sound module: frames + cue scheduling).
#include "core/audio_director.hpp"

#include <cstdio>
#include <string>
#include <vector>

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

static std::vector<uint8_t> bytes(std::initializer_list<int> l) {
  std::vector<uint8_t> v;
  for (int b : l) v.push_back(uint8_t(b));
  return v;
}

static std::vector<uint8_t> drain(AudioDirector &a, int64_t now) {
  uint8_t buf[64];
  const size_t n = a.drain(now, buf, sizeof buf);
  return std::vector<uint8_t>(buf, buf + n);
}

static std::vector<uint8_t> track(int t) {
  uint8_t f[8];
  const uint8_t d[2] = {uint8_t(t >> 8), uint8_t(t & 0xFF)};
  const size_t n = dfr0534::frame(dfr0534::kCmdTrack, d, 2, f);
  return std::vector<uint8_t>(f, f + n);
}
static const std::vector<uint8_t> kStop = bytes({0xAA, 0x04, 0x00, 0xAE});

int main() {
  // frames match the DFRobot DFR0534 reference examples byte for byte
  uint8_t f[8];
  const uint8_t eight[2] = {0x00, 0x08};
  size_t n = dfr0534::frame(dfr0534::kCmdTrack, eight, 2, f);
  CHECK("play track 8 = AA 07 02 00 08 BB", std::vector<uint8_t>(f, f + n) == bytes({0xAA, 0x07, 0x02, 0x00, 0x08, 0xBB}));
  const uint8_t v20 = 0x14;
  n = dfr0534::frame(dfr0534::kCmdVolume, &v20, 1, f);
  CHECK("volume 20 = AA 13 01 14 D2", std::vector<uint8_t>(f, f + n) == bytes({0xAA, 0x13, 0x01, 0x14, 0xD2}));
  n = dfr0534::frame(dfr0534::kCmdStop, nullptr, 0, f);
  CHECK("stop = AA 04 00 AE", std::vector<uint8_t>(f, f + n) == kStop);
  n = dfr0534::frame(dfr0534::kCmdPlay, nullptr, 0, f);
  CHECK("play = AA 02 00 AC", std::vector<uint8_t>(f, f + n) == bytes({0xAA, 0x02, 0x00, 0xAC}));

  // track table: 16 distinct tracks, cries after the 8 cues
  CHECK("cry tracks 9..16", AudioDirector::track_of(Cue::kCry, 0) == 9 && AudioDirector::track_of(Cue::kCry, 7) == 16 &&
                                 AudioDirector::track_of(Cue::kCry, 99) == 16 && kTrackCount == 16);
  CHECK("alarm outranks everything", kCueTracks[size_t(Cue::kAlarm)].priority > kCueTracks[size_t(Cue::kTimerDone)].priority &&
                                         kCueTracks[size_t(Cue::kTimerDone)].priority > kCueTracks[size_t(Cue::kCry)].priority);

  {  // boot: nothing goes out before the module has powered up, then volume + stop
    AudioDirector a;
    a.configure(true, 20, true, 24);
    a.begin(0);
    a.play(Cue::kBoot, 0, 0, 1200);
    CHECK("silent before module boot", drain(a, 100).empty());
    std::vector<uint8_t> want = bytes({0xAA, 0x13, 0x01, 0x14, 0xD2});
    want.insert(want.end(), kStop.begin(), kStop.end());
    CHECK("volume then stop at 800 ms", drain(a, 800) == want);
    a.tick(1200);
    CHECK("boot chime at 1200 ms", drain(a, 1200) == track(1));
    a.tick(1200 + 2500);
    CHECK("boot chime stopped at its max length", drain(a, 3700) == kStop && a.current() == Cue::kCount);
  }
  {  // volume cap from the build (3V3 rail budget until measured)
    AudioDirector a;
    a.configure(true, 30, true, 24);
    a.begin(0);
    CHECK("volume capped to 24", a.volume() == 24 && drain(a, 900) == [] {
      std::vector<uint8_t> w = bytes({0xAA, 0x13, 0x01, 0x18, 0xD6});
      w.insert(w.end(), kStop.begin(), kStop.end());
      return w;
    }());
    a.configure(true, 24, true, 24);
    CHECK("unchanged volume is not re-sent", drain(a, 1000).empty());
    a.configure(true, 10, true, 24);
    CHECK("new volume sent once", drain(a, 1100) == bytes({0xAA, 0x13, 0x01, 0x0A, 0xC8}) && drain(a, 1200).empty());
  }
  {  // priorities: alarm is not interrupted by a tap; a tap is replaced by a cry
    AudioDirector a;
    a.configure(true, 20, true, 30);
    a.begin(-1000);
    drain(a, 0);
    CHECK("alarm starts", a.play(Cue::kAlarm, 0) && drain(a, 0) == track(8));
    CHECK("tap dropped while the alarm rings", !a.play(Cue::kTap, 100) && drain(a, 100).empty());
    CHECK("cry dropped while the alarm rings", !a.play(Cue::kCry, 200, 3) && drain(a, 200).empty());
    a.tick(3000);
    CHECK("alarm repeats by re-sending play", drain(a, 3000) == track(8) && a.current() == Cue::kAlarm);
    a.tick(6000);
    CHECK("alarm repeats again", drain(a, 6000) == track(8));
    a.stop(Cue::kTap);
    CHECK("stop(other cue) keeps the alarm", a.current() == Cue::kAlarm && drain(a, 6100).empty());
    a.stop(Cue::kAlarm);
    CHECK("alarm stop sends Stop", drain(a, 6200) == kStop && a.current() == Cue::kCount);
    a.play(Cue::kTap, 7000);
    CHECK("tap plays", drain(a, 7000) == track(4));
    CHECK("cry replaces the tap", a.play(Cue::kCry, 7100, 2) && drain(a, 7100) == track(11));
    CHECK("timer done replaces the cry", a.play(Cue::kTimerDone, 7200) && drain(a, 7200) == track(7));
    CHECK("alarm replaces timer done", a.play(Cue::kAlarm, 7300) && drain(a, 7300) == track(8));
  }
  {  // lid: open sound, then the partner cry after the delay; close sound can be turned off
    AudioDirector a;
    a.configure(true, 20, true, 30);
    a.begin(-1000);
    drain(a, 0);
    a.play(Cue::kLidOpen, 0);
    a.play(Cue::kCry, 0, 5, 700);
    CHECK("lid open sound first", drain(a, 0) == track(2));
    a.tick(500);
    CHECK("cry waits for its delay", drain(a, 500).empty());
    a.tick(700);
    CHECK("partner cry after 700 ms", drain(a, 700) == track(14) && a.current() == Cue::kCry);
    a.play(Cue::kLidClose, 1000);
    CHECK("lid close cuts the cry short", drain(a, 1000) == track(3));
    a.tick(3000);
    CHECK("close sound ends with Stop", drain(a, 3000) == kStop);
    a.configure(true, 20, false, 30);
    CHECK("lid close sound off", !a.play(Cue::kLidClose, 5000) && drain(a, 5000).empty());
    a.play(Cue::kCry, 6000, 0, 700);
    a.stop_all();
    a.tick(7000);
    CHECK("stop_all drops the pending cry", drain(a, 7000).empty());
  }
  {  // mute: sound off or volume 0 stops what plays and refuses new cues
    AudioDirector a;
    a.configure(true, 20, true, 30);
    a.begin(-1000);
    drain(a, 0);
    a.play(Cue::kAlarm, 0);
    drain(a, 0);
    a.configure(false, 20, true, 30);
    CHECK("sound off stops the alarm", drain(a, 10) == kStop && !a.play(Cue::kTap, 20) && drain(a, 20).empty());
    a.configure(true, 0, true, 30);
    std::vector<uint8_t> vol0 = bytes({0xAA, 0x13, 0x01, 0x00, 0xBE});
    CHECK("volume 0 = muted", !a.enabled() && drain(a, 30) == vol0 && !a.play(Cue::kAlarm, 40));
    a.configure(true, 18, true, 30);
    CHECK("unmute restores", a.enabled() && a.play(Cue::kTap, 50) && drain(a, 50).size() == 5 + 6);
  }
  {  // a module that never answers cannot block anything: drain only produces bytes, cap respected
    AudioDirector a;
    a.configure(true, 20, true, 30);
    a.begin(0);
    a.play(Cue::kAlarm, 0);
    uint8_t small[6];
    const size_t k = a.drain(900, small, sizeof small);
    CHECK("drain respects the buffer size", k == 5);
    CHECK("rest follows on the next call", drain(a, 901) == track(8));
  }
  std::printf("%s: %d passed, %d failed\n", g_fail ? "FAIL" : "PASS", g_pass, g_fail);
  return g_fail ? 1 : 0;
}
