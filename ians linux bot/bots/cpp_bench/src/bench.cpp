// Fuel micro-benchmarks. Every BENCH line prints net fuel (minus the cost of the
// fuel_remaining() probe itself) for `reps` repetitions, and the per-repetition cost.
#include <cambc.h>
#include "bench.h"
#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <vector>

namespace bench {
using cambc::bitboard;
using cambc::distance_field;
using cambc::team;
using cambc::vec2;

static volatile std::uint64_t sink;
static std::uint64_t overhead = 0;

static std::uint64_t F() { return cambc::fuel_remaining(); }

static void report(const char* name, int reps, std::uint64_t used, long extra)
{
	const std::uint64_t net = used > overhead ? used - overhead : 0;
	std::cout << "BENCH " << name << " reps=" << reps << " total=" << net << " per=" << (net / std::uint64_t(std::max(1, reps)));
	if (extra >= 0)
		std::cout << " n=" << extra;
	std::cout << '\n';
}

#define BENCH(name, reps, extra, ...)                                                                                                 \
	do                                                                                                                                \
	{                                                                                                                                 \
		const std::uint64_t _f0 = F();                                                                                                \
		for (int _i = 0; _i < (reps); ++_i)                                                                                           \
		{                                                                                                                             \
			__VA_ARGS__;                                                                                                              \
		}                                                                                                                             \
		const std::uint64_t _f1 = F();                                                                                                \
		report(name, reps, _f0 - _f1, extra);                                                                                         \
	} while (0)

// ---------------------------------------------------------------- native helpers
static bitboard dilate(const bitboard& bb, int r)
{
	bitboard out{ bb };
	for (int i = 0; i < r; ++i)
	{
		bitboard h = out | out.shift_right(1) | out.shift_right(-1);
		out = h | h.shift_up(1) | h.shift_up(-1);
	}
	return out;
}

// Native bit test on the engine-chunked raw buffer: 8x8 chunks, one u64 per chunk.
static inline bool raw_test(const bitboard& b, int x, int y)
{
	const auto& L = cambc::detail::layout();
	const std::uint64_t w = b.ptr()[(y >> 3) * L.chunk_stride + (x >> 3)];
	return (w >> (((y & 7) << 3) | (x & 7))) & 1u;
}

// Plain queue BFS (8-neighbour) on a padded grid; returns tiles reached.
static int native_bfs(const std::vector<std::uint8_t>& wall, int W, int H, int sx, int sy, std::vector<std::uint16_t>& dist,
					  std::vector<int>& q)
{
	const int PW = W + 2;
	std::fill(dist.begin(), dist.end(), 65535);
	const int s = (sy + 1) * PW + (sx + 1);
	const int off[8] = { -PW - 1, -PW, -PW + 1, -1, 1, PW - 1, PW, PW + 1 };
	dist[s] = 0;
	int head = 0, tail = 0;
	q[tail++] = s;
	while (head < tail)
	{
		const int c = q[head++];
		const std::uint16_t nd = dist[c] + 1;
		for (int k = 0; k < 8; ++k)
		{
			const int n = c + off[k];
			if (!wall[n] && dist[n] == 65535)
			{
				dist[n] = nd;
				q[tail++] = n;
			}
		}
	}
	return tail;
}

// Bit-parallel BFS: rows of u64 words (W <= 128 -> 2 words). Wavefront dilation per step,
// distances assigned to newly reached bits. Returns tiles reached.
static int bitset_bfs(const std::vector<std::uint64_t>& walls, int W, int H, int NW, int sx, int sy, std::vector<std::uint16_t>& dist)
{
	std::vector<std::uint64_t> vis(std::size_t(H) * NW, 0), fr(std::size_t(H) * NW, 0), nx(std::size_t(H) * NW, 0);
	std::fill(dist.begin(), dist.end(), 65535);
	vis[sy * NW + (sx >> 6)] |= 1ull << (sx & 63);
	fr[sy * NW + (sx >> 6)] |= 1ull << (sx & 63);
	dist[sy * W + sx] = 0;
	int reached = 1, ylo = sy, yhi = sy;
	for (std::uint16_t d = 1;; ++d)
	{
		const int a = std::max(0, ylo - 1), b = std::min(H - 1, yhi + 1);
		int nlo = H, nhi = -1;
		for (int y = a; y <= b; ++y)
		{
			for (int w = 0; w < NW; ++w)
			{
				std::uint64_t m = fr[y * NW + w];
				if (y > 0)
					m |= fr[(y - 1) * NW + w];
				if (y + 1 < H)
					m |= fr[(y + 1) * NW + w];
				// horizontal spread with carries between words
				std::uint64_t left = m << 1, right = m >> 1;
				if (w > 0)
				{
					std::uint64_t pm = fr[y * NW + w - 1];
					if (y > 0) pm |= fr[(y - 1) * NW + w - 1];
					if (y + 1 < H) pm |= fr[(y + 1) * NW + w - 1];
					left |= pm >> 63;
				}
				if (w + 1 < NW)
				{
					std::uint64_t nm = fr[y * NW + w + 1];
					if (y > 0) nm |= fr[(y - 1) * NW + w + 1];
					if (y + 1 < H) nm |= fr[(y + 1) * NW + w + 1];
					right |= nm << 63;
				}
				std::uint64_t n = (m | left | right) & ~walls[y * NW + w] & ~vis[y * NW + w];
				nx[y * NW + w] = n;
				if (n)
				{
					vis[y * NW + w] |= n;
					nlo = std::min(nlo, y);
					nhi = std::max(nhi, y);
					while (n)
					{
						const int bit = __builtin_ctzll(n);
						n &= n - 1;
						dist[y * W + (w << 6) + bit] = d;
						++reached;
					}
				}
			}
		}
		// rows outside [a,b] of nx are stale zeros; swap frontier
		for (int y = a; y <= b; ++y)
			for (int w = 0; w < NW; ++w)
			{
				fr[y * NW + w] = nx[y * NW + w];
				nx[y * NW + w] = 0;
			}
		if (nhi < 0)
			break;
		ylo = nlo;
		yhi = nhi;
	}
	return reached;
}

static bitboard walk_block()
{
	return cambc::map::walls() | cambc::map::holes() | cambc::map::altars() | cambc::map::spawn_region(team::enemy);
}

// ---------------------------------------------------------------- turn 1
void static_benches()
{
	auto& me = cambc::self();
	const auto& L = cambc::detail::layout();
	const int W = L.width, H = L.height;
	std::cout << "MAP w=" << W << " h=" << H << " cw=" << L.chunked_width << " ch=" << L.chunked_height << " stride=" << L.chunk_stride
			  << " board_bytes=" << L.board_bytes << " field_bytes=" << L.field_bytes << " fuel_now=" << F() << '\n';
	{
		const auto f0 = F();
		const auto f1 = F();
		overhead = f0 - f1;
		std::cout << "BENCH fuel_remaining_probe per=" << overhead << '\n';
	}
	BENCH("empty_loop_x1000", 1000, -1, sink = sink + 1);

	// ------------------------------------------------ scalar SDK calls
	BENCH("round_number", 100, -1, sink = cambc::round_number());
	BENCH("me.position", 100, -1, sink = me.position().x);
	BENCH("me.health", 100, -1, sink = std::uint64_t(me.health()));
	BENCH("me.state(can_move)", 100, -1, sink = me.can_move());
	BENCH("me.is_alive", 100, -1, sink = me.is_alive());
	BENCH("me.gold_count", 100, -1, sink = me.gold_count());
	BENCH("me.gem_count", 100, -1, sink = me.gem_count());
	BENCH("me.champion_name", 100, -1, sink = std::uint64_t(me.champion_name()));
	BENCH("raw sdk_champion (all fields)", 100, -1, {
		cambc::detail::champion_info ci{};
		cambc::detail::sdk_champion(static_cast<std::uint32_t>(static_cast<cambc::handle_champion_t>(me)), &ci);
		sink = ci.x + ci.state;
	});
	BENCH("me.item_count", 20, -1, sink = me.item_count()[cambc::item_type::power_shard_of_health]);
	BENCH("me.abilities (copy)", 20, -1, sink = me.abilities()[0].slot());
	{
		const auto abs = me.abilities();
		BENCH("ability.is_ready", 20, -1, sink = abs[0].is_ready());
		BENCH("ability.cooldown", 20, -1, sink = abs[0].cooldown());
		BENCH("ability.is_dash (cached info)", 100, -1, sink = abs[0].is_dash() + abs[1].is_dash());
		BENCH("ability.damage_amount", 20, -1, {
			try { sink = std::uint64_t(abs[1].damage_amount()); } catch (...) { sink = 0; }
		});
	}
	BENCH("consumable.count", 20, -1, sink = me.consumables()[cambc::consumable_type::altar_lock].count());
	BENCH("me.can_buy(item)", 20, -1, sink = me.can_buy(cambc::item_type::power_shard_of_strength));
	BENCH("me.ward_cooldown", 20, -1, sink = me.ward_cooldown());
	BENCH("global_submitted_gems", 20, -1, sink = cambc::global_submitted_gems(team::ally));
	BENCH("cambc::champions(ally) (all handles)", 5, -1, sink = cambc::champions(team::ally).size());
	BENCH("cambc::champions(enemy) (all handles)", 5, -1, sink = cambc::champions(team::enemy).size());

	// shared memory
	{
		std::array<std::byte, 8> buf{};
		BENCH("shared_memory.read(8)", 100, -1, cambc::shared_memory.read(0, buf); sink = std::uint64_t(buf[0]));
		BENCH("shared_memory[7] read", 100, -1, sink = std::uint8_t(cambc::shared_memory[7]));
		BENCH("shared_memory[6]=v write", 100, -1, cambc::shared_memory[6] = std::uint8_t(_i & 1 ? 0 : 0));
	}

	// exceptions: a thrown and caught engine error
	BENCH("throw+catch cambc::error (champion_at empty)", 10, -1, {
		try { sink = cambc::vision::champion_at({ 0, 0 }).position().x; } catch (const std::exception&) { sink = 1; }
	});

	// ------------------------------------------------ bitboards
	const vec2 pos = me.position();
	bitboard blk = walk_block();
	const bitboard& walls = cambc::map::walls();
	BENCH("bitboard() ctor (alloc+zero)", 100, -1, bitboard b; sink = b.ptr()[0]);
	BENCH("bitboard copy ctor", 100, -1, bitboard b{ blk }; sink = b.ptr()[0]);
	BENCH("a | b (new board)", 100, -1, bitboard b = blk | walls; sink = b.ptr()[0]);
	{
		bitboard acc;
		BENCH("a |= b (in place)", 100, -1, acc |= walls);
		BENCH("a &= b (in place)", 100, -1, acc &= blk);
		BENCH("~a (new board)", 100, -1, bitboard b = ~acc; sink = b.ptr()[0]);
	}
	BENCH("walk_block() 4-way union", 20, -1, bitboard b = walk_block(); sink = b.ptr()[0]);
	BENCH("shift_right(1)", 100, -1, bitboard b = blk.shift_right(1); sink = b.ptr()[0]);
	BENCH("shift_up(1)", 100, -1, bitboard b = blk.shift_up(1); sink = b.ptr()[0]);
	BENCH("dilate r=1", 20, -1, bitboard b = dilate(blk, 1); sink = b.ptr()[0]);
	BENCH("dilate r=3", 10, -1, bitboard b = dilate(blk, 3); sink = b.ptr()[0]);
	BENCH("is_set (SDK)", 1000, -1, sink = blk.is_set({ _i % W, (_i / W) % H }));
	BENCH("raw_test (native)", 1000, -1, sink = raw_test(blk, _i % W, (_i / W) % H));
	{
		bitboard b;
		BENCH("set (SDK)", 1000, -1, b.set({ _i % W, (_i / W) % H }));
	}
	BENCH("is_empty", 100, -1, sink = blk.is_empty());
	BENCH("count", 100, -1, sink = blk.count());
	{
		bitboard small;
		small.draw_chebyshev(pos, 1);
		bitboard mid;
		mid.draw_chebyshev(pos, 5);
		bitboard big;
		big.draw_chebyshev(pos, 15);
		BENCH("positions() 9 bits", 20, small.count(), sink = small.positions().size());
		BENCH("positions() ~121 bits", 20, mid.count(), sink = mid.positions().size());
		BENCH("positions() ~961 bits", 10, big.count(), sink = big.positions().size());
		BENCH("positions() walk_block", 5, blk.count(), sink = blk.positions().size());
		BENCH("draw_chebyshev r=1 (+ctor)", 100, -1, bitboard b; b.draw_chebyshev(pos, 1); sink = b.ptr()[0]);
		BENCH("draw_chebyshev r=8 (+ctor)", 100, -1, bitboard b; b.draw_chebyshev(pos, 8); sink = b.ptr()[0]);
	}
	{
		bitboard blocked = blk;
		blocked.set(pos, false);
		BENCH("reachable_tiles(pos,1)", 100, -1, bitboard r = blocked.reachable_tiles(pos, 1); sink = r.ptr()[0]);
		bitboard comp = blocked.reachable_tiles(pos, std::uint16_t(W * H));
		BENCH("reachable_tiles(pos,W*H) component", 5, comp.count(), bitboard r = blocked.reachable_tiles(pos, std::uint16_t(W * H)); sink = r.ptr()[0]);
		BENCH("shadow_cast(pos,10)", 20, -1, bitboard r = (walls | cambc::map::bushes()).shadow_cast(pos, 10); sink = r.ptr()[0]);
	}
	// linear export: format probe
	{
		std::vector<std::uint8_t> lin;
		BENCH("bitboard export_linear_buffer", 20, bitboard::linear_buffer_size(), lin = blk.export_linear_buffer());
		long nz = 0;
		for (auto v : lin) nz += v != 0;
		std::cout << "LINEAR bitboard bytes=" << lin.size() << " nonzero=" << nz << " count=" << blk.count() << '\n';
		std::vector<std::uint8_t> raw;
		BENCH("bitboard export_raw_buffer", 20, bitboard::raw_buffer_size(), raw = blk.export_raw_buffer());
		// verify the native raw layout against the SDK on every tile (free in debug builds)
		long bad = 0;
		debug_block({
			for (int y = 0; y < H; ++y)
				for (int x = 0; x < W; ++x)
					if (raw_test(blk, x, y) != blk.is_set({ x, y }))
						++bad;
		});
		std::cout << "RAWLAYOUT mismatches=" << bad << '\n';
	}

	// ------------------------------------------------ distance fields
	BENCH("distance_field() ctor", 20, -1, distance_field f; sink = f.width());
	bitboard roots;
	roots.set(pos);
	bitboard blocked = blk;
	blocked.set(pos, false);
	distance_field full;
	bitboard visited;
	std::uint16_t steps = 0;
	BENCH("df.compute full map from pos", 3, -1, steps = full.compute_with_expansion_count(blocked, roots, visited));
	std::cout << "INFO full field expansions=" << steps << " visited=" << visited.count() << '\n';
	// pick destinations at distance ~10, ~30 and the farthest reached tile (native scan of an export)
	std::vector<std::uint16_t> lin;
	BENCH("df.export_linear_buffer", 5, -1, lin = full.export_linear_buffer());
	vec2 d10{ -1, -1 }, d30{ -1, -1 }, dfar{ -1, -1 };
	int far = -1;
	for (int i = 0; i < W * H; ++i)
	{
		const int v = lin[i];
		if (v == 65535)
			continue;
		if (v == 10 && d10.x < 0) d10 = { i % W, i / W };
		if (v == 30 && d30.x < 0) d30 = { i % W, i / W };
		if (v > far) { far = v; dfar = { i % W, i / W }; }
	}
	std::cout << "INFO far=" << far << '\n';
	BENCH("df.get (SDK)", 1000, -1, sink = full.get({ _i % W, (_i / W) % H }));
	BENCH("linear lookup (native)", 1000, -1, sink = lin[(_i % W) + ((_i / W) % H) * W]);
	BENCH("df.next_move_from", 100, -1, { auto m = full.next_move_from(dfar); sink = m ? m->x : 0; });
	for (int md : { 5, 10, 20, 40 })
	{
		distance_field f;
		bitboard v;
		std::uint16_t s = 0;
		const char* names[] = { "df.compute max_distance=5", "df.compute max_distance=10", "df.compute max_distance=20", "df.compute max_distance=40" };
		const int idx = md == 5 ? 0 : md == 10 ? 1 : md == 20 ? 2 : 3;
		BENCH(names[idx], 3, -1, s = f.compute_with_expansion_count(blocked, roots, v, std::uint16_t(md)));
		std::cout << "INFO md=" << md << " expansions=" << s << " visited=" << v.count() << '\n';
	}
	for (auto [name, dst] : { std::pair{ "df.compute_to dest@10", d10 }, std::pair{ "df.compute_to dest@30", d30 }, std::pair{ "df.compute_to dest@far", dfar } })
	{
		if (dst.x < 0)
			continue;
		distance_field f;
		bitboard v, dests;
		dests.set(dst);
		std::uint16_t s = 0;
		BENCH(name, 3, -1, s = f.compute_to_with_expansion_count(blocked, roots, dests, v));
		std::cout << "INFO " << name << " expansions=" << s << " visited=" << v.count() << '\n';
	}
	// step_toward pattern: field rooted at goals, stop when we are reached, then scan 8 neighbours
	if (d30.x >= 0)
	{
		bitboard goal;
		goal.set(d30);
		bitboard start;
		start.set(pos);
		BENCH("step_toward(goal@30) compute_to+neighbours", 3, -1, {
			distance_field f;
			bitboard v;
			bitboard w2 = blocked & ~goal;
			f.compute_to(w2, goal, start, v);
			std::uint16_t bd = f.get(pos);
			vec2 best = pos;
			for (vec2 t : w2.reachable_tiles(pos, 1).positions())
				if (t != pos && v.is_set(t) && f.get(t) < bd) { bd = f.get(t); best = t; }
			sink = best.x;
		});
	}
	// static field rooted at an altar ring (what sf_fuel caches per altar)
	{
		auto altars = cambc::map::altars().positions();
		if (!altars.empty())
		{
			bitboard ring;
			ring.draw_chebyshev(altars[0], 1);
			ring &= ~blk;
			distance_field f;
			BENCH("df.compute full map from altar ring", 3, -1, f.compute(blk & ~ring, ring, visited));
		}
	}

	// ------------------------------------------------ native BFS baselines
	{
		std::vector<std::uint8_t> packed = blk.export_linear_buffer();
		std::vector<std::uint8_t> wall(std::size_t(W + 2) * (H + 2), 1);
		BENCH("native: unpack walk mask to padded u8 grid", 1, -1, {
			for (int y = 0; y < H; ++y)
				for (int x = 0; x < W; ++x)
				{
					const int i = y * W + x;
					wall[(y + 1) * (W + 2) + x + 1] = (packed[i >> 3] >> (i & 7)) & 1;
				}
		});
		wall[(pos.y + 1) * (W + 2) + pos.x + 1] = 0;
		std::vector<std::uint16_t> dist(std::size_t(W + 2) * (H + 2));
		std::vector<int> q(std::size_t(W + 2) * (H + 2));
		int reached = 0;
		BENCH("native queue BFS full map", 2, -1, reached = native_bfs(wall, W, H, pos.x, pos.y, dist, q));
		std::cout << "INFO native queue BFS reached=" << reached << '\n';
		// correctness check vs SDK field
		long bad = 0;
		for (int y = 0; y < H; ++y)
			for (int x = 0; x < W; ++x)
				if (dist[(y + 1) * (W + 2) + x + 1] != lin[y * W + x]) ++bad;
		std::cout << "INFO native queue BFS mismatches=" << bad << '\n';

		const int NW = (W + 63) / 64;
		std::vector<std::uint64_t> wrows(std::size_t(H) * NW, 0);
		for (int y = 0; y < H; ++y)
			for (int x = 0; x < W; ++x)
				if (wall[(y + 1) * (W + 2) + x + 1]) wrows[y * NW + (x >> 6)] |= 1ull << (x & 63);
		// out-of-map bits in the last word count as walls
		for (int y = 0; y < H; ++y)
			for (int x = W; x < NW * 64; ++x) wrows[y * NW + (x >> 6)] |= 1ull << (x & 63);
		std::vector<std::uint16_t> d2(std::size_t(W) * H);
		BENCH("native bitset BFS full map", 2, -1, reached = bitset_bfs(wrows, W, H, NW, pos.x, pos.y, d2));
		bad = 0;
		for (int i = 0; i < W * H; ++i) if (d2[i] != lin[i]) ++bad;
		std::cout << "INFO native bitset BFS reached=" << reached << " mismatches=" << bad << '\n';
		BENCH("native: scan 10k u16 (sum)", 1, -1, {
			std::uint64_t s = 0;
			for (int i = 0; i < W * H; ++i) s += lin[i];
			sink = s;
		});
	}

	// ------------------------------------------------ static enumeration
	std::size_t ngroups = 0, ncamps = 0;
	BENCH("map::camp_groups() full load", 3, -1, {
		auto gs = cambc::map::camp_groups();
		ngroups = gs.size();
		ncamps = 0;
		for (auto& g : gs) ncamps += g.camps().size();
	});
	std::cout << "INFO groups=" << ngroups << " camps=" << ncamps << '\n';
	{
		auto gs = cambc::map::camp_groups();
		BENCH("camp.base_stats() (per camp)", 20, -1, sink = std::uint64_t(gs[0].camps()[0].base_stats().base_health));
		BENCH("group.spawn_tiles() (per group)", 20, -1, bitboard b = gs[0].spawn_tiles(); sink = b.ptr()[0]);
	}
	BENCH("map::altars().positions()", 20, -1, sink = cambc::map::altars().positions().size());
	BENCH("std::cout one short line", 10, -1, std::cout << "x\n");

	// ------------------------------------------------ allocation-free variants (design input)
	{
		bitboard out, tmp;
		BENCH("shift_right_into (prealloc)", 100, -1, blk.shift_right_into(1, out));
		BENCH("vision::camp_tiles_into (prealloc)", 100, -1, cambc::vision::camp_tiles_into(out));
		BENCH("out = a; out |= b (copy-assign + or)", 100, -1, out = blk; out |= walls);
		BENCH("dilate1 into scratch (4 into + 4 |=)", 20, -1, {
			blk.shift_right_into(1, tmp); out = blk; out |= tmp;
			blk.shift_right_into(-1, tmp); out |= tmp;
			out.shift_up_into(1, tmp); bitboard& o = out; o |= tmp;
			out.shift_up_into(-1, tmp); out |= tmp;
		});
		std::array<vec2, 128> buf{};
		bitboard small;
		small.draw_chebyshev(pos, 2);
		BENCH("positions_into(span) 25 bits", 20, small.count(), sink = small.positions_into(buf));
		BENCH("positions() 25 bits", 20, small.count(), sink = small.positions().size());
	}
	// cached champion handles: is_visible on every enemy (no per-turn construction)
	{
		static const auto enemies = cambc::champions(team::enemy);
		BENCH("cached enemies: is_visible() all", 10, long(enemies.size()), {
			int n = 0;
			for (const auto& e : enemies) n += e.is_visible();
			sink = n;
		});
	}
	// step along a cached static field: 8 neighbour gets + blocked test
	{
		bitboard blocked_now = blk | cambc::vision::champion_tiles() | cambc::vision::camp_tiles();
		blocked_now.set(pos, false);
		BENCH("static-field step (8 nbr get + is_set)", 20, -1, {
			std::uint16_t bd = full.get(dfar);
			vec2 best = dfar;
			for (int dx = -1; dx <= 1; ++dx)
				for (int dy = -1; dy <= 1; ++dy)
				{
					const vec2 t{ dfar.x + dx, dfar.y + dy };
					if ((dx || dy) && t.x >= 0 && t.y >= 0 && t.x < W && t.y < H && !blocked_now.is_set(t))
					{
						const auto v = full.get(t);
						if (v < bd) { bd = v; best = t; }
					}
				}
			sink = best.x;
		});
	}
	// a full static-field build with every allocation (what build_static_fields pays per key)
	{
		auto gs = cambc::map::camp_groups();
		std::vector<distance_field> fields;
		fields.reserve(4);
		std::uint64_t total = 0;
		int built = 0;
		for (std::size_t i = 0; i < gs.size() && built < 4; ++i)
		{
			const vec2 c = gs[i].camps().empty() ? vec2{ 0, 0 } : gs[i].camps()[0].spawn_position();
			const std::uint64_t f0 = F();
			bitboard r;
			r.set(c);
			distance_field f;
			bitboard v;
			const auto e = f.compute_with_expansion_count(blk & ~r, r, v);
			fields.push_back(std::move(f));
			const std::uint64_t used = f0 - F();
			total += used;
			++built;
			std::cout << "INFO static field group " << i << " expansions=" << e << " fuel=" << used << '\n';
		}
		std::cout << "INFO static field avg=" << (built ? total / built : 0) << '\n';
	}
}

// ---------------------------------------------------------------- later turns
void vision_benches(unsigned round)
{
	auto& me = cambc::self();
	const vec2 pos = me.position();
	std::cout << "VISION round=" << round << " pos=" << pos.x << "," << pos.y << '\n';
	BENCH("vision::visible_tiles", 20, -1, bitboard b = cambc::vision::visible_tiles(); sink = b.ptr()[0]);
	BENCH("vision::champion_tiles() both", 20, -1, bitboard b = cambc::vision::champion_tiles(); sink = b.ptr()[0]);
	BENCH("vision::champion_tiles(enemy)", 20, -1, bitboard b = cambc::vision::champion_tiles(team::enemy); sink = b.ptr()[0]);
	BENCH("vision::camp_tiles", 20, -1, bitboard b = cambc::vision::camp_tiles(); sink = b.ptr()[0]);
	BENCH("vision::awake_camp_tiles", 20, -1, bitboard b = cambc::vision::awake_camp_tiles(); sink = b.ptr()[0]);
	BENCH("vision::teleport_tiles", 20, -1, bitboard b = cambc::vision::teleport_tiles(); sink = b.ptr()[0]);
	BENCH("blocked_now (walk|champ|camp|tp)", 10, -1, {
		bitboard b = walk_block() | cambc::vision::champion_tiles() | cambc::vision::camp_tiles() | cambc::vision::teleport_tiles();
		b.set(pos, false);
		sink = b.ptr()[0];
	});
	std::size_t ne = 0, na = 0, nc = 0;
	BENCH("vision::champions(enemy)", 5, -1, ne = cambc::vision::champions(team::enemy).size());
	std::cout << "INFO visible enemies=" << ne << '\n';
	BENCH("vision::champions(ally)", 5, -1, na = cambc::vision::champions(team::ally).size());
	std::cout << "INFO visible allies(incl self)=" << na << '\n';
	BENCH("vision::camps()", 5, -1, nc = cambc::vision::camps().size());
	std::cout << "INFO visible camps=" << nc << '\n';
	{
		auto camps = cambc::vision::camps();
		if (!camps.empty())
		{
			const auto& c = camps[0];
			BENCH("camp.state()", 20, -1, sink = std::uint64_t(c.state()));
			BENCH("camp.health()", 20, -1, sink = std::uint64_t(c.health()));
			BENCH("camp.position()", 20, -1, sink = c.position().x);
			BENCH("camp.is_visible()", 20, -1, sink = c.is_visible());
			BENCH("camp.attack_range() (base_stats)", 20, -1, sink = c.attack_range());
			BENCH("raw sdk_camp (all fields)", 20, -1, {
				cambc::detail::camp_state cs{};
				cambc::detail::sdk_camp(static_cast<std::uint32_t>(static_cast<cambc::handle_camp_t>(c)), &cs);
				sink = cs.x;
			});
			BENCH("per-camp scan: state+pos+health+strength", 1, long(camps.size()), {
				for (const auto& k : camps)
					if (k.is_awake()) sink = k.position().x + std::uint64_t(k.health() + k.strength());
			});
		}
		auto ens = cambc::vision::champions(team::enemy);
		if (!ens.empty())
		{
			const auto& e = ens[0];
			BENCH("enemy.position()", 20, -1, sink = e.position().x);
			BENCH("enemy.is_submitting_gems()", 20, -1, sink = e.is_submitting_gems());
			BENCH("enemy.gem_count()", 20, -1, sink = e.gem_count());
			if (e.is_submitting_gems() || e.is_recalling() || e.is_teleporting())
				BENCH("enemy.remaining_channel_time()", 20, -1, sink = std::uint64_t(e.remaining_channel_time()));
			BENCH("enemy.health()+strength()+attack_range()", 20, -1, sink = std::uint64_t(e.health() + e.strength()) + e.attack_range());
		}
	}
	// visible camp groups and their state
	{
		static std::vector<cambc::map::camp_group> groups = cambc::map::camp_groups();
		bitboard vis = cambc::vision::visible_tiles();
		int nvis = 0;
		const cambc::map::camp_group* g0 = nullptr;
		BENCH("observe-like: groups intersect vision (bitboard &)", 1, long(groups.size()), {
			for (const auto& g : groups)
			{
				bitboard t = g.spawn_tiles();
				if (!(t & vis).is_empty()) { ++nvis; g0 = &g; }
			}
		});
		std::cout << "INFO groups in vision=" << nvis << '\n';
		if (g0)
			BENCH("group.state()", 10, -1, { auto s = g0->state(); sink = s.index(); });
		BENCH("vision::camp_groups()", 3, -1, sink = cambc::vision::camp_groups().size());
	}
	{
		auto altars = cambc::map::altars().positions();
		BENCH("has_altar_lock (per altar)", 1, long(altars.size()), for (auto a : altars) sink = cambc::vision::has_altar_lock(a));
		BENCH("in_vision (per altar)", 1, long(altars.size()), for (auto a : altars) sink = cambc::vision::in_vision(a));
	}
	BENCH("vision::has_camp", 100, -1, sink = cambc::vision::has_camp(pos));
	BENCH("vision::wards()", 10, -1, sink = cambc::vision::wards().size());
	BENCH("me.ward_positions()", 10, -1, sink = me.ward_positions().size());
	BENCH("me.attack_tiles()", 20, -1, bitboard b = me.attack_tiles(); sink = b.ptr()[0]);
}
} // namespace bench
