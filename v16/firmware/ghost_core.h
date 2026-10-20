#pragma once
// Portable V16 state machine, no display or network dependencies.
#include <algorithm>
#include <cstdint>
#include <stdexcept>
namespace ghost16 {
enum class Mode:uint8_t { Clock, Focus };
enum class Motion:uint8_t { Idle, Enter, Hop, Dance, Spin, Peek, Pose, Celebrate, Exit };
enum Events:uint8_t { None=0, FocusDone=1, AlarmFire=2, CharacterChanged=4, Interaction=8 };
struct Snapshot {
 int character=0; Mode mode=Mode::Clock; Motion motion=Motion::Idle;
 bool running=false; bool paused=false; uint32_t remaining_s=1500;
 bool alarm_enabled=false; int alarm_hhmm=730; uint8_t events=0;
};
class Core {
 public:
 void select(int i,uint64_t now){if(i<0||i>4)throw std::out_of_range("character");s_.character=i;animate(Motion::Enter,now,1200);s_.events|=CharacterChanged;}
 void next(uint64_t now){select((s_.character+1)%5,now);}
 void interact(uint64_t now){animate(Motion::Hop,now,900);s_.events|=Interaction;}
 void preset(uint32_t minutes){if(s_.running)throw std::logic_error("running");if(minutes!=15&&minutes!=25&&minutes!=45)throw std::out_of_range("focus");duration_ms_=minutes*60000u;remaining_ms_=duration_ms_;s_.remaining_s=minutes*60;s_.mode=Mode::Focus;s_.paused=false;}
 void start(uint64_t now){if(s_.running)return;if(s_.paused){resume(now);return;}if(s_.mode!=Mode::Focus){s_.mode=Mode::Focus;remaining_ms_=duration_ms_;}s_.running=true;s_.paused=false;ends_at_=now+remaining_ms_;animate(Motion::Pose,now,900);}
 void pause(uint64_t now){if(!s_.running)return;focus_tick(now);if(!s_.running)return;s_.running=false;s_.paused=true;}
 void resume(uint64_t now){if(!s_.paused||s_.running)return;ends_at_=now+remaining_ms_;s_.running=true;s_.paused=false;}
 void stop(){s_.running=false;s_.paused=false;s_.mode=Mode::Clock;remaining_ms_=duration_ms_;s_.remaining_s=remaining_ms_/1000;}
 void set_alarm(int hhmm,bool enabled){if(hhmm<0||hhmm>2359||hhmm%100>=60)throw std::out_of_range("alarm");s_.alarm_hhmm=hhmm;s_.alarm_enabled=enabled;}
 void tick(uint64_t monotonic_ms,int trusted_date_key=-1,int trusted_hhmm=-1){focus_tick(monotonic_ms);if(s_.motion!=Motion::Idle && monotonic_ms>=motion_until_)s_.motion=Motion::Idle;
 if(s_.alarm_enabled && trusted_date_key>=20200101 && trusted_hhmm==s_.alarm_hhmm){
 const uint64_t key=static_cast<uint64_t>(trusted_date_key)*10000u+static_cast<uint32_t>(trusted_hhmm);
 if(key!=last_alarm_key_){last_alarm_key_=key;s_.events|=AlarmFire;animate(Motion::Celebrate,monotonic_ms,1600);}
 }}
 Snapshot snapshot()const{return s_;}
 uint8_t drain_events(){const uint8_t old=s_.events;s_.events=None;return old;}
 private:
 void animate(Motion m,uint64_t now,uint64_t duration){s_.motion=m;motion_until_=now+duration;}
 void focus_tick(uint64_t now){if(!s_.running)return;
 remaining_ms_=now>=ends_at_?0:ends_at_-now;
 s_.remaining_s=static_cast<uint32_t>((remaining_ms_+999)/1000);
 if(remaining_ms_==0){s_.running=false;s_.paused=false;s_.events|=FocusDone;animate(Motion::Celebrate,now,1600);}
 }
 Snapshot s_{};uint64_t ends_at_=0,motion_until_=0,last_alarm_key_=0;
 uint64_t duration_ms_=1500000,remaining_ms_=1500000;
};
}
