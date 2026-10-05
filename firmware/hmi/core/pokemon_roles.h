#pragma once
#include <stdint.h>

enum class PokemonRole : uint8_t { CALM, MORNING, CHARGING, FOCUS, NIGHT, BIRTHDAY };

inline uint16_t pokemon_for_role(PokemonRole role) {
  switch (role) {
    case PokemonRole::CALM: return 468;
    case PokemonRole::MORNING: return 175;
    case PokemonRole::CHARGING: return 417;
    case PokemonRole::FOCUS: return 448;
    case PokemonRole::NIGHT: return 94;
    case PokemonRole::BIRTHDAY: return 385;
  }
  return 468;
}
