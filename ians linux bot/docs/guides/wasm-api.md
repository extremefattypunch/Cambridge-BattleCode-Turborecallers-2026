<!-- source: https://2026a.battlecode.co.uk/game/docs/wasm-api -->
Handbook/Bot API

# WASM API reference

These are the bot-facing imports registered by the runner under module `env`. Import names are case-sensitive and identical in every guest language.

Find a WASM import, record or constant

338 of 338 declarations

- - ### val host_game_settings : ptr:int32 -> int32

WASM ABI: `i32 game_settings(i32 ptr);`

Read the immutable engine tuning (timers, ranges and memory capacities). This query does not require game initialization.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — Address of a 120-byte `Game_Settings.t` record, aligned to 8 bytes. Memory: at least 120 bytes in exported linear memory; 8-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_item_info : item:int32 -> ptr:int32 -> int32

WASM ABI: `i32 item_info(i32 item, i32 ptr);`

Read an item's price, stat points, passive and automatic-combination recipe, indexed by `Item_Constants`.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param item`: `int32` — `Item_Constants` ID identifying the item to query.
- `@param ptr`: `int32` — Address of the `Game_ItemInfo.t` output. Memory: at least 40 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_consumable_info : consumable:int32 -> ptr:int32 -> int32

WASM ABI: `i32 consumable_info(i32 consumable, i32 ptr);`

Invalid consumable IDs return `e_ErrorCode_invalidAction_buyConsumable_invalidType`, leaving the output unchanged. Null outputs return `e_ErrorCode_nullptr`.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param consumable`: `int32`
- `@param ptr`: `int32` — Address of the `Game_ConsumableInfo.t` output. Memory: at least 8 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_my_team : unit -> int32

WASM ABI: `i32 my_team();`

Return this bot's fixed team: 0 for A, 1 for B.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@return`: `int32` — The team directly, not a status code.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_my_champion : unit -> int32

WASM ABI: `i32 my_champion();`

Return the physical champion handle controlled by this bot. A draft bot has no champion and receives -1 (`Abi_uint32.t` `0xffffffff`).

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@return`: `int32` — The handle directly, not a status code.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_type : unit -> int32

WASM ABI: `i32 champion_type();`

Return the controlled physical `Champion_Constants` design ID, or -1 for a draft bot. `Champion_Constants` and `ChampionDraft_Constants` have different numbering after Cassi & Issac.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@return`: `int32` — The design ID directly, not a status code.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_map_width : unit -> int32

WASM ABI: `i32 map_width();`

Return the map width in tiles.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@return`: `int32` — The width directly, not a status code.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_map_height : unit -> int32

WASM ABI: `i32 map_height();`

Return the map height in tiles.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@return`: `int32` — The height directly, not a status code.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_is_visible : x:int32 -> y:int32 -> ptr:int32 -> int32

WASM ABI: `i32 is_visible(i32 x, i32 y, i32 ptr);`

Test an in-bounds tile against individual vision; neutral always sees it.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_cbool.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_has_camp : x:int32 -> y:int32 -> ptr:int32 -> int32

WASM ABI: `i32 has_camp(i32 x, i32 y, i32 ptr);`

Test for a visible camp on a visible tile.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_cbool.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_has_champion : x:int32 -> y:int32 -> ptr:int32 -> int32

WASM ABI: `i32 has_champion(i32 x, i32 y, i32 ptr);`

Test for a visible champion on a visible tile.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_cbool.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_has_ward : x:int32 -> y:int32 -> ptr:int32 -> int32

WASM ABI: `i32 has_ward(i32 x, i32 y, i32 ptr);`

Test for a ward within the observer's effective vision.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_cbool.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_has_control_ward : x:int32 -> y:int32 -> ptr:int32 -> int32

WASM ABI: `i32 has_control_ward(i32 x, i32 y, i32 ptr);`

Test whether the tile contains a control ward known to the observer.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_cbool.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_is_alive : handle:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion_is_alive(i32 handle, i32 ptr);`

Read public champion life state without requiring vision.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_cbool.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_charges : handle:int32 -> ability:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion_charges(i32 handle, i32 ability, i32 ptr);`

Read actual charges for slot 0 or 1; hidden champions return `api_notInVision`.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ability`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_int32.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` If exported, `champion_query_memory` receives this output instead of memory (the OCaml bridge convention).

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_cooldown : handle:int32 -> ability:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion_cooldown(i32 handle, i32 ability, i32 ptr);`

Read actual cooldown for slot 0 or 1; hidden champions return `api_notInVision`. Positive cooldowns tick at the end of this champion's turn, including the casting turn.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ability`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_int32.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` If exported, `champion_query_memory` receives this output instead of memory (the OCaml bridge convention).

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_submitted_gems : ptr:int32 -> int32

WASM ABI: `i32 submitted_gems(i32 ptr);`

Read submitted gems for team A or B; neutral returns their sum.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — Address of the `Abi_uint32.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_spawn_region : team:int32 -> ptr:int32 -> int32

WASM ABI: `i32 spawn_region(i32 team, i32 ptr);`

Read the spawn region for team A or B, including during draft. Maximum bounds are exclusive.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param team`: `int32`
- `@param ptr`: `int32` — Address of the `Aabb.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_draft_current_round : ptr:int32 -> int32

WASM ABI: `i32 draft_current_round(i32 ptr);`

Read the zero-based current draft round; returns `draft_notDrafting` outside drafting.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — Address of the `Abi_uint8.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_draft_num_rounds : ptr:int32 -> int32

WASM ABI: `i32 draft_num_rounds(i32 ptr);`

Read the map's number of draft rounds, available as soon as the map is loaded.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — Address of the `Abi_uint8.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_draft_champion : champion:int32 -> int32

WASM ABI: `i32 draft_champion(i32 champion);`

Submit a `ChampionDraft_Constants` choice for this team's current draft round. Only the scheduled draft instance may pick. This takes a draft choice ID, not a physical `Champion_Constants` type or champion handle; selecting Cassi & Issac once creates two bodies.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param champion`: `int32`
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_draft_get : of_team:int32 -> round:int32 -> ptr:int32 -> int32

WASM ABI: `i32 draft_get(i32 of_team, i32 round, i32 ptr);`

Read a completed draft round. Pending and unsubmitted picks return `draft_unavailable`.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param of_team`: `int32`
- `@param round`: `int32`
- `@param ptr`: `int32` — Address of the `ChampionDraft_Constants` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_camp_state : handle:int32 -> ptr:int32 -> int32

WASM ABI: `i32 camp_state(i32 handle, i32 ptr);`

Query life/wake state. The current tile (last occupied tile when dead) must be in vision. Observer queries bypass vision. Invalid/hidden queries leave the output unchanged.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ptr`: `int32` — Address of the `Game_CampState_Constants` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_camp_group_state : group:int32 -> ptr:int32 -> int32

WASM ABI: `i32 camp_group_state(i32 group, i32 ptr);`

Any original spawn tile in the champion's effective vision reveals the group. A positive observed timer persists outside vision until due, then becomes unknown. Neutral perspective returns authoritative state. On success, writes `e_Game_CampGroupState_unknown`, `e_Game_CampGroupState_hasCamps`, `e_Game_CampGroupState_waitingForRewardClaim` or `e_Game_CampGroupState_waitingToRespawn` to `out_campState`. The return value is an `ErrorCode`; the output is unchanged on failure.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param group`: `int32`
- `@param ptr`: `int32` — Address of the `Game_CampGroupState_Constants` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_camp_group_capture_state : group:int32 -> ptr:int32 -> int32

WASM ABI: `i32 camp_group_capture_state(i32 group, i32 ptr);`

Read capture progress when any camp spawn tile in the group is visible; otherwise `api_notInVision`. Capturing/contesting champions need not themselves be visible. State is relative to the perspective team. Capturing states return the actual remaining timer (including Capture emblem reductions). Other states return the configured maximum capture time, currently 5. A free reward with no active countdown is `captureAvailable`; living/respawning groups are `noCaptureAvailable`.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param group`: `int32`
- `@param ptr`: `int32` — Address of an 8-byte `Game_CampGroup_CaptureState.t` record, aligned to 4 bytes. `Abi_int32.t` timer is at byte 0; `Abi_int32.t` state is at byte 4 (0 no capture available, 1 ally capturing, 2 contested, 3 enemy capturing, 4 capture available).
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_camp_group_cooldown : group:int32 -> ptr:int32 -> int32

WASM ABI: `i32 camp_group_cooldown(i32 group, i32 ptr);`

Read future camp-respawn phases until due; zero means visibly blocked. Returns `api_campGroupNotWaitingToRespawn` unless the observed state is `waitingToRespawn`.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param group`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_int32.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_map_num_camp_groups : ptr:int32 -> int32

WASM ABI: `i32 map_num_camp_groups(i32 ptr);`

Return the number of runtime camp groups, including mirrored groups.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — Address of the `Abi_uint32.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_map_camp_group_num_camps : group:int32 -> ptr:int32 -> int32

WASM ABI: `i32 map_camp_group_num_camps(i32 group, i32 ptr);`

Return the number of spawn tiles in this runtime group.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param group`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_uint32.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_camp_num_buffs : handle:int32 -> ptr:int32 -> int32

WASM ABI: `i32 camp_num_buffs(i32 handle, i32 ptr);`

Count active buffs on a visible camp.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_uint32.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_num_buffs : handle:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion_num_buffs(i32 handle, i32 ptr);`

Count active buffs on a visible champion.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_uint32.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_num_allies : ptr:int32 -> int32

WASM ABI: `i32 num_allies(i32 ptr);`

Count the public roster, including dead champions and additional Cassi & Issac bodies.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — Address of the `Abi_uint32.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_num_enemies : ptr:int32 -> int32

WASM ABI: `i32 num_enemies(i32 ptr);`

Count the public roster, including dead champions and additional Cassi & Issac bodies.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — Address of the `Abi_uint32.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_map_camp_group : handle:int32 -> ptr:int32 -> int32

WASM ABI: `i32 map_camp_group(i32 handle, i32 ptr);`

Read the public capture rewards for this runtime group.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ptr`: `int32` — Address of the `Game_CampGroup.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_map_camp_info : handle:int32 -> ptr:int32 -> int32

WASM ABI: `i32 map_camp_info(i32 handle, i32 ptr);`

Read a public spawn position and camp design, regardless of whether the camp is alive.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ptr`: `int32` — Address of the `Game_CampInfo.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_map_camp_layout : ptr:int32 -> capacity:int32 -> count:int32 -> int32

WASM ABI: `i32 map_camp_layout(i32 ptr, i32 capacity, i32 count);`

Read the complete static camp layout as `Abi_uint32.t` words. For each group: group ID, gold reward, gem reward, maximum respawn rounds, camp count; then for each camp: camp ID, `Camp_Constants` design ID, x, y. Groups are concatenated with no leading group count.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — Array of `Abi_uint32.t` words, aligned to 4 bytes.
- `@param capacity`: `int32` — Maximum number of words to copy. A short buffer receives a prefix.
- `@param count`: `int32` — Address of the `Abi_uint32.t` total word count, even when truncated. Capacity zero queries this total.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_map_camp_group_of : handle:int32 -> ptr:int32 -> int32

WASM ABI: `i32 map_camp_group_of(i32 handle, i32 ptr);`

Read the camp group a camp spawn belongs to.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ptr`: `int32` — Address of the `Handle_CampGroup.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_map_camp_at : x:int32 -> y:int32 -> ptr:int32 -> int32

WASM ABI: `i32 map_camp_at(i32 x, i32 y, i32 ptr);`

Find the camp that spawns on a tile, regardless of vision or whether the camp is alive.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param ptr`: `int32` — Address of the `Handle_CampInfo.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_camp_at : x:int32 -> y:int32 -> ptr:int32 -> int32

WASM ABI: `i32 camp_at(i32 x, i32 y, i32 ptr);`

Find the lowest visible camp handle on a visible tile; error if absent.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param ptr`: `int32` — Address of the `Handle_Camp.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_camp : handle:int32 -> ptr:int32 -> int32

WASM ABI: `i32 camp(i32 handle, i32 ptr);`

Read current camp state; hidden entities return `api_notInVision`.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ptr`: `int32` — Address of the `Game_Camp.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_at : x:int32 -> y:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion_at(i32 x, i32 y, i32 ptr);`

Find the lowest visible champion handle on a visible tile; error if absent.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param ptr`: `int32` — Address of the `Handle_Champion.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion : handle:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion(i32 handle, i32 ptr);`

Read current champion state; hidden entities return `api_notInVision`.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ptr`: `int32` — Address of the `Game_Champion.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_identity : handle:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion_identity(i32 handle, i32 ptr);`

Read a champion's immutable team and type; no vision restriction, including dead champions.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ptr`: `int32` — Address of the `Game_ChampionIdentity.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_ward_at : x:int32 -> y:int32 -> ptr:int32 -> int32

WASM ABI: `i32 ward_at(i32 x, i32 y, i32 ptr);`

Read a visible ordinary ward handle at (x, y), considering both teams. If both teams have a ward there, return the smaller packed handle. No visible ward returns `api_notFound`.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param ptr`: `int32` — Address of a `Abi_uint32.t` `Handle_Ward.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_ally_ward_at : x:int32 -> y:int32 -> ptr:int32 -> int32

WASM ABI: `i32 ally_ward_at(i32 x, i32 y, i32 ptr);`

Find the visible ally ward at a tile; error if absent. Neutral observers include both teams.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param ptr`: `int32` — Address of the `Handle_Ward.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_enemy_ward_at : x:int32 -> y:int32 -> ptr:int32 -> int32

WASM ABI: `i32 enemy_ward_at(i32 x, i32 y, i32 ptr);`

Find the visible enemy ward at a tile; error if absent. Neutral observers include both teams.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param ptr`: `int32` — Address of the `Handle_Ward.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_ward : handle:int32 -> ptr:int32 -> int32

WASM ABI: `i32 ward(i32 handle, i32 ptr);`

