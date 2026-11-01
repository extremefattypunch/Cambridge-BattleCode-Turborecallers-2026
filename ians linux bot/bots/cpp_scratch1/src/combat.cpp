// Combat: damage model, kit casting, retreat, fight/flee kill-time model (sf_bank + sf_pvp), channel stuns.
#include <algorithm>
#include <tuple>
#include <iostream>

#include "bot.h"

using namespace P;
using AK = cambc::ability_kind;

namespace {
double ability_damage(std::uint32_t myh, int slot, bool& ok)
{
	float f{};
	ok = raw::sdk_champion_ability_damage(myh, static_cast<std::uint32_t>(slot), &f) == 0;
	return f;
}
} // namespace

// ------------------------------------------------------------------ damage model
double Bot::dps()
{
	if (dps_cache >= 0) return dps_cache;
	double d = mystr;
	if (item(1) > 0) d *= 1.15; // MONSTER_EMBLEM_OF_STRENGTH
	double bonus = 0.0;
	for (int s = 0; s < 2; ++s)
	{
		const AbInfo& a = abil[s];
		if (!a.has) continue;
		bool ok = true;
		if (a.kind == AK::attack_reset)
			bonus += mystr / 8.0;
		else if (a.kind == AK::damage || a.kind == AK::cc || a.kind == AK::aoe_damage)
		{
			const double v = ability_damage(myh, s, ok);
			if (ok) bonus += v / 8.0;
		}
		else if (KIT_LANDING_DASH && a.kind == AK::dash && a.modifier > 0)
		{
			const double v = ability_damage(myh, s, ok);
			if (ok) bonus += v / 8.0;
		}
	}
	dps_cache = std::max(1.0, d + bonus);
	return dps_cache;
}

double Bot::champ_dps()
{
	// Our damage per round against champions (no Monster bonus).
	if (cdps_cache >= 0) return cdps_cache;
	double d = mystr;
	for (int s = 0; s < 2; ++s)
	{
		const AbInfo& a = abil[s];
		if (!a.has) continue;
		bool ok = true;
		if (a.kind == AK::attack_reset)
			d += mystr / 8.0;
		else if (a.kind == AK::damage || a.kind == AK::cc || a.kind == AK::aoe_damage)
		{
			const double v = ability_damage(myh, s, ok);
			if (ok) d += v / 8.0;
		}
	}
	cdps_cache = std::max(1.0, d);
	return cdps_cache;
}

// ------------------------------------------------------------------ visible units (engine order)
static void sort_engine(std::vector<Unit>& v, const Bot*, int CW)
{
	auto key = [CW](vec2 p) { return ((((p.y >> 3) * CW) + (p.x >> 3)) << 6) | ((p.y & 7) << 3) | (p.x & 7); };
	std::stable_sort(v.begin(), v.end(), [&](const Unit& a, const Unit& b) { return key(a.pos) < key(b.pos); });
}

// ------------------------------------------------------------------ kit helpers (sf_draft)
void Bot::kit_units(std::vector<std::pair<vec2, double>>& units)
{
	// (position, weight) of units an area hit would touch
	units.clear();
	pl1.fill(camp_occ());
	for (auto p : pl1)
	{
		CampView cv;
		if (!find_camp(p, cv, false)) continue;
		std::uint32_t s{};
		if (raw::sdk_camp_state(cv.h, &s) != 0) continue;
		if (s == 0) continue;
		const bool aw = (s == 1) || (target >= 0 && cv.gi == target);
		units.emplace_back(cv.pos, aw ? 1.0 : -3.0);
	}
	std::vector<Unit> es;
	for (auto h : enemy_handles)
	{
		Unit u;
		if (unit_info(h, u) && (u.state & ST_ALIVE) && enemy_occ().is_set(u.pos)) es.push_back(u);
	}
	sort_engine(es, this, CW);
	for (auto& e : es)
	{
		double w = 2.0;
		if (e.state & (ST_RECALLING | ST_SUBMITTING | ST_TELEPORTING)) w = 4.0;
		units.emplace_back(e.pos, w);
	}
}

