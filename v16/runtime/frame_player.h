#pragma once
// V16 hologram RGB565 compositor for 600x450 AMOLED, host-testable, no device I/O.
// Call on a frame already read from microSD into RAM. Allocations must come from PSRAM
// in device integration. The display QSPI flush and SD driver remain board-specific.
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include "../firmware/ghf_decoder.h"

namespace ghost16 {
struct DisplayFrame { uint16_t* rgb565; size_t capacity_pixels; uint16_t width; uint16_t height; };
struct FrameScratch { uint16_t* color; uint8_t* alpha; size_t capacity_pixels; };
struct FrameParams { int x; int y; int pixel_scale; bool mirror_x; };
enum class ComposeError { Ok, BadFrame, OutputTooSmall, ScratchTooSmall, BadScale };
inline ComposeError compose_frame(const uint8_t* file, size_t len,
                                  DisplayFrame dst, FrameScratch tmp, FrameParams params) {
 if(!dst.rgb565||!tmp.color||!tmp.alpha||dst.width==0||dst.height==0||
    dst.capacity_pixels<size_t(dst.width)*dst.height) return ComposeError::OutputTooSmall;
 if(params.pixel_scale<1||params.pixel_scale>3)return ComposeError::BadScale;
 if(!file||len<12)return ComposeError::BadFrame;
 const uint16_t sw=uint16_t(file[4])|(uint16_t(file[5])<<8);
 const uint16_t sh=uint16_t(file[6])|(uint16_t(file[7])<<8);
 if(sw==0||sh==0||sw>480||sh>480)return ComposeError::BadFrame;
 if(tmp.capacity_pixels<size_t(sw)*sh)return ComposeError::ScratchTooSmall;
 const auto result=decode_ghf1(file,len,tmp.color,tmp.capacity_pixels,0,tmp.alpha,tmp.capacity_pixels);
 if(result.status!=DecodeStatus::Ok)return ComposeError::BadFrame;
 std::fill_n(dst.rgb565,size_t(dst.width)*dst.height,uint16_t(0));
 for(unsigned sy=0;sy<sh;++sy)for(unsigned sx=0;sx<sw;++sx){
  const size_t si=size_t(sy)*sw+sx;if(tmp.alpha[si]==0)continue;
  for(int yy=0;yy<params.pixel_scale;++yy)for(int xx=0;xx<params.pixel_scale;++xx){
   int x=params.x+int(sx)*params.pixel_scale+xx;
   int y=params.y+int(sy)*params.pixel_scale+yy;
   if(params.mirror_x)x=int(dst.width)-1-x;
   if(x<0||y<0||x>=int(dst.width)||y>=int(dst.height))continue;
   dst.rgb565[size_t(y)*dst.width+size_t(x)]=tmp.color[si];
  }
 }
 return ComposeError::Ok;
}
struct PlaybackTimeline {
 const uint16_t* frame_ms=nullptr;size_t frame_count=0;uint64_t started_ms=0;
 size_t index(uint64_t now)const{
  if(!frame_count||!frame_ms)return 0;
  uint64_t sum=0;for(size_t i=0;i<frame_count;++i)sum+=std::max<uint16_t>(frame_ms[i],33);
  if(!sum)return 0;
  uint64_t t=(now>=started_ms?now-started_ms:0)%sum;
  for(size_t i=0;i<frame_count;++i){const uint16_t span=std::max<uint16_t>(frame_ms[i],33);if(t<span)return i;t-=span;}return 0;
 }
};
}
