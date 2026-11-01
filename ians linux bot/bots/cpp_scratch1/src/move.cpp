// Movement (step_toward, go_to, cross_toward) and banking (pick_altar, detour, do_tribute, locks).
#include <algorithm>

#include "bot.h"

using namespace P;

namespace {
// Neighbours of p inside the map, in engine positions() order (chunk-major, then row-major in the chunk)
int nbrs(vec2 p, int W, int H, int CW, std::array<vec2, 8>& out)
{
	int n = 0;
	for (int dy = -1; dy <= 1; ++dy)
		for (int dx = -1; dx <= 1; ++dx)
		{
			if (!dx && !dy) continue;
			const vec2 t{ p.x + dx, p.y + dy };
			if (t.x < 0 || t.y < 0 || t.x >= W || t.y >= H) continue;
			out[n++] = t;
		}
	auto key = [CW](vec2 v) { return ((((v.y >> 3) * CW) + (v.x >> 3)) << 6) | ((v.y & 7) << 3) | (v.x & 7); };
	for (int i = 1; i < n; ++i)
	{
		const vec2 v = out[i];
		const int k = key(v);
		int j = i - 1;
		while (j >= 0 && key(out[j]) > k)
		{
			out[j + 1] = out[j];
			--j;
		}
		out[j + 1] = v;
	}
	return n;
}
} // namespace

bool Bot::step_toward(const bitboard& goals, const bitboard* avoid, const bitboard* no_enter)
{
	if (!can_move()) return false;
	if (goals.is_set(pos) || goals.is_empty()) return false;
	bitboard& ng = sb(SB_ST_NG);
	not_into(ng, goals);
	bitboard& blocked = sb(SB_ST_BLOCKED);
	copy_into(blocked, blocked_now());
	if (no_enter)
	{
		bitboard& ne = sb(SB_ST_NE);
		copy_into(ne, *no_enter);
		ne &= ng;
		ne.set(pos, false);
		blocked |= ne;
	}
	std::array<vec2, 8> nb{};
	const int nn = nbrs(pos, W, H, CW, nb);
	const int passes = avoid ? 2 : 1;
	for (int pass = 0; pass < passes; ++pass)
	{
		const bitboard* av = pass == 0 ? avoid : nullptr;
		bitboard& walls = sb(SB_ST_WALLS);
		copy_into(walls, blocked);
		walls &= ng;
		if (av)
		{
			bitboard& a = sb(SB_ST_AV);
			copy_into(a, *av);
			a &= ng;
			walls |= a;
			walls.set(pos, false);
		}
		mstart->clear();
		mstart->set(pos);
		// fuel cap on the search depth (cost ~ chunks * (depth + 16) + 300)
		const std::uint64_t f = cambc::fuel_remaining();
		if (f < FUEL_RESERVE + 1500) return false;
		std::int64_t maxd = (static_cast<std::int64_t>(f - FUEL_RESERVE) - 300) / chunks - 16;
		if (maxd < 1) return false;
		if (maxd > 65535) maxd = 65535;
		mfield->compute_to(walls, goals, *mstart, *mvisited, static_cast<std::uint16_t>(maxd));
		if (!mvisited->is_set(pos)) continue;
		const int cur = mfield->get(pos);
		int bd = cur, best = -1;
		for (int i = 0; i < nn; ++i)
		{
			const vec2 t = nb[i];
			if (!mvisited->is_set(t)) continue; // walls are never visited
			const int v = mfield->get(t);
			if (v < bd)
			{
				if (no_enter && no_enter->is_set(t)) continue; // stepable = walls | no_enter
				bd = v;
				best = i;
			}
		}
		if (best >= 0) return move_abs(nb[best]) == 1;
	}
	return false;
}

bool Bot::go_to(const bitboard& goals, const bitboard* avoid, const bitboard* no_enter)
{
	const int comp = comp_of(pos);
	bitboard& local = sb(SB_GO_LOCAL);
	copy_into(local, goals);
	local &= *comps[comp];
	if (local.is_empty()) return cross_toward(goals, comp);
	return step_toward(local, avoid, no_enter);
}

