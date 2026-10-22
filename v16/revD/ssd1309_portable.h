#pragma once
// SSD1309 2.42in factory-SPI port-neutral 128x64 framebuffer, 1024 bytes.
// Safe electrical power/reset and manufacturer panel-specific init remain required.
#include <array>
#include <cstdint>
#include <cstddef>
namespace ghost16 {
struct OledBus {virtual ~OledBus()=default;virtual bool command(uint8_t)=0;virtual bool data(const uint8_t*,size_t)=0;};
class OledClock {
public:
 static constexpr size_t WIDTH=128,HEIGHT=64,SIZE=1024;
 void clear(){pixels_.fill(0);}
 bool init(OledBus& bus){const uint8_t cmds[]={0xAE,0xD5,0x80,0xA8,0x3F,0xD3,0,0x40,
  0x20,0x02,0xA1,0xC8,0xDA,0x12,0x81,0x7F,0xD9,0xF1,0xDB,0x3C,0xA4,0xA6,0xAF};
  for(auto x:cmds)if(!bus.command(x))return false;return true;}
 void pixel(int x,int y,bool lit=true){if(x<0||x>=128||y<0||y>=64)return;
  auto i=size_t(x)+(y/8)*128;const uint8_t bit=uint8_t(1u<<(y%8));if(lit)pixels_[i]|=bit;else pixels_[i]&=uint8_t(~bit);}
 void rect(int x,int y,int w,int h){for(int j=y;j<y+h;j++)for(int i=x;i<x+w;i++)pixel(i,j);}
 void clock(int hh,int mm){clear();if(hh<0||hh>23||mm<0||mm>59)return;int ds[]={hh/10,hh%10,-1,mm/10,mm%10};int x=5;
  for(int d:ds){if(d==-1){rect(x+3,19,4,5);rect(x+3,39,4,5);x+=16;}else{digit(x,15,d,5);x+=26;}}}
 bool flush(OledBus& bus){for(uint8_t page=0;page<8;page++){
  if(!bus.command(uint8_t(0xB0|page))||!bus.command(0)||!bus.command(0x10))return false;
  if(!bus.data(pixels_.data()+page*128,128))return false;}return true;}
 const std::array<uint8_t,SIZE>& bytes()const{return pixels_;}
private:
 void digit(int x,int y,int n,int scale){static constexpr uint16_t f[10]={0x7B6F,0x2492,0x73E7,0x73CF,0x5BC9,0x79CF,0x79EF,0x7249,0x7BEF,0x7BCF};
  auto g=f[n];for(int r=0;r<5;r++)for(int c=0;c<3;c++)if(g&(1u<<(14-(r*3+c))))rect(x+c*scale,y+r*scale,scale-1,scale-1);}
 std::array<uint8_t,SIZE> pixels_{};
};
}
