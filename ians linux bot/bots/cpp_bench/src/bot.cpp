// Champion decisions. main.cpp dispatches here after the draft.
#include <cambc.h>
#include "bot.h"
#include <array>
#include <iostream>
#include "random.h"
#include "bench.h"
#include <algorithm>
#include <cstdint>
#include <span>
#include <variant>
#include <utility>
#include <vector>

using cambc::vec2;
using cambc::team;

int distance(vec2 a, vec2 b) {
    return static_cast<int>(a.chebyshev_distance(b));
}

cambc::bitboard tiles_around(vec2 position, int radius) {
    cambc::bitboard tiles;
    tiles.clear();
    tiles.draw_chebyshev(position, radius);
    return tiles;
}

// Combine terrain and visible occupants using native bitboard operations.
cambc::bitboard blocked_tiles() {
    auto blocked = cambc::map::walls() | cambc::map::holes() | cambc::map::altars()
        | cambc::map::spawn_region(team::enemy) | cambc::vision::champion_tiles()
        | cambc::vision::camp_tiles() | cambc::vision::teleport_tiles();
    blocked.set(cambc::self().position(), false);
    return blocked;
}

bool move_towards_closest(cambc::bitboard goals) {
    auto& me = cambc::self();
    if (!me.can_move() || goals.is_set(me.position()))
        return false;

    // Only free goals or occupied camp tiles can seed the field.
    const auto blocked = blocked_tiles();
    goals &= ~blocked | cambc::vision::camp_tiles();
    if (goals.is_empty())
        return false;
    if (goals.count() == 1 && !blocked.is_set(goals.positions()[0]))
        return me.move_towards(goals.positions()[0]);

    // Expand from the goals until our current tile is reached.
    const auto path_walls = blocked & ~goals;
    cambc::distance_field field;
    cambc::bitboard visited;
    field.compute_to(path_walls, goals, tiles_around(me.position(), 0), visited);

    // Choose a reachable step with a smaller distance to the goal.
    auto step = me.position();
    for (auto tile : blocked.reachable_tiles(step, me.base_stats().base_move_speed).positions())
        if (field.get(tile) < field.get(step)) step = tile;

    return step != me.position() && me.move_absolute(step);
}

void Bot::buy_items() {
    auto& me = cambc::self();
    const std::array items{cambc::item_type::power_shard_of_strength,
        cambc::item_type::power_shard_of_focus, cambc::item_type::power_shard_of_health};
    const auto item = items[chosen_stat];
    const unsigned count = me.gold_count() / item.cost();
    if (count && me.can_buy(item, count)) me.buy(item, count);
}

// Compute the attack mask once, rather than once per visible target.
template<class Targets>
bool attack_first_in_range(const Targets& targets) {
    auto& me = cambc::self();
    if (targets.empty() || !me.can_attack()) return false;
    const auto attack_tiles = me.attack_tiles();
    for (const auto& target : targets) {
        if (target.is_visible() && attack_tiles.is_set(target.position()) && target.health() > 0) {
            me.attack(target);
            return true;
        }
    }
    return false;
}

// Attack a camp already in range, otherwise move toward the nearest camp tiles.
void farm_camps() {
    if (attack_first_in_range(cambc::vision::camps())) return;

    // Cache fixed spawn locations; only visible respawn state changes each turn.
    static const auto camp_groups = [] {
        std::vector<std::pair<cambc::map::camp_group, cambc::bitboard>> groups;
        for (const auto& group : cambc::map::camp_groups()) groups.emplace_back(group, group.spawn_tiles());
        return groups;
    }();
    static const auto camp_spawns = [] {
        cambc::bitboard tiles;
        tiles.clear();
        for (const auto& [group, spawns] : camp_groups) tiles |= spawns;
        return tiles;
    }();
    auto goals = camp_spawns;
    const auto visible = cambc::vision::visible_tiles();
    for (const auto& [group, spawns] : camp_groups)
        if (!(spawns & visible).is_empty()
            && std::holds_alternative<cambc::map::camp_group_respawning>(group.state()))
            goals &= ~spawns;

    // Fresh vision after movement may reveal a camp already in range.
    if (move_towards_closest(goals))
        attack_first_in_range(cambc::vision::camps());
}

void Bot::play_turn() {
    // cpp_bench: the lowest-handle ally runs the fuel benchmarks; everyone plays the starter.
    if (chosen_stat < 0) {
        chosen_stat = random_number(3);
        std::vector<std::uint32_t> hs;
        for (const auto& c : cambc::champions(team::ally))
            hs.push_back(static_cast<std::uint32_t>(static_cast<cambc::handle_champion_t>(c)));
        std::sort(hs.begin(), hs.end());
        const auto mine = static_cast<std::uint32_t>(static_cast<cambc::handle_champion_t>(cambc::self()));
        bench_slot = !hs.empty() && hs.front() == mine;
        if (bench_slot) {
            std::cout << "BENCHSTART champion=" << static_cast<int>(cambc::self().champion_name())
                      << " round=" << cambc::round_number() << std::endl;
            try { bench::static_benches(); }
            catch (const std::exception& e) { std::cout << "bench error: " << e.what() << '\n'; }
            std::cout << "BENCHEND fuel_left=" << cambc::fuel_remaining() << std::endl;
            return;
        }
    }
    const unsigned rnd = cambc::round_number();
    if (bench_slot && cambc::self().is_alive() && (rnd % 50 == 0)) {
        try { bench::vision_benches(rnd); }
        catch (const std::exception& e) { std::cout << "bench error: " << e.what() << '\n'; }
    }

    auto& me = cambc::self();

    // Leave channels running and skip turns where we cannot act.
    if (!me.is_alive() || me.is_recalling() || me.is_submitting_gems() || me.is_teleporting()
        || (!me.can_move() && !me.can_attack()))
        return;

    // Shop before leaving spawn.
    const bool at_spawn = cambc::map::spawn_region(team::ally).is_set(me.position());
    if (at_spawn)
        buy_items();

    // Recall immediately when badly hurt away from spawn.
    if (!at_spawn && me.health() < me.max_health() * 0.35f) {
        me.recall();
        return;
    }

    // Attack the first enemy champion already in range.
    if (attack_first_in_range(cambc::vision::champions(team::enemy))) return;

    // Bank any carried gems before farming.
    if (me.gem_count() > 0) {
        // Union all altar approach tiles: the field chooses the nearest reachable altar.
        cambc::bitboard goals;
        goals.clear();
        for (auto altar : cambc::map::altars().positions()) {
            if (distance(me.position(), altar) <= cambc::constants::submit_gems_range
                && !cambc::vision::has_altar_lock(altar)) {
                    me.submit_gems(altar);
                    return;
                }
            if (!cambc::vision::has_altar_lock(altar)) goals |= tiles_around(altar, cambc::constants::submit_gems_range);
        }
        move_towards_closest(goals);
        return;
    }

    farm_camps();

    me.set_priority(1 + random_number(100));
}
