#include "ghost_runtime.h"
#include "ssd1309_portable.h"
#include <cassert>
#include <cstdio>
#include <numeric>
#include <vector>
struct Fake : ghost16::OledBus {
 size_t n=0;unsigned cmds=0;
 bool command(uint8_t)override{cmds++;return true;}
 bool data(const uint8_t*,size_t s)override{n+=s;return s==128;}
};
int main(){
 using namespace ghost16;Runtime r;
 for(int i=0;i<5;i++){r.next();}assert(r.snapshot().character==0);r.drain();
 r.set_focus(25);r.start(400);r.tick(500400);assert(r.snapshot().seconds==1000);
 r.pause(500400);r.tick(700400);assert(r.snapshot().seconds==1000);
 r.resume(700400);r.tick(1700400);assert(r.drain()&FocusFinished);
 r.set_countdown(7);r.start(2000000);r.tick(2007000);assert(r.drain()&TimerFinished);
 r.alarm(420,true);r.tick(3000000,{20261022,420,true});assert(r.snapshot().alarm_ringing);
 assert(r.drain()&AlarmFired);r.tick(3000100,{20261022,420,true});
 assert(!(r.drain()&AlarmFired));r.snooze(20261022,420);r.tick(3000200,{20261022,425,true});
 assert(r.drain()&AlarmFired);r.acknowledge();
 r.tick(3000300,{20261023,420,true});assert(r.drain()&AlarmFired);r.acknowledge();
 r.alarm(1438,true);r.tick(3000400,{20261031,1438,true});
 assert(r.drain()&AlarmFired);r.snooze(20261031,1438);
 r.tick(3000401,{20261101,3,true});assert(r.drain()&AlarmFired);r.acknowledge();
 r.set_focus(15);r.start(4000000);r.alarm(420,true);
 r.tick(4000001,{20261101,420,true});
 assert(r.snapshot().running&&r.snapshot().mode==Mode::Focus&&r.snapshot().alarm_ringing);
 r.acknowledge();r.tick(4900000);assert(r.drain()&FocusFinished);
 bool blocked=false;try{r.request_update(false,true,true);}catch(...){blocked=true;}assert(blocked);
 r.request_update(true,true,true);assert(r.drain()&UpdateRequested);
 Fake fake;OledClock oled;assert(oled.init(fake));oled.clock(21,34);
 assert(std::accumulate(oled.bytes().begin(),oled.bytes().end(),0)>0);
 assert(oled.flush(fake)&&fake.n==1024);std::puts("revD host integration PASS");
}
