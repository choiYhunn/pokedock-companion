#pragma once
// Host-verifiable integration core: device GPIO, RTC trust, OTA and rendering are separate.
#include <cstdint>
#include <stdexcept>
namespace ghost16 {
enum class Mode:uint8_t {Clock,Focus,Countdown,Alarm,Settings,Update};
enum Event:uint32_t {NoEvent=0,CharSwitch=1,Animation=2,FocusFinished=4,TimerFinished=8,AlarmFired=16,Snoozed=32,UpdateRequested=64};
struct Time {uint32_t kst_day=0;uint16_t minute=0;bool trusted=false;};
struct State {Mode mode=Mode::Clock;uint8_t character=0;uint32_t seconds=0;
 bool running=false,paused=false,muted=true,alarm_on=false,alarm_ringing=false;
 uint16_t alarm_minute=450;uint32_t event_mask=0;};
class Runtime {
public:
 void select(uint8_t c){if(c>=5)throw std::out_of_range("character");s_.character=c;s_.event_mask|=CharSwitch;}
 void next(){select((s_.character+1)%5);}
 void interact(){s_.event_mask|=Animation;}
 void set_focus(uint32_t minutes){if(s_.running||s_.paused)throw std::logic_error("active");if(minutes!=15&&minutes!=25&&minutes!=45)throw std::out_of_range("preset");seconds_=minutes*60;s_.seconds=seconds_;s_.mode=Mode::Focus;}
 void set_countdown(uint32_t sec){if(s_.running||s_.paused)throw std::logic_error("active");if(!sec||sec>86400)throw std::out_of_range("countdown");seconds_=sec;s_.seconds=sec;s_.mode=Mode::Countdown;}
 void start(uint64_t ms){if(s_.running)return;if(s_.paused){resume(ms);return;}if(s_.mode!=Mode::Focus&&s_.mode!=Mode::Countdown)throw std::logic_error("choose timer");ends_ms_=ms+uint64_t(s_.seconds)*1000;s_.running=true;}
 void pause(uint64_t ms){tick(ms);if(s_.running){s_.running=false;s_.paused=true;}}
 void resume(uint64_t ms){if(!s_.paused)return;ends_ms_=ms+uint64_t(s_.seconds)*1000;s_.running=true;s_.paused=false;}
 void stop(){s_.running=false;s_.paused=false;s_.mode=Mode::Clock;s_.seconds=0;}
 void alarm(uint16_t min,bool on){if(min>=1440)throw std::out_of_range("HHMM");s_.alarm_minute=min;s_.alarm_on=on;if(!on)s_.alarm_ringing=false;}
 void mute(bool yes){s_.muted=yes;}
 void acknowledge(){s_.alarm_ringing=false;}
 void snooze(uint32_t day,uint16_t minute){if(!s_.alarm_ringing)return;auto d=ordinal(day);if(d<0||minute>=1440)return;snooze_stamp_=uint64_t(d)*1440+minute+5;s_.alarm_ringing=false;s_.event_mask|=Snoozed;}
 void request_update(bool user_ok,bool power_ok,bool idle){if(!(user_ok&&power_ok&&idle)||s_.running||s_.alarm_ringing)throw std::logic_error("unsafe OTA");s_.event_mask|=UpdateRequested;s_.mode=Mode::Update;}
 void tick(uint64_t ms,Time local={}) {
  if(s_.running){if(ms>=ends_ms_){s_.seconds=0;s_.running=false;s_.paused=false;s_.event_mask|=s_.mode==Mode::Focus?FocusFinished:TimerFinished;s_.mode=Mode::Clock;}else s_.seconds=uint32_t((ends_ms_-ms+999)/1000);}
  if(local.trusted&&local.minute<1440){const auto d=ordinal(local.kst_day);if(d<0)return;const uint64_t stamp=uint64_t(d)*1440+local.minute;
   bool due=s_.alarm_on&&local.minute==s_.alarm_minute;
   if(snooze_stamp_&&stamp==snooze_stamp_){due=true;snooze_stamp_=0;}
   if(due&&stamp!=last_fired_){last_fired_=stamp;s_.alarm_ringing=true;s_.event_mask|=AlarmFired;}}
 }
 State snapshot()const{return s_;}
 uint32_t drain(){auto e=s_.event_mask;s_.event_mask=0;return e;}
private:
 static int64_t ordinal(uint32_t ymd){int y=int(ymd/10000),m=int(ymd/100%100),d=int(ymd%100);
  if(y<2020||y>2099||m<1||m>12||d<1)return -1;
  static constexpr int days[]={31,28,31,30,31,30,31,31,30,31,30,31};
  const int maxd=days[m-1]+(m==2&&((y%4==0&&y%100!=0)||y%400==0));if(d>maxd)return -1;
  y-=m<=2;int era=(y>=0?y:y-399)/400;const unsigned yoe=unsigned(y-era*400);
  const unsigned doy=(153u*unsigned(m+(m>2?-3:9))+2)/5+unsigned(d)-1;
  const unsigned doe=yoe*365u+yoe/4u-yoe/100u+doy;
  return int64_t(era*146097)+doe-719468;}
 State s_{};uint32_t seconds_=0;uint64_t ends_ms_=0,last_fired_=0,snooze_stamp_=0;
};
}
