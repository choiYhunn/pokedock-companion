// Dumps director poses/placements for tests/anim_parity_test.mjs (C++ vs the simulator's JS).
#include <cstdio>

#include "../core/anim_director.hpp"

using namespace pokedock;
int main() {
  const int dex[] = {94, 393, 468, 448, 195, 175, 417, 385};
  const int sizes[][2] = {{74, 63}, {30, 41}, {86, 52}, {47, 63}, {128, 128}, {40, 128}};
  for (int a = 0; a < PDK_ANIM_COUNT; ++a)
    for (int d : dex)
      for (int t = 0; t < 4200; t += 7) {
        const Pose p = pose_for(uint8_t(a), t, d);
        std::printf("P %d %d %d %d %d %d %d %d %d\n", a, d, t, p.dx, p.dy, p.zoom_pct, p.overlay, p.overlay_dy, p.overlay_opa);
        if (t % 49 == 0)
          for (int st = 0; st < 3; ++st)
            for (const auto &sz : sizes) {
              const Rect r = place(Stage(st), sz[0], sz[1], p);
              std::printf("R %d %d %d %d %d %d %d %d %d %d %d\n", a, d, t, st, sz[0], sz[1], r.x, r.y, r.w, r.h, r.zoom);
            }
      }
  return 0;
}
