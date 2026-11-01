// Snapshot, raw SDK wrappers, static map analysis (init_static), walk components, static
// distance-field cache (sf_fuel) and shared-memory comms.
#include <algorithm>

#include "bot.h"

using namespace P;

// ------------------------------------------------------------------ fuel helpers
bool Bot::afford(std::uint64_t est) const
{
	return cambc::fuel_remaining() > est + FUEL_RESERVE;
}

int Bot::spawn_dist(vec2 t) const
{
	// min over spawn tiles of cheb(p, t): the spawn region is a rectangle
	int dx = 0, dy = 0;
	if (t.x < spawn_lo.x) dx = spawn_lo.x - t.x;
	else if (t.x > spawn_hi.x) dx = t.x - spawn_hi.x;
	if (t.y < spawn_lo.y) dy = spawn_lo.y - t.y;
	else if (t.y > spawn_hi.y) dy = t.y - spawn_hi.y;
	return dx > dy ? dx : dy;
}

void Bot::dilate_into(const bitboard& in, int r, bitboard& out)
{
	// Python dilate(): out = bb; per step h = out | out>>1 | out<<1, out = h | h^1 | h_1
	copy_into(out, in);
	bitboard& a = sb(SB_DIL1);
	bitboard& b = sb(SB_DIL2);
	for (int i = 0; i < r; ++i)
	{
		out.shift_right_into(1, a);
		out.shift_right_into(-1, b);
		out |= a;
		out |= b;
		out.shift_up_into(1, a);
		out.shift_up_into(-1, b);
		out |= a;
		out |= b;
	}
}

// ------------------------------------------------------------------ snapshot / raw sdk
bool Bot::refresh_me()
{
	raw::champion_info ci{};
	if (raw::sdk_champion(myh, &ci) != 0) return false;
	pos = { ci.x, ci.y };
	hp = ci.health;
	maxhp = ci.max_health;
	mystr = ci.strength;
	myfocus = ci.focus;
	myrange = ci.attack_range;
	mystate = static_cast<std::uint32_t>(ci.state);
	return true;
}

void Bot::load_items()
{
	if (raw::sdk_champion_items(myh, items.data()) != 0) items.fill(0);
	items_ok = true;
}

std::uint32_t Bot::gold()
{
	std::uint32_t v{};
	if (raw::sdk_champion_gold(myh, &v) != 0) return 0;
	return v;
}

std::uint32_t Bot::gems()
{
	std::uint32_t v{};
	if (raw::sdk_champion_gems(myh, &v) != 0) return 0;
	return v;
}

std::uint32_t Bot::cons_count(std::uint32_t rawid)
{
	std::array<std::uint32_t, 4> c{};
	if (raw::sdk_champion_consumables(myh, c.data()) != 0) return 0;
	return c[rawid];
}

bool Bot::ready(int slot)
{
	if (!abil[slot].has) return false;
	std::int32_t cd{};
	if (raw::sdk_champion_cooldown(myh, static_cast<std::uint32_t>(slot), &cd) != 0) return false;
	return cd <= 0 && (mystate & ST_CAN_CAST) != 0;
}

int Bot::cast(int slot, std::uint32_t kind, std::uint32_t h, vec2 p)
{
	std::int32_t ok{};
	const int rc = raw::sdk_cast(static_cast<std::uint32_t>(slot), kind, h, p.x, p.y, &ok);
	if (rc != 0) return -1;
	refresh_me();
	++epoch;
	return ok ? 1 : 0;
}

int Bot::move_abs(vec2 t)
{
	std::int32_t ok{};
	const int rc = raw::sdk_move_to(t.x, t.y, &ok);
	if (rc != 0) return -1;
	refresh_me();
	++epoch;
	return ok ? 1 : 0;
}

bool Bot::attack(Tgt t)
{
	if (!t) return false;
	if (raw::sdk_attack(t.kind, t.h) != 0) return false;
	refresh_me();
	++epoch;
	return true;
}

