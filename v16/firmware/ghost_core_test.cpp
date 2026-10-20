#include "ghost_core.h"
#include <cassert>
#include <cstdio>
using namespace ghost16;
int main(){Core g;assert(g.snapshot().character==0);for(int i=0;i<5;i++)g.next(10);assert(g.snapshot().character==0);
g.preset(15);g.start(100);g.tick(100100);assert(g.snapshot().remaining_s==800);
g.pause(100100);g.tick(200100);assert(g.snapshot().remaining_s==800);
g.resume(200100);g.tick(1000101);assert(g.snapshot().remaining_s==0);assert(g.drain_events() & FocusDone);
g.tick(1000500);assert(!(g.drain_events() & FocusDone));
g.set_alarm(734,true);g.tick(1000600,20261020,734);assert(g.drain_events()&AlarmFire);
g.tick(1000601,20261020,734);assert(!(g.drain_events()&AlarmFire));g.tick(1000602,20261021,734);assert(g.drain_events()&AlarmFire);
g.stop();assert(g.snapshot().mode==Mode::Clock);std::puts("V16 portable core PASS");}
