#pragma once
// C++ port of tb_merge_b (bots/tb_merge_b/src/bot.py). Same decisions and constants; the data access is
// restructured for the 100k fuel budget (see DESIGN.md): raw status-returning SDK calls instead of
// exceptions, one champion snapshot per turn, cached handles, cached static fields.
#include <cambc.h>

#include <array>
#include <cstdint>
#include <memory>
#include <optional>
#include <span>
#include <unordered_map>
#include <vector>

#include "params.h"

using cambc::bitboard;
using cambc::distance_field;
using cambc::vec2;
namespace raw = cambc::detail;

inline int cheb(vec2 a, vec2 b)
{
	int dx = a.x - b.x, dy = a.y - b.y;
	if (dx < 0) dx = -dx;
	if (dy < 0) dy = -dy;
	return dx > dy ? dx : dy;
}

// champion_state bits
constexpr std::uint32_t ST_ALIVE = 1u, ST_RECALLING = 2u, ST_SUBMITTING = 4u, ST_CAN_MOVE = 8u, ST_CAN_ATTACK = 16u,
						ST_CAN_CAST = 2048u, ST_TELEPORTING = 4096u;
// entity kinds for sdk_attack / sdk_cast
constexpr std::uint32_t EK_CHAMP = 1, EK_CAMP = 2, EK_LOCK = 6;
// raw consumable ids (detail::raw_consumable_ids)
constexpr std::uint32_t CONS_TP = 0, CONS_LOCK = 2;

struct CampRec
{
	std::uint32_t h{};
	vec2 p{};
	int type{};
	double st{};   // base strength
	int r{};       // base attack range
	double maxhp{};
	double hp{};   // knowledge (Python G.hp[p])
};

struct Group
{
	int idx{};
	std::uint32_t gh{};
	std::vector<CampRec> camps;
	bitboard tiles;
	vec2 center{};
	int gems{}, gold{};
	double strength{};
	int rng{};
	int n{};
	int status{};          // 0 alive (assumed), 1 reward available, 2 respawning
	std::int64_t ready{};
	double value{};
	double maxhp_sum{};
	std::unique_ptr<bitboard> wait_ring; // dilate(tiles,1) & ~all_camp_tiles & ~walk_block (lazy)

	double hp_left() const
	{
		double s = 0;
		for (const auto& c : camps) s += c.hp;
		return s;
	}
	double alive_strength() const
	{
		double s = 0;
		for (const auto& c : camps)
			if (c.hp > 0) s += c.st;
		return s;
	}
	bool has_spawn(vec2 p) const
	{
		for (const auto& c : camps)
			if (c.p == p) return true;
		return false;
	}
};

struct AbInfo
{
	bool has{};
	cambc::ability_kind kind{};
	double range{}, radius{}, modifier{};
	int duration{};
	bool exclusive{};
	bool is(cambc::ability_kind k) const { return has && kind == k; }
};

// Visible champion snapshot (enemy or ally)
struct Unit
{
	std::uint32_t h{};
	vec2 pos{};
	double hp{}, maxhp{}, str{}, focus{};
	int range{};
	std::uint32_t state{};
	int type{};
	int gems{ -1 }; // lazy
};

// Visible camp snapshot
struct CampView
{
	std::uint32_t h{};
	vec2 pos{};
	vec2 spawn{};
	int gi{ -1 }; // group index
	int type{};
	int r{};
	double str{};
	double hp{};
	bool awake{};
};

// Attack / spell target: a champion or a camp
struct Tgt
{
	std::uint32_t kind{}; // 0 none, EK_CHAMP, EK_CAMP
	std::uint32_t h{};
	explicit operator bool() const { return kind != 0; }
	bool operator==(const Tgt& o) const { return kind == o.kind && h == o.h; }
};

// Reusable list of positions filled from a bitboard (engine order), capacity PL_CAP
constexpr std::size_t PL_CAP = 1024;
struct PosList
{
	vec2* buf{}; // static storage (constant-initialised, no runtime zeroing)
	std::uint32_t n{};
	void fill(const bitboard& b)
	{
		n = b.positions_into(std::span<vec2>{ buf, PL_CAP });
		if (n > PL_CAP) n = static_cast<std::uint32_t>(PL_CAP);
	}
	const vec2* begin() const { return buf; }
	const vec2* end() const { return buf + n; }
	vec2 operator[](std::uint32_t i) const { return buf[i]; }
};
inline vec2 g_pl_store[3][PL_CAP];

