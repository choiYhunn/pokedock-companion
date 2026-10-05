#pragma once
#include <stdint.h>

enum class UiMode : uint8_t {
  HOME, MORNING, DOCKED, FOCUS, NIGHT, CALM, BIRTHDAY, NFC_OVERRIDE, ALARM
};

struct Inputs {
  bool alarm=false;
  bool birthday=false;
  bool nfc=false;
  bool focus=false;
  bool docked=false;
  bool dark=false;
  int hour=12;
  uint16_t nfcPokemon=0;
};

struct View {
  UiMode mode;
  uint16_t pokemonId;
  const char* message;
};

inline View resolveView(const Inputs& in){
  if(in.alarm)    return {UiMode::ALARM,175,"일어날 시간!"};
  if(in.birthday) return {UiMode::BIRTHDAY,385,"A SPECIAL EVENT HAS STARTED."};
  if(in.nfc)      return {UiMode::NFC_OVERRIDE,in.nfcPokemon,"NFC Pokémon loaded."};
  if(in.focus)    return {UiMode::FOCUS,448,"집중 모드. 지금은 이것만."};
  if(in.docked)   return {UiMode::DOCKED,417,"전기 모으는 중 ⚡"};
  if(in.dark || in.hour>=23 || in.hour<6) return {UiMode::NIGHT,94,"밤이 됐다. 화면은 조용하게."};
  if(in.hour>=20) return {UiMode::CALM,468,"오늘도 수고했어."};
  if(in.hour>=6 && in.hour<11) return {UiMode::MORNING,175,"좋은 아침!"};
  return {UiMode::HOME,133,"작은 포켓몬 센터가 열려 있어."};
}