Read current ward state; hidden entities return `api_notInVision`. Both allied and enemy wards require effective vision. Ward vision is owner-only.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ptr`: `int32` — Address of the `Game_Ward.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_control_ward_at : x:int32 -> y:int32 -> ptr:int32 -> int32

WASM ABI: `i32 control_ward_at(i32 x, i32 y, i32 ptr);`

Read a visible control ward handle at (x, y), considering both teams. If both teams have one there, return the smaller packed handle. No visible control ward returns `api_notFound`.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param ptr`: `int32` — Address of a `Abi_uint32.t` `Handle_ControlWard.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_ally_control_ward_at : x:int32 -> y:int32 -> ptr:int32 -> int32

WASM ABI: `i32 ally_control_ward_at(i32 x, i32 y, i32 ptr);`

Find the visible ally control ward at a tile; error if absent. Neutral observers include both teams.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param ptr`: `int32` — Address of the `Handle_ControlWard.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_enemy_control_ward_at : x:int32 -> y:int32 -> ptr:int32 -> int32

WASM ABI: `i32 enemy_control_ward_at(i32 x, i32 y, i32 ptr);`

Find the visible enemy control ward at a tile; error if absent. Neutral observers include both teams.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param ptr`: `int32` — Address of the `Handle_ControlWard.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_control_ward : handle:int32 -> ptr:int32 -> int32

WASM ABI: `i32 control_ward(i32 handle, i32 ptr);`

Read a control ward by handle, subject to placement visibility.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ptr`: `int32` — Address of the `Game_ControlWard.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_gold : handle:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion_gold(i32 handle, i32 ptr);`

Read team gold regardless of visibility; enemies return `api_notTeammate`.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_uint32.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` If exported, `champion_query_memory` receives this output instead of memory (the OCaml bridge convention).

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_gems : handle:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion_gems(i32 handle, i32 ptr);`

Read carried gems for self or a visible champion; otherwise `api_notInVision`.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_uint32.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` If exported, `champion_query_memory` receives this output instead of memory (the OCaml bridge convention).

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_items : handle:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion_items(i32 handle, i32 ptr);`

Write `e_Item_numTypes` item counts for yourself or another visible champion. `in_size` is the capacity in `Abi_uint32.t` entries, not bytes. Returns `api_bufferTooSmall` without writing if insufficient.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ptr`: `int32` — Array of exactly 84 `Abi_uint32.t` counts (336 bytes), indexed by `Item_Constants`. This is an array of counts, not item IDs.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_consumables : handle:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion_consumables(i32 handle, i32 ptr);`

Write `e_Game_Consumable_numTypes` consumable counts for yourself or another visible champion. `in_size` is the capacity in `Abi_uint32.t` entries, not bytes. Returns `api_bufferTooSmall` without writing if insufficient.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ptr`: `int32` — Array of exactly 4 `Abi_uint32.t` counts (16 bytes), indexed by `Game_Consumable_Constants`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_respawn_timer : handle:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion_respawn_timer(i32 handle, i32 ptr);`

Read the public respawn countdown; living champions return `api_championAlive`.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_int32.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_can_sell : handle:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion_can_sell(i32 handle, i32 ptr);`

Sale eligibility: Tavi on her own spawn tiles, subject to shopping restrictions/channels. Independent of inventory, gold, turn ownership and previous sales. Output is unchanged on failure.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_cbool.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_champion_channel_time : handle:int32 -> ptr:int32 -> int32

WASM ABI: `i32 bc_champion_channel_time(i32 handle, i32 ptr);`

Read the remaining turns of a visible champion's recall, gem submission or teleport channel. Flashing reports zero; a champion that is not channeling fails with `invalidAction_cancelChannel_notChanneling`.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_int32.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_camp_group_max_respawn : group:int32 -> ptr:int32 -> int32

WASM ABI: `i32 bc_camp_group_max_respawn(i32 group, i32 ptr);`

Read the longest configured respawn duration among this runtime group's camps.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param group`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_int32.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_champion_ward_positions : handle:int32 -> ptr:int32 -> capacity:int32 -> count:int32 -> int32

WASM ABI: `i32 bc_champion_ward_positions(i32 handle, i32 ptr, i32 capacity, i32 count);`

List a champion's placed ward positions. Private to the owner and the neutral observer; zero size counts.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ptr`: `int32` — Address of an output array of `Game_Position.t` records.
- `@param capacity`: `int32` — Maximum number of records, not bytes. Zero queries the required count. A nonzero buffer must hold every result or the call fails with `api_bufferTooSmall`.
- `@param count`: `int32` — Address of the `Abi_uint32.t` count output; read it on success.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_map_camp_groups : ptr:int32 -> capacity:int32 -> count:int32 -> int32

WASM ABI: `i32 map_camp_groups(i32 ptr, i32 capacity, i32 count);`

Write at most `in_size` group IDs and return the number written.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — Address of an output array of `Handle_CampGroup.t` records.
- `@param capacity`: `int32` — Maximum number of elements, not bytes. The list truncates to this capacity; zero writes no elements and reports zero. Use `map_num_camp_groups` to size the allocation.
- `@param count`: `int32` — Address of the `Abi_uint32.t` number of elements written.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_map_camp_group_camps : group:int32 -> ptr:int32 -> capacity:int32 -> count:int32 -> int32

WASM ABI: `i32 map_camp_group_camps(i32 group, i32 ptr, i32 capacity, i32 count);`

Write at most `in_size` camp spawn IDs and return the number written.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param group`: `int32`
- `@param ptr`: `int32` — Address of an output array of `Handle_CampInfo.t` records.
- `@param capacity`: `int32` — Maximum number of elements, not bytes. The list truncates to this capacity; zero writes no elements and reports zero. Use `map_camp_group_num_camps` to size the allocation.
- `@param count`: `int32` — Address of the `Abi_uint32.t` number of elements written.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_camp_buffs : handle:int32 -> ptr:int32 -> capacity:int32 -> count:int32 -> int32

WASM ABI: `i32 camp_buffs(i32 handle, i32 ptr, i32 capacity, i32 count);`

Write at most `in_size` active buffs and return the number written.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ptr`: `int32` — Address of an output array of `Game_Buff.t` records.
- `@param capacity`: `int32` — Maximum number of elements, not bytes. The list truncates to this capacity; zero writes no elements and reports zero. Use `camp_num_buffs` to size the allocation.
- `@param count`: `int32` — Address of the `Abi_uint32.t` number of elements written.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_buffs : handle:int32 -> ptr:int32 -> capacity:int32 -> count:int32 -> int32

WASM ABI: `i32 champion_buffs(i32 handle, i32 ptr, i32 capacity, i32 count);`

Write at most `in_size` active buffs and return the number written.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ptr`: `int32` — Address of an output array of `Game_Buff.t` records.
- `@param capacity`: `int32` — Maximum number of elements, not bytes. The list truncates to this capacity; zero writes no elements and reports zero. Use `champion_num_buffs` to size the allocation.
- `@param count`: `int32` — Address of the `Abi_uint32.t` number of elements written.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_allies : ptr:int32 -> capacity:int32 -> count:int32 -> int32

WASM ABI: `i32 allies(i32 ptr, i32 capacity, i32 count);`

Write at most `in_size` public roster IDs, including dead champions and Cassi & Issac bodies; neutral lists both teams.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — Address of an output array of `Handle_Champion.t` records.
- `@param capacity`: `int32` — Maximum number of elements, not bytes. The list truncates to this capacity; zero writes no elements and reports zero. Use `num_allies` to size the allocation.
- `@param count`: `int32` — Address of the `Abi_uint32.t` number of elements written.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_enemies : ptr:int32 -> capacity:int32 -> count:int32 -> int32

WASM ABI: `i32 enemies(i32 ptr, i32 capacity, i32 count);`

Write at most `in_size` public roster IDs, including dead champions and Cassi & Issac bodies; neutral lists both teams.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — Address of an output array of `Handle_Champion.t` records.
- `@param capacity`: `int32` — Maximum number of elements, not bytes. The list truncates to this capacity; zero writes no elements and reports zero. Use `num_enemies` to size the allocation.
- `@param count`: `int32` — Address of the `Abi_uint32.t` number of elements written.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_wards : ptr:int32 -> capacity:int32 -> count:int32 -> int32

WASM ABI: `i32 wards(i32 ptr, i32 capacity, i32 count);`

List visible ordinary wards.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — Address of an output array of `Game_Ward.t` records.
- `@param capacity`: `int32` — Maximum number of records, not bytes. Zero queries the required count. A nonzero buffer must hold every result or the call fails with `api_bufferTooSmall`.
- `@param count`: `int32` — Address of the `Abi_uint32.t` count output; read it on success.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_control_wards : ptr:int32 -> capacity:int32 -> count:int32 -> int32

WASM ABI: `i32 control_wards(i32 ptr, i32 capacity, i32 count);`

List visible control wards.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — Address of an output array of `Game_ControlWard.t` records.
- `@param capacity`: `int32` — Maximum number of records, not bytes. Zero queries the required count. A nonzero buffer must hold every result or the call fails with `api_bufferTooSmall`.
- `@param count`: `int32` — Address of the `Abi_uint32.t` count output; read it on success.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bitboard_test : handle:int64 -> x:int32 -> y:int32 -> ptr:int32 -> int32

WASM ABI: `i32 bitboard_test(i64 handle, i32 x, i32 y, i32 ptr);`

Test a logical bit in a caller-owned bitboard.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int64` — A guest bitboard address widened to `i64`, not an opaque host handle. It must fit a positive `i32`, be aligned to 16 bytes, and span `board_bytes` bytes. Storage: `BitboardBuffer.t`.
- `@param x`: `int32`
- `@param y`: `int32`
- `@param ptr`: `int32` — Address of an `Abi_int32.t` boolean (0 or 1). Storage: `Abi_cbool.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bitboard_num_set_bits : handle:int64 -> ptr:int32 -> int32

WASM ABI: `i32 bitboard_num_set_bits(i64 handle, i32 ptr);`

Count set logical tiles, ignoring padding.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int64` — A guest bitboard address widened to `i64`, not an opaque host handle. It must fit a positive `i32`, be aligned to 16 bytes, and span `board_bytes` bytes. Storage: `BitboardBuffer.t`.
- `@param ptr`: `int32` — Address of a `Abi_uint32.t` count.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bitboard_get_set_bits : handle:int64 -> ptr:int32 -> capacity:int32 -> count:int32 -> int32

WASM ABI: `i32 bitboard_get_set_bits(i64 handle, i32 ptr, i32 capacity, i32 count);`

List set tiles as `Game_Position.t` (x, y) pairs, up to capacity.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int64` — A guest bitboard address widened to `i64`, not an opaque host handle. It must fit a positive `i32`, be aligned to 16 bytes, and span `board_bytes` bytes. Storage: `BitboardBuffer.t`.
- `@param ptr`: `int32` — Array of `Game_Position.t` records.
- `@param capacity`: `int32` — Maximum number of elements, not bytes. The list truncates to this capacity; zero writes no elements and reports zero. Use `bitboard_num_set_bits` to size the allocation.
- `@param count`: `int32` — Address of the `Abi_uint32.t` number of elements written.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bitboard_num_chunks : ptr:int32 -> int32

WASM ABI: `i32 bitboard_num_chunks(i32 ptr);`

Read the raw bitboard word count, including padded chunks: `chunk_stride` * `chunked_height`.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — Address of a `Abi_uint32.t` count.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bitboard_copy_to_guest : handle:int64 -> ptr:int32 -> capacity:int32 -> count:int32 -> int32

WASM ABI: `i32 bitboard_copy_to_guest(i64 handle, i32 ptr, i32 capacity, i32 count);`

Copy up to capacity `Abi_uint64.t` words from the raw bitboard, including padding.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int64` — A guest bitboard address widened to `i64`, not an opaque host handle. It must fit a positive `i32`, be aligned to 16 bytes, and span `board_bytes` bytes. Storage: `BitboardBuffer.t`.
- `@param ptr`: `int32` — Array of `Abi_uint64.t` words, aligned to 8 bytes.
- `@param capacity`: `int32` — Maximum number of elements, not bytes. The list truncates to this capacity; zero writes no elements and reports zero. Use `bitboard_num_chunks` to size the allocation.
- `@param count`: `int32` — Address of the `Abi_uint32.t` number of elements written.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_map_bushes : handle:int64 -> int32

WASM ABI: `i32 map_bushes(i64 handle);`

Copy immutable bush tiles into a caller-owned bitboard; available before initialization.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int64` — A guest bitboard address widened to `i64`, not an opaque host handle. It must fit a positive `i32`, be aligned to 16 bytes, and span `board_bytes` bytes. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_map_walls : handle:int64 -> int32

WASM ABI: `i32 map_walls(i64 handle);`

Copy immutable wall tiles into a caller-owned bitboard; available before initialization.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int64` — A guest bitboard address widened to `i64`, not an opaque host handle. It must fit a positive `i32`, be aligned to 16 bytes, and span `board_bytes` bytes. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_map_altars : handle:int64 -> int32

WASM ABI: `i32 map_altars(i64 handle);`

Copy immutable altar tiles into a caller-owned bitboard; available before initialization.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int64` — A guest bitboard address widened to `i64`, not an opaque host handle. It must fit a positive `i32`, be aligned to 16 bytes, and span `board_bytes` bytes. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_map_holes : handle:int64 -> int32

WASM ABI: `i32 map_holes(i64 handle);`

Copy immutable hole tiles into a caller-owned bitboard; available before initialization.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int64` — A guest bitboard address widened to `i64`, not an opaque host handle. It must fit a positive `i32`, be aligned to 16 bytes, and span `board_bytes` bytes. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_vision_mask : champion:int32 -> x:int32 -> y:int32 -> handle:int64 -> int32

WASM ABI: `i32 vision_mask(i32 champion, i32 x, i32 y, i64 handle);`

Compute a champion design's vision at a hypothetical tile, including bush and wall occlusion.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param champion`: `int32`
- `@param x`: `int32`
- `@param y`: `int32`
- `@param handle`: `int64` — A guest bitboard address widened to `i64`, not an opaque host handle. It must fit a positive `i32`, be aligned to 16 bytes, and span `board_bytes` bytes. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_ward_vision_mask : x:int32 -> y:int32 -> handle:int64 -> int32