// Debug-only fuel profiler: marks are recorded inside debug_block (fuel-free in debug builds,
// compiled out in --release and on the platform). A turn above PROF_PRINT fuel prints its marks.
struct Prof
{
	static constexpr int N = 48;
	const char* name[N]{};
	std::uint64_t fuel[N]{};
	int n = 0;
	void reset() { n = 0; }
	void mark(const char* s)
	{
		if (n < N)
		{
			name[n] = s;
			fuel[n] = cambc::fuel_remaining();
			++n;
		}
	}
};
inline Prof g_prof;
#define PROF(s) debug_block({ g_prof.mark(s); })

class Bot
{
public:
	void play_turn();
	void build_static_fields();

private:
	// ------------------------------------------------------------ static map
	bool inited = false;
	int W = 0, H = 0, area = 0, CW = 0, chunks = 0;
	std::uint32_t myh = 0;
	int my_type = -1;
	std::unique_ptr<bitboard> walk_block, spawn, altar_ring, all_camp_tiles, terrain_bad;
	std::vector<vec2> altars;
	std::vector<std::unique_ptr<bitboard>> altar_goal; // ring of altar i & ~walk_block
	std::vector<std::vector<vec2>> altar_goal_pts;
	vec2 spawn_lo{}, spawn_hi{}, spawn0{}; // spawn rectangle (inclusive) and first spawn tile
	std::vector<Group> groups;
	// spawn tile -> (group << 8 | camp), bucketed by 8x8 chunk (no per-tile native arrays: native loops cost
	// ~8 fuel per element, so a 100x100 grid fill would cost 80k)
	std::vector<int> chunk_start;
	std::vector<std::pair<std::int32_t, std::int32_t>> chunk_items; // (y*W+x, code)
	int camp_code(vec2 p) const
	{
		const int c = (p.y >> 3) * CW + (p.x >> 3);
		if (c < 0 || c + 1 >= static_cast<int>(chunk_start.size())) return -1;
		const std::int32_t k = p.y * W + p.x;
		for (int i = chunk_start[c]; i < chunk_start[c + 1]; ++i)
			if (chunk_items[i].first == k) return chunk_items[i].second;
		return -1;
	}
	std::array<int, 8> type_range{}, type_have{};
	std::array<double, 8> type_str{}, type_hp{};
	std::vector<std::uint32_t> ally_handles, enemy_handles; // sorted
	int slot = 0;
	vec2 enemy_spawn{};
	std::vector<vec2> lock_side;
	bool has_dash = false, need_crossing = false;
	std::array<AbInfo, 2> abil{};

	// components and memos
	std::vector<std::unique_ptr<bitboard>> comps;
	std::unordered_map<std::uint64_t, std::unique_ptr<bitboard>> cross_cache;
	// per-group memos keyed by (comp << 1 | crystal-or-10-gold) resp. comp: tiny linear lists (hashing is costly)
	std::vector<std::vector<std::pair<int, char>>> reach_c, escape_c;
	static int memo_get(const std::vector<std::pair<int, char>>& v, int key)
	{
		for (auto& e : v)
			if (e.first == key) return e.second;
		return -1;
	}

	// static distance fields (sf_fuel)
	std::vector<std::unique_ptr<distance_field>> gfield; // per group
	std::vector<std::unique_ptr<distance_field>> afield; // per altar (Python key -2-i)
	std::vector<int> sf_todo;
	bool sf_use = false;
	int e_hint = 0;

	// ------------------------------------------------------------ persistent state
	int target = -1; // group index (Python self.target)
	int stuck = 0, stuck_idx = -1;
	std::vector<std::int64_t> banned;
	std::int64_t last_enemy_near = -P::BIG, last_enemy_danger = -P::BIG, last_ally_death = -P::BIG;
	std::vector<std::int64_t> altar_seen;
	std::vector<char> ally_alive;
	int pref_altar = -1;
	std::vector<std::int64_t> died_at;
	bool was_dead = false;
	double stall = 0.0;
	bool holding = false;
	std::unordered_map<std::uint32_t, int> chase_turns;
	std::unordered_map<std::uint32_t, std::int64_t> chase_ban;
	std::vector<char> enemy_locked;

