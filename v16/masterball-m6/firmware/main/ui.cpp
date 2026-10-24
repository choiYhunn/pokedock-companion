#include "ui.hpp"

#include <cstdio>

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
const lv_color_t kIvory = lv_color_hex(0xFBF8F1), kInk = lv_color_hex(0x4A356D), kMuted = lv_color_hex(0x7D6C94),
                 kTrack = lv_color_hex(0xE8DFEF), kAccent = lv_color_hex(0x7E5BB2), kPill = lv_color_hex(0xF1E6F7);

Actions g_act{};
lv_obj_t *scr, *stage, *clock_lbl, *sprite, *placeholder, *ring, *big_lbl, *unit_lbl, *status_lbl;
lv_obj_t *alarm_box, *alarm_time, *menu, *menu_btn[5], *pair_box, *pair_digits, *msg_box, *msg_lbl;
View g_last;
bool g_menu = false;
uint8_t g_anim = PDK_IDLE;
uint32_t g_frame = 0;
int64_t g_anim_until = 0, g_msg_until = 0;
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
  if (code == LV_EVENT_SHORT_CLICKED && g_act.tap) g_act.tap();
  if (code == LV_EVENT_LONG_PRESSED && g_act.long_press) g_act.long_press();
}

void menu_event(lv_event_t *e) {
  const intptr_t id = reinterpret_cast<intptr_t>(lv_event_get_user_data(e));
  const bool lp = lv_event_get_code(e) == LV_EVENT_LONG_PRESSED;
  switch (id) {
    case 0: g_act.menu_timer(lp); break;
    case 1: if (!lp) g_act.menu_alarm(); break;
    case 2: if (!lp) g_act.menu_brightness(); break;
    case 3: if (!lp) g_act.menu_partner(); break;
    case 4: if (!lp) g_act.menu_pairing(); break;
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

void sprite_tick(lv_timer_t *t) {
  const int64_t now = esp_timer_get_time() / 1000;
  if (g_anim != PDK_IDLE && now > g_anim_until) {
    g_anim = PDK_IDLE;
    g_frame = 0;
  }
  uint16_t ms = 120;
  uint8_t n = 0;
  const lv_img_dsc_t *d = assets_frame(uint16_t(g_last.partner), g_anim, g_frame++, &ms, &n);
  if (d) {
    lv_img_set_src(sprite, d);
    lv_obj_clear_flag(sprite, LV_OBJ_FLAG_HIDDEN);
    lv_obj_add_flag(placeholder, LV_OBJ_FLAG_HIDDEN);
  } else {
    lv_obj_add_flag(sprite, LV_OBJ_FLAG_HIDDEN);
    lv_obj_clear_flag(placeholder, LV_OBJ_FLAG_HIDDEN);
  }
  lv_timer_set_period(t, ms);
  if (g_msg_until && now > g_msg_until) {
    g_msg_until = 0;
    lv_obj_add_flag(msg_box, LV_OBJ_FLAG_HIDDEN);
  }
}

}  // namespace

void init(const Actions &a) {
  g_act = a;
  scr = lv_scr_act();
  lv_obj_set_style_bg_color(scr, kIvory, 0);
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
  lv_img_set_antialias(sprite, false);  // nearest neighbour: crisp integer pixel art
  lv_img_set_zoom(sprite, 768);         // x3 of a 96 px frame = 288 px (22.7 mm)
  lv_obj_align(sprite, LV_ALIGN_CENTER, 0, 30);
  lv_obj_clear_flag(sprite, LV_OBJ_FLAG_CLICKABLE);

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

  alarm_box = lv_obj_create(scr);
  lv_obj_remove_style_all(alarm_box);
  lv_obj_set_size(alarm_box, kSize, kSize);
  lv_obj_add_flag(alarm_box, LV_OBJ_FLAG_EVENT_BUBBLE);
  lv_obj_t *al = label(alarm_box, &pd_ui_48, kAccent);
  lv_label_set_text(al, "일어날 시간!");
  lv_obj_align(al, LV_ALIGN_TOP_MID, 0, 64);
  alarm_time = label(alarm_box, &pd_digits_120, kInk);
  lv_obj_align(alarm_time, LV_ALIGN_CENTER, 0, -20);
  lv_obj_t *hint = label(alarm_box, &pd_ui_48, kMuted);
  lv_label_set_text(hint, "탭: 5분 뒤\n길게: 끄기");
  lv_obj_align(hint, LV_ALIGN_BOTTOM_MID, 0, -56);
  lv_obj_add_flag(alarm_box, LV_OBJ_FLAG_HIDDEN);

  menu = lv_obj_create(scr);
  lv_obj_remove_style_all(menu);
  lv_obj_set_size(menu, kSize, kSize);
  lv_obj_set_style_bg_color(menu, kIvory, 0);
  lv_obj_set_style_bg_opa(menu, LV_OPA_COVER, 0);
  lv_obj_add_flag(menu, LV_OBJ_FLAG_EVENT_BUBBLE);
  menu_btn[0] = menu_button(menu, 0, -92, -70, 170, 120);
  menu_btn[1] = menu_button(menu, 1, 92, -70, 170, 120);
  menu_btn[2] = menu_button(menu, 2, -92, 62, 170, 120);
  menu_btn[3] = menu_button(menu, 3, 92, 62, 170, 120);
  menu_btn[4] = menu_button(menu, 4, 0, 168, 190, 64);
  lv_obj_t *back = label(menu, &pd_ui_40, kMuted);
  lv_label_set_text(back, "뒤로");
  lv_obj_align(back, LV_ALIGN_TOP_MID, 0, 40);
  lv_obj_add_flag(menu, LV_OBJ_FLAG_HIDDEN);

  pair_box = lv_obj_create(scr);
  lv_obj_remove_style_all(pair_box);
  lv_obj_set_size(pair_box, kSize, kSize);
  lv_obj_set_style_bg_color(pair_box, kIvory, 0);
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
  lv_obj_set_style_bg_color(msg_box, lv_color_hex(0xFAF1E7), 0);
  lv_obj_set_style_border_width(msg_box, 0, 0);
  lv_obj_clear_flag(msg_box, LV_OBJ_FLAG_CLICKABLE);
  msg_lbl = label(msg_box, &pd_msg_30, kInk);
  lv_obj_set_width(msg_lbl, 320);
  lv_label_set_long_mode(msg_lbl, LV_LABEL_LONG_WRAP);
  lv_obj_center(msg_lbl);
  lv_obj_add_flag(msg_box, LV_OBJ_FLAG_HIDDEN);

  g_sprite_timer = lv_timer_create(sprite_tick, 120, nullptr);
}

bool menu_open() { return g_menu; }

void close_menu() {
  g_menu = false;
  lv_obj_add_flag(menu, LV_OBJ_FLAG_HIDDEN);
}

void set_screen_on(bool on) {
  board_display_power(on);
  if (on) lv_obj_invalidate(scr);
}

void show_message(const std::string &m) {
  lv_label_set_text(msg_lbl, m.c_str());
  lv_obj_clear_flag(msg_box, LV_OBJ_FLAG_HIDDEN);
  g_msg_until = esp_timer_get_time() / 1000 + 4500;
}

void react(uint8_t anim) {
  g_anim = anim;
  g_frame = 0;
  g_anim_until = esp_timer_get_time() / 1000 + 1800;
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
    lv_img_set_zoom(sprite, 256);  // x1 cheering partner under the number
    lv_obj_align(sprite, LV_ALIGN_CENTER, 0, 150);
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
    lv_img_set_zoom(sprite, 768);
    lv_obj_align(sprite, LV_ALIGN_CENTER, 0, 30);
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