WASM ABI: `i32 ward_vision_mask(i32 x, i32 y, i64 handle);`

Compute a ward's vision at a hypothetical tile.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param handle`: `int64` — A guest bitboard address widened to `i64`, not an opaque host handle. It must fit a positive `i32`, be aligned to 16 bytes, and span `board_bytes` bytes. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_control_ward_vision_mask : x:int32 -> y:int32 -> handle:int64 -> int32

WASM ABI: `i32 control_ward_vision_mask(i32 x, i32 y, i64 handle);`

Write the vision mask of a control ward owned by the observer.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param handle`: `int64` — A guest bitboard address widened to `i64`, not an opaque host handle. It must fit a positive `i32`, be aligned to 16 bytes, and span `board_bytes` bytes. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_vision : handle:int64 -> int32

WASM ABI: `i32 vision(i64 handle);`

Copy current individual vision, including owned wards and tile reveals; neutral fills the output with ones.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int64` — A guest bitboard address widened to `i64`, not an opaque host handle. It must fit a positive `i32`, be aligned to 16 bytes, and span `board_bytes` bytes. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_camp_occupancy : handle:int64 -> int32

WASM ABI: `i32 camp_occupancy(i64 handle);`

Copy visible camp occupancy; neutral includes all teams without visibility filtering.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int64` — A guest bitboard address widened to `i64`, not an opaque host handle. It must fit a positive `i32`, be aligned to 16 bytes, and span `board_bytes` bytes. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_awake_camp_occupancy : handle:int64 -> int32

WASM ABI: `i32 awake_camp_occupancy(i64 handle);`

Like `Game_API_GetCampOccupancy`, but includes only awake camps. Dead camps are excluded.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int64` — A guest bitboard address widened to `i64`, not an opaque host handle. It must fit a positive `i32`, be aligned to 16 bytes, and span `board_bytes` bytes. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_asleep_camp_occupancy : handle:int64 -> int32

WASM ABI: `i32 asleep_camp_occupancy(i64 handle);`

Like `Game_API_GetCampOccupancy`, but includes only asleep camps. Dead camps are excluded.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int64` — A guest bitboard address widened to `i64`, not an opaque host handle. It must fit a positive `i32`, be aligned to 16 bytes, and span `board_bytes` bytes. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_ally_occupancy : handle:int64 -> int32

WASM ABI: `i32 ally_occupancy(i64 handle);`

Copy visible ally occupancy; neutral includes all teams without visibility filtering.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int64` — A guest bitboard address widened to `i64`, not an opaque host handle. It must fit a positive `i32`, be aligned to 16 bytes, and span `board_bytes` bytes. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_enemy_occupancy : handle:int64 -> int32

WASM ABI: `i32 enemy_occupancy(i64 handle);`

Copy visible enemy occupancy; neutral includes all teams without visibility filtering.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int64` — A guest bitboard address widened to `i64`, not an opaque host handle. It must fit a positive `i32`, be aligned to 16 bytes, and span `board_bytes` bytes. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_ally_ward_occupancy : handle:int64 -> int32

WASM ABI: `i32 ally_ward_occupancy(i64 handle);`

Copy allied ward placements in effective vision; neutral includes both teams.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int64` — A guest bitboard address widened to `i64`, not an opaque host handle. It must fit a positive `i32`, be aligned to 16 bytes, and span `board_bytes` bytes. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_ally_control_ward_occupancy : handle:int64 -> int32

WASM ABI: `i32 ally_control_ward_occupancy(i64 handle);`

Write allied control-ward placements within the observer's effective vision.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int64` — A guest bitboard address widened to `i64`, not an opaque host handle. It must fit a positive `i32`, be aligned to 16 bytes, and span `board_bytes` bytes. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_enemy_ward_occupancy : handle:int64 -> int32

WASM ABI: `i32 enemy_ward_occupancy(i64 handle);`

Copy enemy ward occupancy in individual effective vision. Neutral includes all teams without visibility filtering.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int64` — A guest bitboard address widened to `i64`, not an opaque host handle. It must fit a positive `i32`, be aligned to 16 bytes, and span `board_bytes` bytes. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_enemy_control_ward_occupancy : handle:int64 -> int32

WASM ABI: `i32 enemy_control_ward_occupancy(i64 handle);`

Write enemy control-ward placements within the observer's effective vision.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int64` — A guest bitboard address widened to `i64`, not an opaque host handle. It must fit a positive `i32`, be aligned to 16 bytes, and span `board_bytes` bytes. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_teleport_occupancy : handle:int64 -> int32

WASM ABI: `i32 teleport_occupancy(i64 handle);`

Write visible teleport reservations, always including the observer's own destination.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int64` — A guest bitboard address widened to `i64`, not an opaque host handle. It must fit a positive `i32`, be aligned to 16 bytes, and span `board_bytes` bytes. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_is_occupied_by_teleport : x:int32 -> y:int32 -> ptr:int32 -> int32

WASM ABI: `i32 is_occupied_by_teleport(i32 x, i32 y, i32 ptr);`

Reservations are visible in effective vision; the caster always knows their own destination.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_cbool.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_altar_lock : x:int32 -> y:int32 -> lock_team:int32 -> ptr:int32 -> int32

WASM ABI: `i32 altar_lock(i32 x, i32 y, i32 lock_team, i32 ptr);`

Read one team's lock on a visible altar tile.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param lock_team`: `int32`
- `@param ptr`: `int32` — Address of the `Game_AltarLock.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_altar_locks : ptr:int32 -> capacity:int32 -> count:int32 -> int32

WASM ABI: `i32 altar_locks(i32 ptr, i32 capacity, i32 count);`

List visible altar locks from both teams, including their entity handles, positions and remaining hits.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — Array of `Game_AltarLock.t` records.
- `@param capacity`: `int32` — Maximum number of records, not bytes. Zero queries the required count. A nonzero buffer must hold every result or the call fails with `api_bufferTooSmall`.
- `@param count`: `int32` — Address of the `Abi_uint32.t` count output; read it on success.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_teleports : ptr:int32 -> capacity:int32 -> count:int32 -> int32

WASM ABI: `i32 teleports(i32 ptr, i32 capacity, i32 count);`

List visible teleport reservations, including the observer's own channel.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — Address of an output array of `Game_Teleport.t` records.
- `@param capacity`: `int32` — Maximum number of records, not bytes. Zero queries the required count. A nonzero buffer must hold every result or the call fails with `api_bufferTooSmall`.
- `@param count`: `int32` — Address of the `Abi_uint32.t` count output; read it on success.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_teleport_at : x:int32 -> y:int32 -> ptr:int32 -> int32

WASM ABI: `i32 teleport_at(i32 x, i32 y, i32 ptr);`

Read the visible teleport reservation on a tile, including the observer's own channel.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param ptr`: `int32` — Address of the `Game_Teleport.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` If exported, `champion_query_memory` receives this output instead of memory (the OCaml bridge convention).

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_teleport : champion:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion_teleport(i32 champion, i32 ptr);`

The caster's own channel, independent of destination visibility.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param champion`: `int32`
- `@param ptr`: `int32` — Address of the `Game_Teleport.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_shared_memory_size : ptr:int32 -> int32

WASM ABI: `i32 shared_memory_size(i32 ptr);`

Configured capacity of each team's persistent memory buffers, in bytes.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — Address of the `Abi_uint32.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_draft_memory_size : ptr:int32 -> int32

WASM ABI: `i32 draft_memory_size(i32 ptr);`

Return the configured draft-memory capacity per team, in bytes.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — Address of the `Abi_uint32.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_design : kind:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion_design(i32 kind, i32 ptr);`

Copy immutable type designs. Valid before draft/game initialization; no team visibility restriction. Failure leaves the output unchanged. `Champion_Constants` uses physical body types, not draft choices.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param kind`: `int32`
- `@param ptr`: `int32` — Address of the `Game_ChampionDesign.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_camp_design : kind:int32 -> ptr:int32 -> int32

WASM ABI: `i32 camp_design(i32 kind, i32 ptr);`

Copy the immutable camp design without requiring vision or a completed draft.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param kind`: `int32`
- `@param ptr`: `int32` — Address of the `Game_CampDesign.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_restrictions : champion:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion_restrictions(i32 champion, i32 ptr);`

Union of `e_BuffRestriction_`* flags from active buffs. Uses the same visibility rules as `GetBuffs`. Death and channel state are not included. Output is unchanged on failure.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param champion`: `int32`
- `@param ptr`: `int32` — Address of the `BuffRestriction_Constants` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_can_shop : champion:int32 -> consumable:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion_can_shop(i32 champion, i32 consumable, i32 ptr);`

Shopping location/passive eligibility, including dead champions and active restrictions/channels.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param champion`: `int32`
- `@param consumable`: `int32` — Zero tests item shopping; nonzero tests consumable shopping.
- `@param ptr`: `int32` — Address of the `Abi_cbool.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_wards : champion:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion_wards(i32 champion, i32 ptr);`

Ward resources are private to the owning champion and the neutral observer. This query works while dead. Other champions receive `api_notOwner`, even with vision.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param champion`: `int32`
- `@param ptr`: `int32` — Address of the `Game_TrinketState.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_ability_damage : champion:int32 -> slot:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion_ability_damage(i32 champion, i32 slot, i32 ptr);`

Query the ability slot's damage amount without performing an action. The amount is written as `Abi_float32.t`; vision and ability-type checks still apply.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param champion`: `int32`
- `@param slot`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_float32.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_ability_damage_against : champion:int32 -> slot:int32 -> target:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion_ability_damage_against(i32 champion, i32 slot, i32 target, i32 ptr);`

Query the ability slot's damage amount without performing an action, accounting for the target champion. The amount is written as `Abi_float32.t`; vision and ability-type checks still apply.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param champion`: `int32`
- `@param slot`: `int32`
- `@param target`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_float32.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_ability_heal : champion:int32 -> slot:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion_ability_heal(i32 champion, i32 slot, i32 ptr);`

Query the ability slot's heal amount without performing an action. The amount is written as `Abi_float32.t`; vision and ability-type checks still apply.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param champion`: `int32`
- `@param slot`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_float32.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_ability_heal_against : champion:int32 -> slot:int32 -> target:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion_ability_heal_against(i32 champion, i32 slot, i32 target, i32 ptr);`

Query the ability slot's heal amount without performing an action, accounting for the target champion. The amount is written as `Abi_float32.t`; vision and ability-type checks still apply.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param champion`: `int32`
- `@param slot`: `int32`
- `@param target`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_float32.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_ability_shield : champion:int32 -> slot:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion_ability_shield(i32 champion, i32 slot, i32 ptr);`

Query the ability slot's shield amount without performing an action. The amount is written as `Abi_float32.t`; vision and ability-type checks still apply.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param champion`: `int32`
- `@param slot`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_float32.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_ability_shield_against : champion:int32 -> slot:int32 -> target:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion_ability_shield_against(i32 champion, i32 slot, i32 target, i32 ptr);`

Query the ability slot's shield amount without performing an action, accounting for the target champion. The amount is written as `Abi_float32.t`; vision and ability-type checks still apply.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param champion`: `int32`
- `@param slot`: `int32`
- `@param target`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_float32.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_ability_props : champion:int32 -> slot:int32 -> ptr:int32 -> int32

WASM ABI: `i32 champion_ability_props(i32 champion, i32 slot, i32 ptr);`

Read slot configuration for a champion; no vision restriction, since the design never changes.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param champion`: `int32`
- `@param slot`: `int32`
- `@param ptr`: `int32` — Address of the `Game_AbilityProps.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_camp_ability_props : camp:int32 -> slot:int32 -> ptr:int32 -> int32

WASM ABI: `i32 camp_ability_props(i32 camp, i32 slot, i32 ptr);`

Read the selected ability design of a camp; no vision restriction.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param camp`: `int32`
- `@param slot`: `int32`
- `@param ptr`: `int32` — Address of the `Game_AbilityProps.t` output.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_read_shared_memory : offset:int32 -> ptr:int32 -> size:int32 -> int32

WASM ABI: `i32 read_shared_memory(i32 offset, i32 ptr, i32 size);`

`Team_Constants` communication buffers are unrecorded and require the owning team's live turn. Shared memory is writable during draft and gameplay. Draft memory freezes after the final pick. Ranges must fit the configured capacity. Nonempty operations require a buffer of at least `in_size` bytes. A zero-length operation permits a null pointer and an offset at the end of the buffer.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param offset`: `int32`
- `@param ptr`: `int32` — Destination byte buffer; copy size bytes from team memory at byte offset offset. Storage: `Abi_uint8.t`.
- `@param size`: `int32`
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_write_shared_memory : offset:int32 -> ptr:int32 -> size:int32 -> int32

WASM ABI: `i32 write_shared_memory(i32 offset, i32 ptr, i32 size);`

Write a team-memory buffer without recording a gameplay action.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param offset`: `int32`
- `@param ptr`: `int32` — Source byte buffer; copy size bytes into team memory at byte offset offset. Storage: `Abi_uint8.t`.
- `@param size`: `int32`
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_read_draft_memory : offset:int32 -> ptr:int32 -> size:int32 -> int32

WASM ABI: `i32 read_draft_memory(i32 offset, i32 ptr, i32 size);`

Read draft memory without recording a gameplay action.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param offset`: `int32`
- `@param ptr`: `int32` — Destination byte buffer; copy size bytes from team memory at byte offset offset. Storage: `Abi_uint8.t`.
- `@param size`: `int32`
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_write_draft_memory : offset:int32 -> ptr:int32 -> size:int32 -> int32

WASM ABI: `i32 write_draft_memory(i32 offset, i32 ptr, i32 size);`

Write draft memory during the team's draft input; reject writes during gameplay.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param offset`: `int32`
- `@param ptr`: `int32` — Source byte buffer; copy size bytes into team memory at byte offset offset. Storage: `Abi_uint8.t`.
- `@param size`: `int32`
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_debug_dot : x:int32 -> y:int32 -> rgb:int32 -> int32