bool Bot::do_recall()
{
	if (raw::sdk_recall() != 0) return false;
	refresh_me();
	return true;
}

bool Bot::unit_info(std::uint32_t h, Unit& u)
{
	raw::champion_info ci{};
	if (raw::sdk_champion(h, &ci) != 0) return false;
	if (ci.x < 0 || ci.y < 0) return false;
	u.h = h;
	u.pos = { ci.x, ci.y };
	u.hp = ci.health;
	u.maxhp = ci.max_health;
	u.str = ci.strength;
	u.focus = ci.focus;
	u.range = ci.attack_range;
	u.state = static_cast<std::uint32_t>(ci.state);
	u.type = ci.type;
	u.gems = -1;
	return true;
}

bool Bot::tgt_info(Tgt t, vec2& p, double& h)
{
	if (t.kind == EK_CHAMP)
	{
		Unit u;
		if (!unit_info(t.h, u)) return false;
		p = u.pos;
		h = u.hp;
		return true;
	}
	if (t.kind == EK_CAMP)
	{
		raw::camp_state cs{};
		if (raw::sdk_camp(t.h, &cs) != 0) return false;
		p = { cs.x, cs.y };
		h = cs.health;
		return true;
	}
	return false;
}

int Bot::enemy_gems(Unit& u)
{
	if (u.gems < 0)
	{
		std::uint32_t v{};
		u.gems = raw::sdk_champion_gems(u.h, &v) == 0 ? static_cast<int>(v) : 0;
	}
	return u.gems;
}

static bool load_type(int type, std::array<int, 8>& have, std::array<int, 8>& rng, std::array<double, 8>& str,
					  std::array<double, 8>& hpv)
{
	if (type < 0 || type >= 8) return false;
	if (have[type]) return true;
	raw::camp_design d{};
	if (raw::sdk_camp_design(type, &d) != 0) return false;
	have[type] = 1;
	rng[type] = d.base_stats.base_attack_range;
	str[type] = d.base_stats.base_strength;
	hpv[type] = d.base_stats.base_health;
	return true;
}

bool Bot::find_camp(vec2 p, CampView& cv, bool)
{
	raw::camp_state cs{};
	if (in_bounds(p))
	{
		const int code = camp_code(p);
		if (code >= 0)
		{
			const CampRec& r = groups[code >> 8].camps[code & 255];
			if (raw::sdk_camp(r.h, &cs) == 0 && cs.x == p.x && cs.y == p.y)
			{
				cv.h = r.h;
				cv.pos = p;
				cv.spawn = r.p;
				cv.gi = code >> 8;
				cv.type = r.type;
				cv.r = r.r;
				cv.str = cs.strength;
				cv.hp = cs.health;
				return true;
			}
		}
	}
	std::uint32_t h{};
	if (raw::sdk_camp_at(p.x, p.y, &h) != 0) return false;
	if (raw::sdk_camp(h, &cs) != 0) return false;
	raw::camp_info ci{};
	if (raw::sdk_map_camp_info(h, &ci) != 0) return false;
	if (!load_type(ci.type, type_have, type_range, type_str, type_hp)) return false;
	cv.h = h;
	cv.pos = { cs.x, cs.y };
	cv.spawn = { ci.x, ci.y };
	cv.type = ci.type;
	cv.r = type_range[ci.type];
	cv.str = cs.strength;
	cv.hp = cs.health;
	cv.gi = -1;
	if (in_bounds(cv.spawn))
	{
		const int code = camp_code(cv.spawn);
		if (code >= 0) cv.gi = code >> 8;
	}
	return true;
}

int Bot::dash_ability()
{
	for (int s = 0; s < 2; ++s)
		if (abil[s].is(cambc::ability_kind::dash) && ready(s)) return s;
	return -1;
}

// ------------------------------------------------------------------ lazy per-epoch boards
bool Bot::fresh(LazyBoard& l)
{
	if (!l.b) l.b = std::make_unique<bitboard>();
	if (l.ep == epoch && l.r == rnd) return true;
	l.ep = epoch;
	l.r = rnd;
	return false;
}

