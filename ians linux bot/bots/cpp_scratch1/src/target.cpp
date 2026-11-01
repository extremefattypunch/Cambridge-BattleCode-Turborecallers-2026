// Target scoring (choose_target with pruned order), stuck guard, shop, altar locks, wards.
#include <algorithm>

#include "bot.h"

using namespace P;
using IE = cambc::item_type::enum_type;

namespace {
constexpr std::uint32_t id(IE e) { return static_cast<std::uint32_t>(e); }
} // namespace

// ------------------------------------------------------------------ targeting
int Bot::choose_target()
{
	// Python: score every reachable group in order of the upper bound value*1.95/(d+6) (current target
	// first), skipping groups whose bound is below the best score. The result is the arg-max score (ties to the
	// lower index) whatever the order, so this port selects lazily on a cheaper per-group bound
	// value*mult_max/(cheb + ttk + 6) (cheb <= walking distance; cost >= d + ttk + 6; mult_max = the product of
	// the multipliers that can apply to this group) and only computes the walking distance (static field / turn
	// field / reachability) for groups that can still win. The arg-max is unchanged.
	read_claims();
	const double dp = dps();
	const double dmg_mult = jungle() ? 0.7 : 1.0;
	int best = -1;
	double best_score = 0.0;
	const int comp = comp_of(pos);
	const int cg = (has_crystal() || gold() >= 10) ? 1 : 0;
	const int rkey = (comp << 1) | cg;
	const bool low_hp = hp < maxhp * 0.6;
	auto& cands = ct_cands;
	cands.clear();
	cands.reserve(groups.size());
	for (auto& G : groups)
	{
		if (G.n == 0 || banned[G.idx] > rnd) continue;
		if (memo_get(reach_c[G.idx], rkey) == 0) continue; // known unreachable from here (group_dist is None too)
		const int c = claims[G.idx];
		double ttk = 0.0, mult;
		if (G.status == 1)
			mult = c ? 0.9 : 1.5;
		else
		{
			const double hl = G.status == 0 ? G.hp_left() : G.maxhp_sum;
			ttk = hl / (dp + c * 55.0);
			mult = c ? 1.2 : 1.0;
			if (rnd - died_at[G.idx] < DEATH_MEMORY) mult *= DEATH_PENALTY;
			if (low_hp && G.idx != target && G.strength > 0)
			{
				const double s = G.status == 0 ? G.alive_strength() : G.strength;
				if (s > 0) continue; // Python skips it (hp < 60% and not the current target)
			}
		}
		if (G.idx == target) mult *= 1.3;
		cands.push_back({ G.value * mult / (cheb(pos, G.center) + ttk + 6), G.idx });
	}
	int new_reach = 0, new_esc = 0;
	auto eval = [&](int gi) {
		Group& G = groups[gi];
		const auto d0 = group_dist(G);
		double d;
		if (!d0)
		{
			// can_reach depends only on (G, comp, crystal-or-10-gold): memoized
			int m = memo_get(reach_c[gi], rkey);
			if (m < 0)
			{
				// first-time reachability (flood fill / staging dilation) only with fuel to spare
				if (new_reach >= MAX_NEW_REACH || cambc::fuel_remaining() < FUEL_COMP_MIN) return;
				++new_reach;
				m = can_reach(gi, comp) ? 1 : 0;
				reach_c[gi].emplace_back(rkey, static_cast<char>(m));
			}
			if (!m) return;
			d = cheb(pos, G.center) * 1.5 + 12;
		}
		else
			d = *d0;
		if (G.value * SCORE_BOUND_MULT / (d + 6) < best_score) return; // Python's bound skip
		if (G.status == 2 && G.ready > rnd + d) return;
		const double wait = G.status == 2 ? std::max(0.0, G.ready - rnd - d) : 0.0;
		const int c = claims[gi];
		double extra = 0.0;
		bool solo_ok = true;
		double ttk;
		if (G.status == 1)
			ttk = 0.0;
		else
		{
			const double hl = G.status == 0 ? G.hp_left() : G.maxhp_sum;
			const double s = G.status == 0 ? G.alive_strength() : G.strength;
			const double tdps = dp + c * 55.0;
			ttk = hl / tdps;
			if (s > 0)
			{
				const double share = G.n == 1 ? 1.0 : 0.7;
				const double dmg_solo = s * (hl / dp) * share * dmg_mult;
				solo_ok = dmg_solo <= hp - 150;
				const double dmg = s * ttk * share * dmg_mult / (1 + c);
				if (target != gi && low_hp) return;
				if (dmg > hp - 150)
				{
					const double budget = maxhp - s * dmg_mult * (G.rng + 1) - 80;
					if (budget <= 0) return;
					const double per_cycle = budget / (s * dmg_mult) * tdps;
					const double cycles = hl / per_cycle;
					if (cycles > 4) return;
					if (memo_get(escape_c[gi], comp) < 0)
					{
						// first-time escape zone (dilation + flood): budgeted per call, skip the group meanwhile
						if (new_esc >= MAX_NEW_ESCAPE || cambc::fuel_remaining() < FUEL_COMP_MIN) return;
						++new_esc;
					}
					if (!escape_ok(gi, comp)) return;
					extra = cycles * 30.0;
				}
			}
		}
		if (rnd + d + ttk + 8 > MAX_ROUNDS) return;
		const double cost = d + ttk + 6 + extra + wait;
		double score = G.value / cost;
		if (G.status == 1) score *= 1.5;
		if (c)
		{
			if (G.status == 1)
				score *= 0.6;
			else if (solo_ok)
				score *= 0.3;
			else
				score *= 1.2;
		}
		if (target == gi) score *= 1.3;
		if (G.status != 1 && rnd - died_at[gi] < DEATH_MEMORY) score *= DEATH_PENALTY;
		if (score > best_score || (score == best_score && best >= 0 && gi < best))
		{
			best_score = score;
			best = gi;
		}
	};
	// the current target first: it usually wins (x1.3) and raises the pruning bar
	for (auto& c : cands)
		if (c.idx == target)
		{
			eval(c.idx);
			c.cb = -1.0;
			break;
		}
	while (true)
	{
		int k = -1;
		double kb = -1.0;
		const int n = static_cast<int>(cands.size());
		for (int i = 0; i < n; ++i)
			if (cands[i].cb > kb)
			{
				kb = cands[i].cb;
				k = i;
			}
		if (k < 0 || kb < best_score) break;
		if (best >= 0 && cambc::fuel_remaining() < FUEL_SCORE_FLOOR) break;
		cands[k].cb = -1.0;
		eval(cands[k].idx);
	}
	return best;
}