WASM ABI: `i32 debug_dot(i32 x, i32 y, i32 rgb);`

Draw a debug dot on the current turn's replay overlay. Coordinates must be within the map and 0..255; `rgb` is 0xRRGGBB (0..`0xffffff`). Requires an active logged turn.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param rgb`: `int32`
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_debug_line : x0:int32 -> y0:int32 -> x1:int32 -> y1:int32 -> rgb:int32 -> int32

WASM ABI: `i32 debug_line(i32 x0, i32 y0, i32 x1, i32 y1, i32 rgb);`

Draw a debug line between two tiles on the current turn's replay overlay. Both endpoints must be within the map and 0..255; `rgb` is 0xRRGGBB. Requires an active logged turn.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x0`: `int32`
- `@param y0`: `int32`
- `@param x1`: `int32`
- `@param y1`: `int32`
- `@param rgb`: `int32`
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_movement_mask : champion:int32 -> handle:int64 -> int32

WASM ABI: `i32 champion_movement_mask(i32 champion, i64 handle);`

Replace the output with legal movement destinations from this champion's perspective. Hidden occupants remain valid destinations; the query never consumes actions.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param champion`: `int32`
- `@param handle`: `int64` — A guest bitboard address widened to `i64`, not an opaque host handle. It must fit a positive `i32`, be aligned to 16 bytes, and span `board_bytes` bytes. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_move_to_with_result : x:int32 -> y:int32 -> ptr:int32 -> int32

WASM ABI: `i32 move_to_with_result(i32 x, i32 y, i32 ptr);`

`Champion_Constants` actions require explicit cancellation of an active recall or gem submission. Priority updates and cancellation remain available while channelling. These destination actions require `out_successful`. Successful actions set it to `ENGINE_TRUE`. A hidden blocked destination reveals the tile, spends nothing, and returns success with `ENGINE_FALSE`. Known blocked destinations and other invalid actions return their error code with `ENGINE_FALSE`.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param ptr`: `int32` — Address of an `Abi_int32.t` successful flag: 1 when completed, 0 when an unseen blocker was revealed. A 0 flag with status 0 is a committed action; do not interpret it as an engine error. Storage: `Abi_cbool.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` If exported, `champion_query_memory` receives this output instead of memory (the OCaml bridge convention).

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_cast_with_result : slot:int32 -> kind:int32 -> index:int32 -> x:int32 -> y:int32 -> ptr:int32 -> int32

WASM ABI: `i32 cast_with_result(i32 slot, i32 kind, i32 index, i32 x, i32 y, i32 ptr);`

Cast one of the scheduled champion's two abilities; both slots share one successful cast per turn. A hidden blocked dash reveals the tile and returns success with `out_successful` = `ENGINE_FALSE`, without spending charges or cooldown. Known blocked landings return `spellCast_badDestination`. Completed casts set `ENGINE_TRUE`.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param slot`: `int32`
- `@param kind`: `int32` — `Game_EntityKind_Constants` tag.
- `@param index`: `int32` — `Champion_Constants`/camp ID or packed entity handle. For ground casts, use kind = 0 and index = 0; supply (x, y). Entity casts use the target kind/index. Ability slot is zero-based (0 or 1).
- `@param x`: `int32`
- `@param y`: `int32`
- `@param ptr`: `int32` — Address of an `Abi_int32.t` successful flag: 1 when completed, 0 when an unseen blocker was revealed. A 0 flag with status 0 is a committed action; do not interpret it as an engine error. Storage: `Abi_cbool.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` If exported, `champion_query_memory` receives this output instead of memory (the OCaml bridge convention).

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_use_consumable_with_result : kind:int32 -> x:int32 -> y:int32 -> ptr:int32 -> int32

WASM ABI: `i32 use_consumable_with_result(i32 kind, i32 x, i32 y, i32 ptr);`

Scrolls and crystals reserve destinations while channeling; neither can be manually cancelled. Occupied scroll destinations return `invalidAction_tpScroll_occupied`; crystals use `move_badDestination`. Rejected destinations do not consume the item. Hidden collisions reveal the tile and return success with `out_successful` = `ENGINE_FALSE` without consuming the item. Successfully used consumables (including starting teleport channels) set `out_successful` = `ENGINE_TRUE`.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param kind`: `int32`
- `@param x`: `int32`
- `@param y`: `int32`
- `@param ptr`: `int32` — Address of an `Abi_int32.t` successful flag: 1 when completed, 0 when an unseen blocker was revealed. A 0 flag with status 0 is a committed action; do not interpret it as an engine error. Storage: `Abi_cbool.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` If exported, `champion_query_memory` receives this output instead of memory (the OCaml bridge convention).

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_place_ward_with_result : x:int32 -> y:int32 -> ptr:int32 -> int32

WASM ABI: `i32 place_ward_with_result(i32 x, i32 y, i32 ptr);`

Place a ward using the scheduled champion's trinket charge. An existing allied ordinary or control ward returns `e_ErrorCode_invalidAction_placeWard_allyWardPresent`. Enemy wards may share the tile. A hidden allied ward reveals only the destination, recorded like a blocked hidden move. Hidden collisions return success with `out_successful` = `ENGINE_FALSE`; completed placements set `ENGINE_TRUE`. Rejected placements spend no charges; known occupied tiles return `allyWardPresent` without another reveal.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param ptr`: `int32` — Address of an `Abi_int32.t` successful flag: 1 when completed, 0 when an unseen blocker was revealed. A 0 flag with status 0 is a committed action; do not interpret it as an engine error. Storage: `Abi_cbool.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` If exported, `champion_query_memory` receives this output instead of memory (the OCaml bridge convention).

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_move_to : x:int32 -> y:int32 -> int32

WASM ABI: `i32 move_to(i32 x, i32 y);`

`Champion_Constants` actions require explicit cancellation of an active recall or gem submission. Priority updates and cancellation remain available while channelling. These destination actions require `out_successful`. Successful actions set it to `ENGINE_TRUE`. A hidden blocked destination reveals the tile, spends nothing, and returns success with `ENGINE_FALSE`. Known blocked destinations and other invalid actions return their error code with `ENGINE_FALSE`.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Compatibility form. Prefer `move_to_with_result` to distinguish a committed hidden-blocker reveal from an invalid action. This form translates a successful reveal with successful = 0 into a legacy blocked-destination error.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_attack : kind:int32 -> index:int32 -> int32

WASM ABI: `i32 attack(i32 kind, i32 index);`

Attack a visible target with the scheduled champion.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param kind`: `int32` — `Game_EntityKind_Constants` tag.
- `@param index`: `int32` — `Champion_Constants`/camp ID or packed entity handle. For ground casts, use kind = 0 and index = 0; supply (x, y). Entity casts use the target kind/index. Ability slot is zero-based (0 or 1).
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_cast : slot:int32 -> kind:int32 -> index:int32 -> x:int32 -> y:int32 -> int32

WASM ABI: `i32 cast(i32 slot, i32 kind, i32 index, i32 x, i32 y);`

Cast one of the scheduled champion's two abilities; both slots share one successful cast per turn. A hidden blocked dash reveals the tile and returns success with `out_successful` = `ENGINE_FALSE`, without spending charges or cooldown. Known blocked landings return `spellCast_badDestination`. Completed casts set `ENGINE_TRUE`.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param slot`: `int32`
- `@param kind`: `int32` — `Game_EntityKind_Constants` tag.
- `@param index`: `int32` — `Champion_Constants`/camp ID or packed entity handle. For ground casts, use kind = 0 and index = 0; supply (x, y). Entity casts use the target kind/index. Ability slot is zero-based (0 or 1).
- `@param x`: `int32`
- `@param y`: `int32`
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Compatibility form. Prefer `cast_with_result` to distinguish a committed hidden-blocker reveal from an invalid action. This form translates a successful reveal with successful = 0 into a legacy blocked-destination error.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_recall : unit -> int32

WASM ABI: `i32 recall();`

Start a recall countdown; damage or interrupting crowd control cancels it. Can start once per champion turn; repeated starts return `e_ErrorCode_invalidAction_recall_alreadyUsed`.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_submit_gems : x:int32 -> y:int32 -> int32

WASM ABI: `i32 submit_gems(i32 x, i32 y);`

Channel at an altar using the initial gem count for duration, then submit all carried gems. Requires at least one carried gem; otherwise returns `e_ErrorCode_invalidAction_submitGems_noGems` without starting a channel or recording an action. Can start once per champion turn; repeated starts return `e_ErrorCode_invalidAction_submitGems_alreadyUsed`.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_cancel_channel : unit -> int32

WASM ABI: `i32 cancel_channel();`

Cancel either channel without spending gems; legal even while crowd controlled. Each channel type can be cancelled once per champion turn. A repeated cancellation returns `e_ErrorCode_invalidAction_cancelChannel_alreadyUsed`; no active channel returns `e_ErrorCode_invalidAction_cancelChannel_notChanneling`. The runner resets these limits when it ends the turn.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_sell : item:int32 -> int32

WASM ABI: `i32 sell(i32 item);`

Buy equipment for the scheduled champion and apply automatic upgrades. Sell one owned item at full value from your own spawn tiles; Tavi only, no per-round limit.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param item`: `int32`
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_buy_item : item:int32 -> count:int32 -> int32

WASM ABI: `i32 buy_item(i32 item, i32 count);`

Buy count copies of `Item_Constants` for the scheduled champion. The host checks shopping eligibility, gold and automatic combinations.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param item`: `int32`
- `@param count`: `int32`
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_buy_consumable : kind:int32 -> int32

WASM ABI: `i32 buy_consumable(i32 kind);`

Buy one consumable for the scheduled champion.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param kind`: `int32`
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_use_consumable : kind:int32 -> x:int32 -> y:int32 -> int32

WASM ABI: `i32 use_consumable(i32 kind, i32 x, i32 y);`

Scrolls and crystals reserve destinations while channeling; neither can be manually cancelled. Occupied scroll destinations return `invalidAction_tpScroll_occupied`; crystals use `move_badDestination`. Rejected destinations do not consume the item. Hidden collisions reveal the tile and return success with `out_successful` = `ENGINE_FALSE` without consuming the item. Successfully used consumables (including starting teleport channels) set `out_successful` = `ENGINE_TRUE`.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param kind`: `int32`
- `@param x`: `int32`
- `@param y`: `int32`
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Compatibility form. Prefer `use_consumable_with_result` to distinguish a committed hidden-blocker reveal from an invalid action. This form translates a successful reveal with successful = 0 into a legacy blocked-destination error.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_place_ward : x:int32 -> y:int32 -> int32

WASM ABI: `i32 place_ward(i32 x, i32 y);`

Place a ward using the scheduled champion's trinket charge. An existing allied ordinary or control ward returns `e_ErrorCode_invalidAction_placeWard_allyWardPresent`. Enemy wards may share the tile. A hidden allied ward reveals only the destination, recorded like a blocked hidden move. Hidden collisions return success with `out_successful` = `ENGINE_FALSE`; completed placements set `ENGINE_TRUE`. Rejected placements spend no charges; known occupied tiles return `allyWardPresent` without another reveal.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Compatibility form. Prefer `place_ward_with_result` to distinguish a committed hidden-blocker reveal from an invalid action. This form translates a successful reveal with successful = 0 into a legacy blocked-destination error.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_set_priority : next_round_priority:int32 -> int32

WASM ABI: `i32 set_priority(i32 next_round_priority);`

Set the scheduled champion's priority for the next round without ending its current turn. If omitted, its previously submitted priority is retained (initially zero).

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param next_round_priority`: `int32`
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_board_camp_occupancy : ptr:int32 -> int32

WASM ABI: `i32 board_camp_occupancy(i32 ptr);`

Copy visible camp occupancy; neutral includes all teams without visibility filtering.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — A caller-owned, 16-byte-aligned bitboard of `board_bytes` bytes; the host replaces its contents. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_board_awake_camp_occupancy : ptr:int32 -> int32

WASM ABI: `i32 board_awake_camp_occupancy(i32 ptr);`

Like `Game_API_GetCampOccupancy`, but includes only awake camps. Dead camps are excluded.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — A caller-owned, 16-byte-aligned bitboard of `board_bytes` bytes; the host replaces its contents. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_board_asleep_camp_occupancy : ptr:int32 -> int32

WASM ABI: `i32 board_asleep_camp_occupancy(i32 ptr);`

Like `Game_API_GetCampOccupancy`, but includes only asleep camps. Dead camps are excluded.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — A caller-owned, 16-byte-aligned bitboard of `board_bytes` bytes; the host replaces its contents. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_board_ally_occupancy : ptr:int32 -> int32

WASM ABI: `i32 board_ally_occupancy(i32 ptr);`

Copy visible ally occupancy; neutral includes all teams without visibility filtering.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — A caller-owned, 16-byte-aligned bitboard of `board_bytes` bytes; the host replaces its contents. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_board_enemy_occupancy : ptr:int32 -> int32

WASM ABI: `i32 board_enemy_occupancy(i32 ptr);`

Copy visible enemy occupancy; neutral includes all teams without visibility filtering.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — A caller-owned, 16-byte-aligned bitboard of `board_bytes` bytes; the host replaces its contents. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_board_ally_ward_occupancy : ptr:int32 -> int32

WASM ABI: `i32 board_ally_ward_occupancy(i32 ptr);`

Copy allied ward placements in effective vision; neutral includes both teams.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — A caller-owned, 16-byte-aligned bitboard of `board_bytes` bytes; the host replaces its contents. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_board_enemy_ward_occupancy : ptr:int32 -> int32

WASM ABI: `i32 board_enemy_ward_occupancy(i32 ptr);`

Copy enemy ward occupancy in individual effective vision. Neutral includes all teams without visibility filtering.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — A caller-owned, 16-byte-aligned bitboard of `board_bytes` bytes; the host replaces its contents. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_board_ally_control_ward_occupancy : ptr:int32 -> int32

WASM ABI: `i32 board_ally_control_ward_occupancy(i32 ptr);`

Write allied control-ward placements within the observer's effective vision.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — A caller-owned, 16-byte-aligned bitboard of `board_bytes` bytes; the host replaces its contents. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_board_enemy_control_ward_occupancy : ptr:int32 -> int32

WASM ABI: `i32 board_enemy_control_ward_occupancy(i32 ptr);`

Write enemy control-ward placements within the observer's effective vision.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — A caller-owned, 16-byte-aligned bitboard of `board_bytes` bytes; the host replaces its contents. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_board_ally_altar_lock_occupancy : ptr:int32 -> int32

WASM ABI: `i32 board_ally_altar_lock_occupancy(i32 ptr);`

Write allied altar-lock occupancy within effective vision; neutral includes both teams.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — A caller-owned, 16-byte-aligned bitboard of `board_bytes` bytes; the host replaces its contents. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_board_enemy_altar_lock_occupancy : ptr:int32 -> int32

WASM ABI: `i32 board_enemy_altar_lock_occupancy(i32 ptr);`

Write enemy altar-lock occupancy within effective vision; neutral includes both teams.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — A caller-owned, 16-byte-aligned bitboard of `board_bytes` bytes; the host replaces its contents. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_board_teleport_occupancy : ptr:int32 -> int32

WASM ABI: `i32 board_teleport_occupancy(i32 ptr);`

Write visible teleport reservations, always including the observer's own destination.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — A caller-owned, 16-byte-aligned bitboard of `board_bytes` bytes; the host replaces its contents. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_board_vision : ptr:int32 -> int32

WASM ABI: `i32 board_vision(i32 ptr);`

Copy current individual vision, including owned wards and tile reveals; neutral fills the output with ones.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — A caller-owned, 16-byte-aligned bitboard of `board_bytes` bytes; the host replaces its contents. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_board_vision_mask : champion:int32 -> x:int32 -> y:int32 -> ptr:int32 -> int32

WASM ABI: `i32 board_vision_mask(i32 champion, i32 x, i32 y, i32 ptr);`

Compute a champion design's vision at a hypothetical tile, including bush and wall occlusion.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param champion`: `int32`
- `@param x`: `int32`
- `@param y`: `int32`
- `@param ptr`: `int32` — A caller-owned, 16-byte-aligned bitboard of `board_bytes` bytes; the host replaces its contents. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_board_ward_vision_mask : x:int32 -> y:int32 -> ptr:int32 -> int32

