// Host tests for core/anim_director.hpp: mood selection, one-shot timing, Gengar-specific motion,
// and that every pose at every frame size stays inside the round panel and off the text.
#include "../core/anim_director.hpp"

#include <algorithm>
#include <cstdio>
#include <initializer_list>

using namespace pokedock;
static int g_pass = 0, g_fail = 0;
#define CHECK(name, cond)                                         \
  do {                                                            \
    if (cond) {                                                   \
      ++g_pass;                                                   \
    } else {                                                      \
      ++g_fail;                                                   \
      std::printf("FAIL %s (%s:%d)\n", name, __FILE__, __LINE__); \
    }                                                             \
  } while (0)

static const int kDex[] = {94, 393, 468, 448, 195, 175, 417, 385};
// Gen-V Black/White animated sprite canvases used by the V17 app (w x h), plus extremes.
static const int kSizes[][2] = {{74, 63}, {30, 41}, {86, 52}, {47, 63}, {67, 58}, {40, 38}, {53, 55}, {55, 47},
                                {16, 16}, {96, 96}, {128, 128}, {128, 40}, {40, 128}};

static void moods() {
  Director d;
  DirectorInput in;
  in.now_ms = 1000;
  CHECK("day idle", d.decide(in).anim == PDK_IDLE && d.decide(in).stage == Stage::kHome);
  in.night = true;
  in.last_touch_ms = 1000;
  in.now_ms = 1000 + kSleepAfterMs - 1;
  CHECK("night but recently touched: awake", d.decide(in).anim == PDK_IDLE);
  in.now_ms = 1000 + kSleepAfterMs;
  CHECK("night idle 60 s: sleeps", d.decide(in).anim == PDK_SLEEP);
  CHECK("sleep has Zzz", d.decide(in).pose.overlay == kOvZzz);
  d.touched(in);
  d.trigger(PDK_TOUCH, in.now_ms);  // the same tap also reaches the app's tap handler
  in.now_ms += 10;
  Shot s = d.decide(in);
  CHECK("touch while asleep: wakes with greet (not a heart)", s.anim == PDK_GREET);
  in.now_ms += one_shot_ms(PDK_GREET) + 10;
  CHECK("after greet: idle (awake again)", d.decide(in).anim == PDK_IDLE);
  in.night = false;
  in.focus_active = true;
  s = d.decide(in);
  CHECK("focus: cheer loop on the focus stage", s.anim == PDK_CHEER && s.stage == Stage::kFocus);
  d.trigger(PDK_TOUCH, in.now_ms);
  CHECK("tap during focus plays touch", d.decide(in).anim == PDK_TOUCH);
  in.now_ms += one_shot_ms(PDK_TOUCH);
  CHECK("touch ends exactly at its length", d.decide(in).anim == PDK_CHEER);
  in.ringing = true;
  d.trigger(PDK_CELEBRATE, in.now_ms);
  s = d.decide(in);
  CHECK("alarm wins over one-shots", s.anim == PDK_ALARM && s.stage == Stage::kAlarm);
  CHECK("alarm shows !", s.pose.overlay == kOvExclaim);
  in.ringing = false;
  in.focus_active = false;
  CHECK("one-shot during alarm is dropped", d.decide(in).anim == PDK_IDLE);
  d.trigger(PDK_IDLE, in.now_ms);
  CHECK("loops are not triggerable", d.decide(in).anim == PDK_IDLE);
  d.trigger(PDK_CELEBRATE, in.now_ms);
  in.now_ms += 900;
  s = d.decide(in);
  CHECK("celebrate clip time", s.anim == PDK_CELEBRATE && s.t_ms == 900);
  CHECK("celebrate sparkles", s.pose.overlay == kOvSparkle);
}