void Bot::note_progress(int gi, bool progress)
{
	// Stuck guard: STUCK_TURNS farming turns in a row without a move or an attack on the same group.
	if (progress)
	{
		stuck = 0;
		return;
	}
	if (stuck_idx != gi)
	{
		stuck_idx = gi;
		stuck = 0;
	}
	++stuck;
	if (stuck >= STUCK_TURNS)
	{
		banned[gi] = rnd + STUCK_BAN;
		stuck = 0;
	}
}

// ------------------------------------------------------------------ shop
int Bot::bruiser_item()
{
	// Bruiser shards of the champion's main stat: finish a partly bought emblem, then the lowest shards/weight.
	if (!ITEMS_BRUISER) return -1;
	struct PI
	{
		std::uint32_t shard, emblem;
		double w;
	};
	const PI S{ id(IE::bruiser_shard_of_strength), id(IE::bruiser_emblem_of_strength), 0 };
	const PI H{ id(IE::bruiser_shard_of_health), id(IE::bruiser_emblem_of_health), 0 };
	const PI F{ id(IE::bruiser_shard_of_focus), id(IE::bruiser_emblem_of_focus), 0 };
	auto w = [](PI p, double v) {
		p.w = v;
		return p;
	};
	std::array<PI, 3> plan{};
	int n = 0;
	using CT = cambc::champion_type;
	switch (static_cast<CT>(my_type))
	{
	case CT::vesper_vale:
	case CT::vendetta:
	case CT::tavi:
		plan[0] = w(S, 2.0);
		plan[1] = w(H, 1.0);
		n = 2;
		break;
	case CT::heart_of_ruin:
		plan[0] = w(H, 1.0);
		plan[1] = w(F, 1.0);
		n = 2;
		break;
	case CT::ryth:
		plan[0] = w(H, 2.0);
		plan[1] = w(S, 1.0);
		n = 2;
		break;
	case CT::marcella:
		plan[0] = w(F, 1.0);
		plan[1] = w(H, 1.0);
		plan[2] = w(S, 1.0);
		n = 3;
		break;
	default:
		return -1;
	}
	if (JUNGLE_FIRST && items[id(IE::jungle_emblem_of_strength)] == 0) return static_cast<int>(id(IE::jungle_shard_of_strength));
	int best = -1;
	double bk = 0;
	int bi = 0;
	for (int i = 0; i < n; ++i)
	{
		const std::uint32_t part = items[plan[i].shard];
		if (part % 5) return static_cast<int>(plan[i].shard);
		const double k = (part + 5.0 * items[plan[i].emblem]) / plan[i].w;
		if (best < 0 || k < bk || (k == bk && i < bi))
		{
			bk = k;
			bi = i;
			best = static_cast<int>(plan[i].shard);
		}
	}
	return best;
}

namespace {
bool can_shop(std::uint32_t h, bool consumable)
{
	std::int32_t r{};
	return raw::sdk_champion_can_shop(h, consumable ? 1 : 0, &r) == 0 && r != 0;
}
} // namespace

void Bot::buy_lock()
{
	// me.can_buy(ALTAR_LOCK): can shop, gold >= cost, count < carry limit
	const auto lk = cambc::consumable_type::altar_lock;
	if (cons_count(CONS_LOCK) != 0) return;
	const std::uint32_t g = gold();
	if (g < static_cast<std::uint32_t>(LOCK_MIN_GOLD) || g < lk.cost() || lk.carry_limit() == 0) return;
	if (!can_shop(myh, true)) return;
	raw::sdk_buy_consumable(CONS_LOCK);
}

