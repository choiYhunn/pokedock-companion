#include "frame_player.h"
#include <cassert>
#include <array>
#include <cstdio>
using namespace ghost16;
int main(){
 // 2×2 source: opaque red, transparent, opaque BLACK, opaque green.
 const uint8_t file[]={ 'G','H','F','1', 2,0,2,0, 9,0,0,0,
     0, 0x00,0xf8, 0x80,1, 0,0,0xe0,0x07 };
 std::array<uint16_t,24> dst{};std::array<uint16_t,4> tmp{};std::array<uint8_t,4> alpha{};
 auto result=compose_frame(file,sizeof(file),{dst.data(),dst.size(),6,4},{tmp.data(),alpha.data(),4},{1,1,1,false});
 assert(result==ComposeError::Ok);assert(dst[1+1*6]==0xf800);assert(dst[2+1*6]==0);
 assert(dst[1+2*6]==0);assert(alpha[2]==255);assert(alpha[1]==0);
 assert(dst[2+2*6]==0x07e0);
 result=compose_frame(file,sizeof(file),{dst.data(),dst.size(),6,4},{tmp.data(),alpha.data(),4},{1,1,1,true});
 assert(result==ComposeError::Ok);assert(dst[4+1*6]==0xf800);assert(dst[3+2*6]==0x07e0);
 result=compose_frame(file,14,{dst.data(),dst.size(),6,4},{tmp.data(),alpha.data(),4},{1,1,1,true});
 assert(result==ComposeError::BadFrame);
 result=compose_frame(file,sizeof(file),{dst.data(),dst.size(),6,4},{tmp.data(),alpha.data(),1},{1,1,1,false});
 assert(result==ComposeError::ScratchTooSmall);
 const uint16_t times[]={100,300,200};PlaybackTimeline t{times,3,1000};
 assert(t.index(1000)==0&&t.index(1100)==1&&t.index(1450)==2&&t.index(1600)==0);
 std::puts("V16 GHF1 RGB565+alpha compositor, mirror, clipping and timeline PASS");
}