static vec2 best_area_tile(const PosList& cands, const std::vector<std::pair<vec2, double>>& units, double radius,
						   const vec2* bonus, bool& found, double& bs)
{
	vec2 best{};
	found = false;
	bs = 0.0;
	for (auto t : cands)
	{
		double sc = 0.0;
		for (auto& [p, w] : units)
			if (cheb(p, t) <= radius) sc += w;
		if (bonus && cheb(*bonus, t) <= 1) sc += 0.5;
		if (sc > bs)
		{
			bs = sc;
			best = t;
			found = true;
		}
	}
	return best;
}

vec2 Bot::aim_area(double rng, double radius, vec2 fallback)
{
	// Python quirk: dilate(bb, float radius) raises -> always the fallback (see params.h KIT_RADIUS_FIX)
	if (!KIT_RADIUS_FIX) return fallback;
	std::vector<std::pair<vec2, double>> units;
	kit_units(units);
	bitboard& pb = sb(SB_K1);
	pb.clear();
	for (auto& [p, w] : units)
		if (w > 0) pb.set(p);
	if (pb.is_empty()) return fallback;
	bitboard& c = sb(SB_K2);
	dilate_into(pb, static_cast<int>(radius), c);
	bitboard& near = sb(SB_K3);
	near.clear();
	near.draw_chebyshev(pos, static_cast<float>(rng));
	c &= near;
	pl3.fill(c);
	bool found;
	double bs;
	const vec2 b = best_area_tile(pl3, units, radius, nullptr, found, bs);
	return found ? b : fallback;
}

bool Bot::cast_landing_dash(Tgt tg)
{
	// HoR slot 1: dash landing 1.5xF in radius 1 + stun, aimed at the most units.
	int dash = -1;
	for (int s = 0; s < 2; ++s)
		if (abil[s].is(AK::dash) && ready(s))
		{
			if (abil[s].radius > 0 && abil[s].modifier > 0) dash = s;
			break;
		}
	if (dash < 0) return false;
	if (hp < maxhp * 0.35) return false;
	// Python quirk: dilate(pos_bb, info.radius) raises TypeError -> False (see params.h KIT_RADIUS_FIX)
	if (!KIT_RADIUS_FIX) return false;
	std::vector<std::pair<vec2, double>> units;
	kit_units(units);
	bitboard& pb = sb(SB_K1);
	pb.clear();
	for (auto& [p, w] : units)
		if (w > 0) pb.set(p);
	if (pb.is_empty()) return false;
	bitboard& c = sb(SB_K2);
	dilate_into(pb, static_cast<int>(abil[dash].radius), c);
	bitboard& near = sb(SB_K3);
	near.clear();
	near.draw_chebyshev(pos, 2);
	c &= near;
	not_into(near, blocked_now());
	c &= near;
	c &= *not_walk;
	c.set(pos, false);
	vec2 tpos{};
	bool have_t = false;
	if (tg)
	{
		double th;
		have_t = tgt_info(tg, tpos, th);
	}
	pl3.fill(c);
	bool found;
	double bs;
	const vec2 best = best_area_tile(pl3, units, abil[dash].radius, have_t ? &tpos : nullptr, found, bs);
	if (!found || bs < 1.0) return false;
	if (cast_at(dash, best) != 1) return false;
	if (can_attack())
	{
		const Tgt nxt = reset_target(tg);
		if (nxt) attack(nxt);
	}
	return true;
}