const bitboard& Bot::vis_tiles()
{
	if (!fresh(lb_vis)) cambc::vision::visible_tiles_into(*lb_vis.b);
	return *lb_vis.b;
}
const bitboard& Bot::camp_occ()
{
	if (!fresh(lb_camp)) cambc::vision::camp_tiles_into(*lb_camp.b);
	return *lb_camp.b;
}
const bitboard& Bot::awake_occ()
{
	if (!fresh(lb_awake)) cambc::vision::awake_camp_tiles_into(*lb_awake.b);
	return *lb_awake.b;
}
const bitboard& Bot::ally_occ()
{
	if (!fresh(lb_ally)) cambc::vision::champion_tiles_into(cambc::team::ally, *lb_ally.b);
	return *lb_ally.b;
}
const bitboard& Bot::enemy_occ()
{
	if (!fresh(lb_enemy)) cambc::vision::champion_tiles_into(cambc::team::enemy, *lb_enemy.b);
	return *lb_enemy.b;
}
const bitboard& Bot::tp_occ()
{
	if (!fresh(lb_tp)) cambc::vision::teleport_tiles_into(*lb_tp.b);
	return *lb_tp.b;
}
const bitboard& Bot::enemy_lock()
{
	if (!fresh(lb_elock)) cambc::vision::altar_lock_tiles_into(cambc::team::enemy, *lb_elock.b);
	return *lb_elock.b;
}
const bitboard& Bot::blocked_now()
{
	// walk_block | champion_tiles | camp_tiles | teleport_tiles, minus our own tile
	if (!fresh(lb_blocked))
	{
		bitboard& b = *lb_blocked.b;
		copy_into(b, *walk_block);
		b |= ally_occ();
		b |= enemy_occ();
		b |= camp_occ();
		b |= tp_occ();
		b.set(pos, false);
	}
	return *lb_blocked.b;
}