WASM ABI: `i32 board_ward_vision_mask(i32 x, i32 y, i32 ptr);`

Compute a ward's vision at a hypothetical tile.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param ptr`: `int32` — A caller-owned, 16-byte-aligned bitboard of `board_bytes` bytes; the host replaces its contents. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_board_control_ward_vision_mask : x:int32 -> y:int32 -> ptr:int32 -> int32

WASM ABI: `i32 board_control_ward_vision_mask(i32 x, i32 y, i32 ptr);`

Write the vision mask of a control ward owned by the observer.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param ptr`: `int32` — A caller-owned, 16-byte-aligned bitboard of `board_bytes` bytes; the host replaces its contents. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_champion_buff_data : champion:int32 -> ptr:int32 -> capacity:int32 -> count:int32 -> int32

WASM ABI: `i32 champion_buff_data(i32 champion, i32 ptr, i32 capacity, i32 count);`

Copy all active typed buffs; count-only calls use zero capacity.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param champion`: `int32`
- `@param ptr`: `int32` — Address of an output array of `Game_BuffData.t` records. Memory: at least capacity * 12 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@param capacity`: `int32` — Maximum number of records, not bytes. Zero queries the required count. A nonzero buffer must hold every result or the call fails with `api_bufferTooSmall`.
- `@param count`: `int32` — Address of the `Abi_uint32.t` count output; read it on success. Memory: at least 4 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_get_last_error : ptr:int32 -> capacity:int32 -> int32

WASM ABI: `i32 bc_get_last_error(i32 ptr, i32 capacity);`

Read the engine's latest diagnostic message. Call immediately after an engine error; runner-only -1 failures do not set an engine diagnostic.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — Byte buffer for the message. Capacity is in bytes; zero queries the full length without accessing `ptr`. Copies min(capacity, length) bytes without a terminating NUL. Memory: at least capacity bytes in exported linear memory; 1-byte alignment. Nonempty ranges must start at a positive address. Storage: `Abi_uint8.t`.
- `@param capacity`: `int32`
- `@return`: `int32` — Full message length in bytes (even when truncated), or -1 for invalid guest memory. This is not a status-returning function.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_resign : unit -> int32

WASM ABI: `i32 resign();`

Resign for the currently scheduled bot's team, ending the game.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@return`: `int32` — On success, execution stops immediately without returning to the bot. On failure, returns an engine error code.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_round_number : ptr:int32 -> int32

WASM ABI: `i32 bc_round_number(i32 ptr);`

Read the current round counter; available during the draft.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — Address of the `Abi_uint32.t` output. Memory: at least 4 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_submitted_gems : side:int32 -> ptr:int32 -> int32

WASM ABI: `i32 bc_submitted_gems(i32 side, i32 ptr);`

Read submitted gems for team A or B; neutral returns their sum.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param side`: `int32`
- `@param ptr`: `int32` — Address of the `Abi_uint32.t` output. Memory: at least 4 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_champion_priority : handle:int32 -> next:int32 -> ptr:int32 -> int32

WASM ABI: `i32 bc_champion_priority(i32 handle, i32 next, i32 ptr);`

Read a visible champion's current turn priority, or the priority queued for next round.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param next`: `int32` — Zero reads the current round's priority; nonzero reads the next round's priority.
- `@param ptr`: `int32` — Address of the `Abi_int32.t` output. Memory: at least 4 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_metadata : ptr:int32 -> int32

WASM ABI: `i32 bc_metadata(i32 ptr);`

Read the current map dimensions, chunk layout and required buffer sizes.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — Address of a 28-byte `Runner_Metadata.t` record, aligned to 4 bytes. Memory: at least 28 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_map_symmetry : ptr:int32 -> int32

WASM ABI: `i32 bc_map_symmetry(i32 ptr);`

Read the loaded map's symmetry.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — Address of the `Symmetry_Constants` output. Memory: at least 4 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address. Storage: `Abi_int32.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_champion_vision : handle:int32 -> ptr:int32 -> int32

WASM ABI: `i32 bc_champion_vision(i32 handle, i32 ptr);`

Write the current champion's effective vision; for another observable champion, compute its design's vision mask at its current position. A dead champion produces an empty board.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param handle`: `int32`
- `@param ptr`: `int32` — A 16-byte-aligned bitboard of `board_bytes` bytes. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_map_mask : kind:int32 -> ptr:int32 -> int32

WASM ABI: `i32 bc_map_mask(i32 kind, i32 ptr);`

Write static map terrain: kind 0 = walls, 1 = bushes, 2 = holes, 3 = altars. Other values return `invalidAction`.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param kind`: `int32`
- `@param ptr`: `int32` — A 16-byte-aligned bitboard of `board_bytes` bytes. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_submit_draft_memory : ptr:int32 -> size:int32 -> int32

WASM ABI: `i32 bc_submit_draft_memory(i32 ptr, i32 size);`

During your team's draft input, copy a prefix of guest bytes to draft memory at offset zero. Copies min(size, `draft_memory_size`) bytes; leaves the remaining draft memory unchanged. This does not submit a champion pick or yield.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param ptr`: `int32` — Source byte buffer, not an output; size is in bytes. Memory: at least size bytes in exported linear memory; 1-byte alignment. Nonempty ranges must start at a positive address. Storage: `Abi_uint8.t`.
- `@param size`: `int32`
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_zero : buffer:int32 -> int32

WASM ABI: `i32 bc_Bitboard_Zero(i32 buffer);`

Fill all storage bits, including padding, with zero.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Output storage need not be initialized before this call. Import operations require initialized source bytes.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_one : buffer:int32 -> int32

WASM ABI: `i32 bc_Bitboard_One(i32 buffer);`

Fill all storage bits, including padding, with one.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Output storage need not be initialized before this call. Import operations require initialized source bytes.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_importrawbuffer : buffer:int32 -> bytes:int32 -> size:int32 -> int32

WASM ABI: `i32 bc_Bitboard_ImportRawBuffer(i32 buffer, i32 bytes, i32 size);`

Load physical storage, including padding.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param bytes`: `int32` — Source byte buffer. Memory: at least size bytes in exported linear memory; 1-byte alignment. Nonempty ranges must start at a positive address. Storage: `Abi_uint8.t`.
- `@param size`: `int32` — Byte capacity, not element count. Raw storage includes padding and requires `board_bytes` bytes. The complete size-byte guest range must be valid. Too little capacity returns `api_bufferTooSmall`; extra capacity is not copied. Buffer and bytes must be disjoint.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Output storage need not be initialized before this call. Import operations require initialized source bytes.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_importlinearbuffer : buffer:int32 -> bytes:int32 -> size:int32 -> int32

WASM ABI: `i32 bc_Bitboard_ImportLinearBuffer(i32 buffer, i32 bytes, i32 size);`

Load packed row-major bits, LSB first.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param bytes`: `int32` — Source byte buffer. Memory: at least size bytes in exported linear memory; 1-byte alignment. Nonempty ranges must start at a positive address. Storage: `Abi_uint8.t`.
- `@param size`: `int32` — Byte capacity, not element count. Linear storage is ceil(width * height / 8) bytes of packed row-major bits, least-significant bit first. The complete size-byte guest range must be valid. Too little capacity returns `api_bufferTooSmall`; extra capacity is not copied. Buffer and bytes must be disjoint.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Output storage need not be initialized before this call. Import operations require initialized source bytes.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_exportrawbuffer : buffer:int32 -> bytes:int32 -> size:int32 -> int32

WASM ABI: `i32 bc_Bitboard_ExportRawBuffer(i32 buffer, i32 bytes, i32 size);`

Copy physical storage, including padding.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param bytes`: `int32` — Destination byte buffer. Memory: at least size bytes in exported linear memory; 1-byte alignment. Nonempty ranges must start at a positive address. Storage: `Abi_uint8.t`.
- `@param size`: `int32` — Byte capacity, not element count. Raw storage includes padding and requires `board_bytes` bytes. The complete size-byte guest range must be valid. Too little capacity returns `api_bufferTooSmall`; extra capacity is not copied. Buffer and bytes must be disjoint.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_exportlinearbuffer : buffer:int32 -> bytes:int32 -> size:int32 -> int32

WASM ABI: `i32 bc_Bitboard_ExportLinearBuffer(i32 buffer, i32 bytes, i32 size);`

Copy packed row-major bits, LSB first.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param bytes`: `int32` — Destination byte buffer. Memory: at least size bytes in exported linear memory; 1-byte alignment. Nonempty ranges must start at a positive address. Storage: `Abi_uint8.t`.
- `@param size`: `int32` — Byte capacity, not element count. Linear storage is ceil(width * height / 8) bytes of packed row-major bits, least-significant bit first. The complete size-byte guest range must be valid. Too little capacity returns `api_bufferTooSmall`; extra capacity is not copied. Buffer and bytes must be disjoint.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_print : buffer:int32 -> int32

WASM ABI: `i32 bc_Bitboard_Print(i32 buffer);`

Print logical tile values.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_test : buffer:int32 -> x:int32 -> y:int32 -> value:int32 -> int32

WASM ABI: `i32 bc_Bitboard_Test(i32 buffer, i32 x, i32 y, i32 value);`

Test one logical tile.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param x`: `int32`
- `@param y`: `int32`
- `@param value`: `int32` — Address of an `Abi_int32.t` boolean output (0 or 1). Memory: at least 4 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_set : buffer:int32 -> x:int32 -> y:int32 -> value:int32 -> int32

WASM ABI: `i32 bc_Bitboard_Set(i32 buffer, i32 x, i32 y, i32 value);`

Set one logical tile.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param x`: `int32`
- `@param y`: `int32`
- `@param value`: `int32` — The value to write, passed directly (not an address).
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` This operation modifies existing storage; initialize the full buffer first. For a new empty bitboard, call `bc_Bitboard_Zero`.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_toggle : buffer:int32 -> x:int32 -> y:int32 -> int32

WASM ABI: `i32 bc_Bitboard_Toggle(i32 buffer, i32 x, i32 y);`

Toggle one logical tile.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param x`: `int32`
- `@param y`: `int32`
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` This operation modifies existing storage; initialize the full buffer first. For a new empty bitboard, call `bc_Bitboard_Zero`.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_iszero : buffer:int32 -> value:int32 -> int32

WASM ABI: `i32 bc_Bitboard_IsZero(i32 buffer, i32 value);`

Inspect logical tiles, ignoring padding.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param value`: `int32` — Address of an `Abi_int32.t` boolean output: 1 if every logical bit is zero. Memory: at least 4 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_numsetbits : buffer:int32 -> value:int32 -> int32

WASM ABI: `i32 bc_Bitboard_NumSetBits(i32 buffer, i32 value);`

Inspect logical tiles, ignoring padding.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param value`: `int32` — Address of a `Abi_uint32.t` count output. Memory: at least 4 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_getsetbits : buffer:int32 -> positions:int32 -> capacity:int32 -> count:int32 -> int32

WASM ABI: `i32 bc_Bitboard_GetSetBits(i32 buffer, i32 positions, i32 capacity, i32 count);`

Write up to `in_capacity` (x, y) pairs into 2 * `in_capacity` `Abi_int32.t` slots; zero capacity permits null.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param positions`: `int32` — Address of capacity `Game_Position.t` records (8 bytes each). Capacity counts positions, not `Abi_int32.t` words. Memory: at least capacity * 8 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@param capacity`: `int32`
- `@param count`: `int32` — Address of the `Abi_uint32.t` number written. Truncates to capacity; use `bc_Bitboard_NumSetBits` to obtain the full count. Memory: at least 4 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` The positions array must not overlap the input bitboard. Keep count in a separate 4-byte-aligned `Abi_uint32.t` slot.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_not : buffer:int32 -> result:int32 -> int32

WASM ABI: `i32 bc_Bitboard_Not(i32 buffer, i32 result);`