Tgt Bot::reset_target(Tgt tg)
{
	// A unit in basic-attack range worth hitting: the target if alive, else an enemy champion,
	// else the weakest awake / target-group camp.
	if (tg)
	{
		vec2 tp;
		double th;
		if (tgt_info(tg, tp, th) && th > 0 && in_range(tp)) return tg;
	}
	Tgt best{};
	double bh = 0;
	std::vector<Unit> es;
	for (auto h : enemy_handles)
	{
		Unit u;
		if (unit_info(h, u) && (u.state & ST_ALIVE) && enemy_occ().is_set(u.pos)) es.push_back(u);
	}
	sort_engine(es, this, CW);
	for (auto& e : es)
		if (in_range(e.pos) && (!best || e.hp < bh))
		{
			best = { EK_CHAMP, e.h };
			bh = e.hp;
		}
	if (best) return best;
	pl1.fill(camp_occ());
	for (auto p : pl1)
	{
		CampView cv;
		if (!find_camp(p, cv, false)) continue;
		std::uint32_t s{};
		if (raw::sdk_camp_state(cv.h, &s) != 0) continue;
		if (s == 0 || !in_range(cv.pos)) continue;
		if (!(s == 1 || (target >= 0 && cv.gi == target))) continue;
		if (!best || cv.hp < bh)
		{
			best = { EK_CAMP, cv.h };
			bh = cv.hp;
		}
	}
	return best;
}

bool Bot::reset_and_hit(Tgt tg)
{
	for (int s = 0; s < 2; ++s)
	{
		if (!(abil[s].is(AK::attack_reset) && ready(s))) continue;
		const Tgt nxt = reset_target(tg);
		if (!nxt) return false;
		if (cast_none(s) == 1)
		{
			if (can_attack()) attack(nxt);
			return true;
		}
	}
	return false;
}

void Bot::cast_combat(Tgt tg, bool moved, double incoming, bool attacked)
{
	// One cast per turn: shield if taking damage, else damage, else attack reset.
	const vec2 p0 = pos;
	for (int s = 0; s < 2; ++s)
	{
		if (!(abil[s].is(AK::shield) && ready(s) && incoming > 0)) continue;
		std::array<raw::buff_data, 4> bd{};
		std::uint32_t cnt{};
		if (raw::sdk_champion_buff_data(myh, bd.data(), static_cast<std::uint32_t>(bd.size()), &cnt) != 0) continue;
		bool shield = false;
		for (std::uint32_t i = 0; i < cnt && i < bd.size(); ++i)
			if (bd[i].type == static_cast<std::uint32_t>(cambc::buff_types::shield)) shield = true;
		if (shield) continue;
		if (cast_none(s) == 1) return;
	}
	if (KIT_LANDING_DASH && (tg || incoming > 0))
		if (cast_landing_dash(tg)) return;
	if (tg)
	{
		for (int s = 0; s < 2; ++s)
		{
			if (!ready(s)) continue;
			const AbInfo& a = abil[s];
			if (!(a.kind == AK::damage || a.kind == AK::cc || a.kind == AK::aoe_damage)) continue;
			if (a.exclusive && moved) continue;
			vec2 tp;
			double th;
			if (!tgt_info(tg, tp, th)) continue; // target.position() raised
			if (cheb(tp, p0) > a.range) continue;
			if (a.kind == AK::aoe_damage)
			{
				if (KIT_AOE_AIM) tp = aim_area(a.range, a.radius, tp);
				if (cast_at(s, tp) == 1) return;
			}
			else
			{
				if (cast_on(s, tg) == 1) return;
			}
		}
	}
	for (int s = 0; s < 2; ++s)
	{
		if (!(abil[s].is(AK::heal) && ready(s))) continue;
		std::vector<Unit> al;
		for (auto h : ally_handles)
		{
			if (h == myh) continue;
			Unit u;
			if (!unit_info(h, u) || !(u.state & ST_ALIVE)) continue;
			if (!ally_occ().is_set(u.pos)) continue; // vision.champions(ALLY)
			al.push_back(u);
		}
		sort_engine(al, this, CW);
		const Unit* best = nullptr;
		for (auto& a : al)
			if (cheb(a.pos, p0) <= 4 && a.hp < a.maxhp * 0.7)
				if (!best || a.hp < best->hp) best = &a;
		if (best && cast_on(s, { EK_CHAMP, best->h }) == 1) return;
	}
	if (attacked && tg)
	{
		if (KIT_RESET_RETARGET)
		{
			reset_and_hit(tg);
			return;
		}
		for (int s = 0; s < 2; ++s)
		{
			if (!(abil[s].is(AK::attack_reset) && ready(s))) continue;
			if (cast_none(s) == 1)
			{
				vec2 tp;
				double th;
				if (can_attack() && tgt_info(tg, tp, th) && th > 0 && in_range(tp)) attack(tg);
				return;
			}
		}
	}
}