	// ------------------------------------------------------------ per-turn state
	std::int64_t rnd = 0;
	vec2 pos{};
	double hp = 0, maxhp = 0, mystr = 0, myfocus = 0;
	int myrange = 0;
	std::uint32_t mystate = 0;
	int epoch = 0; // bumped after every move/dash (vision and occupancy change)
	std::array<std::uint32_t, 84> items{};
	bool items_ok = false;
	double dps_cache = -1, cdps_cache = -1;
	std::vector<Unit> enemies;  // visible enemies within ENEMY_SIGHT, engine order
	std::vector<CampView> awake; // visible awake camps, engine order
	std::vector<int> claims;
	struct Cand
	{
		double cb;
		int idx;
	};
	std::vector<Cand> ct_cands; // choose_target scratch (capacity reused across turns)

	// per-turn field (dist_field)
	std::unique_ptr<distance_field> tfield;
	std::unique_ptr<bitboard> tvisited;
	bool tfield_ok = false;

	// lazy per-epoch boards
	struct LazyBoard
	{
		std::unique_ptr<bitboard> b;
		int ep = -1;
		std::int64_t r = -1;
	};
	LazyBoard lb_vis, lb_camp, lb_awake, lb_ally, lb_enemy, lb_tp, lb_elock, lb_blocked;
	const bitboard& vis_tiles();
	const bitboard& camp_occ();
	const bitboard& awake_occ();
	const bitboard& ally_occ();
	const bitboard& enemy_occ();
	const bitboard& tp_occ();
	const bitboard& enemy_lock();
	const bitboard& blocked_now();
	bool fresh(LazyBoard& l);

	// scratch boards (each id has one owner function family, so nested calls never clobber)
	enum SB
	{
		SB_T1, SB_T2, SB_T3, SB_DIL1, SB_DIL2, SB_FV, SB_ROOTS, SB_SFW,
		SB_ST_BLOCKED, SB_ST_NE, SB_ST_WALLS, SB_ST_AV, SB_ST_NG,
		SB_GO_LOCAL, SB_CR_LAND, SB_CR_NB,
		SB_TR_FREE, SB_TR_NB, SB_TR_GOALS, SB_TR_LOCAL, SB_TR_TMP,
		SB_F_ALIVE, SB_F_UNSEEN, SB_F_BUSH, SB_F_RG, SB_F_AVOID, SB_F_FREE, SB_F_NG,
		SB_K1, SB_K2, SB_K3, SB_W1, SB_W2, SB_R1, SB_S1, SB_S2, SB_COMP,
		SB_COUNT
	};
	std::array<std::unique_ptr<bitboard>, SB_COUNT> sbs;
	bitboard& sb(int i)
	{
		auto& p = sbs[i];
		if (!p) p = std::make_unique<bitboard>();
		return *p;
	}
	static void copy_into(bitboard& dst, const bitboard& src)
	{
		if (&dst == &src) return;
		dst.clear();
		dst |= src;
	}
	// complement within the board; only ever used as an AND mask (padding bits are irrelevant there)
	static void not_into(bitboard& dst, const bitboard& src)
	{
		dst.fill();
		dst ^= src;
	}
	std::unique_ptr<bitboard> not_walk, not_camp, not_walk_camp;
	PosList pl1{ g_pl_store[0] }, pl2{ g_pl_store[1] }, pl3{ g_pl_store[2] };
	std::unique_ptr<distance_field> mfield;
	std::unique_ptr<bitboard> mvisited, mstart;

	// ------------------------------------------------------------ helpers
	int okey(vec2 v) const { return ((((v.y >> 3) * CW) + (v.x >> 3)) << 6) | ((v.y & 7) << 3) | (v.x & 7); }
	bool in_bounds(vec2 v) const { return v.x >= 0 && v.y >= 0 && v.x < W && v.y < H; }
	int spawn_dist(vec2 t) const;
	bool afford(std::uint64_t est) const;
	std::uint64_t field_cost(int depth) const { return std::uint64_t(chunks) * std::uint64_t(depth + 16) + 300; }
	void dilate_into(const bitboard& in, int r, bitboard& out);