void Bot::shop()
{
	{
		const auto tp = cambc::consumable_type::tp_crystal;
		if (need_crossing && !has_crystal() && gold() >= tp.cost() && tp.carry_limit() > 0 && can_shop(myh, true))
			raw::sdk_buy_consumable(CONS_TP);
	}
	buy_lock();
	const bool can = can_shop(myh, false);
	std::uint32_t g = can ? gold() : 0;
	for (int k = 0; k < 12 && can; ++k)
	{
		load_items();
		int it = bruiser_item();
		if (it < 0)
		{
			if (items[id(IE::jungle_emblem_of_strength)] == 0)
				it = static_cast<int>(id(IE::jungle_shard_of_strength));
			else if (items[id(IE::monster_emblem_of_strength)] == 0)
				it = static_cast<int>(id(IE::monster_shard_of_strength));
			else if (items[id(IE::power_shard_of_health)] < items[id(IE::power_shard_of_strength)])
				it = static_cast<int>(id(IE::power_shard_of_health));
			else
				it = static_cast<int>(id(IE::power_shard_of_strength));
		}
		const auto info = cambc::item_type{ static_cast<IE>(it) }.info(); // cached table
		if (!info.purchasable || g < info.cost) break;                     // me.can_buy(item, 1)
		if (raw::sdk_buy_item(static_cast<std::uint32_t>(it), 1) != 0) break;
		g = gold();
	}
	items_ok = false;
	dps_cache = -1;
	cdps_cache = -1;
	refresh_me();
}

// ------------------------------------------------------------------ altar locks and wards (sf_pvp)
bool Bot::try_lock()
{
	// Lock an altar within 2 where a visible enemy is tributing (cancels its channel), else a lock-side altar.
	if (cons_count(CONS_LOCK) == 0) return false;
	auto use_lock = [&](vec2 a) -> bool {
		if (cambc::vision::has_altar_lock(a)) return false;
		std::int32_t ok{};
		if (raw::sdk_use_consumable(CONS_LOCK, a.x, a.y, &ok) != 0) return false;
		refresh_me();
		++epoch;
		return ok != 0;
	};
	for (auto& e : enemies)
	{
		if (!(e.state & ST_SUBMITTING)) continue;
		for (auto a : altars)
			if (cheb(a, e.pos) <= 1 && cheb(a, pos) <= 2)
				if (use_lock(a)) return true;
	}
	for (auto a : lock_side)
		if (cheb(a, pos) <= 2)
			if (use_lock(a)) return true;
	return false;
}

bool Bot::try_ward()
{
	// Place the ward whenever it is charged: by the altar when banking, else ahead.
	if (!USE_WARDS) return false;
	raw::ward_resources wr{};
	if (raw::sdk_champion_wards(myh, &wr) != 0 || wr.cooldown > 0) return false;
	std::uint32_t wn{};
	if (raw::sdk_champion_ward_positions(myh, nullptr, 0, &wn) != 0) return false;
	std::vector<raw::position> wp(wn);
	if (wn && raw::sdk_champion_ward_positions(myh, wp.data(), wn, &wn) != 0) return false;
	int alt = -1;
	std::int64_t ad = BIG;
	for (std::size_t i = 0; i < altars.size(); ++i)
	{
		const int d = cheb(altars[i], pos);
		if (d < ad)
		{
			ad = d;
			alt = static_cast<int>(i);
		}
	}
	vec2 anchor;
	if (alt >= 0 && ad <= 4)
	{
		anchor = altars[alt];
		if (wn && cheb({ wp[0].x, wp[0].y }, anchor) <= 2) return false;
	}
	else
	{
		if (wn && cheb({ wp[0].x, wp[0].y }, pos) <= 6) return false;
		anchor = enemy_spawn;
	}
	bitboard& bad = sb(SB_W1);
	copy_into(bad, *terrain_bad);
	bitboard& t = sb(SB_W2);
	cambc::vision::ward_tiles_into(cambc::team::ally, t);
	bad |= t;
	cambc::vision::ward_tiles_into(cambc::team::enemy, t);
	bad |= t;
	bad |= ally_occ();
	bad |= enemy_occ();
	bad |= camp_occ();
	bad.set(pos, false);
	not_into(t, bad);
	bitboard& area = sb(SB_W1);
	area.clear();
	area.draw_chebyshev(pos, 2);
	area &= t;
	pl3.fill(area);
	const auto& bush = cambc::map::bushes();
	std::vector<std::pair<std::pair<int, int>, vec2>> cands;
	for (auto c : pl3) cands.push_back({ { cheb(c, anchor), bush.is_set(c) ? 0 : 1 }, c });
	std::stable_sort(cands.begin(), cands.end(), [](const auto& a, const auto& b) { return a.first < b.first; });
	const int lim = std::min<int>(3, static_cast<int>(cands.size()));
	for (int i = 0; i < lim; ++i)
	{
		const vec2 c = cands[i].second;
		std::int32_t ok{};
		if (raw::sdk_place_ward(c.x, c.y, &ok) != 0) continue;
		++epoch;
		if (ok) return true;
	}
	return false;
}
