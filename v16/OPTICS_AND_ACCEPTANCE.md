# V16 Optical / Industrial Design Sign-Off
## Honest constraints
A beamsplitter/reflector makes a virtual **2D image**, not physical free-space holography or omnidirectional 3D. Marketing renders can be far brighter, more opaque and more colorful than the real result. Character facial features and text must pass real ambient light and viewing-angle testing.
- Do not curve the internal reflector; use a flat optically clear piece.
- The rounded outer wall may be molded clear acrylic or a clear box with rounded edges, but curved optical windows may introduce distortion.
- Dust, doubled glass reflections and edge glare need evaluation. No visible tape/glue blobs.
- Clock OLED is independent because a 1.43in optical source may not make digits readable in daylight. Do not assume it works from a 3D mock.
- The version-1 CAD only contains a mock base and visual placement, *not* joinery for actual modules, screws, encoder, O-ring, optics or cable strain relief.
## Three test scenes
1. Unlit desk / power off: chamfer/fillets, cable exit, optical transparency, scratches.
2. Everyday bright desk (500 lux): read clock at 60cm, recognize ghost eyes and mouth at 60cm. 2 observers; photograph at fixed phone exposure, no post-brightening.
3. Evening (150 lux): watch continuous idle and one 2-second dance; check glare from phone/camera and reflections behind clear film.
## Decision rule
Reject module if optical apparent character is less than ~30mm high, blurred, noticeably doubled, or only visible in a dark room. If failed, try larger brighter source/beam splitter redesign ONCE, then screen-style alternative. No sunk-cost continuation.
## Priorities
A: visual crispness. B: physical off-state appearance. C: clock readability. D: 5V safety. E: maintainability. Optional surround lighting should not mask optical artifacts.
