#include "ghf_decoder.h"
#include <cassert>
#include <cstdio>
#include <fstream>
#include <vector>
int main(int argc,char **argv){
 assert(argc==2);
 std::ifstream f(argv[1],std::ios::binary);
 std::vector<uint8_t> b((std::istreambuf_iterator<char>(f)),{});
 std::vector<uint16_t> dst(64*64);
 auto good=ghost16::decode_ghf1(b.data(),b.size(),dst.data(),dst.size());
 assert(good.status==ghost16::DecodeStatus::Ok && good.pixels==4096);
 assert(dst[0]==0 && dst[20*64+20]!=0);
 assert(ghost16::decode_ghf1(b.data(),b.size()-1,dst.data(),dst.size()).status!=ghost16::DecodeStatus::Ok);
 assert(ghost16::decode_ghf1(b.data(),b.size(),dst.data(),32).status!=ghost16::DecodeStatus::Ok);
 b[0]='X';assert(ghost16::decode_ghf1(b.data(),b.size(),dst.data(),dst.size()).status==ghost16::DecodeStatus::Header);
 std::puts("GHF1 C++ decoder PASS");
}
