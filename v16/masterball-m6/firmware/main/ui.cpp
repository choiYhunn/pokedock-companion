#include "ui.hpp"

#include <cstdio>

#include "anim_director.hpp"
#include "assets.h"
#include "board.h"
#include "esp_timer.h"
#include "lvgl.h"
#include "pdk_format.h"

LV_FONT_DECLARE(pd_digits_210);
LV_FONT_DECLARE(pd_digits_140);
LV_FONT_DECLARE(pd_digits_120);
LV_FONT_DECLARE(pd_digits_80);
LV_FONT_DECLARE(pd_ui_48);
LV_FONT_DECLARE(pd_ui_40);
LV_FONT_DECLARE(pd_msg_30);

namespace ui {
namespace {

constexpr lv_coord_t kSize = PD_LCD_RES;
// Night theme (m7-0.5.1, matches the owner's concept photo; dark pixels also cost the AMOLED almost no power).
// WCAG contrast on kBg: kInk 14.6:1, kMuted 6.5:1, kAccent 6.8:1 (ink on pill 12.3:1). Sprites keep their transparency;
// a mid-purple partner (e.g. Gengar ~#705898) is only ~2.8:1 on kBg: judge it on the real AMOLED.
const lv_color_t kBg = lv_color_hex(0x1F1A3A), kInk = lv_color_hex(0xF3EEFF), kMuted = lv_color_hex(0xA99BCB),
                 kTrack = lv_color_hex(0x3A3160), kAccent = lv_color_hex(0xB794F6), kPill = lv_color_hex(0x2D2650),
                 kMsgBg = lv_color_hex(0x332B5A);

Actions g_act{};
lv_obj_t *scr, *stage, *clock_lbl, *sprite, *placeholder, *ring, *big_lbl, *unit_lbl, *status_lbl;
lv_obj_t *overlay_lbl, *alarm_title;
lv_obj_t *alarm_box, *alarm_time, *menu, *menu_btn[6], *pair_box, *pair_digits, *msg_box, *msg_lbl;
lv_obj_t *edit_box, *edit_title, *edit_ctx, *edit_value, *edit_unit, *edit_prev, *edit_next;
View g_last;
bool g_menu = false;
int64_t g_msg_until = 0;
pokedock::Director g_dir;  // partner moods: state loops + one-shots (core/anim_director.hpp)
struct {                   // last decoded frame, so a 30 Hz motion tick only decodes on frame change
  int dex = -1, anim = -1, idx = -1;
  uint16_t w = 0, h = 0;
} g_frame_key;
struct {  // on-device performance log (every 30 s): decode cost and real frame interval
  uint32_t decodes = 0, ticks = 0;
  int64_t decode_us = 0, decode_max_us = 0, since = 0;
} g_perf;

using pokedock::ClockField;
constexpr ClockField kClockFields[] = {ClockField::kYear, ClockField::kMonth, ClockField::kDay, ClockField::kHour,
                                       ClockField::kMinute};
constexpr ClockField kAlarmFields[] = {ClockField::kHour, ClockField::kMinute};
pokedock::LocalDateTime g_edit;
const ClockField *g_fields = kClockFields;
int g_nfields = 5, g_fi = 0;
bool g_edit_open = false, g_edit_alarm = false;
lv_timer_t *g_sprite_timer;

const char *partner_name(int dex) {
  switch (dex) {
    case 94: return "팬텀";
    case 393: return "팽도리";
    case 468: return "토게키스";
    case 448: return "루카리오";
    case 195: return "누오";
    case 175: return "토게피";
    case 417: return "파치리스";
    case 385: return "지라치";
    default: return "";
  }
}

lv_obj_t *label(lv_obj_t *parent, const lv_font_t *f, lv_color_t c) {
  lv_obj_t *l = lv_label_create(parent);
  lv_obj_set_style_text_font(l, f, 0);
  lv_obj_set_style_text_color(l, c, 0);
  lv_obj_set_style_text_align(l, LV_TEXT_ALIGN_CENTER, 0);
  lv_obj_clear_flag(l, LV_OBJ_FLAG_CLICKABLE);
  return l;
}

lv_obj_t *pill(lv_obj_t *parent) {
  lv_obj_t *p = label(parent, &pd_ui_48, kInk);
  lv_obj_set_style_bg_color(p, kPill, 0);
  lv_obj_set_style_bg_opa(p, LV_OPA_COVER, 0);
  lv_obj_set_style_radius(p, 24, 0);
  lv_obj_set_style_pad_hor(p, 18, 0);
  lv_obj_set_style_pad_ver(p, 6, 0);
  return p;
}

void screen_event(lv_event_t *e) {
  lv_event_code_t code = lv_event_get_code(e);
  if (code == LV_EVENT_GESTURE) {
    lv_dir_t d = lv_indev_get_gesture_dir(lv_indev_get_act());
    if (d == LV_DIR_BOTTOM && !g_menu) {
      g_menu = true;
      lv_obj_clear_flag(menu, LV_OBJ_FLAG_HIDDEN);
    } else if (d == LV_DIR_TOP && g_menu) {
      close_menu();
    }
    return;
  }
  if (g_menu) return;
  if (code == LV_EVENT_SHORT_CLICKED || code == LV_EVENT_LONG_PRESSED) {
    pokedock::DirectorInput in;
    in.now_ms = esp_timer_get_time() / 1000;
    in.night = g_last.night;
    g_dir.touched(in);  // a touch wakes a sleeping partner (greet)
  }
  if (code == LV_EVENT_SHORT_CLICKED && g_act.tap) g_act.tap();
  if (code == LV_EVENT_LONG_PRESSED && g_act.long_press) g_act.long_press();
}

void menu_event(lv_event_t *e) {
  const intptr_t id = reinterpret_cast<intptr_t>(lv_event_get_user_data(e));
  const bool lp = lv_event_get_code(e) == LV_EVENT_LONG_PRESSED;
  switch (id) {
    case 0: g_act.menu_timer(lp); break;
    case 1: g_act.menu_alarm(lp); break;
    case 2: g_act.menu_brightness(lp); break;
    case 3: if (!lp) g_act.menu_partner(); break;
    case 4: if (!lp) g_act.menu_pairing(); break;
    case 5: if (!lp) g_act.menu_time(); break;
    default: break;
  }
}

lv_obj_t *menu_button(lv_obj_t *parent, int id, lv_coord_t x, lv_coord_t y, lv_coord_t w, lv_coord_t h) {
  lv_obj_t *b = lv_btn_create(parent);
  lv_obj_set_size(b, w, h);
  lv_obj_align(b, LV_ALIGN_CENTER, x, y);
  lv_obj_set_style_radius(b, 40, 0);
  lv_obj_set_style_bg_color(b, kPill, 0);
  lv_obj_set_style_shadow_width(b, 0, 0);
  lv_obj_t *l = label(b, &pd_ui_40, kInk);
  lv_obj_center(l);
  lv_obj_add_event_cb(b, menu_event, LV_EVENT_SHORT_CLICKED, reinterpret_cast<void *>(static_cast<intptr_t>(id)));
  lv_obj_add_event_cb(b, menu_event, LV_EVENT_LONG_PRESSED, reinterpret_cast<void *>(static_cast<intptr_t>(id)));
  return b;
}

void set_menu_text(int i, const char *t) { lv_label_set_text(lv_obj_get_child(menu_btn[i], 0), t); }

// ---- touch editor: one field per page. The panel is only 36.75 mm wide (1 px = 0.079 mm), so the
// -/+ targets are 110 px (8.7 mm) circles and the page buttons 120 x 64 px; no text below 40 px.
const char *field_unit(ClockField f) {
  switch (f) {
    case ClockField::kYear: return "년";
    case ClockField::kMonth: return "월";
    case ClockField::kDay: return "일";
    case ClockField::kHour: return "시";
    default: return "분";
  }
}

void edit_refresh() {
  char buf[40];
  const ClockField f = g_fields[g_fi];
  lv_label_set_text(edit_title, g_edit_alarm ? "알람 시각" : "시간 맞추기");
  if (f == ClockField::kHour || f == ClockField::kMinute)
    snprintf(buf, sizeof buf, "%02d:%02d", g_edit.hour, g_edit.minute);
  else
    snprintf(buf, sizeof buf, "%04d.%02d.%02d", g_edit.year, g_edit.month, g_edit.day);
  lv_label_set_text(edit_ctx, buf);
  const int v = pokedock::field_value(g_edit, f);
  lv_obj_set_style_text_font(edit_value, f == ClockField::kYear ? &pd_digits_80 : &pd_digits_120, 0);
  snprintf(buf, sizeof buf, f == ClockField::kYear ? "%04d" : "%02d", v);
  lv_label_set_text(edit_value, buf);
  snprintf(buf, sizeof buf, "%s  %d/%d", field_unit(f), g_fi + 1, g_nfields);
  lv_label_set_text(edit_unit, buf);
  lv_label_set_text(lv_obj_get_child(edit_prev, 0), g_fi == 0 ? "취소" : "이전");
  lv_label_set_text(lv_obj_get_child(edit_next, 0), g_fi == g_nfields - 1 ? "저장" : "다음");
}

void edit_step_event(lv_event_t *e) {
  const int delta = int(reinterpret_cast<intptr_t>(lv_event_get_user_data(e)));
  g_edit = pokedock::step_field(g_edit, g_fields[g_fi], delta);
  edit_refresh();
}

void edit_prev_event(lv_event_t *) {
  if (g_fi == 0) return close_editor();
  --g_fi;
  edit_refresh();
}

void edit_next_event(lv_event_t *) {
  if (g_fi < g_nfields - 1) {
    ++g_fi;
    return edit_refresh();
  }
  const pokedock::LocalDateTime t = g_edit;
  const bool alarm = g_edit_alarm;
  close_editor();
  if (alarm) g_act.alarm_time_saved(t.hour, t.minute);
  else g_act.clock_saved(t);
}

lv_obj_t *edit_button(lv_obj_t *parent, const char *text, lv_coord_t x, lv_coord_t y, lv_coord_t w, lv_coord_t h,
                      const lv_font_t *font) {
  lv_obj_t *b = lv_btn_create(parent);
  lv_obj_set_size(b, w, h);
  lv_obj_align(b, LV_ALIGN_CENTER, x, y);
  lv_obj_set_style_radius(b, h / 2, 0);
  lv_obj_set_style_bg_color(b, kPill, 0);
  lv_obj_set_style_shadow_width(b, 0, 0);
  lv_obj_t *l = label(b, font, kInk);
  lv_label_set_text(l, text);
  lv_obj_center(l);
  return b;
}

// -/+ drawn as solid bars (a "-" glyph is only a few px tall on this panel): 44 x 10 px = 3.5 x 0.8 mm
lv_obj_t *sign_button(lv_obj_t *parent, lv_coord_t x, bool plus) {
  lv_obj_t *b = edit_button(parent, "", x, 0, 110, 110, &pd_ui_40);
  for (int i = 0; i < (plus ? 2 : 1); i++) {
    lv_obj_t *bar = lv_obj_create(b);
    lv_obj_remove_style_all(bar);
    lv_obj_set_size(bar, i ? 10 : 44, i ? 44 : 10);
    lv_obj_set_style_radius(bar, 5, 0);
    lv_obj_set_style_bg_color(bar, kInk, 0);
    lv_obj_set_style_bg_opa(bar, LV_OPA_COVER, 0);
    lv_obj_clear_flag(bar, LV_OBJ_FLAG_CLICKABLE);
    lv_obj_center(bar);
  }
  return b;
}

void pill_event(lv_event_t *) {
  if (!g_last.clock_trusted && g_act.menu_time) g_act.menu_time();  // "시간 맞춰줘" opens the editor
}

const char *overlay_text(uint8_t ov) {
  switch (ov) {
    case pokedock::kOvHeart: return "\xe2\x99\xa5";    // U+2665, in pd_msg_30
    case pokedock::kOvSparkle: return "\xe2\x98\x85";  // U+2605
    case pokedock::kOvZzz: return "Zzz";
    case pokedock::kOvExclaim: return "!";
    default: return "";
  }
}

// 30 Hz motion tick. The clip frame comes from the pack (decoded only when it changes); the pose,
// overlay and stage come from the director. Without a pack the neutral placeholder stays.
void sprite_tick(lv_timer_t *) {
  const int64_t now = esp_timer_get_time() / 1000;
  const bool focus = g_last.phase == pokedock::FocusPhase::kRunning || g_last.phase == pokedock::FocusPhase::kPaused;
  pokedock::DirectorInput in;
  in.now_ms = now;
  in.dex = g_last.partner;
  in.ringing = g_last.ringing;
  in.focus_active = focus;
  in.night = g_last.night;
  const pokedock::Shot shot = g_dir.decide(in);
  uint16_t w = 0, h = 0, ms = 100;
  uint8_t frames = 0, clip = shot.anim;
  const lv_img_dsc_t *d = nullptr;
  if (assets_clip(uint16_t(g_last.partner), &clip, &w, &h, &ms, &frames)) {
    const int idx = int((shot.t_ms / (ms ? ms : 100)) % (frames ? frames : 1));
    if (g_frame_key.dex == g_last.partner && g_frame_key.anim == clip && g_frame_key.idx == idx) {
      d = static_cast<const lv_img_dsc_t *>(lv_img_get_src(sprite));
    } else {
      const int64_t t0 = esp_timer_get_time();
      d = assets_frame(uint16_t(g_last.partner), clip, uint32_t(idx), nullptr, nullptr);
      const int64_t us = esp_timer_get_time() - t0;
      g_perf.decodes++;
      g_perf.decode_us += us;
      if (us > g_perf.decode_max_us) g_perf.decode_max_us = us;
      if (d) {
        lv_img_set_src(sprite, d);
        g_frame_key = {g_last.partner, clip, idx, w, h};
      }
    }
  }
  if (d) {
    lv_obj_t *parent = shot.stage == pokedock::Stage::kAlarm ? alarm_box : stage;
    if (lv_obj_get_parent(sprite) != parent) {
      lv_obj_set_parent(sprite, parent);
      lv_obj_set_parent(overlay_lbl, parent);
    }
    const pokedock::Rect r = pokedock::place(shot.stage, w, h, shot.pose);
    lv_img_set_zoom(sprite, uint16_t(r.zoom));
    lv_obj_align(sprite, LV_ALIGN_CENTER, r.x + r.w / 2, r.y + r.h / 2);  // zoom pivots on the centre
    lv_obj_clear_flag(sprite, LV_OBJ_FLAG_HIDDEN);
    lv_obj_add_flag(placeholder, LV_OBJ_FLAG_HIDDEN);
    if (shot.stage == pokedock::Stage::kAlarm) lv_obj_add_flag(alarm_title, LV_OBJ_FLAG_HIDDEN);  // partner takes its place
    if (shot.pose.overlay && shot.pose.overlay_opa) {
      lv_label_set_text(overlay_lbl, overlay_text(shot.pose.overlay));
      lv_obj_set_style_text_font(overlay_lbl, shot.pose.overlay == pokedock::kOvZzz || shot.pose.overlay == pokedock::kOvExclaim ? &pd_ui_48 : &pd_msg_30, 0);
      lv_obj_set_style_opa(overlay_lbl, shot.pose.overlay_opa, 0);
      lv_obj_align(overlay_lbl, LV_ALIGN_CENTER, r.x + r.w * 4 / 5, r.y + 12 + shot.pose.overlay_dy);
      lv_obj_clear_flag(overlay_lbl, LV_OBJ_FLAG_HIDDEN);
    } else {
      lv_obj_add_flag(overlay_lbl, LV_OBJ_FLAG_HIDDEN);
    }
  } else {
    if (lv_obj_get_parent(sprite) != stage) {
      lv_obj_set_parent(sprite, stage);
      lv_obj_set_parent(overlay_lbl, stage);
    }
    lv_obj_add_flag(sprite, LV_OBJ_FLAG_HIDDEN);
    lv_obj_add_flag(overlay_lbl, LV_OBJ_FLAG_HIDDEN);
    lv_obj_clear_flag(placeholder, LV_OBJ_FLAG_HIDDEN);
    lv_obj_clear_flag(alarm_title, LV_OBJ_FLAG_HIDDEN);
  }
  g_perf.ticks++;
  if (!g_perf.since) g_perf.since = now;
  if (now - g_perf.since >= 30000) {
    printf("I (%lld) pd_anim: %lu ticks/30s (%.1f Hz), %lu decodes, avg %lld us, max %lld us, frame %ux%u zoom %d\n",
           (long long)now, (unsigned long)g_perf.ticks, g_perf.ticks / 30.0, (unsigned long)g_perf.decodes,
           (long long)(g_perf.decodes ? g_perf.decode_us / g_perf.decodes : 0), (long long)g_perf.decode_max_us,
           g_frame_key.w, g_frame_key.h, d ? lv_img_get_zoom(sprite) : 0);
    g_perf = {};
    g_perf.since = now;
  }
  if (g_msg_until && now > g_msg_until) {
    g_msg_until = 0;
    lv_obj_add_flag(msg_box, LV_OBJ_FLAG_HIDDEN);
  }
}

}  // namespace

void init(const Actions &a) {
  g_act = a;
  scr = lv_scr_act();
  lv_obj_set_style_bg_color(scr, kBg, 0);
  lv_obj_set_style_bg_opa(scr, LV_OPA_COVER, 0);
  lv_obj_clear_flag(scr, LV_OBJ_FLAG_SCROLLABLE);
  lv_obj_add_event_cb(scr, screen_event, LV_EVENT_ALL, nullptr);

  stage = lv_obj_create(scr);  // everything that pixel-shifts for burn-in protection
  lv_obj_remove_style_all(stage);
  lv_obj_set_size(stage, kSize, kSize);
  lv_obj_clear_flag(stage, LV_OBJ_FLAG_CLICKABLE);
  lv_obj_add_flag(stage, LV_OBJ_FLAG_EVENT_BUBBLE);

  ring = lv_arc_create(stage);
  lv_obj_set_size(ring, 446, 446);
  lv_obj_center(ring);
  lv_arc_set_bg_angles(ring, 0, 360);
  lv_arc_set_rotation(ring, 270);
  lv_arc_set_range(ring, 0, 1000);
  lv_obj_remove_style(ring, nullptr, LV_PART_KNOB);
  lv_obj_clear_flag(ring, LV_OBJ_FLAG_CLICKABLE);
  lv_obj_set_style_arc_color(ring, kTrack, LV_PART_MAIN);
  lv_obj_set_style_arc_color(ring, kAccent, LV_PART_INDICATOR);

  clock_lbl = label(stage, &pd_digits_80, kInk);
  lv_obj_align(clock_lbl, LV_ALIGN_TOP_MID, 0, 48);  // +/-3 px burn-in shift stays inside the circle

  sprite = lv_img_create(stage);
  lv_img_set_antialias(sprite, false);  // nearest neighbour: crisp integer pixel art (zoom from the director)
  lv_obj_clear_flag(sprite, LV_OBJ_FLAG_CLICKABLE);
  lv_obj_add_flag(sprite, LV_OBJ_FLAG_HIDDEN);
  overlay_lbl = label(stage, &pd_msg_30, kAccent);  // original marks only: heart, star, Zzz, !
  lv_obj_add_flag(overlay_lbl, LV_OBJ_FLAG_HIDDEN);

  placeholder = lv_obj_create(stage);  // neutral, clearly not a Pokémon
  lv_obj_set_size(placeholder, 240, 240);
  lv_obj_align(placeholder, LV_ALIGN_CENTER, 0, 30);
  lv_obj_set_style_radius(placeholder, LV_RADIUS_CIRCLE, 0);
  lv_obj_set_style_bg_color(placeholder, kPill, 0);
  lv_obj_set_style_border_width(placeholder, 0, 0);
  lv_obj_clear_flag(placeholder, LV_OBJ_FLAG_CLICKABLE);
  lv_obj_t *ph = label(placeholder, &pd_ui_48, kMuted);
  lv_label_set_text(ph, "포켓몬\n이미지 필요");
  lv_obj_center(ph);

  big_lbl = label(stage, &pd_digits_210, kInk);
  lv_obj_align(big_lbl, LV_ALIGN_CENTER, 0, -22);
  unit_lbl = label(stage, &pd_ui_48, kMuted);
  lv_obj_align(unit_lbl, LV_ALIGN_CENTER, 0, 110);
  status_lbl = pill(stage);
  lv_obj_align(status_lbl, LV_ALIGN_BOTTOM_MID, 0, -46);
  lv_obj_add_flag(status_lbl, LV_OBJ_FLAG_CLICKABLE);
  lv_obj_set_ext_click_area(status_lbl, 16);
  lv_obj_add_event_cb(status_lbl, pill_event, LV_EVENT_SHORT_CLICKED, nullptr);

  alarm_box = lv_obj_create(scr);
  lv_obj_remove_style_all(alarm_box);
  lv_obj_set_size(alarm_box, kSize, kSize);
  lv_obj_add_flag(alarm_box, LV_OBJ_FLAG_EVENT_BUBBLE);
  alarm_title = label(alarm_box, &pd_ui_48, kAccent);  // hidden while the partner is shown instead
  lv_label_set_text(alarm_title, "일어날 시간!");
  lv_obj_align(alarm_title, LV_ALIGN_TOP_MID, 0, 64);
  alarm_time = label(alarm_box, &pd_digits_120, kInk);
  lv_obj_align(alarm_time, LV_ALIGN_CENTER, 0, -20);
  lv_obj_t *hint = label(alarm_box, &pd_ui_48, kMuted);
  lv_label_set_text(hint, "탭: 5분 뒤\n길게: 끄기");
  lv_obj_align(hint, LV_ALIGN_BOTTOM_MID, 0, -56);
  lv_obj_add_flag(alarm_box, LV_OBJ_FLAG_HIDDEN);

  menu = lv_obj_create(scr);
  lv_obj_remove_style_all(menu);
  lv_obj_set_size(menu, kSize, kSize);
  lv_obj_set_style_bg_color(menu, kBg, 0);
  lv_obj_set_style_bg_opa(menu, LV_OPA_COVER, 0);
  lv_obj_add_flag(menu, LV_OBJ_FLAG_EVENT_BUBBLE);
  menu_btn[0] = menu_button(menu, 0, -92, -70, 170, 120);
  menu_btn[1] = menu_button(menu, 1, 92, -70, 170, 120);
  menu_btn[2] = menu_button(menu, 2, -92, 62, 170, 120);
  menu_btn[3] = menu_button(menu, 3, 92, 62, 170, 120);
  menu_btn[4] = menu_button(menu, 4, 0, 168, 190, 64);
  menu_btn[5] = menu_button(menu, 5, 0, -168, 190, 64);  // took the place of the hint label; swipe up still closes
  set_menu_text(5, "시간");
  lv_obj_add_flag(menu, LV_OBJ_FLAG_HIDDEN);

  edit_box = lv_obj_create(scr);  // above the menu, below pairing and the message
  lv_obj_remove_style_all(edit_box);
  lv_obj_set_size(edit_box, kSize, kSize);
  lv_obj_set_style_bg_color(edit_box, kBg, 0);
  lv_obj_set_style_bg_opa(edit_box, LV_OPA_COVER, 0);
  lv_obj_clear_flag(edit_box, LV_OBJ_FLAG_SCROLLABLE);
  edit_title = label(edit_box, &pd_ui_40, kMuted);
  lv_obj_align(edit_title, LV_ALIGN_CENTER, 0, -160);
  edit_ctx = label(edit_box, &pd_ui_40, kAccent);
  lv_obj_align(edit_ctx, LV_ALIGN_CENTER, 0, -100);
  edit_value = label(edit_box, &pd_digits_120, kInk);
  lv_obj_align(edit_value, LV_ALIGN_CENTER, 0, 0);
  edit_unit = label(edit_box, &pd_ui_40, kMuted);
  lv_obj_align(edit_unit, LV_ALIGN_CENTER, 0, 78);
  lv_obj_t *minus = sign_button(edit_box, -165, false);  // outer edge 220 px < 233 px radius; "2026" fits between
  lv_obj_t *plus = sign_button(edit_box, 165, true);
  lv_obj_add_event_cb(minus, edit_step_event, LV_EVENT_SHORT_CLICKED, reinterpret_cast<void *>(intptr_t(-1)));
  lv_obj_add_event_cb(minus, edit_step_event, LV_EVENT_LONG_PRESSED_REPEAT, reinterpret_cast<void *>(intptr_t(-1)));
  lv_obj_add_event_cb(plus, edit_step_event, LV_EVENT_SHORT_CLICKED, reinterpret_cast<void *>(intptr_t(1)));
  lv_obj_add_event_cb(plus, edit_step_event, LV_EVENT_LONG_PRESSED_REPEAT, reinterpret_cast<void *>(intptr_t(1)));
  edit_prev = edit_button(edit_box, "취소", -70, 150, 120, 64, &pd_ui_40);
  edit_next = edit_button(edit_box, "다음", 70, 150, 120, 64, &pd_ui_40);
  lv_obj_add_event_cb(edit_prev, edit_prev_event, LV_EVENT_SHORT_CLICKED, nullptr);
  lv_obj_add_event_cb(edit_next, edit_next_event, LV_EVENT_SHORT_CLICKED, nullptr);
  lv_obj_add_flag(edit_box, LV_OBJ_FLAG_HIDDEN);

  pair_box = lv_obj_create(scr);
  lv_obj_remove_style_all(pair_box);
  lv_obj_set_size(pair_box, kSize, kSize);
  lv_obj_set_style_bg_color(pair_box, kBg, 0);
  lv_obj_set_style_bg_opa(pair_box, LV_OPA_COVER, 0);
  lv_obj_t *pt = label(pair_box, &pd_ui_48, kAccent);
  lv_label_set_text(pt, "페어링");
  lv_obj_align(pt, LV_ALIGN_TOP_MID, 0, 90);
  pair_digits = label(pair_box, &pd_digits_80, kInk);
  lv_obj_center(pair_digits);
  lv_obj_t *ph2 = label(pair_box, &pd_ui_40, kMuted);
  lv_label_set_text(ph2, "번호를 앱에 입력");
  lv_obj_align(ph2, LV_ALIGN_BOTTOM_MID, 0, -96);
  lv_obj_add_flag(pair_box, LV_OBJ_FLAG_HIDDEN);

  msg_box = lv_obj_create(scr);
  lv_obj_set_size(msg_box, 360, LV_SIZE_CONTENT);
  lv_obj_center(msg_box);
  lv_obj_set_style_radius(msg_box, 28, 0);
  lv_obj_set_style_bg_color(msg_box, kMsgBg, 0);
  lv_obj_set_style_border_width(msg_box, 0, 0);
  lv_obj_clear_flag(msg_box, LV_OBJ_FLAG_CLICKABLE);
  msg_lbl = label(msg_box, &pd_msg_30, kInk);
  lv_obj_set_width(msg_lbl, 320);
  lv_label_set_long_mode(msg_lbl, LV_LABEL_LONG_WRAP);
  lv_obj_center(msg_lbl);
  lv_obj_add_flag(msg_box, LV_OBJ_FLAG_HIDDEN);

  g_sprite_timer = lv_timer_create(sprite_tick, 33, nullptr);  // motion at ~30 Hz; clips decode at their own rate
  g_dir.trigger(PDK_GREET, esp_timer_get_time() / 1000);       // appear on boot
}

bool menu_open() { return g_menu; }

void open_clock_editor(const pokedock::LocalDateTime &start) {
  g_edit = pokedock::valid_local(start) ? start : pokedock::LocalDateTime{};
  g_fields = kClockFields;
  g_nfields = 5;
  g_fi = 0;
  g_edit_alarm = false;
  g_edit_open = true;
  close_menu();
  edit_refresh();
  lv_obj_clear_flag(edit_box, LV_OBJ_FLAG_HIDDEN);
}

void open_alarm_editor(int hour, int minute) {
  g_edit = pokedock::LocalDateTime{};
  g_edit.hour = hour;
  g_edit.minute = minute;
  g_fields = kAlarmFields;
  g_nfields = 2;
  g_fi = 0;
  g_edit_alarm = true;
  g_edit_open = true;
  close_menu();
  edit_refresh();
  lv_obj_clear_flag(edit_box, LV_OBJ_FLAG_HIDDEN);
}

bool editor_open() { return g_edit_open; }

void close_editor() {
  g_edit_open = false;
  lv_obj_add_flag(edit_box, LV_OBJ_FLAG_HIDDEN);
}

void close_menu() {
  g_menu = false;
  lv_obj_add_flag(menu, LV_OBJ_FLAG_HIDDEN);
}

void set_screen_on(bool on) {
  board_display_power(on);
  if (on) {
    lv_obj_invalidate(scr);
    g_dir.trigger(PDK_GREET, esp_timer_get_time() / 1000);  // the partner says hello when the screen wakes
  }
}

void show_message(const std::string &m) {
  lv_label_set_text(msg_lbl, m.c_str());
  lv_obj_clear_flag(msg_box, LV_OBJ_FLAG_HIDDEN);
  g_msg_until = esp_timer_get_time() / 1000 + 4500;
}

void react(uint8_t anim) {
  if (anim == PDK_CHEER) anim = PDK_TOUCH;  // cheering is the focus loop; a tap there is a touch
  if (anim == PDK_ALARM) return;            // the alarm loop follows the ringing state
  g_dir.trigger(anim, esp_timer_get_time() / 1000);
}

void update(const View &v) {
  using pokedock::FocusPhase;
  char buf[32];
  const bool focus = v.phase == FocusPhase::kRunning || v.phase == FocusPhase::kPaused;

  // burn-in: shift the stage by up to +/-3 px once a minute
  static const int8_t kShift[8][2] = {{0, 0}, {2, 1}, {-1, 2}, {-2, -1}, {1, -2}, {3, 0}, {0, 3}, {-3, 0}};
  const int s = v.mm % 8;
  lv_obj_set_pos(stage, kShift[s][0], kShift[s][1]);

  lv_obj_add_flag(alarm_box, LV_OBJ_FLAG_HIDDEN);
  if (v.ringing && g_edit_open) close_editor();  // a ringing alarm always wins over an unfinished edit
  if (v.ringing) {
    snprintf(buf, sizeof buf, "%02d:%02d", v.alarm_h, v.alarm_m);
    lv_label_set_text(alarm_time, buf);
    lv_obj_clear_flag(alarm_box, LV_OBJ_FLAG_HIDDEN);
    lv_obj_add_flag(stage, LV_OBJ_FLAG_HIDDEN);
  } else {
    lv_obj_clear_flag(stage, LV_OBJ_FLAG_HIDDEN);
  }

  if (focus) {
    lv_obj_add_flag(clock_lbl, LV_OBJ_FLAG_HIDDEN);
    lv_obj_set_style_arc_width(ring, 14, LV_PART_MAIN);
    lv_obj_set_style_arc_width(ring, 14, LV_PART_INDICATOR);
    lv_arc_set_value(ring, v.total_s ? int16_t(1000L * v.remaining_s / v.total_s) : 0);
    lv_obj_clear_flag(ring, LV_OBJ_FLAG_HIDDEN);
    lv_obj_clear_flag(big_lbl, LV_OBJ_FLAG_HIDDEN);
    if (v.remaining_s >= 600) {
      lv_obj_set_style_text_font(big_lbl, &pd_digits_210, 0);
      snprintf(buf, sizeof buf, "%d", (v.remaining_s + 59) / 60);
      lv_label_set_text(unit_lbl, v.phase == FocusPhase::kPaused ? "일시정지" : "분 남음");
    } else {
      lv_obj_set_style_text_font(big_lbl, &pd_digits_140, 0);
      snprintf(buf, sizeof buf, "%02d:%02d", v.remaining_s / 60, v.remaining_s % 60);
      lv_label_set_text(unit_lbl, v.phase == FocusPhase::kPaused ? "일시정지" : "집중");
    }
    lv_label_set_text(big_lbl, buf);
    lv_obj_clear_flag(unit_lbl, LV_OBJ_FLAG_HIDDEN);
    lv_obj_align(placeholder, LV_ALIGN_CENTER, 0, 300);  // keep the placeholder off-screen in focus
  } else {
    lv_obj_clear_flag(clock_lbl, LV_OBJ_FLAG_HIDDEN);
    if (v.clock_trusted) snprintf(buf, sizeof buf, "%02d:%02d", v.hh, v.mm);
    else snprintf(buf, sizeof buf, "--:--");
    lv_label_set_text(clock_lbl, buf);
    lv_obj_add_flag(big_lbl, LV_OBJ_FLAG_HIDDEN);
    lv_obj_add_flag(unit_lbl, LV_OBJ_FLAG_HIDDEN);
    const bool done = v.phase == FocusPhase::kDone;
    lv_obj_set_style_arc_width(ring, 6, LV_PART_MAIN);
    lv_obj_set_style_arc_width(ring, 6, LV_PART_INDICATOR);
    lv_arc_set_value(ring, done ? 1000 : 0);
    if (done) lv_obj_clear_flag(ring, LV_OBJ_FLAG_HIDDEN);
    else lv_obj_add_flag(ring, LV_OBJ_FLAG_HIDDEN);
    lv_obj_align(placeholder, LV_ALIGN_CENTER, 0, 30);
  }

  const char *status = nullptr;
  if (v.usb_low) status = "전원 약함";
  else if (!v.clock_trusted) status = "시간 맞춰줘";
  else if (v.phase == FocusPhase::kDone) status = "수고했어!";
  if (status && !focus) {
    lv_label_set_text(status_lbl, status);
    lv_obj_clear_flag(status_lbl, LV_OBJ_FLAG_HIDDEN);
  } else {
    lv_obj_add_flag(status_lbl, LV_OBJ_FLAG_HIDDEN);
  }

  // menu labels
  if (focus) set_menu_text(0, "타이머\n길게: 그만");
  else {
    snprintf(buf, sizeof buf, "타이머\n%d분", v.preset_min);
    set_menu_text(0, buf);
  }
  if (v.alarm_en) snprintf(buf, sizeof buf, "알람\n%02d:%02d", v.alarm_h, v.alarm_m);
  else snprintf(buf, sizeof buf, "알람\n꺼짐");
  set_menu_text(1, buf);
  snprintf(buf, sizeof buf, "밝기\n%d", v.brightness);
  set_menu_text(2, buf);
  snprintf(buf, sizeof buf, "파트너\n%s", partner_name(v.partner));
  set_menu_text(3, buf);
  set_menu_text(4, "페어링");

  if (v.passkey) {
    snprintf(buf, sizeof buf, "%06lu", static_cast<unsigned long>(v.passkey % 1000000));
    lv_label_set_text(pair_digits, buf);
    lv_obj_clear_flag(pair_box, LV_OBJ_FLAG_HIDDEN);
  } else {
    lv_obj_add_flag(pair_box, LV_OBJ_FLAG_HIDDEN);
  }
  g_last = v;
}

}  // namespace ui
