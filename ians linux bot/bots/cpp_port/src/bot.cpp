// Bot::play_turn: the turn flow of tb_merge_b's Bot.play_turn (bots/tb_merge_b/src/bot.py).
#include <algorithm>

#include "bot.h"

using namespace P;

static_assert(static_cast<std::uint32_t>(cambc::item_type::enum_type::jungle_emblem_of_strength) == 25);
static_assert(static_cast<std::uint32_t>(cambc::item_type::enum_type::monster_emblem_of_strength) == 1);

void Bot::play_turn()
{
	if (!inited)
	{
		init_static();
		PROF("init_static");
		std::int32_t alive{};
		raw::sdk_champion_is_alive(myh, &alive);
		if (cambc::fuel_remaining() < FUEL_FIRST_TURN_MIN && alive)
		{
			// init used most of the 2x first-turn budget: shop now, build static fields with the rest
			if (refresh_me() && spawn->is_set(pos)) shop();
			return;
		}
	}
	rnd = cambc::round_number();
	items_ok = false;
	dps_cache = -1;
	cdps_cache = -1;
	tfield_ok = false;
	std::int32_t alive{};
	raw::sdk_champion_is_alive(myh, &alive);
	if (!alive)
	{
		if (!was_dead && target >= 0) died_at[target] = rnd;
		was_dead = true;
		write_claim(-1);
		update_alerts(false);
		shop();
		return;
	}
	was_dead = false;
	if (!refresh_me()) return;
	observe();
	PROF("observe");
	if (mystate & (ST_RECALLING | ST_SUBMITTING | ST_TELEPORTING)) return;
	try_ward();
	const bool at_spawn = spawn->is_set(pos);
	if (at_spawn) shop();
	PROF("ward_shop");

	const double incoming = threats();
	try_lock();
	update_alerts(true);
	stall *= STALL_DECAY;
	PROF("threats_lock_alerts");

	// Heal up fully on spawn before leaving.
	if (at_spawn && hp < maxhp * 0.92 && incoming == 0) return;

	// ---- danger handling: never die to camps
	if (incoming > 0)
	{
		int steps = 1;
		for (auto& c : awake)
			if (cheb(c.pos, pos) <= c.r) steps = std::max(steps, c.r - cheb(c.pos, pos) + 1);
		double hit_hp = 0.0;
		for (auto& c : awake)
			if (cheb(c.pos, pos) <= c.r) hit_hp += c.hp;
		const double finish_turns = hit_hp / dps() + 1;
		const bool safe_finish = finish_turns * incoming < hp - 60 && enemies.empty();
		if (!safe_finish && hp <= incoming * (steps + 1) + 60)
		{
			// an adjacent melee enemy that dies to our next hit is finished, not fled
			const int adj = enemies.empty() ? -1 : adjacent_melee(enemies);
			if (adj >= 0 && enemies[adj].hp <= mystr)
			{
				strike({ EK_CHAMP, enemies[adj].h }, incoming);
				return;
			}
			retreat(enemies);
			return;
		}
	}

	// ---- fight or avoid enemy champions
	if (!enemies.empty() && handle_enemies(incoming)) return;
	PROF("enemies");

	// ---- recall to heal / shop when safe
	if (incoming == 0 && !at_spawn)
	{
		const int spawn_d = spawn_dist(pos);
		const bool low = hp < maxhp * 0.45;
		const std::uint32_t gd = gold();
		bool rich = gd >= 400;
		if (!rich && gd >= 150) rich = gems() < 8;
		if ((low || rich) && spawn_d > 6 && recall_safe())
		{
			if (do_recall())
			{
				write_claim(-1);
				return;
			}
		}
		else if (low)
		{
			step_toward(*spawn);
			return;
		}
	}

	turn_field(); // sets sf_use; per-turn field only while static fields are missing
	PROF("turn_field");
	const int comp = comp_of(pos);
	(void)comp;
	PROF("comp_of");

	// ---- tribute decision
	const int gm = static_cast<int>(gems());
	int tgt = -1;
	bool chosen = false;
	int pref = -1;
	if (gm > 0)
	{
		pref_altar = -1;
		std::int64_t ad = pick_altar(pref);
		if (ad >= BIG) ad = 40;
		const std::int64_t total = static_cast<std::int64_t>(cambc::global_submitted_gems(cambc::team::ally)) + gm;
		const bool thr = threatened();
		bool go = rnd + ad + gm / 10 + 12 >= MAX_ROUNDS || total >= 1000 || rnd >= BANK_LATE_ROUND ||
				  bank_now(gm, BANK_DETOUR ? BIG : ad, thr);
		PROF("pick_altar");
		if (!go)
		{
			tgt = choose_target();
			PROF("choose_target");
			chosen = true;
			if (tgt < 0)
				go = true;
			else if (BANK_DETOUR)
				go = bank_detour(gm, detour(ad, tgt), thr);
		}
		if (go)
		{
			write_claim(-1);
			do_tribute(pref);
			return;
		}
	}

	// ---- farming
	const int gi = chosen ? tgt : choose_target();
	PROF("choose_target2");
	target = gi;
	write_claim(gi);
	if (gi < 0)
	{
		if (gm > 0)
			do_tribute(pref);
		else if (!at_spawn && (gold() >= 60 || hp < maxhp * 0.7))
			do_recall();
		return;
	}
	Group& G = groups[gi];

	if (G.status != 1 && all_camp_tiles->is_set(pos))
	{
		// never block a camp's respawn by standing on its spawn tile
		const bitboard& blocked = blocked_now();
		std::array<std::pair<int, vec2>, 8> cands{};
		int k = 0;
		for (int dy = -1; dy <= 1; ++dy)
			for (int dx = -1; dx <= 1; ++dx)
			{
				if (!dx && !dy) continue;
				const vec2 t{ pos.x + dx, pos.y + dy };
				if (!in_bounds(t) || blocked.is_set(t) || all_camp_tiles->is_set(t)) continue;
				cands[k++] = { okey(t), t };
			}
		std::sort(cands.begin(), cands.begin() + k, [](const auto& a, const auto& b) { return a.first < b.first; });
		if (k && can_move())
		{
			int bi = 0;
			for (int i = 1; i < k; ++i)
				if (cheb(cands[i].second, G.center) < cheb(cands[bi].second, G.center)) bi = i;
			move_abs(cands[bi].second);
			return;
		}
	}
	if (G.status == 2)
	{
		if (!G.wait_ring)
		{
			G.wait_ring = std::make_unique<bitboard>();
			dilate_into(G.tiles, 1, *G.wait_ring);
			*G.wait_ring &= *not_walk_camp;
		}
		if (!G.wait_ring->is_set(pos)) go_to(*G.wait_ring);
		return;
	}
	if (G.status == 0 && cheb(G.center, pos) <= 3)
	{
		bool seen_alive = false;
		for (auto& c : G.camps)
		{
			raw::camp_state cs{};
			if (raw::sdk_camp(c.h, &cs) != 0) continue;
			std::uint32_t s{};
			if (raw::sdk_camp_state(c.h, &s) != 0) continue;
			if (s != 0)
			{
				seen_alive = true;
				break;
			}
		}
		if (!seen_alive)
		{
			G.status = 2;
			G.ready = rnd + 10;
			return;
		}
	}
	if (G.status == 1)
	{
		// capture: stand on a free spawn tile of the group
		if (G.tiles.is_set(pos)) return;
		bitboard& fr = sb(SB_F_FREE);
		not_into(fr, blocked_now());
		fr &= G.tiles;
		if (fr.is_empty()) copy_into(fr, G.tiles);
		go_to(fr);
		return;
	}

	// avoid walking into range of other awake camps (quirk: compares the camp's position with G's spawn tiles)
	bitboard* avoid = nullptr;
	for (auto& c : awake)
		if (!G.has_spawn(c.pos))
		{
			if (!avoid)
			{
				avoid = &sb(SB_F_AVOID);
				avoid->clear();
			}
			avoid->draw_chebyshev(c.pos, static_cast<float>(c.r));
		}

	bool moved = false;
	Tgt tg = pick_camp_in_range(G);
	const bool ranged = myrange > 1;
	if (!tg)
	{
		bitboard& alive_b = sb(SB_F_ALIVE);
		alive_tiles(G, alive_b);
		if (alive_b.is_empty()) copy_into(alive_b, G.tiles);
		const bitboard* goals = &alive_b;
		if (cheb(G.center, pos) <= 5)
		{
			bitboard& unseen = sb(SB_F_UNSEEN);
			not_into(unseen, vis_tiles());
			unseen &= alive_b;
			if (!unseen.is_empty())
			{
				bitboard& bush = sb(SB_F_BUSH);
				dilate_into(unseen, 1, bush);
				bush &= cambc::map::bushes();
				bitboard& na = sb(SB_F_NG);
				not_into(na, alive_b);
				bush &= na;
				bush &= *not_walk;
				if (!bush.is_empty()) goals = &bush;
			}
		}
		if (ranged && goals == &alive_b)
		{
			bitboard& rg = sb(SB_F_RG);
			dilate_into(alive_b, myrange, rg);
			bitboard& na = sb(SB_F_NG);
			not_into(na, alive_b);
			rg &= na;
			rg &= *not_walk;
			if (!rg.is_empty()) goals = &rg;
		}
		PROF("goals");
		moved = go_to(*goals, avoid, &alive_b);
		PROF("go_to");
		tg = pick_camp_in_range(G);
	}
	bool attacked = false;
	if (tg && can_attack()) attacked = attack(tg);
	if (tg || incoming > 0) cast_combat(tg, moved, incoming, attacked);
	note_progress(gi, moved || attacked);
}