// ------------------------------------------------------------------ init_static
void Bot::init_static()
{
	W = cambc::map::width();
	H = cambc::map::height();
	area = W * H;
	const auto& L = raw::layout();
	CW = static_cast<int>(L.chunked_width);
	chunks = static_cast<int>(L.chunked_width * L.chunked_height);
	auto& me = cambc::self();
	myh = static_cast<std::uint32_t>(static_cast<cambc::handle_champion_t>(me));
	{
		raw::champion_identity id{};
		if (raw::sdk_champion_identity(myh, &id) == 0) my_type = id.type;
	}
	refresh_me();
	PROF("init_ids");

	const auto& walls = cambc::map::walls();
	const auto& holes = cambc::map::holes();
	const auto& alt = cambc::map::altars();
	walk_block = std::make_unique<bitboard>(walls | holes);
	*walk_block |= alt;
	*walk_block |= cambc::map::spawn_region(cambc::team::enemy);
	terrain_bad = std::make_unique<bitboard>(walls | holes);
	*terrain_bad |= alt;
	spawn = std::make_unique<bitboard>(cambc::map::spawn_region(cambc::team::ally));
	not_walk = std::make_unique<bitboard>(~*walk_block);

	PROF("init_boards");
	altars = alt.positions();
	altar_ring = std::make_unique<bitboard>();
	for (auto a : altars) altar_ring->draw_chebyshev(a, 1);
	*altar_ring &= *not_walk;
	{
		auto sp = spawn->positions();
		if (!sp.empty())
		{
			spawn0 = sp[0];
			spawn_lo = spawn_hi = sp[0];
			for (auto p : sp)
			{
				spawn_lo.x = std::min(spawn_lo.x, p.x);
				spawn_lo.y = std::min(spawn_lo.y, p.y);
				spawn_hi.x = std::max(spawn_hi.x, p.x);
				spawn_hi.y = std::max(spawn_hi.y, p.y);
			}
		}
	}
	for (auto a : altars)
	{
		auto r1 = std::make_unique<bitboard>();
		r1->draw_chebyshev(a, 1);
		*r1 &= *not_walk;
		altar_goal_pts.push_back(r1->positions());
		altar_goal.push_back(std::move(r1));
	}

	PROF("init_altars");
	// camp groups straight from the raw layout (same order as map::camp_groups())
	{
		static std::uint32_t g_words[4096];
		std::vector<std::uint32_t> big;
		std::uint32_t* words = g_words;
		std::uint32_t count{};
		raw::sdk_map_camp_layout(nullptr, 0, &count); // count only (host cost scales with the capacity)
		PROF("init_layout_count");
		if (count > 4096)
		{
			big.resize(count);
			words = big.data();
		}
		raw::sdk_map_camp_layout(words, count, &count);
		PROF("init_layout");
		{
			// count groups first: reserve once (wasm malloc and vector growth are expensive in fuel)
			std::size_t ng = 0, k = 0;
			while (k + 5 <= count)
			{
				k += 5 + 4 * std::size_t(words[k + 4]);
				++ng;
			}
			groups.reserve(ng);
		}
		std::size_t i = 0;
		while (i + 5 <= count)
		{
			Group G;
			G.idx = static_cast<int>(groups.size());
			G.gh = words[i];
			G.gold = static_cast<int>(words[i + 1]);
			G.gems = static_cast<int>(words[i + 2]);
			const std::uint32_t size = words[i + 4];
			i += 5;
			G.camps.reserve(size);
			for (std::uint32_t m = 0; m < size && i + 4 <= count; ++m, i += 4)
			{
				CampRec c;
				c.h = words[i];
				c.type = static_cast<int>(words[i + 1]);
				c.p = { static_cast<std::int32_t>(words[i + 2]), static_cast<std::int32_t>(words[i + 3]) };
				if (load_type(c.type, type_have, type_range, type_str, type_hp))
				{
					c.st = type_str[c.type];
					c.r = type_range[c.type];
					c.maxhp = type_hp[c.type];
				}
				c.hp = c.maxhp;
				G.strength += c.st;
				G.rng = std::max(G.rng, c.r);
				G.maxhp_sum += c.maxhp;
				G.tiles.set(c.p);
				G.camps.push_back(c);
			}
			G.n = static_cast<int>(G.camps.size());
			G.center = G.camps.empty() ? vec2{ 0, 0 } : G.camps[0].p;
			G.value = G.gems + 0.25 * G.gold;
			groups.push_back(std::move(G));
		}
	}
	{
		const int CH = static_cast<int>(L.chunked_height);
		chunk_start.assign(static_cast<std::size_t>(CW * CH + 1), 0);
		std::size_t total = 0;
		for (auto& G : groups)
			for (auto& c : G.camps)
				if (in_bounds(c.p))
				{
					++chunk_start[(c.p.y >> 3) * CW + (c.p.x >> 3) + 1];
					++total;
				}
		for (std::size_t i = 1; i < chunk_start.size(); ++i) chunk_start[i] += chunk_start[i - 1];
		chunk_items.resize(total);
		std::vector<int> cur(chunk_start.begin(), chunk_start.end() - 1);
		for (auto& G : groups)
			for (std::size_t k = 0; k < G.camps.size(); ++k)
			{
				const vec2 p = G.camps[k].p;
				if (!in_bounds(p)) continue;
				chunk_items[cur[(p.y >> 3) * CW + (p.x >> 3)]++] = { p.y * W + p.x, (G.idx << 8) | static_cast<int>(k) };
			}
	}
	PROF("init_groups");
	all_camp_tiles = std::make_unique<bitboard>();
	for (auto& G : groups) *all_camp_tiles |= G.tiles;
	not_camp = std::make_unique<bitboard>(~*all_camp_tiles);
	not_walk_camp = std::make_unique<bitboard>(*not_walk & *not_camp);

	// handles
	{
		std::uint32_t n{};
		raw::sdk_num_allies(&n);
		ally_handles.resize(n);
		raw::sdk_allies(ally_handles.data(), n, &n);
		ally_handles.resize(n);
		std::sort(ally_handles.begin(), ally_handles.end());
		slot = 0;
		for (std::size_t i = 0; i < ally_handles.size(); ++i)
			if (ally_handles[i] == myh) slot = static_cast<int>(i);
		slot = std::min(slot, 7);
		ally_alive.assign(ally_handles.size(), 1);
	}
	{
		std::uint32_t n{};
		raw::sdk_num_enemies(&n);
		enemy_handles.resize(n);
		raw::sdk_enemies(enemy_handles.data(), n, &n);
		enemy_handles.resize(n);
		std::sort(enemy_handles.begin(), enemy_handles.end());
		auto esp = cambc::map::spawn_region(cambc::team::enemy).positions();
		if (!esp.empty())
		{
			enemy_spawn = esp[0];
			for (auto a : altars)
				if (cheb(a, enemy_spawn) <= cheb(a, spawn0) + LOCK_SIDE_MARGIN) lock_side.push_back(a);
		}
		else
			enemy_spawn = { W / 2, H / 2 };
	}
	// abilities (own slots: info never throws for self)
	{
		auto abs = me.abilities();
		for (int s = 0; s < 2; ++s)
		{
			const auto& oi = abs[s].info();
			if (!oi) continue;
			AbInfo a;
			a.has = true;
			std::visit(
				[&](const auto& v) {
					a.kind = std::decay_t<decltype(v)>::kind;
					a.exclusive = v.exclusive_with_movement;
					if constexpr (requires { v.range; }) a.range = v.range;
					if constexpr (requires { v.radius; }) a.radius = v.radius;
					if constexpr (requires { v.modifier; }) a.modifier = v.modifier;
					if constexpr (requires { v.duration; }) a.duration = v.duration;
				},
				*oi);
			abil[s] = a;
			if (a.kind == cambc::ability_kind::dash) has_dash = true;
		}
	}
	PROF("init_handles_abil");
	tfield = std::make_unique<distance_field>();
	mfield = std::make_unique<distance_field>();
	tvisited = std::make_unique<bitboard>();
	mvisited = std::make_unique<bitboard>();
	mstart = std::make_unique<bitboard>();

	PROF("init_fields_alloc");
	const int home = comp_of(spawn0);
	PROF("init_home_comp");
	need_crossing = false;
	for (auto& G : groups)
	{
		bool in = false;
		for (auto& c : G.camps)
			if (comps[home]->is_set(c.p))
			{
				in = true;
				break;
			}
		if (!in)
		{
			need_crossing = true;
			break;
		}
	}
	if (!need_crossing)
	{
		bitboard& t = sb(SB_T1);
		copy_into(t, *altar_ring);
		t &= *comps[home];
		if (t.is_empty()) need_crossing = true;
	}
	// build order: pop() from the back -> altar rings first, then groups farthest from our spawn
	PROF("init_crossing");
	{
		// stable bucket sort by cheb(center, spawn0) (native comparison sorts are expensive in fuel)
		const int maxd = std::max(W, H);
		std::vector<int> cnt(static_cast<std::size_t>(maxd + 2), 0);
		for (auto& G : groups)
			if (G.n > 0) ++cnt[std::min(cheb(G.center, spawn0), maxd) + 1];
		for (int i = 1; i <= maxd + 1; ++i) cnt[i] += cnt[i - 1];
		std::vector<int> gs(static_cast<std::size_t>(cnt[maxd + 1]));
		for (auto& G : groups)
			if (G.n > 0) gs[cnt[std::min(cheb(G.center, spawn0), maxd)]++] = G.idx;
		sf_todo = gs;
		for (int i = 0; i < static_cast<int>(altars.size()); ++i) sf_todo.push_back(-2 - i);
	}
	PROF("init_crossing_todo");
	gfield.resize(groups.size());
	reach_c.resize(groups.size());
	escape_c.resize(groups.size());
	afield.resize(altars.size());
	banned.assign(groups.size(), 0);
	died_at.assign(groups.size(), -BIG);
	altar_seen.assign(altars.size(), -BIG);
	enemy_locked.assign(altars.size(), 0);
	claims.assign(groups.size(), 0);
	e_hint = 0;
	inited = true;
}

