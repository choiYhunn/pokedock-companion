#include <cassert>
#include <iostream>
#include "../focus_ledger.h"

class FakeStore: public LedgerStorage {
public:
  std::array<uint8_t,48> raw[2]{};
  bool has[2]={false,false};
  bool fail_write=false,partial_write=false;
  bool read(uint8_t n,std::array<uint8_t,48>& b) override {
    if(!has[n]) return false;
    b = raw[n];
    return true;
  }
  bool write_durable(uint8_t n,const std::array<uint8_t,48>& b) override {
    if(fail_write)return false;
    raw[n]=b;has[n]=true;
    if(partial_write){raw[n][12]^=0xff;return false;}
    return true;
  }
};

int main(){
  FakeStore s;
  FocusLedger l(s);
  StudyBondResult out{};
  assert(l.load()&&l.ready());
  assert(l.commit(1,15,20261019,out));
  assert(out.accepted&&l.progress().credited_minutes==15);
  assert(!l.commit(1,15,20261019,out));
  assert(l.progress().credited_minutes==15);
  s.fail_write=true;
  assert(!l.commit(2,45,20261019,out));
  assert(l.progress().last_session_id==1);
  s.fail_write=false;
  s.partial_write=true; // corrupt inactive slot
  assert(!l.commit(2,45,20261019,out));
  FocusLedger recovered(s);
  assert(recovered.load());
  assert(recovered.progress().credited_minutes==15);
  s.partial_write=false;
  assert(recovered.commit(2,45,20261019,out));
  assert(out.accepted&&out.new_stars==1&&(out.new_unlocks&UNLOCK_GENGAR));
  FocusLedger rebooted(s);
  assert(rebooted.load());
  assert(rebooted.progress().credited_minutes==60);
  assert(!rebooted.commit(2,45,20261019,out));
  assert(!rebooted.commit(3,5,20261019,out));
  assert(!rebooted.commit(3,15,20260230,out));
  assert(rebooted.commit(3,15,20261020,out));
  assert(rebooted.progress().credited_minutes==75);
  s.raw[0][1]^=0xff;s.raw[1][2]^=0xff;
  FocusLedger corrupted(s);
  assert(!corrupted.load()); // fail closed instead of silently clearing record
  assert(!corrupted.commit(4,15,20261020,out));
  std::cout<<"V14 durable focus ledger host-fault injection PASS (NVS adapter untested)\n";
}