static void gengar_character() {
  // Gengar peeks in from the side; others drop from above.
  const Pose g0 = pose_for(PDK_GREET, 0, 94), g_end = pose_for(PDK_GREET, 1290, 94);
  CHECK("gengar greet starts off to the side", g0.dx >= 140 && g0.dy == 0);
  CHECK("gengar greet settles", std::abs(g_end.dx) <= 1);
  const Pose p0 = pose_for(PDK_GREET, 0, 393);
  CHECK("piplup greet drops from above", p0.dy <= -45 && p0.dx == 0);
  int max_shake = 0;
  for (int t = 0; t < 900; t += 10) max_shake = std::max(max_shake, std::abs(pose_for(PDK_TOUCH, t, 94).dx));
  CHECK("gengar giggle shake on touch", max_shake >= 6);
  CHECK("non-gengar touch is a hop", pose_for(PDK_TOUCH, 225, 448).dy <= -18 && pose_for(PDK_TOUCH, 225, 448).dx == 0);
  int hover = 0;
  for (int t = 0; t < 3000; t += 50) hover = std::max(hover, std::abs(pose_for(PDK_IDLE, t, 94).dy));
  CHECK("gengar hovers when idle", hover >= 5);
  int ground = 0, zoomed = 0;
  for (int a = 0; a < PDK_ANIM_COUNT; ++a)
    for (int t = 0; t < 4000; t += 10) {
      if (a == PDK_IDLE) ground = std::max(ground, std::abs(pose_for(PDK_IDLE, t, 195).dy));
      for (int d : kDex) zoomed += pose_for(uint8_t(a), t, d).zoom_pct != 100;
    }
  CHECK("quagsire only bobs 2 px (no hovering)", ground == 2);
  CHECK("no mood changes the zoom: pixel art stays integer-scaled", zoomed == 0);
  CHECK("touch heart fades out", pose_for(PDK_TOUCH, 899, 94).overlay_opa < 10 && pose_for(PDK_TOUCH, 100, 94).overlay_opa == 255);
}

static void geometry() {
  const uint8_t anims[] = {PDK_IDLE, PDK_SLEEP, PDK_GREET, PDK_JUMP, PDK_DANCE, PDK_TOUCH, PDK_CHEER, PDK_CELEBRATE, PDK_ALARM, PDK_EGG};
  const Stage stages[] = {Stage::kHome, Stage::kFocus, Stage::kAlarm};
  int outside = 0, over_clock = 0, over_label = 0, alarm_text = 0, on_ring = 0, checked = 0;
  for (Stage st : stages)
    for (const auto &sz : kSizes)
      for (int dex : kDex)
        for (uint8_t a : anims) {
          // only what Director::decide can produce on each stage (alarm drops one-shots, no sleep in focus)
          if (st == Stage::kAlarm && a != PDK_ALARM) continue;
          if (st != Stage::kAlarm && a == PDK_ALARM) continue;
          if (st == Stage::kFocus && a == PDK_SLEEP) continue;
          if (st == Stage::kHome && a == PDK_CHEER) continue;
          for (int t = 0; t < 4000; t += 20) {
            const Rect r = place(st, sz[0], sz[1], pose_for(a, t, dex));
            ++checked;
            for (int cx : {r.x, r.x + r.w})
              for (int cy : {r.y, r.y + r.h})
                if (cx * cx + cy * cy > (kPanelR - 3) * (kPanelR - 3)) ++outside;
            if (st == Stage::kHome && r.y < kHomeTopLimit) ++over_clock;
            if (st == Stage::kFocus && r.y < kFocusTopLimit) ++over_label;
            if (st == Stage::kFocus)
              for (int cx : {r.x, r.x + r.w})
                for (int cy : {r.y, r.y + r.h})
                  if (cx * cx + cy * cy > (kFocusRingR + 1) * (kFocusRingR + 1)) ++on_ring;
            if (st == Stage::kAlarm && r.y + r.h > -92) ++alarm_text;  // alarm time label top
          }
        }
  std::printf("placements checked: %d\n", checked);
  CHECK("every frame corner inside the circle", outside == 0);
  CHECK("home partner never covers the clock", over_clock == 0);
  CHECK("focus partner never covers the minutes label", over_label == 0);
  CHECK("focus partner stays inside the progress ring", on_ring == 0);
  CHECK("alarm partner never covers the alarm time", alarm_text == 0);
  // crisp integer scale at home for the real partner sprites
  for (int i = 0; i < 8; ++i) {
    const int z = base_zoom(Stage::kHome, kSizes[i][0], kSizes[i][1]);
    CHECK("home zoom is an integer multiple", z % 256 == 0);
  }
  CHECK("gengar x3 at home", base_zoom(Stage::kHome, 74, 63) == 768);
  CHECK("togekiss x2 (86 px wide)", base_zoom(Stage::kHome, 86, 52) == 512);
  CHECK("gen-V sprites stay 1x in focus", base_zoom(Stage::kFocus, 74, 63) == 256);
  CHECK("oversized frame shrinks in focus", base_zoom(Stage::kFocus, 128, 128) < 256);
}

int main() {
  moods();
  gengar_character();
  geometry();
  std::printf("%s: %d passed, %d failed\n", g_fail ? "FAIL" : "PASS", g_pass, g_fail);
  return g_fail ? 1 : 0;
}