// ------------------------------------------------------------------ components
int Bot::comp_of(vec2 p)
{
	for (std::size_t i = 0; i < comps.size(); ++i)
		if (comps[i]->is_set(p)) return static_cast<int>(i);
	bitboard& blk = sb(SB_COMP);
	copy_into(blk, *walk_block);
	blk.set(p, false);
	auto c = std::make_unique<bitboard>(cambc::uninitialized);
	blk.reachable_tiles_into(p, static_cast<std::uint16_t>(std::min(area, 65535)), *c);
	c->set(p);
	comps.push_back(std::move(c));
	return static_cast<int>(comps.size()) - 1;
}

const bitboard& Bot::staging(int comp, int tcomp, int r)
{
	const std::uint64_t key = (std::uint64_t(comp) << 40) | (std::uint64_t(tcomp) << 8) | std::uint64_t(r);
	auto it = cross_cache.find(key);
	if (it != cross_cache.end()) return *it->second;
	auto st = std::make_unique<bitboard>();
	dilate_into(*comps[tcomp], r, *st);
	*st &= *comps[comp];
	auto& ref = *st;
	cross_cache.emplace(key, std::move(st));
	return ref;
}

bool Bot::can_reach(int gi, int comp)
{
	const Group& G = groups[gi];
	for (auto& c : G.camps)
		if (comps[comp]->is_set(c.p)) return true;
	const int tcomp = comp_of(G.center);
	if (has_dash && !staging(comp, tcomp, 2).is_empty()) return true;
	if ((has_crystal() || gold() >= 10) && !staging(comp, tcomp, 3).is_empty()) return true;
	return false;
}

