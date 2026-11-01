#pragma once
// Constants of tb_merge_b (bots/tb_merge_b/src/bot.py), same names and values.
// Python fuel constants (FUEL_BUILD_FLOOR / FUEL_SCORE_FLOOR / FUEL_FIRST_TURN_MIN) are replaced
// by the C++ guards at the bottom (100k per turn instead of 2.5M).
#include <cstdint>

namespace P {
constexpr std::int64_t BIG = 1000000;
constexpr int MAX_ROUNDS = 2000;
constexpr int UNREACHED = 65535;
constexpr double SCORE_BOUND_MULT = 1.95;
// stuck guard
constexpr int STUCK_TURNS = 6;
constexpr int STUCK_BAN = 30;
// threat weight by channel (none, tribute, teleport, recall)
constexpr double CHAN_THREAT[4] = { 1.0, 0.5, 0.0, 1.0 };
constexpr int LOCK_MIN_GOLD = 40;
constexpr bool USE_WARDS = true;
constexpr int LOCK_SIDE_MARGIN = 4;
constexpr int FOCUS_BYTE = 7;
constexpr int FOCUS_TTL = 3;
constexpr int ENEMY_SIGHT = 8;
// sf_bank census banking
constexpr int BANK_ANY = 30;
constexpr int BANK_NEAR = 15;
constexpr int BANK_NEAR_D = 15;
constexpr int BANK_CLOSE = 5;
constexpr int BANK_CLOSE_D = 4;
constexpr int BANK_LATE_ROUND = 1900;
constexpr int ALTAR_DANGER_PEN = 12;
constexpr bool BANK_DETOUR = true;
constexpr int BANK_DETOUR_NEAR_D = 8;
constexpr int BANK_DETOUR_CLOSE_D = 3;
constexpr bool BANK_THREAT_LOSING_ONLY = false;
// sf_bank fight / flee
constexpr double FIGHT_ENGAGE = 0.85;
constexpr double FIGHT_ENGAGE_RICH = 0.7;
constexpr int FIGHT_RICH_GEMS = 30;
constexpr double FIGHT_CARRIER_BONUS = 0.15;
constexpr double FIGHT_FLEE = 1.6;
constexpr int RECALL_SAFE_MARGIN = 4;
constexpr double STALL_DECAY = 0.98;
constexpr double STALL_LIMIT = 25.0;
constexpr int CHASE_MAX = 6;
constexpr int CHASE_BAN = 40;
constexpr int DEATH_MEMORY = 250;
constexpr double DEATH_PENALTY = 0.3;
// sf_draft
constexpr bool ITEMS_BRUISER = true;
constexpr bool JUNGLE_FIRST = false;
constexpr bool KIT_LANDING_DASH = true;
constexpr bool KIT_AOE_AIM = true;
constexpr bool KIT_RESET_RETARGET = true;
// Python quirk (verified with bots/cpp_scratch_py): AbilityDash/AbilityAoeDamage.radius is a float, so
// tb_merge_b's dilate(bb, info.radius) raises TypeError inside a try: cast_landing_dash() always returns
// False and aim_area() always returns its fallback (the target tile). false = reproduce that exactly;
// true = the intended behaviour (dilate by int(radius)). Flip only in a measured A/B.
constexpr bool KIT_RADIUS_FIX = false;

// ---- C++ fuel guards (budget 100k per turn, 200k on the first play turn)
constexpr std::uint64_t FUEL_HARD_FLOOR = 4000;      // below: stop optional work
constexpr std::uint64_t FUEL_RESERVE = 8000;         // optional work needs est + this
constexpr std::uint64_t FUEL_SCORE_FLOOR = 20000;    // choose_target: keep best so far below this
constexpr std::uint64_t FUEL_TURNFIELD_MIN = 40000;  // skip the capped per-turn field below this
constexpr std::uint64_t FUEL_BUILD_RESERVE = 12000;  // static field builds after play_turn
constexpr std::uint64_t FUEL_FIRST_TURN_MIN = 85000; // after init_static on turn 1, else shop and return
// (the first turn also pays ~25k of wasm start-up before main; a full play turn on 100x100 is ~70k)
constexpr std::uint64_t FUEL_COMP_MIN = 60000;       // new walk component flood fill (can_reach) only above
constexpr int TURN_FIELD_MAXD = 60;
constexpr int MAX_NEW_REACH = 4;   // first-time can_reach computations per choose_target call
constexpr int MAX_NEW_ESCAPE = 2;  // first-time escape_ok computations per choose_target call
} // namespace P
