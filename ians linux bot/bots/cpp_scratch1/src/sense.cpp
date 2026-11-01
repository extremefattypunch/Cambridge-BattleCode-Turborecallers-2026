// Knowledge: observe (camp-group states), threats (incoming damage, awake camps, enemies), alerts.
#include <algorithm>

#include "bot.h"

using namespace P;

void Bot::observe()
{
	const bitboard* vis = nullptr;
	for (auto& G : groups)
	{
		if (G.status == 2 && rnd >= G.ready)
		{
			G.status = 0;
			for (auto& c : G.camps) c.hp = c.maxhp;
		}
		if (cheb(G.center, pos) > 10) continue;
		if (!vis) vis = &vis_tiles();
		bool seen = false; // (G.tiles & vis) not empty
		for (auto& c : G.camps)
			if (vis->is_set(c.p))
			{
				seen = true;
				break;
			}
		if (!seen) continue;
		std::uint32_t st{};
		if (raw::sdk_camp_group_state(G.gh, &st) != 0) continue;
		if (st == 3)
		{
			std::int32_t timer{};
			if (raw::sdk_camp_group_cooldown(G.gh, &timer) != 0) continue;
			G.status = 2;
			G.ready = rnd + timer;
			for (auto& c : G.camps) c.hp = c.maxhp;
		}
		else if (st == 2)
		{
			G.status = 1;
			for (auto& c : G.camps) c.hp = 0;
		}
		else if (st == 1)
		{
			G.status = 0;
			for (auto& c : G.camps)
			{
				if (vis->is_set(c.p))
				{
					std::int32_t has{};
					const int rc = raw::sdk_has_camp(c.p.x, c.p.y, &has);
					if (rc != 0 && rc != static_cast<int>(cambc::error_code::api_not_in_vision)) continue; // exception: pass
					if (rc != 0) has = 0;
					if (!has)
					{
						c.hp = 0;
						continue;
					}
				}
				raw::camp_state cs{};
				if (raw::sdk_camp(c.h, &cs) != 0) continue; // not visible
				std::uint32_t s{};
				if (raw::sdk_camp_state(c.h, &s) != 0) continue;
				c.hp = (s == 0) ? 0.0 : static_cast<double>(cs.health);
			}
		}
		// st == 0 (unknown): Python's state() raises -> continue
	}
}

double Bot::threats()
{
	// incoming damage per round from awake camps in range and enemy champions in range + 1
	double inc = 0.0;
	awake.clear();
	pl1.fill(awake_occ());
	for (auto p : pl1)
	{
		CampView cv;
		if (!find_camp(p, cv, false)) continue;
		cv.awake = true;
		awake.push_back(cv);
		if (cheb(cv.pos, pos) <= cv.r) inc += cv.str;
	}
	enemies.clear();
	for (auto h : enemy_handles)
	{
		Unit u;
		if (!unit_info(h, u)) continue;
		if (!(u.state & ST_ALIVE)) continue;
		if (!enemy_occ().is_set(u.pos)) continue; // vision.champions(ENEMY) = enemy occupancy board
		if (cheb(u.pos, pos) > ENEMY_SIGHT) continue; // seen via our ward only
		enemies.push_back(u);
	}
	// vision.champions() order = engine board order
	std::stable_sort(enemies.begin(), enemies.end(), [&](const Unit& a, const Unit& b) { return okey(a.pos) < okey(b.pos); });
	for (auto& e : enemies)
		if (cheb(e.pos, pos) <= e.range + 1) inc += e.str;
	if (jungle()) inc *= 0.8; // Jungle emblem: 30% less camp damage (approximate on the total)
	return inc;
}

void Bot::update_alerts(bool with_enemies)
{
	if (with_enemies)
	{
		for (auto& e : enemies)
		{
			if (cheb(e.pos, pos) <= 14) last_enemy_near = rnd;
			for (std::size_t i = 0; i < altars.size(); ++i)
				if (cheb(e.pos, altars[i]) <= 8) altar_seen[i] = rnd;
		}
	}
	for (std::size_t i = 0; i < ally_handles.size(); ++i)
	{
		std::int32_t alive{};
		if (raw::sdk_champion_is_alive(ally_handles[i], &alive) != 0) break;
		if (ally_alive[i] && !alive) last_ally_death = rnd;
		ally_alive[i] = alive ? 1 : 0;
	}
}

bool Bot::threatened() const
{
	const std::int64_t seen = BANK_THREAT_LOSING_ONLY ? last_enemy_danger : last_enemy_near;
	return rnd - seen <= 40 || rnd - last_ally_death <= 100 || hp < maxhp * 0.6;
}