bool Bot::escape_ok(int gi, int comp)
{
	const int m = memo_get(escape_c[gi], comp);
	if (m >= 0) return m != 0;
	const Group& G = groups[gi];
	bitboard& zone = sb(SB_T1);
	zone.clear();
	for (auto& c : G.camps)
		if (c.r > 0 && c.st > 0) zone.draw_chebyshev(c.p, static_cast<float>(c.r));
	bitboard& stand = sb(SB_T2);
	dilate_into(G.tiles, 1, stand);
	stand &= *not_walk_camp;
	bitboard& t = sb(SB_T3);
	copy_into(t, stand);
	t &= *comps[comp];
	int a = comp;
	if (t.is_empty()) a = comp_of(G.center);
	copy_into(t, *comps[a]);
	bitboard& nz = sb(SB_T2);
	not_into(nz, zone);
	t &= nz;
	t &= *not_camp;
	const bool v = !t.is_empty();
	escape_c[gi].emplace_back(comp, v ? 1 : 0);
	return v;
}

// ------------------------------------------------------------------ static distance fields (sf_fuel)
void Bot::build_static_fields()
{
	if (!inited) return;
	while (!sf_todo.empty())
	{
		// expansions: at least max(W, H) (open map from a corner), else the largest seen; +20% margin
		const int eh = e_hint > 0 ? std::max(e_hint, std::max(W, H)) : (W + H);
		const std::uint64_t est = std::uint64_t(chunks * (eh * 1.2 + 16)) + 3000;
		if (cambc::fuel_remaining() <= est + FUEL_BUILD_RESERVE) break;
		const int key = sf_todo.back();
		bitboard& roots = sb(SB_ROOTS);
		bitboard& walls = sb(SB_SFW);
		copy_into(walls, *walk_block);
		if (key <= -2)
		{
			copy_into(roots, *altar_goal[-2 - key]); // disjoint from walk_block by construction
		}
		else
		{
			roots.clear();
			roots.set(groups[key].center);
			walls.set(groups[key].center, false);
		}
		auto f = std::make_unique<distance_field>();
		const int E = f->compute_with_expansion_count(walls, roots, sb(SB_FV));
		e_hint = std::max(e_hint, E);
		if (key <= -2)
			afield[-2 - key] = std::move(f);
		else
			gfield[key] = std::move(f);
		sf_todo.pop_back();
		PROF(key <= -2 ? "sf_altar" : "sf_group");
	}
}

