#pragma once
// V16 GHF1 portable decoder. Supply PSRAM RGB565 output with size >= width*height.
// Pixel opcodes distinguish transparency from opaque RGB565 black. For safe compositing,
// pass alpha_mask[width*height] (0=transparent,255=opaque). Legacy null mask uses
// 0x0000 sentinel and therefore cannot distinguish true black from transparency.
#include <cstdint>
#include <cstddef>
namespace ghost16 {
enum class DecodeStatus{ Ok, Truncated, Header, Dimensions, Overflow };
struct Decoded { DecodeStatus status; uint16_t width; uint16_t height; size_t pixels; };
inline Decoded decode_ghf1(const uint8_t* data,size_t bytes,uint16_t* out,size_t cap,
                            uint16_t transparent=0x0000,
                            uint8_t* alpha_mask=nullptr,size_t alpha_cap=0){
 if(!data||!out||bytes<12)return {DecodeStatus::Truncated,0,0,0};
 if(data[0]!='G'||data[1]!='H'||data[2]!='F'||data[3]!='1')return {DecodeStatus::Header,0,0,0};
 auto u16=[&](size_t at)->uint16_t{return uint16_t(data[at])|uint16_t(data[at+1])<<8;};
 auto u32=[&](size_t at)->uint32_t{return uint32_t(data[at])|uint32_t(data[at+1])<<8|uint32_t(data[at+2])<<16|uint32_t(data[at+3])<<24;};
 const uint16_t w=u16(4),h=u16(6);const uint32_t payload=u32(8);
 if(w==0||h==0||w>480||h>480)return {DecodeStatus::Dimensions,w,h,0};
 const size_t needed=size_t(w)*h;if(cap<needed)return {DecodeStatus::Overflow,w,h,0};
 if(payload!=bytes-12)return {DecodeStatus::Header,w,h,0};
 if(alpha_mask && alpha_cap<needed)return {DecodeStatus::Overflow,w,h,0};
 size_t i=12,j=0;
 while(i<bytes){const uint8_t op=data[i++];size_t n;
  if(op<0x80){n=size_t(op)+1;if(i+n*2>bytes)return {DecodeStatus::Truncated,w,h,j};
   if(j+n>needed)return {DecodeStatus::Overflow,w,h,j};
   for(size_t k=0;k<n;k++){out[j]=u16(i);if(alpha_mask)alpha_mask[j]=255;j++;i+=2;}}
  else if(op<0xC0){n=(op&63)+1;if(j+n>needed)return {DecodeStatus::Overflow,w,h,j};
   for(size_t k=0;k<n;k++){out[j]=transparent;if(alpha_mask)alpha_mask[j]=0;j++;}}
  else {n=(op&63)+1;if(i+2>bytes)return {DecodeStatus::Truncated,w,h,j};
   const uint16_t c=u16(i);i+=2;if(j+n>needed)return {DecodeStatus::Overflow,w,h,j};
   for(size_t k=0;k<n;k++){out[j]=c;if(alpha_mask)alpha_mask[j]=255;j++;}}
 }
 if(j!=needed)return {DecodeStatus::Truncated,w,h,j};
 return {DecodeStatus::Ok,w,h,j};
}
}