bool Bot::cross_toward(const bitboard& goals, int comp)
{
	// Move toward goals in another walk component using a dash or a TP crystal.
	pl2.fill(goals);
	if (pl2.n == 0) return false;
	const vec2 g0 = pl2[0];
	const int tcomp = comp_of(g0);
	const int dash = dash_ability();
	const bool crystal = has_crystal();
	const bitboard* st2 = has_dash ? &staging(comp, tcomp, 2) : nullptr;
	const bitboard& st3 = staging(comp, tcomp, 3);
	const bitboard* stg = nullptr;
	int r = 0;
	if (st2 && !st2->is_empty() && (!crystal || st2->is_set(pos) || dash >= 0))
	{
		stg = st2;
		r = 2;
	}
	else if (!st3.is_empty())
	{
		if (!crystal)
		{
			if (gold() >= 10 && !spawn->is_set(pos)) return do_recall();
			return false;
		}
		stg = &st3;
		r = 3;
	}
	else
		return false;
	if (stg->is_set(pos))
	{
		bitboard& land = sb(SB_CR_LAND);
		land.clear();
		land.draw_chebyshev(pos, static_cast<float>(r));
		land &= *comps[tcomp];
		bitboard& nbk = sb(SB_CR_NB);
		not_into(nbk, blocked_now());
		land &= nbk;
		pl2.fill(land);
		std::vector<vec2> cands(pl2.begin(), pl2.end());
		std::stable_sort(cands.begin(), cands.end(), [&](vec2 a, vec2 b) { return cheb(a, g0) < cheb(b, g0); });
		if (dash >= 0)
			for (auto t : cands)
			{
				if (cheb(t, pos) > 2) continue;
				if (cast_at(dash, t) == 1) return true;
			}
		if (crystal)
			for (auto t : cands)
			{
				std::int32_t ok{};
				if (raw::sdk_use_consumable(CONS_TP, t.x, t.y, &ok) != 0) continue;
				refresh_me();
				++epoch;
				if (ok) return true;
			}
		return false;
	}
	return step_toward(*stg);
}

// ------------------------------------------------------------------ banking
std::int64_t Bot::pick_altar(int& goal_altar)
{
	// Nearest usable altar by path (+penalty where enemies were seen recently).
	std::int64_t best = BIG;
	goal_altar = -1;
	for (std::size_t i = 0; i < altars.size(); ++i)
	{
		const vec2 a = altars[i];
		if (enemy_lock().is_set(a)) continue;
		std::int64_t d = BIG;
		if (sf_use && afield[i])
		{
			const int v = afield[i]->get(pos);
			if (v < UNREACHED) d = v;
		}
		else if (tfield_ok)
		{
			for (auto t : altar_goal_pts[i])
				if (tvisited->is_set(t))
				{
					const int v = tfield->get(t);
					if (v < d) d = v;
				}
		}
		if (d >= BIG) continue;
		if (rnd - altar_seen[i] <= 40) d += ALTAR_DANGER_PEN;
		if (d < best)
		{
			best = d;
			goal_altar = static_cast<int>(i);
			pref_altar = static_cast<int>(i);
		}
	}
	return best;
}

std::int64_t Bot::detour(std::int64_t ad, int gi)
{
	// Extra walking to bank on the way to group gi (Chebyshev for the altar->G leg).
	if (pref_altar < 0 || gi < 0) return ad;
	const auto gd = group_dist(groups[gi]);
	if (!gd) return ad;
	return std::max<std::int64_t>(0, ad + cheb(altars[pref_altar], groups[gi].center) - *gd);
}

