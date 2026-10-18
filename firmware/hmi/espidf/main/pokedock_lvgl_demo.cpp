#include "pokedock_lvgl_demo.h"

#include <cstdint>
#include <cstdio>
#include "bsp/esp-bsp.h"
#include "esp_err.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "lvgl.h"
#include "study_engine.h"

// Minimal native LVGL 9 preview for 800x480.
// English diagnostics only: Hangul requires bundled Korean font glyphs.
// No assets are scraped/packed; "GENGAR" placeholder is text only.
// No NVS, RTC, Wi-Fi, rewards or automatic software updates.
namespace {
static constexpr const char* TAG = "PokéDock-LVGL";
static StudyEngine focus;
static StudyEngine countdown;
static lv_obj_t* title_label = nullptr;
static lv_obj_t* timer_label = nullptr;
static lv_obj_t* status_label = nullptr;
static uint32_t focus_duration = 25u * 60u;

uint64_t monotonic_ms() {
    return static_cast<uint64_t>(esp_timer_get_time()) / 1000u;
}
void set_status(const char* message) {
    lv_label_set_text(status_label, message);
}
void on_preset(lv_event_t* ev) {
    const uint32_t minutes =
      static_cast<uint32_t>(reinterpret_cast<uintptr_t>(lv_event_get_user_data(ev)));
    if(minutes!=15 && minutes!=25 && minutes!=45)return;
    focus_duration = minutes * 60u;
    lv_label_set_text_fmt(timer_label, "%02u:00", static_cast<unsigned>(minutes));
    set_status("Focus preset selected - press START");
}
void on_start(lv_event_t*) {
    focus.startFocus(focus_duration, monotonic_ms());
    set_status("Focus running (no persistent credit)");
}
void on_pause(lv_event_t*) {
    if(focus.snapshot().paused)focus.resume(monotonic_ms());
    else focus.pause(monotonic_ms());
}
void on_stop(lv_event_t*) {
    focus.stop(monotonic_ms());
    countdown.stop(monotonic_ms());
    lv_label_set_text_fmt(timer_label, "%02u:00",
                         static_cast<unsigned>(focus_duration/60u));
    set_status("Stopped. Incomplete Focus gives no reward.");
}
void on_break(lv_event_t*) {
    focus.stop(monotonic_ms());
    countdown.startCountdown(5u*60u, monotonic_ms());
    set_status("Five-minute break: no Focus reward");
}
void on_timer(lv_timer_t*) {
    const uint64_t now = monotonic_ms();
    if(focus.snapshot().mode==RunMode::FOCUS){
        const StudyEvent event=focus.tick(now);
        if(event==StudyEvent::FOCUS_COMPLETE)
            set_status("Focus complete (demo - NOT saved)");
        const uint32_t remaining=focus.snapshot().remaining_s;
        lv_label_set_text_fmt(timer_label,"%02u:%02u",
            static_cast<unsigned>(remaining/60),static_cast<unsigned>(remaining%60));
    } else if(countdown.snapshot().mode==RunMode::COUNTDOWN){
        const StudyEvent event=countdown.tick(now);
        if(event==StudyEvent::COUNTDOWN_COMPLETE)set_status("Break ended");
        const uint32_t remaining=countdown.snapshot().remaining_s;
        lv_label_set_text_fmt(timer_label,"%02u:%02u",
            static_cast<unsigned>(remaining/60),static_cast<unsigned>(remaining%60));
    }
}
lv_obj_t* add_button(lv_obj_t* root,const char* label,int x,int y,
                     lv_event_cb_t cb,void* userdata=nullptr) {
    lv_obj_t* b=lv_button_create(root);
    lv_obj_set_size(b,125,48);
    lv_obj_set_pos(b,x,y);
    lv_obj_add_event_cb(b,cb,LV_EVENT_CLICKED,userdata);
    lv_obj_t* txt=lv_label_create(b);
    lv_label_set_text(txt,label);
    lv_obj_center(txt);
    return b;
}
} // namespace

void pokedock_lvgl_demo_start(){
    ESP_LOGW(TAG,"UNVERIFIED: first native HOME/FOCUS demo; confirm LCD/GT911 on physical SKU 33630");
    lv_display_t* disp=bsp_display_start();
    if(!disp){
        ESP_LOGE(TAG,"Managed BSP display init failed");
        return;
    }
    if(bsp_display_lock(0)!=ESP_OK){
        ESP_LOGE(TAG,"LVGL lock failed");
        return;
    }
    lv_obj_t* screen=lv_screen_active();
    lv_obj_set_style_bg_color(screen,lv_color_hex(0xF7F3EE),LV_PART_MAIN);
    title_label=lv_label_create(screen);
    lv_label_set_text(title_label,"POKEDOCK  /  GENGAR");
    lv_obj_set_style_text_color(title_label,lv_color_hex(0x4D3E63),LV_PART_MAIN);
    lv_obj_set_pos(title_label,26,18);
    timer_label=lv_label_create(screen);
    lv_label_set_text(timer_label,"25:00");
    lv_obj_set_style_text_color(timer_label,lv_color_hex(0x211C29),LV_PART_MAIN);
    lv_obj_set_style_text_font(timer_label,&lv_font_montserrat_48,LV_PART_MAIN);
    lv_obj_set_pos(timer_label,40,98);
    status_label=lv_label_create(screen);
    lv_label_set_text(status_label,"V14 native touch demo / no saved data");
    lv_obj_set_pos(status_label,24,390);
    add_button(screen,"15 MIN",25,225,on_preset,reinterpret_cast<void*>(15));
    add_button(screen,"25 MIN",165,225,on_preset,reinterpret_cast<void*>(25));
    add_button(screen,"45 MIN",305,225,on_preset,reinterpret_cast<void*>(45));
    add_button(screen,"START",25,295,on_start);
    add_button(screen,"PAUSE",165,295,on_pause);
    add_button(screen,"STOP",305,295,on_stop);
    add_button(screen,"5 MIN BREAK",455,295,on_break);
    lv_timer_create(on_timer,250,nullptr);
    bsp_display_unlock();
    ESP_LOGI(TAG,"LVGL widgets created; verify on real panel before enabling as firmware default");
    (void)bsp_display_backlight_on();
}
