#pragma once
// Fuel micro-benchmarks for the C++ SDK (see bots/cpp_port/DESIGN.md).
// Run with a large --fuel quantum so no measurement is split by a suspension.

namespace bench {
// Turn-1 static measurements: SDK primitives, bitboards, distance fields, native BFS.
void static_benches();
// Vision / enumeration measurements; call on later turns when units are in view.
void vision_benches(unsigned round);
}