Tgt Bot::pick_camp_in_range(const Group& G)
{
	Tgt best{};
	double bh = 0;
	for (auto& c : G.camps)
	{
		raw::camp_state cs{};
		if (raw::sdk_camp(c.h, &cs) != 0) continue;
		std::uint32_t s{};
		if (raw::sdk_camp_state(c.h, &s) != 0 || s == 0) continue;
		if (cheb({ cs.x, cs.y }, pos) <= myrange)
			if (!best || cs.health < bh)
			{
				best = { EK_CAMP, c.h };
				bh = cs.health;
			}
	}
	return best;
}

void Bot::alive_tiles(const Group& G, bitboard& out)
{
	out.clear();
	for (auto& c : G.camps)
		if (c.hp > 0) out.set(c.p);
}

// ------------------------------------------------------------------ retreat / fight-flee
bool Bot::retreat(const std::vector<Unit>& ens)
{
	// Step to the adjacent tile with the least incoming damage.
	const bitboard& blocked = blocked_now();
	using Key = std::tuple<double, int, int, int>;
	auto danger = [&](vec2 t) -> Key {
		double d = 0.0;
		for (auto& c : awake)
			if (cheb(c.pos, t) <= c.r) d += c.str;
		for (auto& e : ens)
			if (cheb(e.pos, t) <= e.range + 1) d += e.str;
		int md = 0;
		bool first = true;
		for (auto& c : awake)
		{
			const int v = cheb(c.pos, t) - c.r;
			if (first || v < md) md = v;
			first = false;
		}
		int emd = 8;
		first = true;
		for (auto& e : ens)
		{
			const int v = std::min(cheb(e.pos, t), 8);
			if (first || v < emd) emd = v;
			first = false;
		}
		return Key{ d, -md, -emd, spawn_dist(t) };
	};
	std::array<vec2, 9> cands{};
	int nc = 0;
	cands[nc++] = pos;
	{
		// blocked.reachable_tiles(pos, 1).positions() without pos, in engine order
		std::array<std::pair<int, vec2>, 8> tmp{};
		int k = 0;
		for (int dy = -1; dy <= 1; ++dy)
			for (int dx = -1; dx <= 1; ++dx)
			{
				if (!dx && !dy) continue;
				const vec2 t{ pos.x + dx, pos.y + dy };
				if (!in_bounds(t) || blocked.is_set(t)) continue;
				tmp[k++] = { okey(t), t };
			}
		std::sort(tmp.begin(), tmp.begin() + k, [](const auto& a, const auto& b) { return a.first < b.first; });
		for (int i = 0; i < k; ++i) cands[nc++] = tmp[i].second;
	}
	const int dash = dash_ability();
	if (dash >= 0)
	{
		bitboard& far = sb(SB_R1);
		far.clear();
		far.draw_chebyshev(pos, 2);
		bitboard& nb = sb(SB_T1);
		not_into(nb, blocked);
		far &= nb;
		far &= *not_walk;
		pl3.fill(far);
		std::vector<std::pair<Key, vec2>> dc;
		for (auto t : pl3) dc.emplace_back(danger(t), t);
		std::stable_sort(dc.begin(), dc.end(), [](const auto& a, const auto& b) { return a.first < b.first; });
		if (!dc.empty())
		{
			const Key k0 = dc[0].first, kp = danger(pos);
			const auto t0 = std::make_tuple(std::get<0>(k0), std::get<1>(k0), std::get<2>(k0));
			const auto tp = std::make_tuple(std::get<0>(kp), std::get<1>(kp), std::get<2>(kp));
			if (t0 < tp)
			{
				const int lim = std::min<int>(4, static_cast<int>(dc.size()));
				for (int i = 0; i < lim; ++i)
				{
					const vec2 t = dc[i].second;
					if (cheb(t, pos) < 2) continue;
					if (cast_at(dash, t) == 1) return true;
				}
			}
		}
	}
	if (!can_move()) return false;
	int bi = 0;
	Key bk = danger(cands[0]);
	for (int i = 1; i < nc; ++i)
	{
		const Key k = danger(cands[i]);
		if (k < bk)
		{
			bk = k;
			bi = i;
		}
	}
	if (cands[bi] != pos) return move_abs(cands[bi]) == 1;
	return false;
}