void Bot::sf_dests(bitboard& out)
{
	out.clear();
	for (int key : sf_todo)
	{
		if (key <= -2)
			out |= *altar_goal[-2 - key];
		else
			out.set(groups[key].center);
	}
}

void Bot::turn_field()
{
	// Python dist_field(): full field when standing on walk_block, field toward the unbuilt keys while
	// sf_todo is not empty, none once every static field exists. Capped at TURN_FIELD_MAXD for fuel.
	tfield_ok = false;
	sf_use = !walk_block->is_set(pos);
	if (sf_use && sf_todo.empty()) return;
	if (cambc::fuel_remaining() < FUEL_TURNFIELD_MIN) return;
	bitboard& blk = sb(SB_T1);
	copy_into(blk, *walk_block);
	blk.set(pos, false);
	bitboard& roots = sb(SB_T2);
	roots.clear();
	roots.set(pos);
	if (!sf_use)
		tfield->compute(blk, roots, *tvisited, TURN_FIELD_MAXD);
	else
	{
		bitboard& d = sb(SB_T3);
		sf_dests(d);
		tfield->compute_to(blk, roots, d, *tvisited, TURN_FIELD_MAXD);
	}
	tfield_ok = true;
}

std::optional<int> Bot::group_dist(const Group& G)
{
	if (sf_use && gfield[G.idx])
	{
		const int v = gfield[G.idx]->get(pos);
		if (v >= UNREACHED) return std::nullopt;
		return v;
	}
	if (tfield_ok && tvisited->is_set(G.center)) return static_cast<int>(tfield->get(G.center));
	return std::nullopt;
}

// ------------------------------------------------------------------ shared memory
void Bot::read_claims()
{
	std::fill(claims.begin(), claims.end(), 0);
	std::array<std::uint8_t, 8> buf{};
	if (raw::sdk_read_shared_memory(0, buf.data(), 8) != 0) return;
	for (int s = 0; s < FOCUS_BYTE; ++s)
		if (s != slot && buf[s])
		{
			const int i = buf[s] - 1;
			if (i < static_cast<int>(claims.size())) ++claims[i];
		}
}

void Bot::write_claim(int idx)
{
	const std::uint8_t v = (idx < 0 || idx >= 255) ? 0 : static_cast<std::uint8_t>(idx + 1);
	raw::sdk_write_shared_memory(slot, &v, 1);
}

std::int64_t Bot::read_focus()
{
	std::uint8_t v{};
	if (raw::sdk_read_shared_memory(FOCUS_BYTE, &v, 1) != 0) return -1;
	if (!v) return -1;
	std::int64_t m = (rnd - (v & 31)) % 32;
	if (m < 0) m += 32;
	if (m > FOCUS_TTL) return -1;
	const int i = (v >> 5) - 1;
	if (i >= 0 && i < static_cast<int>(enemy_handles.size())) return enemy_handles[i];
	return -1;
}

void Bot::write_focus(std::uint32_t h)
{
	int i = -1;
	for (std::size_t k = 0; k < enemy_handles.size(); ++k)
		if (enemy_handles[k] == h)
		{
			i = static_cast<int>(k);
			break;
		}
	if (i < 0 || i >= 7) return;
	const std::uint8_t v = static_cast<std::uint8_t>(((i + 1) << 5) | (rnd & 31));
	raw::sdk_write_shared_memory(FOCUS_BYTE, &v, 1);
}