	// snapshot / sdk
	bool refresh_me();
	void load_items();
	std::uint32_t item(std::uint32_t id) { if (!items_ok) load_items(); return items[id]; }
	bool jungle() { return item(25) > 0; }
	std::uint32_t gold();
	std::uint32_t gems();
	std::uint32_t cons_count(std::uint32_t rawid);
	bool ready(int slot);
	int cast(int slot, std::uint32_t kind, std::uint32_t h, vec2 p); // -1 error, 0 false, 1 true
	int cast_none(int slot) { return cast(slot, 0, 0, { -1, -1 }); }
	int cast_at(int slot, vec2 p) { return cast(slot, 0, 0, p); }
	int cast_on(int slot, Tgt t) { return cast(slot, t.kind, t.h, { -1, -1 }); }
	int move_abs(vec2 t); // -1 error, 0 false, 1 true
	bool attack(Tgt t);
	bool do_recall();
	bool can_move() const { return (mystate & ST_CAN_MOVE) != 0; }
	bool can_attack() const { return (mystate & ST_CAN_ATTACK) != 0; }
	bool in_range(vec2 t) const { return cheb(pos, t) <= myrange; }
	bool unit_info(std::uint32_t h, Unit& u);
	bool tgt_info(Tgt t, vec2& p, double& h);
	int enemy_gems(Unit& u);
	bool find_camp(vec2 p, CampView& cv, bool need_state);
	int dash_ability();
	bool has_crystal() { return cons_count(CONS_TP) > 0; }

	// map / static
	void init_static();
	int comp_of(vec2 p);
	const bitboard& staging(int comp, int tcomp, int r);
	bool can_reach(int gi, int comp);
	bool escape_ok(int gi, int comp);
	void sf_dests(bitboard& out);
	void turn_field();
	std::optional<int> group_dist(const Group& G);

	// comms
	void read_claims();
	void write_claim(int idx);
	std::int64_t read_focus();
	void write_focus(std::uint32_t h);

	// knowledge
	void observe();
	double threats();
	void update_alerts(bool with_enemies);
	bool threatened() const;

	// movement
	bool step_toward(const bitboard& goals, const bitboard* avoid = nullptr, const bitboard* no_enter = nullptr);
	bool go_to(const bitboard& goals, const bitboard* avoid = nullptr, const bitboard* no_enter = nullptr);
	bool cross_toward(const bitboard& goals, int comp);

	// shop
	void shop();
	int bruiser_item();
	void buy_lock();

	// combat
	double dps();
	double champ_dps();
	void cast_combat(Tgt target, bool moved, double incoming, bool attacked);
	void kit_units(std::vector<std::pair<vec2, double>>& units);
	vec2 aim_area(double rng, double radius, vec2 fallback);
	bool cast_landing_dash(Tgt target);
	Tgt reset_target(Tgt target);
	bool reset_and_hit(Tgt target);
	Tgt pick_camp_in_range(const Group& G);
	void alive_tiles(const Group& G, bitboard& out);
	bool retreat(const std::vector<Unit>& ens);
	double enemy_dps(const Unit& e) const { return e.str + 0.15 * e.focus; }
	bool recall_safe() const;
	int adjacent_melee(const std::vector<Unit>& ens);
	bool strike(Tgt t, double incoming);
	bool handle_enemies(double incoming);
	int chan_kind(const Unit& e) const;
	void focus_bias(Unit& e, std::int64_t focus, int my_gems, double& ratio, int& tier, int& eg);
	bool stun_channel(Unit& e, double ttk);

	// targeting
	int choose_target();
	void note_progress(int gi, bool progress);

	// banking
	std::int64_t pick_altar(int& goal_altar);
	std::int64_t detour(std::int64_t ad, int gi);
	bool bank_detour(int g, std::int64_t det, bool thr) const;
	bool bank_now(int g, std::int64_t ad, bool thr) const;
	bool do_tribute(int pref);
	void locked_altars();
	bool break_lock(bool force);

	// pvp
	bool try_lock();
	bool try_ward();
};