bool Bot::bank_detour(int g, std::int64_t det, bool thr) const
{
	const double k = thr ? 0.5 : 1.0;
	if (det <= BANK_DETOUR_NEAR_D && g >= BANK_NEAR * k) return true;
	if (det <= BANK_DETOUR_CLOSE_D && g >= BANK_CLOSE * k) return true;
	return false;
}

bool Bot::bank_now(int g, std::int64_t ad, bool thr) const
{
	const double k = thr ? 0.5 : 1.0;
	if (g >= BANK_ANY * k) return true;
	if (ad <= BANK_NEAR_D && g >= BANK_NEAR * k) return true;
	if (ad <= BANK_CLOSE_D && g >= BANK_CLOSE * k) return true;
	return false;
}

void Bot::locked_altars()
{
	// Altars last seen with an enemy lock (remembered while out of sight).
	for (std::size_t i = 0; i < altars.size(); ++i)
	{
		if (!vis_tiles().is_set(altars[i])) continue;
		enemy_locked[i] = enemy_lock().is_set(altars[i]) ? 1 : 0;
	}
}

bool Bot::break_lock(bool force)
{
	// Hit an adjacent enemy lock when no free altar is close; True if we attacked.
	std::int64_t free_d = BIG;
	for (std::size_t i = 0; i < altars.size(); ++i)
		if (!enemy_locked[i]) free_d = std::min<std::int64_t>(free_d, cheb(altars[i], pos));
	if ((free_d <= 8 && !force) || !can_attack()) return false;
	for (std::size_t i = 0; i < altars.size(); ++i)
	{
		if (!enemy_locked[i]) continue;
		const vec2 a = altars[i];
		if (!in_range(a) || !cambc::vision::has_altar_lock(a)) continue;
		try
		{
			const auto lk = cambc::vision::altar_lock_at(a);
			cambc::self().attack(lk);
			refresh_me();
			++epoch;
			return true;
		}
		catch (...)
		{
		}
	}
	return false;
}

bool Bot::do_tribute(int pref)
{
	for (std::size_t i = 0; i < altars.size(); ++i)
	{
		const vec2 a = altars[i];
		if (cheb(a, pos) > 1) continue;
		if (enemy_lock().is_set(a)) continue;
		if (raw::sdk_submit_gems(a.x, a.y) == 0)
		{
			refresh_me();
			return true;
		}
	}
	const bitboard* ring = altar_ring.get();
	locked_altars();
	bool any_locked = false;
	for (auto l : enemy_locked) any_locked = any_locked || l;
	if (any_locked)
	{
		bitboard& fr = sb(SB_TR_FREE);
		fr.clear();
		for (std::size_t i = 0; i < altars.size(); ++i)
			if (!enemy_locked[i]) fr.draw_chebyshev(altars[i], 1);
		fr &= *not_walk;
		const int c0 = comp_of(pos);
		bitboard& t = sb(SB_TR_TMP);
		copy_into(t, fr);
		t &= *comps[c0];
		const bool reach_free = !t.is_empty();
		if (break_lock(!reach_free)) return true;
		if (reach_free) ring = &fr;
	}
	// sf_bank: preferred altar (pick_altar already skips enemy-locked ones)
	bitboard& nbk = sb(SB_TR_NB);
	not_into(nbk, blocked_now());
	if (pref >= 0)
	{
		bitboard& t = sb(SB_TR_TMP);
		copy_into(t, *altar_goal[pref]);
		t &= nbk;
		if (!t.is_empty()) ring = altar_goal[pref].get();
	}
	bitboard& goals = sb(SB_TR_GOALS);
	copy_into(goals, *ring);
	goals &= nbk;
	if (goals.is_empty()) copy_into(goals, *ring);
	const int comp = comp_of(pos);
	bitboard& loc = sb(SB_TR_LOCAL);
	copy_into(loc, goals);
	loc &= *comps[comp];
	if (loc.is_empty())
	{
		if (cross_toward(goals, comp)) return true;
		if (!spawn->is_set(pos) && do_recall()) return true;
		return false;
	}
	return step_toward(loc);
}
