<!-- source: https://2026a.battlecode.co.uk/game/docs/bitboards -->
Handbook/Guides

# Bitboards

4 min read · Current game rules

On this page

BasicsOperationsBuild a pathfinding maskCopies and snapshotsAdvanced: storage and bit layout

## Basics#

A bit is a single binary value: either 0 or 1. In a bitboard, each bit corresponds to a tile on a two-dimensional grid. A 1 means the tile is selected; a 0 means it is not. Think of it as a map of yes/no answers laid over the game board, rather than a list of individual coordinates.

What those answers mean depends on the board. A walls bitboard marks wall tiles with 1; a visibility bitboard marks tiles your bot can see. A tile can be selected in several different boards. These boards store locations, not champion identities or the full contents of each tile.

- Plan movement: combine walls and holes into a set of blocked tiles, then exclude them from candidate destinations.
- Filter targets: keep only goal tiles that are also visible or reachable.
- Track exploration: remember visited tiles and find places you have not explored.
- Compare turns: find tiles whose membership changed between two snapshots.

Operations combine entire sets tile by tile, so you can narrow down useful locations before iterating over their coordinates. The examples below use an 8×8 board to keep things readable; game maps can be larger.

## Operations#

Choose an operation, then select tiles in boards A and B to see how the result changes. Every result bit depends on the input bits at the same coordinate. Union and OR are two names for the same operation; intersection and AND are another pair.

Operation Union / ORIntersection / ANDExclusive ORDifference: A minus B

A OR B selects a tile if either input is 1, including when both are 1. Combine walls and holes into one blocked-tile mask.

Click or keyboard-toggle tiles in A and B. A 1 is selected; the result updates immediately.

A: 8 tilesB: 8 tilesResult: 14 tiles1111100010100000101000001111100000000000000000000000000000000000

14 tiles selected in the result.

| Operation | Expression | Use |
| --- | --- | --- |
| Union / OR | Bitboard.union a b | Tiles in either mask: walls OR holes. |
| Intersection / AND | Bitboard.intersect a b | Tiles in both: candidates AND visibility. |
| Exclusive OR | Bitboard.xor a b | Tiles in exactly one mask: compare old and new state. |
| Complement / NOT | Bitboard.complement a | Invert membership within map bounds. |
| Difference | Bitboard.intersect a (Bitboard.complement b) | Remove B from candidate set A. |
| Count | Bitboard.count a | Count selected tiles. |
| Membership | Bitboard.is_set a p | Test one coordinate. |

Use `positions()` (`Bitboard.positions` in OCaml) to enumerate coordinates. Combine and filter masks before materialising large position lists to save memory and fuel.

## Build a pathfinding mask#

Terrain masks in OCaml

```
open Cambc
let terrain_candidates () =
  let blocked = Bitboard.union (Game_map.walls ()) (Game_map.holes ()) in
  let _avoid = Bitboard.union blocked (Game_map.bushes ()) in
  let open_bushes = Bitboard.intersect (Game_map.bushes ()) (Bitboard.complement blocked) in
  List.iter (fun tile -> ignore tile) (Bitboard.positions open_bushes);
  open_bushes
```

Bushes are walkable

Walls and holes block normal movement. Including bushes in an avoidance mask is a strategy choice, not a movement rule. Vision blockers and movement blockers are different sets.

This terrain example is not a complete movement validator. Also account for altars, enemy spawn tiles and known occupied tiles. The SDK pathfinding helper builds the full mask. Hidden occupants can still block a step, so check the movement action result.

To query a group of goals, set one bit per acceptable destination, then intersect with reachable or visible tiles. Camp group IDs are not bit indices: use their tile coordinates.

## Copies and snapshots#

Map masks are cached values. `Bitboard.copy` makes a working copy. `union`/`intersect`/`complement` return new boards; `_assign` functions mutate their first argument.

Refresh dynamic visibility and unit masks during play. They are snapshots, not live subscriptions, and cannot reveal information outside your permitted vision.

## Advanced: storage and bit layout#

Map width 16 tiles (no padding)24 tiles (padded chunk rows)

Select a tile or memory bit. Its whole chunk is highlighted in both layouts; the outline marks the exact bit. Toggle the selected bit to follow its value.

Tile (9, 0) → linear bit `9` (byte 1, bit 1); raw word `1`, bit `1` (byte 8, bit 1). Chunk stride: 4 words.

#### Linear export · 48 bytes

Consecutive tiles in row-major order. Rows below show groups of 64 bits.

`bits 0``bits 64``bits 128``bits 192``bits 256``bits 320`

#### Engine raw storage · 64 bytes

Each row is one 64-bit chunk. Grey cells are padding.

`word 0``word 1``word 2``word 3``word 4``word 5``word 6``word 7`

Bit indices increase left to right here. Byte offsets describe the little-endian raw representation used by the SDK. Padding is not a playable tile; use import/export helpers rather than treating raw storage as linear.

Internally, each 8 by 8 chunk occupies a 64-bit word. For tile `(x, y)`, chunk coordinates are `(x >> 3, y >> 3)`, and the bit within the word is `(y & 7) * 8 + (x & 7)`. Bit 0 is the first tile of the chunk; each next group of eight bits is the next local row.

Logical tile to physical bit

```
word_index = (y >> 3) * chunkStride + (x >> 3)
bit_index = (y & 7) * 8 + (x & 7)
mask = 1 << bit_index
```

Physical stride includes alignment padding; edge chunks also contain bits outside the map. Do not substitute `ceil(width / 8)` for `chunkStride` or interpret raw storage as a flat width-by-height bitmap. Native raw buffers require 16-byte alignment. Use SDK size and import/export helpers instead of guessing buffer sizes. Raw transfers include chunk padding; linear transfers are a separate interchange representation.

Prefer SDK operations to preserve map bounds and padding. Shifting a set is not pathfinding around obstacles. `reachable_tiles` computes reachability; `shadow_cast` computes visibility. See their language-specific signatures in the API.

← PreviousGetting Started←→ turn pagesNext →Distance Fields