bool Bot::recall_safe() const
{
	// True when no visible enemy could reach us during a recall channel.
	for (auto& e : enemies)
		if (cheb(e.pos, pos) <= e.range + RECALL_SAFE_MARGIN) return false;
	return true;
}

int Bot::adjacent_melee(const std::vector<Unit>& ens)
{
	// Lowest-HP adjacent melee enemy we can hit right now.
	if (!can_attack()) return -1;
	int best = -1;
	for (int i = 0; i < static_cast<int>(ens.size()); ++i)
	{
		const Unit& e = ens[i];
		if (e.range <= 1 && cheb(e.pos, pos) <= 1 && in_range(e.pos))
			if (best < 0 || e.hp < ens[best].hp) best = i;
	}
	return best;
}

bool Bot::strike(Tgt t, double incoming)
{
	// Stand and hit target (attack + one combat cast).
	bool attacked = false;
	vec2 tp;
	double th;
	if (can_attack() && tgt_info(t, tp, th) && in_range(tp)) attacked = attack(t);
	cast_combat(t, false, incoming, attacked);
	return true;
}

int Bot::chan_kind(const Unit& e) const
{
	// 0 none, 1 tribute, 2 teleport, 3 recall
	if (e.state & ST_SUBMITTING) return 1;
	if (e.state & ST_TELEPORTING) return 2;
	if (e.state & ST_RECALLING) return 3;
	return 0;
}

void Bot::focus_bias(Unit& e, std::int64_t focus, int my_gems, double& ratio, int& tier, int& eg)
{
	// (engage ratio, priority tier, enemy gems): channellers, then team focus, then rest.
	const int ch = chan_kind(e);
	eg = enemy_gems(e);
	ratio = 0.8;
	tier = 2;
	if (ch == 1 || ch == 2)
	{
		ratio = 1.2;
		tier = 0;
	}
	else if (ch == 3)
	{
		ratio = 1.0;
		tier = 0;
	}
	ratio += std::min(0.3, eg / 100.0);
	if (focus >= 0 && static_cast<std::int64_t>(e.h) == focus)
	{
		ratio += 0.2;
		tier = std::min(tier, 1);
	}
	if (my_gems >= 30 && ch == 0) ratio = std::min(ratio, 0.8);
}

bool Bot::stun_channel(Unit& e, double ttk)
{
	// Stun a channelling enemy (not Marcella) before moving when we cannot kill it first.
	const int ch = chan_kind(e);
	if (ch == 0) return false;
	if (e.type == static_cast<int>(cambc::champion_type::marcella)) return false;
	const vec2 tp = e.pos;
	const vec2 p0 = pos;
	if (ch == 3 && can_attack() && in_range(tp)) return false; // damage alone cancels a recall
	if (ch != 3)
	{
		std::int32_t left = 1;
		std::int32_t v{};
		if (raw::sdk_champion_channel_time(e.h, &v) == 0) left = v;
		if (ttk < left) return false; // keep it channelling and take the bag
	}
	for (int s = 0; s < 2; ++s)
	{
		if (!ready(s)) continue;
		const AbInfo& a = abil[s];
		if (a.kind == AK::cc)
		{
			if (cheb(tp, p0) <= a.range && cast_on(s, { EK_CHAMP, e.h }) == 1) return true;
		}
		else if (a.kind == AK::aoe_damage && a.duration > 0)
		{
			if (cheb(tp, p0) <= a.range && cast_at(s, tp) == 1) return true;
		}
		else if (a.kind == AK::dash && a.duration > 0 && a.radius >= 1)
		{
			bitboard& land = sb(SB_S1);
			land.clear();
			land.draw_chebyshev(tp, static_cast<float>(static_cast<int>(a.radius)));
			bitboard& reach = sb(SB_S2);
			reach.clear();
			reach.draw_chebyshev(p0, static_cast<float>(static_cast<int>(a.range)));
			land &= reach;
			not_into(reach, blocked_now());
			land &= reach;
			pl3.fill(land);
			std::vector<vec2> ts(pl3.begin(), pl3.end());
			for (auto t : ts)
			{
				const int rc = cast_at(s, t);
				if (rc == 1) return true;
				if (rc < 0) break; // exception leaves this ability
			}
		}
	}
	return false;
}