Not logical tiles; exact input/output aliasing is permitted.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param result`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_union : a:int32 -> b:int32 -> result:int32 -> int32

WASM ABI: `i32 bc_Bitboard_Union(i32 a, i32 b, i32 result);`

Combine logical bits using OR. The result may exactly alias either input; a and b may also be identical. Partial overlap is invalid.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param a`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param b`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param result`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_intersect : a:int32 -> b:int32 -> result:int32 -> int32

WASM ABI: `i32 bc_Bitboard_Intersect(i32 a, i32 b, i32 result);`

Combine logical bits using AND. The result may exactly alias either input; a and b may also be identical. Partial overlap is invalid.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param a`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param b`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param result`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_xor : a:int32 -> b:int32 -> result:int32 -> int32

WASM ABI: `i32 bc_Bitboard_Xor(i32 a, i32 b, i32 result);`

Combine logical bits using XOR. The result may exactly alias either input; a and b may also be identical. Partial overlap is invalid.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param a`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param b`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param result`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_isequal : a:int32 -> b:int32 -> value:int32 -> int32

WASM ABI: `i32 bc_Bitboard_IsEqual(i32 a, i32 b, i32 value);`

Compare logical tiles, ignoring padding. Inputs may be identical or disjoint; partial overlap is invalid.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param a`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param b`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param value`: `int32` — Address of an `Abi_int32.t` boolean output: 1 if logical tiles match. Memory: at least 4 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_shiftright : buffer:int32 -> result:int32 -> count:int32 -> int32

WASM ABI: `i32 bc_Bitboard_ShiftRight(i32 buffer, i32 result, i32 count);`

`ShiftRight` logical tiles; exact input/output aliasing is permitted.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param result`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param count`: `int32` — Signed horizontal shift: positive moves right, negative moves left; bits shifted beyond the map are discarded.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_shiftup : buffer:int32 -> result:int32 -> count:int32 -> int32

WASM ABI: `i32 bc_Bitboard_ShiftUp(i32 buffer, i32 result, i32 count);`

`ShiftUp` logical tiles; exact input/output aliasing is permitted.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param result`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param count`: `int32` — Signed vertical shift: positive increases y, negative decreases y; bits shifted beyond the map are discarded.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_reflect : buffer:int32 -> result:int32 -> symmetry:int32 -> int32

WASM ABI: `i32 bc_Bitboard_Reflect(i32 buffer, i32 result, i32 symmetry);`

Apply symmetry 0 = horizontal, 1 = vertical, 2 = rotation by 180 degrees.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param result`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param symmetry`: `int32` — `Symmetry_Constants` enum: 0 = horizontal reflection, 1 = vertical reflection, 2 = rotate 180 degrees. Input and output must be disjoint.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_drawcircle : buffer:int32 -> x:int32 -> y:int32 -> radius:float -> int32

WASM ABI: `i32 bc_Bitboard_DrawCircle(i32 buffer, i32 x, i32 y, f32 radius);`

Add the shape around an in-bounds center, preserving existing logical bits.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param x`: `int32`
- `@param y`: `int32`
- `@param radius`: `float` — Euclidean radius as `f32`; adds tiles within the circle without clearing existing bits.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` This operation modifies existing storage; initialize the full buffer first. For a new empty bitboard, call `bc_Bitboard_Zero`.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_drawmanhattan : buffer:int32 -> x:int32 -> y:int32 -> radius:float -> int32

WASM ABI: `i32 bc_Bitboard_DrawManhattan(i32 buffer, i32 x, i32 y, f32 radius);`

Add the shape around an in-bounds center, preserving existing logical bits.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param x`: `int32`
- `@param y`: `int32`
- `@param radius`: `float` — Manhattan radius as `f32`; adds tiles within the diamond without clearing existing bits.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` This operation modifies existing storage; initialize the full buffer first. For a new empty bitboard, call `bc_Bitboard_Zero`.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_drawchebyshev : buffer:int32 -> x:int32 -> y:int32 -> radius:float -> int32

WASM ABI: `i32 bc_Bitboard_DrawChebyshev(i32 buffer, i32 x, i32 y, f32 radius);`

Add the shape around an in-bounds center, preserving existing logical bits.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param x`: `int32`
- `@param y`: `int32`
- `@param radius`: `float` — Chebyshev radius as `f32`; adds tiles within the square without clearing existing bits.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` This operation modifies existing storage; initialize the full buffer first. For a new empty bitboard, call `bc_Bitboard_Zero`.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_reflecthorizontalposition : x:int32 -> y:int32 -> out_x:int32 -> out_y:int32 -> int32

WASM ABI: `i32 bc_Bitboard_ReflectHorizontalPosition(i32 x, i32 y, i32 out_x, i32 out_y);`

Transform a logical coordinate using the map dimensions.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param out_x`: `int32` — Address of an `Abi_int32.t` output. Memory: at least 4 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@param out_y`: `int32` — Address of a separate `Abi_int32.t` output. Memory: at least 4 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_reflectverticalposition : x:int32 -> y:int32 -> out_x:int32 -> out_y:int32 -> int32

WASM ABI: `i32 bc_Bitboard_ReflectVerticalPosition(i32 x, i32 y, i32 out_x, i32 out_y);`

Transform a logical coordinate using the map dimensions.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param out_x`: `int32` — Address of an `Abi_int32.t` output. Memory: at least 4 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@param out_y`: `int32` — Address of a separate `Abi_int32.t` output. Memory: at least 4 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_rotate180position : x:int32 -> y:int32 -> out_x:int32 -> out_y:int32 -> int32

WASM ABI: `i32 bc_Bitboard_Rotate180Position(i32 x, i32 y, i32 out_x, i32 out_y);`

Transform a logical coordinate using the map dimensions.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param x`: `int32`
- `@param y`: `int32`
- `@param out_x`: `int32` — Address of an `Abi_int32.t` output. Memory: at least 4 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@param out_y`: `int32` — Address of a separate `Abi_int32.t` output. Memory: at least 4 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_reachablemask : walls:int32 -> x:int32 -> y:int32 -> result:int32 -> distance:int32 -> int32

WASM ABI: `i32 bc_Bitboard_ReachableMask(i32 walls, i32 x, i32 y, i32 result, i32 distance);`

Compute king-move reachability; all buffers must be disjoint.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param walls`: `int32` — Input obstacle bitboard. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param x`: `int32`
- `@param y`: `int32`
- `@param result`: `int32` — Output bitboard. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param distance`: `int32` — Integer range in 0..65535. Scratch variants also require separate frontier and scratch bitboards.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_shadowcast : walls:int32 -> x:int32 -> y:int32 -> result:int32 -> distance:int32 -> int32

WASM ABI: `i32 bc_Bitboard_ShadowCast(i32 walls, i32 x, i32 y, i32 result, i32 distance);`

Compute visibility from a non-opaque origin; all buffers must be disjoint.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param walls`: `int32` — Input obstacle bitboard. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param x`: `int32`
- `@param y`: `int32`
- `@param result`: `int32` — Output bitboard. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param distance`: `int32` — Integer range in 0..65535. Scratch variants also require separate frontier and scratch bitboards.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_reachablemaskwithscratch : walls:int32 -> x:int32 -> y:int32 -> result:int32 -> distance:int32 -> frontier:int32 -> scratch:int32 -> int32

WASM ABI: `i32 bc_Bitboard_ReachableMaskWithScratch(i32 walls, i32 x, i32 y, i32 result, i32 distance, i32 frontier, i32 scratch);`

Compute king-move reachability; all buffers must be disjoint.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param walls`: `int32` — Input obstacle bitboard. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param x`: `int32`
- `@param y`: `int32`
- `@param result`: `int32` — Output bitboard. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param distance`: `int32` — Integer range in 0..65535. Scratch variants also require separate frontier and scratch bitboards.
- `@param frontier`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param scratch`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_distancefield_importrawbuffer : buffer:int32 -> bytes:int32 -> size:int32 -> int32

WASM ABI: `i32 bc_DistanceField_ImportRawBuffer(i32 buffer, i32 bytes, i32 size);`

Load physical storage, including padding.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `field_bytes` bytes in exported linear memory; 2-byte alignment. Nonempty ranges must start at a positive address. Storage: `DistanceFieldBuffer.t`.
- `@param bytes`: `int32` — Source byte buffer. Memory: at least size bytes in exported linear memory; 1-byte alignment. Nonempty ranges must start at a positive address. Storage: `Abi_uint8.t`.
- `@param size`: `int32` — Byte capacity, not element count. Raw storage includes padding and requires `field_bytes` bytes. The complete size-byte guest range must be valid. Too little capacity returns `api_bufferTooSmall`; extra capacity is not copied. Buffer and bytes must be disjoint.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Output storage need not be initialized before this call. Import operations require initialized source bytes.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_distancefield_importlinearbuffer : buffer:int32 -> bytes:int32 -> size:int32 -> int32

WASM ABI: `i32 bc_DistanceField_ImportLinearBuffer(i32 buffer, i32 bytes, i32 size);`

Load row-major `Abi_uint16.t` values in native byte order (little-endian on WASM).

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `field_bytes` bytes in exported linear memory; 2-byte alignment. Nonempty ranges must start at a positive address. Storage: `DistanceFieldBuffer.t`.
- `@param bytes`: `int32` — Source byte buffer. Memory: at least size bytes in exported linear memory; 1-byte alignment. Nonempty ranges must start at a positive address. Storage: `Abi_uint8.t`.
- `@param size`: `int32` — Byte capacity, not element count. Linear storage is width * height little-endian `Abi_uint16.t` values (2 bytes each), row-major. The complete size-byte guest range must be valid. Too little capacity returns `api_bufferTooSmall`; extra capacity is not copied. Buffer and bytes must be disjoint.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Output storage need not be initialized before this call. Import operations require initialized source bytes.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_distancefield_exportrawbuffer : buffer:int32 -> bytes:int32 -> size:int32 -> int32

WASM ABI: `i32 bc_DistanceField_ExportRawBuffer(i32 buffer, i32 bytes, i32 size);`

Copy physical storage, including padding.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `field_bytes` bytes in exported linear memory; 2-byte alignment. Nonempty ranges must start at a positive address. Storage: `DistanceFieldBuffer.t`.
- `@param bytes`: `int32` — Destination byte buffer. Memory: at least size bytes in exported linear memory; 1-byte alignment. Nonempty ranges must start at a positive address. Storage: `Abi_uint8.t`.
- `@param size`: `int32` — Byte capacity, not element count. Raw storage includes padding and requires `field_bytes` bytes. The complete size-byte guest range must be valid. Too little capacity returns `api_bufferTooSmall`; extra capacity is not copied. Buffer and bytes must be disjoint.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_distancefield_exportlinearbuffer : buffer:int32 -> bytes:int32 -> size:int32 -> int32

WASM ABI: `i32 bc_DistanceField_ExportLinearBuffer(i32 buffer, i32 bytes, i32 size);`

Copy row-major `Abi_uint16.t` values in native byte order (little-endian on WASM).

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `field_bytes` bytes in exported linear memory; 2-byte alignment. Nonempty ranges must start at a positive address. Storage: `DistanceFieldBuffer.t`.
- `@param bytes`: `int32` — Destination byte buffer. Memory: at least size bytes in exported linear memory; 1-byte alignment. Nonempty ranges must start at a positive address. Storage: `Abi_uint8.t`.
- `@param size`: `int32` — Byte capacity, not element count. Linear storage is width * height little-endian `Abi_uint16.t` values (2 bytes each), row-major. The complete size-byte guest range must be valid. Too little capacity returns `api_bufferTooSmall`; extra capacity is not copied. Buffer and bytes must be disjoint.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_distancefield_print : buffer:int32 -> int32

WASM ABI: `i32 bc_DistanceField_Print(i32 buffer);`

Print logical tile values.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `field_bytes` bytes in exported linear memory; 2-byte alignment. Nonempty ranges must start at a positive address. Storage: `DistanceFieldBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_distancefield_copy : source:int32 -> destination:int32 -> int32

WASM ABI: `i32 bc_DistanceField_Copy(i32 source, i32 destination);`

Copy physical storage, including padding. Exact self-copy is allowed; partial overlap is invalid.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param source`: `int32` — Memory: at least `field_bytes` bytes in exported linear memory; 2-byte alignment. Nonempty ranges must start at a positive address. Storage: `DistanceFieldBuffer.t`.
- `@param destination`: `int32` — Memory: at least `field_bytes` bytes in exported linear memory; 2-byte alignment. Nonempty ranges must start at a positive address. Storage: `DistanceFieldBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_distancefield_copywithmask : source:int32 -> mask:int32 -> destination:int32 -> int32

WASM ABI: `i32 bc_DistanceField_CopyWithMask(i32 source, i32 mask, i32 destination);`

