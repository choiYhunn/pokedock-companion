#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include "study_bond_policy.h"

// Host-portable two-slot durable Focus ledger; real NVS binding NOT YET IMPLEMENTED.
// write_durable must commit/sync data. Do not use a nontransactional raw file adapter.
struct LedgerStorage {
  virtual ~LedgerStorage() = default;
  virtual bool read(uint8_t slot, std::array<uint8_t,48>& out) = 0;
  virtual bool write_durable(uint8_t slot, const std::array<uint8_t,48>& bytes) = 0;
};

class FocusLedger {
public:
  explicit FocusLedger(LedgerStorage& store): store_(store) {}
  bool load() {
    StudyBondProgress p{};
    uint32_t latest=0;
    int8_t chosen=-1;
    bool saw_corrupt=false;
    for(int i=0;i<2;++i){
      std::array<uint8_t,48> b{};
      if(!store_.read(static_cast<uint8_t>(i),b))continue;
      StudyBondProgress candidate{};
      uint32_t gen=0;
      if(!decode(b,candidate,gen)){saw_corrupt=true;continue;}
      if(chosen<0||gen>latest){p=candidate;latest=gen;chosen=static_cast<int8_t>(i);}
    }
    if(chosen<0&&saw_corrupt){ready_=false;return false;}
    progress_=p;generation_=latest;active_=chosen;ready_=true;
    return true;
  }
  bool ready() const {return ready_;}
  const StudyBondProgress& progress() const {return progress_;}
  bool commit(uint64_t session_id,uint16_t duration,uint32_t trusted_local_day,StudyBondResult& result){
    result={};
    if(!ready_||generation_==UINT32_MAX)return false;
    StudyBondProgress candidate=progress_;
    const auto proposed=commit_verified_focus(candidate,session_id,duration,trusted_local_day);
    if(!proposed.accepted)return false;
    const uint32_t next_gen=generation_+1;
    const uint8_t next_slot=static_cast<uint8_t>(active_==0?1:0);
    const auto bytes=encode(candidate,next_gen);
    if(!store_.write_durable(next_slot,bytes))return false;
    // Only acknowledge/animate the reward after durable write AND readback.
    std::array<uint8_t,48> verified{};
    if(!store_.read(next_slot,verified)||verified!=bytes)return false;
    StudyBondProgress check{};
    uint32_t gen=0;
    if(!decode(verified,check,gen)||gen!=next_gen||check.last_session_id!=session_id)return false;
    progress_=candidate;active_=static_cast<int8_t>(next_slot);generation_=next_gen;
    result=proposed;
    return true;
  }
private:
  static void put32(std::array<uint8_t,48>& b,int i,uint32_t x) {
    for(int j=0;j<4;++j)b[i+j]=static_cast<uint8_t>(x>>(8*j));
  }
  static uint32_t get32(const std::array<uint8_t,48>& b,int i){
    uint32_t x=0;for(int j=0;j<4;++j)x|=uint32_t(b[i+j])<<(8*j);return x;
  }
  static void put64(std::array<uint8_t,48>& b,int i,uint64_t x){
    for(int j=0;j<8;++j)b[i+j]=static_cast<uint8_t>(x>>(8*j));
  }
  static uint64_t get64(const std::array<uint8_t,48>& b,int i){
    uint64_t x=0;for(int j=0;j<8;++j)x|=uint64_t(b[i+j])<<(8*j);return x;
  }
  static uint32_t hash(const std::array<uint8_t,48>& b){
    uint32_t x=2166136261u;
    for(int i=0;i<44;++i){x^=b[i];x*=16777619u;}
    return x;
  }
  static std::array<uint8_t,48> encode(const StudyBondProgress& p,uint32_t generation){
    std::array<uint8_t,48> b{};
    put32(b,0,0x504B444Bu); // PKDK
    put32(b,4,1u);
    put32(b,8,generation);
    put32(b,12,p.credited_minutes);
    put32(b,16,p.total_stars);
    put32(b,20,p.total_focus_sessions);
    put32(b,24,p.last_day_key);
    put64(b,28,p.last_session_id);
    b[36]=p.day_bond_awards;
    b[37]=static_cast<uint8_t>(p.bond);
    b[38]=static_cast<uint8_t>(p.bond>>8);
    b[39]=p.unlock_bits;
    put32(b,44,hash(b));
    return b;
  }
  static bool decode(const std::array<uint8_t,48>& b,StudyBondProgress& p,uint32_t& generation){
    if(get32(b,0)!=0x504B444Bu||get32(b,4)!=1u||get32(b,44)!=hash(b))return false;
    generation=get32(b,8);
    if(generation==0)return false;
    p.credited_minutes=get32(b,12);
    p.total_stars=get32(b,16);
    p.total_focus_sessions=get32(b,20);
    p.last_day_key=get32(b,24);
    p.last_session_id=get64(b,28);
    p.day_bond_awards=b[36];
    p.bond=static_cast<uint16_t>(b[37]|(uint16_t(b[38])<<8));
    p.unlock_bits=b[39];
    if(p.day_bond_awards>2||p.bond>100||p.credited_minutes/60!=p.total_stars)return false;
    if(p.last_day_key&&!verified_local_day_key(p.last_day_key))return false;
    if(p.total_focus_sessions>p.credited_minutes/15)return false;
    if(p.total_focus_sessions&&!p.last_session_id)return false;
    return true;
  }
  LedgerStorage& store_;
  StudyBondProgress progress_{};
  uint32_t generation_=0;
  int8_t active_=-1;
  bool ready_=false;
};