bool Bot::handle_enemies(double incoming)
{
	// Chase and kill weaker enemy champions nearby; step away from stronger ones.
	const vec2 p0 = pos;
	const double my_str = champ_dps();
	std::vector<std::pair<int, int>> near; // (index in enemies, distance)
	double threat = 0.0, fight_dps = 0.0;
	const std::int64_t focus = read_focus();
	for (int i = 0; i < static_cast<int>(enemies.size()); ++i)
	{
		Unit& e = enemies[i];
		const int d = cheb(e.pos, p0);
		const double cw = CHAN_THREAT[chan_kind(e)];
		if (d <= 6 || (d <= 8 && static_cast<std::int64_t>(e.h) == focus))
		{
			near.emplace_back(i, d);
			fight_dps += enemy_dps(e) * cw;
		}
		if (d <= e.range + 2) threat += e.str * cw;
	}
	if (near.empty()) return false;
	double camp_inc = 0.0;
	for (auto& c : awake)
		if (cheb(c.pos, p0) <= c.r) camp_inc += c.str;
	double ally_str = 0.0;
	int n_allies = 0;
	for (auto h : ally_handles)
	{
		if (h == myh) continue;
		Unit u;
		if (!unit_info(h, u) || !(u.state & ST_ALIVE)) continue;
		if (!ally_occ().is_set(u.pos)) continue;
		const int d = cheb(u.pos, p0);
		if (d <= 6)
		{
			++n_allies;
			if (d <= 4) ally_str += u.str * 0.7;
		}
	}
	const int g = static_cast<int>(gems());
	const bool rich = g >= FIGHT_RICH_GEMS;
	const double their_ttk = hp / std::max(1.0, std::max(threat, fight_dps) + camp_inc);
	int best = -1;
	std::tuple<int, double, int> best_key{};
	double best_ratio = static_cast<double>(BIG);
	double best_ttk = 0.0;
	for (auto& [i, d] : near)
	{
		Unit& e = enemies[i];
		const double eh = e.hp;
		const double kill = eh / (my_str + ally_str);
		const double my_ttk = kill + std::max(0, d - myrange) * 0.5;
		const double ratio = my_ttk / std::max(0.1, their_ttk);
		best_ratio = std::min(best_ratio, kill / std::max(0.1, their_ttk));
		double limit = rich ? FIGHT_ENGAGE_RICH : FIGHT_ENGAGE;
		double pr;
		int tier, eg;
		focus_bias(e, focus, g, pr, tier, eg);
		double bonus = std::max(0.0, pr - 0.8);
		if (eg >= 15) bonus = std::max(bonus, FIGHT_CARRIER_BONUS);
		limit += bonus;
		auto cb = chase_ban.find(e.h);
		if (cb != chase_ban.end() && cb->second > rnd) continue;
		if (ratio <= limit || (eh <= my_str && d <= myrange))
		{
			const std::tuple<int, double, int> key{ tier, my_ttk / (1.0 + eg / 20.0), d };
			if (best < 0 || key < best_key)
			{
				best_key = key;
				best = i;
				best_ttk = kill + std::max(0, d - myrange);
			}
		}
	}
	const bool clearly_losing =
		best_ratio > (rich ? 1.0 : FIGHT_FLEE) || static_cast<int>(near.size()) > n_allies + 1;
	debug_block({
		if (rnd >= 40 && rnd <= 75) {
		std::cout << "HE r" << rnd << " me" << my_type << " p(" << pos.x << "," << pos.y << ") hp " << hp << "/" << maxhp << " str " << my_str << " ally " << ally_str << "/" << n_allies
				  << " threat " << threat << " fdps " << fight_dps << " camp " << camp_inc << " ttk " << their_ttk << " bestratio " << best_ratio << " best " << best << " losing " << clearly_losing << " stall " << stall << " hold " << holding << " near";
		for (auto& [i, d] : near) std::cout << " [t" << enemies[i].type << " d" << d << " hp" << enemies[i].hp << " s" << enemies[i].str << " f" << enemies[i].focus << " r" << enemies[i].range << " st" << enemies[i].state << "]";
		std::cout << std::endl; }
	});
	if (best < 0) last_enemy_danger = rnd;
	if (best >= 0)
	{
		Unit& e = enemies[best];
		write_focus(e.h);
		bool moved = stun_channel(e, best_ttk);
		Unit cur;
		if (!unit_info(e.h, cur)) return true; // the stun killed the target or it left vision
		const Tgt t{ EK_CHAMP, e.h };
		if (!in_range(cur.pos))
		{
			const int dash = dash_ability();
			if (dash >= 0 && cheb(cur.pos, p0) >= 3)
			{
				bitboard& ring = sb(SB_W1);
				ring.clear();
				ring.draw_chebyshev(p0, 2);
				bitboard& adj = sb(SB_W2);
				adj.clear();
				adj.draw_chebyshev(cur.pos, static_cast<float>(myrange));
				ring &= adj;
				not_into(adj, blocked_now());
				ring &= adj;
				pl3.fill(ring);
				std::vector<vec2> ts(pl3.begin(), pl3.end());
				for (auto tt : ts)
					if (cast_at(dash, tt) == 1)
					{
						moved = true;
						break;
					}
			}
			if (!moved)
			{
				bitboard& goal = sb(SB_W1);
				goal.clear();
				goal.set(cur.pos);
				moved = step_toward(goal);
			}
		}
		bool attacked = false;
		{
			Unit now;
			if (can_attack() && unit_info(e.h, now) && in_range(now.pos)) attacked = attack(t);
		}
		cast_combat(t, moved, incoming, attacked);
		const std::uint32_t h = e.h;
		if (attacked)
			chase_turns[h] = 0;
		else
		{
			const int ct = ++chase_turns[h];
			if (ct > CHASE_MAX)
			{
				chase_turns[h] = 0;
				chase_ban[h] = rnd + CHASE_BAN;
			}
		}
		return true;
	}
	// never turn our back on an adjacent melee enemy we can hit, unless clearly losing with an escape
	std::vector<Unit> nl;
	for (auto& [i, d] : near) nl.push_back(enemies[i]);
	const int adj = adjacent_melee(nl);
	if (adj >= 0)
	{
		const bool escape = dash_ability() >= 0 || spawn_dist(p0) <= 2;
		if (!(clearly_losing && escape)) return strike({ EK_CHAMP, nl[adj].h }, incoming);
	}
	// stall breaker
	if (stall > STALL_LIMIT)
		holding = true;
	else if (stall < STALL_LIMIT * 0.4)
		holding = false;
	if (!clearly_losing && holding) return false;
	if (threat > 0 || (clearly_losing && (static_cast<int>(near.size()) > n_allies + 1 || rich)))
	{
		if (!clearly_losing) stall += 1.0;
		if (hp < maxhp * 0.5 && incoming == 0 && !spawn->is_set(pos) && recall_safe())
			if (do_recall()) return true;
		retreat(nl);
		return true;
	}
	return false;
}