Copy only logical tiles selected by `in_mask`, preserving every unselected destination value. Mask padding is ignored and destination padding is preserved. Mask must not overlap either field. Fields may exactly alias; partial overlap is invalid. Fields require `Abi_uint16.t` alignment.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param source`: `int32` — Memory: at least `field_bytes` bytes in exported linear memory; 2-byte alignment. Nonempty ranges must start at a positive address. Storage: `DistanceFieldBuffer.t`.
- `@param mask`: `int32` — Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param destination`: `int32` — Memory: at least `field_bytes` bytes in exported linear memory; 2-byte alignment. Nonempty ranges must start at a positive address. Storage: `DistanceFieldBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Initialize destination before copying: unselected logical tiles and destination padding keep their previous values.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_distancefield_get : buffer:int32 -> x:int32 -> y:int32 -> value:int32 -> int32

WASM ABI: `i32 bc_DistanceField_Get(i32 buffer, i32 x, i32 y, i32 value);`

Read one logical distance.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `field_bytes` bytes in exported linear memory; 2-byte alignment. Nonempty ranges must start at a positive address. Storage: `DistanceFieldBuffer.t`.
- `@param x`: `int32`
- `@param y`: `int32`
- `@param value`: `int32` — Address of a `Abi_uint16.t` output (2 bytes, aligned to 2). Memory: at least 2 bytes in exported linear memory; 2-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_distancefield_set : buffer:int32 -> x:int32 -> y:int32 -> value:int32 -> int32

WASM ABI: `i32 bc_DistanceField_Set(i32 buffer, i32 x, i32 y, i32 value);`

Write one logical distance.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `int32` — Memory: at least `field_bytes` bytes in exported linear memory; 2-byte alignment. Nonempty ranges must start at a positive address. Storage: `DistanceFieldBuffer.t`.
- `@param x`: `int32`
- `@param y`: `int32`
- `@param value`: `int32` — The value to write, passed directly (not an address). An integer in 0..65535; 65535 represents unreachable/uncomputed.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Set preserves other tiles. Initialize the full field with a compute or import operation before reading those tiles.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_distancefield_computewithexpansioncount : walls:int32 -> roots:int32 -> visited:int32 -> distances:int32 -> max_distance:int32 -> count:int32 -> int32

WASM ABI: `i32 bc_DistanceField_ComputeWithExpansionCount(i32 walls, i32 roots, i32 visited, i32 distances, i32 max_distance, i32 count);`

Compute king-move distances using reusable thread-local scratch. All buffers must be disjoint. Count attempted expansions, including the final empty one.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param walls`: `int32` — Input obstacle bitboard. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param roots`: `int32` — Input seed bitboard. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param visited`: `int32` — Output visited bitboard. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param distances`: `int32` — Output distance field. Memory: at least `field_bytes` bytes in exported linear memory; 2-byte alignment. Nonempty ranges must start at a positive address. Storage: `DistanceFieldBuffer.t`.
- `@param max_distance`: `int32` — Integer limit in 0..65535.
- `@param count`: `int32` — Address of a `Abi_uint16.t` expansion count, not `Abi_uint32.t`. Unreachable/uncomputed tiles have distance 65535. All participating buffers must be disjoint. Memory: at least 2 bytes in exported linear memory; 2-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Output storage need not be initialized before this call. Import operations require initialized source bytes.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_distancefield_computetowithexpansioncount : walls:int32 -> roots:int32 -> destinations:int32 -> visited:int32 -> distances:in…

WASM ABI: `i32 bc_DistanceField_ComputeToWithExpansionCount(i32 walls, i32 roots, i32 destinations, i32 visited, i32 distances, i32 max_distance, i32 count);`

Compute until all destinations are reached or the frontier stops using reusable thread-local scratch. All buffers must be disjoint. Count attempted expansions, including the final empty one.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param walls`: `int32` — Input obstacle bitboard. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param roots`: `int32` — Input seed bitboard. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param destinations`: `int32` — Input target bitboard. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param visited`: `int32` — Output visited bitboard. Memory: at least `board_bytes` bytes in exported linear memory; 16-byte alignment. Nonempty ranges must start at a positive address. Storage: `BitboardBuffer.t`.
- `@param distances`: `int32` — Output distance field. Memory: at least `field_bytes` bytes in exported linear memory; 2-byte alignment. Nonempty ranges must start at a positive address. Storage: `DistanceFieldBuffer.t`.
- `@param max_distance`: `int32` — Integer limit in 0..65535.
- `@param count`: `int32` — Address of a `Abi_uint16.t` expansion count, not `Abi_uint32.t`. Unreachable/uncomputed tiles have distance 65535. All participating buffers must be disjoint. Memory: at least 2 bytes in exported linear memory; 2-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Output storage need not be initialized before this call. Import operations require initialized source bytes.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_zero_gc : buffer:BitboardBuffer.t -> int32

WASM ABI: `i32 bc_Bitboard_Zero_gc(arrayref buffer);`

Fill all storage bits, including padding, with zero.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Output storage need not be initialized before this call. Import operations require initialized source bytes.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_one_gc : buffer:BitboardBuffer.t -> int32

WASM ABI: `i32 bc_Bitboard_One_gc(arrayref buffer);`

Fill all storage bits, including padding, with one.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Output storage need not be initialized before this call. Import operations require initialized source bytes.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_importrawbuffer_gc : buffer:BitboardBuffer.t -> bytes:bytes -> size:int32 -> int32

WASM ABI: `i32 bc_Bitboard_ImportRawBuffer_gc(arrayref buffer, arrayref bytes, i32 size);`

Load physical storage, including padding.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param bytes`: `bytes` — Source byte buffer. Memory: a non-null mutable WasmGC i8 array of exactly size bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `Abi_uint8.t`.
- `@param size`: `int32` — Byte capacity, not element count. Raw storage includes padding and requires `board_bytes` bytes. The complete size-byte guest range must be valid. Too little capacity returns `api_bufferTooSmall`; extra capacity is not copied.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Output storage need not be initialized before this call. Import operations require initialized source bytes.

`@note` Use the required transfer size. The GC bridge limits size to `round_up`(max(`board_bytes`, `field_bytes`), 16); larger scratch requests return `api_valueOutOfRange`.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_importlinearbuffer_gc : buffer:BitboardBuffer.t -> bytes:bytes -> size:int32 -> int32

WASM ABI: `i32 bc_Bitboard_ImportLinearBuffer_gc(arrayref buffer, arrayref bytes, i32 size);`

Load packed row-major bits, LSB first.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param bytes`: `bytes` — Source byte buffer. Memory: a non-null mutable WasmGC i8 array of exactly size bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `Abi_uint8.t`.
- `@param size`: `int32` — Byte capacity, not element count. Linear storage is ceil(width * height / 8) bytes of packed row-major bits, least-significant bit first. The complete size-byte guest range must be valid. Too little capacity returns `api_bufferTooSmall`; extra capacity is not copied.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Output storage need not be initialized before this call. Import operations require initialized source bytes.

`@note` Use the required transfer size. The GC bridge limits size to `round_up`(max(`board_bytes`, `field_bytes`), 16); larger scratch requests return `api_valueOutOfRange`.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_exportrawbuffer_gc : buffer:BitboardBuffer.t -> bytes:bytes -> size:int32 -> int32

WASM ABI: `i32 bc_Bitboard_ExportRawBuffer_gc(arrayref buffer, arrayref bytes, i32 size);`

Copy physical storage, including padding.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param bytes`: `bytes` — Destination byte buffer. Memory: a non-null mutable WasmGC i8 array of exactly size bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `Abi_uint8.t`.
- `@param size`: `int32` — Byte capacity, not element count. Raw storage includes padding and requires `board_bytes` bytes. The complete size-byte guest range must be valid. Too little capacity returns `api_bufferTooSmall`; extra capacity is not copied.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Use the required transfer size. The GC bridge limits size to `round_up`(max(`board_bytes`, `field_bytes`), 16); larger scratch requests return `api_valueOutOfRange`.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_exportlinearbuffer_gc : buffer:BitboardBuffer.t -> bytes:bytes -> size:int32 -> int32

WASM ABI: `i32 bc_Bitboard_ExportLinearBuffer_gc(arrayref buffer, arrayref bytes, i32 size);`

Copy packed row-major bits, LSB first.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param bytes`: `bytes` — Destination byte buffer. Memory: a non-null mutable WasmGC i8 array of exactly size bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `Abi_uint8.t`.
- `@param size`: `int32` — Byte capacity, not element count. Linear storage is ceil(width * height / 8) bytes of packed row-major bits, least-significant bit first. The complete size-byte guest range must be valid. Too little capacity returns `api_bufferTooSmall`; extra capacity is not copied.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Use the required transfer size. The GC bridge limits size to `round_up`(max(`board_bytes`, `field_bytes`), 16); larger scratch requests return `api_valueOutOfRange`.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_print_gc : buffer:BitboardBuffer.t -> int32

WASM ABI: `i32 bc_Bitboard_Print_gc(arrayref buffer);`

Print logical tile values.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_test_gc : buffer:BitboardBuffer.t -> x:int32 -> y:int32 -> value:int32 -> int32

WASM ABI: `i32 bc_Bitboard_Test_gc(arrayref buffer, i32 x, i32 y, i32 value);`

Test one logical tile.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param x`: `int32`
- `@param y`: `int32`
- `@param value`: `int32` — Address of an `Abi_int32.t` boolean output (0 or 1). Memory: at least 4 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_set_gc : buffer:BitboardBuffer.t -> x:int32 -> y:int32 -> value:int32 -> int32

WASM ABI: `i32 bc_Bitboard_Set_gc(arrayref buffer, i32 x, i32 y, i32 value);`

Set one logical tile.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param x`: `int32`
- `@param y`: `int32`
- `@param value`: `int32` — The value to write, passed directly (not an address).
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` This operation modifies existing storage; initialize the full buffer first. For a new empty bitboard, call `bc_Bitboard_Zero`.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_toggle_gc : buffer:BitboardBuffer.t -> x:int32 -> y:int32 -> int32

WASM ABI: `i32 bc_Bitboard_Toggle_gc(arrayref buffer, i32 x, i32 y);`

Toggle one logical tile.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param x`: `int32`
- `@param y`: `int32`
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` This operation modifies existing storage; initialize the full buffer first. For a new empty bitboard, call `bc_Bitboard_Zero`.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_iszero_gc : buffer:BitboardBuffer.t -> value:int32 -> int32

WASM ABI: `i32 bc_Bitboard_IsZero_gc(arrayref buffer, i32 value);`

Inspect logical tiles, ignoring padding.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param value`: `int32` — Address of an `Abi_int32.t` boolean output: 1 if every logical bit is zero. Memory: at least 4 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_numsetbits_gc : buffer:BitboardBuffer.t -> value:int32 -> int32

WASM ABI: `i32 bc_Bitboard_NumSetBits_gc(arrayref buffer, i32 value);`

Inspect logical tiles, ignoring padding.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param value`: `int32` — Address of a `Abi_uint32.t` count output. Memory: at least 4 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_getsetbits_gc : buffer:BitboardBuffer.t -> positions:int32 -> capacity:int32 -> count:int32 -> int32

WASM ABI: `i32 bc_Bitboard_GetSetBits_gc(arrayref buffer, i32 positions, i32 capacity, i32 count);`

Write up to `in_capacity` (x, y) pairs into 2 * `in_capacity` `Abi_int32.t` slots; zero capacity permits null.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param positions`: `int32` — Address of capacity `Game_Position.t` records (8 bytes each). Capacity counts positions, not `Abi_int32.t` words. Memory: at least capacity * 8 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@param capacity`: `int32`
- `@param count`: `int32` — Address of the `Abi_uint32.t` number written. Truncates to capacity; use `bc_Bitboard_NumSetBits` to obtain the full count. Memory: at least 4 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` The positions array must not overlap the input bitboard. Keep count in a separate 4-byte-aligned `Abi_uint32.t` slot.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_not_gc : buffer:BitboardBuffer.t -> result:BitboardBuffer.t -> int32

WASM ABI: `i32 bc_Bitboard_Not_gc(arrayref buffer, arrayref result);`

Not logical tiles; exact input/output aliasing is permitted.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param result`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_union_gc : a:BitboardBuffer.t -> b:BitboardBuffer.t -> result:BitboardBuffer.t -> int32

WASM ABI: `i32 bc_Bitboard_Union_gc(arrayref a, arrayref b, arrayref result);`

Combine logical bits using OR.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param a`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param b`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param result`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_intersect_gc : a:BitboardBuffer.t -> b:BitboardBuffer.t -> result:BitboardBuffer.t -> int32

WASM ABI: `i32 bc_Bitboard_Intersect_gc(arrayref a, arrayref b, arrayref result);`

Combine logical bits using AND.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param a`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param b`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param result`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_xor_gc : a:BitboardBuffer.t -> b:BitboardBuffer.t -> result:BitboardBuffer.t -> int32

WASM ABI: `i32 bc_Bitboard_Xor_gc(arrayref a, arrayref b, arrayref result);`

Combine logical bits using XOR.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param a`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param b`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param result`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_isequal_gc : a:BitboardBuffer.t -> b:BitboardBuffer.t -> value:int32 -> int32

WASM ABI: `i32 bc_Bitboard_IsEqual_gc(arrayref a, arrayref b, i32 value);`

Compare logical tiles, ignoring padding.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param a`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param b`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param value`: `int32` — Address of an `Abi_int32.t` boolean output: 1 if logical tiles match. Memory: at least 4 bytes in exported linear memory; 4-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_shiftright_gc : buffer:BitboardBuffer.t -> result:BitboardBuffer.t -> count:int32 -> int32

WASM ABI: `i32 bc_Bitboard_ShiftRight_gc(arrayref buffer, arrayref result, i32 count);`

`ShiftRight` logical tiles; exact input/output aliasing is permitted.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param result`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param count`: `int32` — Signed horizontal shift: positive moves right, negative moves left; bits shifted beyond the map are discarded.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_shiftup_gc : buffer:BitboardBuffer.t -> result:BitboardBuffer.t -> count:int32 -> int32

WASM ABI: `i32 bc_Bitboard_ShiftUp_gc(arrayref buffer, arrayref result, i32 count);`

`ShiftUp` logical tiles; exact input/output aliasing is permitted.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param result`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param count`: `int32` — Signed vertical shift: positive increases y, negative decreases y; bits shifted beyond the map are discarded.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_reflect_gc : buffer:BitboardBuffer.t -> result:BitboardBuffer.t -> symmetry:int32 -> int32

WASM ABI: `i32 bc_Bitboard_Reflect_gc(arrayref buffer, arrayref result, i32 symmetry);`

Apply symmetry 0 = horizontal, 1 = vertical, 2 = rotation by 180 degrees.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param result`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param symmetry`: `int32` — `Symmetry_Constants` enum: 0 = horizontal reflection, 1 = vertical reflection, 2 = rotate 180 degrees.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_drawcircle_gc : buffer:BitboardBuffer.t -> x:int32 -> y:int32 -> radius:float -> int32

WASM ABI: `i32 bc_Bitboard_DrawCircle_gc(arrayref buffer, i32 x, i32 y, f32 radius);`

Add the shape around an in-bounds center, preserving existing logical bits.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param x`: `int32`
- `@param y`: `int32`
- `@param radius`: `float` — Euclidean radius as `f32`; adds tiles within the circle without clearing existing bits.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` This operation modifies existing storage; initialize the full buffer first. For a new empty bitboard, call `bc_Bitboard_Zero`.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_drawmanhattan_gc : buffer:BitboardBuffer.t -> x:int32 -> y:int32 -> radius:float -> int32

WASM ABI: `i32 bc_Bitboard_DrawManhattan_gc(arrayref buffer, i32 x, i32 y, f32 radius);`

Add the shape around an in-bounds center, preserving existing logical bits.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param x`: `int32`
- `@param y`: `int32`
- `@param radius`: `float` — Manhattan radius as `f32`; adds tiles within the diamond without clearing existing bits.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` This operation modifies existing storage; initialize the full buffer first. For a new empty bitboard, call `bc_Bitboard_Zero`.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_drawchebyshev_gc : buffer:BitboardBuffer.t -> x:int32 -> y:int32 -> radius:float -> int32

WASM ABI: `i32 bc_Bitboard_DrawChebyshev_gc(arrayref buffer, i32 x, i32 y, f32 radius);`

Add the shape around an in-bounds center, preserving existing logical bits.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param x`: `int32`
- `@param y`: `int32`
- `@param radius`: `float` — Chebyshev radius as `f32`; adds tiles within the square without clearing existing bits.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` This operation modifies existing storage; initialize the full buffer first. For a new empty bitboard, call `bc_Bitboard_Zero`.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_reachablemask_gc : walls:BitboardBuffer.t -> x:int32 -> y:int32 -> result:BitboardBuffer.t -> distance:int32 -> int32

WASM ABI: `i32 bc_Bitboard_ReachableMask_gc(arrayref walls, i32 x, i32 y, arrayref result, i32 distance);`

Compute king-move reachability;

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param walls`: `BitboardBuffer``.t` — Input obstacle bitboard. Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param x`: `int32`
- `@param y`: `int32`
- `@param result`: `BitboardBuffer``.t` — Output bitboard. Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param distance`: `int32` — Integer range in 0..65535. Scratch variants also require separate frontier and scratch bitboards.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_shadowcast_gc : walls:BitboardBuffer.t -> x:int32 -> y:int32 -> result:BitboardBuffer.t -> distance:int32 -> int32

WASM ABI: `i32 bc_Bitboard_ShadowCast_gc(arrayref walls, i32 x, i32 y, arrayref result, i32 distance);`

Compute visibility from a non-opaque origin;

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param walls`: `BitboardBuffer``.t` — Input obstacle bitboard. Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param x`: `int32`
- `@param y`: `int32`
- `@param result`: `BitboardBuffer``.t` — Output bitboard. Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param distance`: `int32` — Integer range in 0..65535. Scratch variants also require separate frontier and scratch bitboards.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_bitboard_reachablemaskwithscratch_gc : walls:BitboardBuffer.t -> x:int32 -> y:int32 -> result:BitboardBuffer.t -> distance:in…

WASM ABI: `i32 bc_Bitboard_ReachableMaskWithScratch_gc(arrayref walls, i32 x, i32 y, arrayref result, i32 distance, arrayref frontier, arrayref scratch);`

Compute king-move reachability;

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param walls`: `BitboardBuffer``.t` — Input obstacle bitboard. Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param x`: `int32`
- `@param y`: `int32`
- `@param result`: `BitboardBuffer``.t` — Output bitboard. Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param distance`: `int32` — Integer range in 0..65535. Scratch variants also require separate frontier and scratch bitboards.
- `@param frontier`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param scratch`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_distancefield_importrawbuffer_gc : buffer:DistanceFieldBuffer.t -> bytes:bytes -> size:int32 -> int32

WASM ABI: `i32 bc_DistanceField_ImportRawBuffer_gc(arrayref buffer, arrayref bytes, i32 size);`

Load physical storage, including padding.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `DistanceFieldBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `field_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `DistanceFieldBuffer.t`.
- `@param bytes`: `bytes` — Source byte buffer. Memory: a non-null mutable WasmGC i8 array of exactly size bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `Abi_uint8.t`.
- `@param size`: `int32` — Byte capacity, not element count. Raw storage includes padding and requires `field_bytes` bytes. The complete size-byte guest range must be valid. Too little capacity returns `api_bufferTooSmall`; extra capacity is not copied.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Output storage need not be initialized before this call. Import operations require initialized source bytes.

`@note` Use the required transfer size. The GC bridge limits size to `round_up`(max(`board_bytes`, `field_bytes`), 16); larger scratch requests return `api_valueOutOfRange`.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_distancefield_importlinearbuffer_gc : buffer:DistanceFieldBuffer.t -> bytes:bytes -> size:int32 -> int32

WASM ABI: `i32 bc_DistanceField_ImportLinearBuffer_gc(arrayref buffer, arrayref bytes, i32 size);`

Load row-major `Abi_uint16.t` values in native byte order (little-endian on WASM).

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `DistanceFieldBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `field_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `DistanceFieldBuffer.t`.
- `@param bytes`: `bytes` — Source byte buffer. Memory: a non-null mutable WasmGC i8 array of exactly size bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `Abi_uint8.t`.
- `@param size`: `int32` — Byte capacity, not element count. Linear storage is width * height little-endian `Abi_uint16.t` values (2 bytes each), row-major. The complete size-byte guest range must be valid. Too little capacity returns `api_bufferTooSmall`; extra capacity is not copied.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Output storage need not be initialized before this call. Import operations require initialized source bytes.

`@note` Use the required transfer size. The GC bridge limits size to `round_up`(max(`board_bytes`, `field_bytes`), 16); larger scratch requests return `api_valueOutOfRange`.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_distancefield_exportrawbuffer_gc : buffer:DistanceFieldBuffer.t -> bytes:bytes -> size:int32 -> int32

WASM ABI: `i32 bc_DistanceField_ExportRawBuffer_gc(arrayref buffer, arrayref bytes, i32 size);`

Copy physical storage, including padding.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `DistanceFieldBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `field_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `DistanceFieldBuffer.t`.
- `@param bytes`: `bytes` — Destination byte buffer. Memory: a non-null mutable WasmGC i8 array of exactly size bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `Abi_uint8.t`.
- `@param size`: `int32` — Byte capacity, not element count. Raw storage includes padding and requires `field_bytes` bytes. The complete size-byte guest range must be valid. Too little capacity returns `api_bufferTooSmall`; extra capacity is not copied.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Use the required transfer size. The GC bridge limits size to `round_up`(max(`board_bytes`, `field_bytes`), 16); larger scratch requests return `api_valueOutOfRange`.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_distancefield_exportlinearbuffer_gc : buffer:DistanceFieldBuffer.t -> bytes:bytes -> size:int32 -> int32

WASM ABI: `i32 bc_DistanceField_ExportLinearBuffer_gc(arrayref buffer, arrayref bytes, i32 size);`

Copy row-major `Abi_uint16.t` values in native byte order (little-endian on WASM).

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `DistanceFieldBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `field_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `DistanceFieldBuffer.t`.
- `@param bytes`: `bytes` — Destination byte buffer. Memory: a non-null mutable WasmGC i8 array of exactly size bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `Abi_uint8.t`.
- `@param size`: `int32` — Byte capacity, not element count. Linear storage is width * height little-endian `Abi_uint16.t` values (2 bytes each), row-major. The complete size-byte guest range must be valid. Too little capacity returns `api_bufferTooSmall`; extra capacity is not copied.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Use the required transfer size. The GC bridge limits size to `round_up`(max(`board_bytes`, `field_bytes`), 16); larger scratch requests return `api_valueOutOfRange`.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_distancefield_print_gc : buffer:DistanceFieldBuffer.t -> int32

WASM ABI: `i32 bc_DistanceField_Print_gc(arrayref buffer);`

Print logical tile values.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `DistanceFieldBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `field_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `DistanceFieldBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_distancefield_get_gc : buffer:DistanceFieldBuffer.t -> x:int32 -> y:int32 -> value:int32 -> int32

WASM ABI: `i32 bc_DistanceField_Get_gc(arrayref buffer, i32 x, i32 y, i32 value);`

Read one logical distance.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `DistanceFieldBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `field_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `DistanceFieldBuffer.t`.
- `@param x`: `int32`
- `@param y`: `int32`
- `@param value`: `int32` — Address of a `Abi_uint16.t` output (2 bytes, aligned to 2). Memory: at least 2 bytes in exported linear memory; 2-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_distancefield_set_gc : buffer:DistanceFieldBuffer.t -> x:int32 -> y:int32 -> value:int32 -> int32

WASM ABI: `i32 bc_DistanceField_Set_gc(arrayref buffer, i32 x, i32 y, i32 value);`

Write one logical distance.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param buffer`: `DistanceFieldBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `field_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `DistanceFieldBuffer.t`.
- `@param x`: `int32`
- `@param y`: `int32`
- `@param value`: `int32` — The value to write, passed directly (not an address). An integer in 0..65535; 65535 represents unreachable/uncomputed.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Set preserves other tiles. Initialize the full field with a compute or import operation before reading those tiles.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_distancefield_copy_gc : source:DistanceFieldBuffer.t -> destination:DistanceFieldBuffer.t -> int32

WASM ABI: `i32 bc_DistanceField_Copy_gc(arrayref source, arrayref destination);`

Copy physical storage, including padding.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param source`: `DistanceFieldBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `field_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `DistanceFieldBuffer.t`.
- `@param destination`: `DistanceFieldBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `field_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `DistanceFieldBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_distancefield_copywithmask_gc : source:DistanceFieldBuffer.t -> mask:BitboardBuffer.t -> destination:DistanceFieldBuffer.t -> int32

WASM ABI: `i32 bc_DistanceField_CopyWithMask_gc(arrayref source, arrayref mask, arrayref destination);`

Copy only logical tiles selected by `in_mask`, preserving every unselected destination value. Mask padding is ignored and destination padding is preserved.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param source`: `DistanceFieldBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `field_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `DistanceFieldBuffer.t`.
- `@param mask`: `BitboardBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param destination`: `DistanceFieldBuffer``.t` — Memory: a non-null mutable WasmGC i8 array of exactly `field_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `DistanceFieldBuffer.t`.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Initialize destination before copying: unselected logical tiles and destination padding keep their previous values.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_distancefield_computewithexpansioncount_gc : walls:BitboardBuffer.t -> roots:BitboardBuffer.t -> visited:BitboardBuffer.t ->…

WASM ABI: `i32 bc_DistanceField_ComputeWithExpansionCount_gc(arrayref walls, arrayref roots, arrayref visited, arrayref distances, i32 max_distance, i32 count);`

Compute king-move distances using reusable thread-local scratch.  Count attempted expansions, including the final empty one.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param walls`: `BitboardBuffer``.t` — Input obstacle bitboard. Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param roots`: `BitboardBuffer``.t` — Input seed bitboard. Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param visited`: `BitboardBuffer``.t` — Output visited bitboard. Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param distances`: `DistanceFieldBuffer``.t` — Output distance field. Memory: a non-null mutable WasmGC i8 array of exactly `field_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `DistanceFieldBuffer.t`.
- `@param max_distance`: `int32` — Integer limit in 0..65535.
- `@param count`: `int32` — Address of a `Abi_uint16.t` expansion count, not `Abi_uint32.t`. Unreachable/uncomputed tiles have distance 65535. Memory: at least 2 bytes in exported linear memory; 2-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Output storage need not be initialized before this call. Import operations require initialized source bytes.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_bc_distancefield_computetowithexpansioncount_gc : walls:BitboardBuffer.t -> roots:BitboardBuffer.t -> destinations:BitboardBuffe…

WASM ABI: `i32 bc_DistanceField_ComputeToWithExpansionCount_gc(arrayref walls, arrayref roots, arrayref destinations, arrayref visited, arrayref distances, i32 max_distance, i32 count);`

Compute until all destinations are reached or the frontier stops using reusable thread-local scratch.  Count attempted expansions, including the final empty one.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@param walls`: `BitboardBuffer``.t` — Input obstacle bitboard. Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param roots`: `BitboardBuffer``.t` — Input seed bitboard. Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param destinations`: `BitboardBuffer``.t` — Input target bitboard. Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param visited`: `BitboardBuffer``.t` — Output visited bitboard. Memory: a non-null mutable WasmGC i8 array of exactly `board_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `BitboardBuffer.t`.
- `@param distances`: `DistanceFieldBuffer``.t` — Output distance field. Memory: a non-null mutable WasmGC i8 array of exactly `field_bytes` bytes. It is an array reference, not a linear-memory address; the host supplies aligned scratch storage. Storage: `DistanceFieldBuffer.t`.
- `@param max_distance`: `int32` — Integer limit in 0..65535.
- `@param count`: `int32` — Address of a `Abi_uint16.t` expansion count, not `Abi_uint32.t`. Unreachable/uncomputed tiles have distance 65535. Memory: at least 2 bytes in exported linear memory; 2-byte alignment. Nonempty ranges must start at a positive address.
- `@return`: `int32` — 0 on success; an engine error code on failure, or -1 for invalid guest memory. Read outputs only on success.

`@note` Output storage need not be initialized before this call. Import operations require initialized source bytes.

`@note` WasmGC variant: `arrayref` means (ref null array). Each array parameter is staged in a separate aligned host buffer, so input/output array references may be identical. Use distinct arrays for independent outputs: later write-backs would overwrite an earlier result in a shared array. Scalar and position outputs still use linear memory. See Bitboards, distance fields and WasmGC above.

Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- ### val host_yield : unit -> unit

WASM ABI: `void yield();`

End this bot's turn voluntarily. Execution suspends at the call and resumes immediately after it when this bot next receives input; stack and memory persist. A draft and each physical champion use separate instances. Returning from `_start` exits the instance instead of yielding.

The OCaml wrapper below packs scalar arguments for the WAT bridge and decodes its result. Pointer arguments are linear-memory offsets; WasmGC buffers are OCaml `bytes`. Record definitions provide types and byte decoders for reading outputs.

- `@return`: `unit`Import and use in OCamlOCaml declaration and call

```

```

WAT wrapper: add this import and function to bridge.wat

```

```

Shared OCaml bridge support
- - 
- 
- 
- 
-← PreviousBot API reference←→ turn pagesNext →Errors