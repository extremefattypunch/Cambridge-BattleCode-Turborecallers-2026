<!-- source: https://2026a.battlecode.co.uk/game/docs/errors -->
Handbook/Bot API

# Errors

On this page

Engine error codes

Engine errors appear as error codes. These can be caught and translated to text:

Error messages and code names

```
let () =
  try
    ignore (Cambc.round_number ())
  with Cambc.Cambc_error (code, message) ->
    prerr_endline message;
    prerr_endline (Cambc.Error_code.to_string code)

let text = Cambc.Error_code.to_string Cambc.Error_code.Api_not_in_vision

(* The public OCaml SDK has no integer-to-error conversion.
   Look up a numeric code, such as 97, in the table below. *)
```

## Engine error codes#

Find an error code

134 of 134 error codes

| Enum name | Value | Description |
| --- | --- | --- |
| Success | 0 | No error. |
| Invalid_handle | 1 | A handle does not refer to a live engine object. |
| Out_of_memory | 2 | The engine could not allocate memory. |
| File_not_found | 3 | A requested file does not exist. |
| Null_pointer | 4 | A required pointer argument was null. |
| Invalid_argument | 5 | An argument was invalid, misaligned or overlapping. |
| Map_parse_error | 6 | A map file could not be parsed. |
| Invalid_map_file | 7 | A map file is malformed. |
| Invalid_map_version | 8 | A map file has an unsupported version. |
| Replay_parse_error | 9 | A replay file could not be parsed. |
| Invalid_replay_file | 10 | A replay file is malformed. |
| Invalid_replay_version | 11 | A replay file has an unsupported version. |
| Invalid_draft | 12 | The draft request is invalid. |
| Draft_not_drafting | 13 | The draft is not in progress. |
| Draft_duplicate_champion | 14 | The champion has already been picked. |
| Draft_invalid_round | 15 | The draft request does not belong to the current pick round. |
| Draft_unavailable | 16 | Draft information is unavailable in the current phase. |
| Already_initialized | 17 | The object has already been initialised. |
| Invalid_action | 18 | The action is not allowed. |
| Invalid_action_memory_bad_range | 19 | A memory write falls outside the buffer. |
| Invalid_action_memory_draft_frozen | 20 | Draft memory is read-only after the draft. |
| Invalid_action_move_cant_move | 21 | The champion cannot move this turn. |
| Invalid_action_move_bad_destination | 22 | The destination is not a legal landing tile. |
| Invalid_action_spell_cast_invalid_source | 23 | The caster cannot cast spells. |
| Invalid_action_spell_cast_invalid_slot | 24 | The ability slot does not exist. |
| Invalid_action_spell_cast_no_ability | 25 | The slot has no ability. |
| Invalid_action_spell_cast_cant_cast | 26 | The champion cannot cast this turn. |
| Invalid_action_spell_cast_already_cast | 27 | The champion has already cast a spell this turn. |
| Invalid_action_spell_cast_on_cooldown | 28 | The ability is on cooldown. |
| Invalid_action_spell_cast_no_charges | 29 | The ability has no charges left. |
| Invalid_action_spell_cast_bad_target | 30 | The target is not valid for this ability. |
| Invalid_action_spell_cast_out_of_range | 31 | The target is out of the ability's range. |
| Invalid_action_spell_cast_bad_destination | 32 | The ability's destination tile is not legal. |
| Invalid_action_cant_act | 33 | The champion cannot act, for example while stunned. |
| Invalid_action_is_recalling | 34 | The action is not allowed while recalling. |
| Invalid_action_is_submitting_gems | 35 | The action is not allowed while tributing gems. |
| Invalid_action_move_already_moved | 36 | The champion has already moved this turn. |
| Invalid_action_move_out_of_range | 37 | The destination is beyond the champion's movement range. |
| Invalid_action_move_unreachable | 38 | No legal path reaches the destination. |
| Invalid_action_attack_invalid_source | 39 | The attacker cannot attack. |
| Invalid_action_attack_cant_attack | 40 | The champion cannot attack this turn. |
| Invalid_action_attack_already_attacked | 41 | The champion has already attacked this turn. |
| Invalid_action_attack_bad_target | 42 | The target cannot be attacked. |
| Invalid_action_attack_out_of_range | 43 | The target is out of attack range. |
| Invalid_action_recall_cant_channel | 44 | The champion cannot start a recall now. |
| Invalid_action_submit_gems_cant_channel | 45 | The champion cannot start a tribute now. |
| Invalid_action_submit_gems_no_gems | 46 | The champion carries no gems. |
| Invalid_action_submit_gems_bad_altar | 47 | The position is not an altar. |
| Invalid_action_submit_gems_out_of_range | 48 | The altar is out of tribute range. |
| Invalid_action_buy_item_not_on_spawn | 49 | Items can only be bought on spawn or while dead. |
| Invalid_action_buy_item_invalid_item | 50 | The item does not exist. |
| Invalid_action_buy_item_invalid_count | 51 | The purchase count is invalid. |
| Invalid_action_buy_item_not_enough_gold | 52 | The champion cannot afford the purchase. |
| Invalid_action_buy_item_inventory_full | 53 | The inventory has no room for the item. |
| Invalid_action_buy_item_stats_overflow | 54 | The purchase would overflow a stat. |
| Invalid_action_buy_consumable_not_on_spawn | 55 | Consumables can only be bought on spawn or while dead. |
| Invalid_action_buy_consumable_invalid_type | 56 | The consumable does not exist. |
| Invalid_action_buy_consumable_invalid_count | 57 | The purchase count is invalid. |
| Invalid_action_buy_consumable_inventory_full | 58 | The champion already carries that consumable. |
| Invalid_action_buy_consumable_not_enough_gold | 59 | The champion cannot afford the consumable. |
| Invalid_action_use_consumable_invalid_type | 60 | The consumable does not exist. |
| Invalid_action_use_consumable_not_owned | 61 | The champion does not carry that consumable. |
| Invalid_action_place_ward_no_charges | 62 | The ward trinket has no charge. |
| Invalid_action_place_ward_cant_place | 63 | The champion cannot place a ward now. |
| Invalid_action_place_ward_bad_destination | 64 | The ward tile is not legal. |
| Invalid_action_place_ward_out_of_range | 65 | The ward tile is out of placement range. |
| Map_set_team_aspawn_area_bad_position | 66 | Map editing: bad spawn-area position. |
| Map_add_bush_bad_position | 67 | Map editing: bad bush position. |
| Map_remove_bush_bad_position | 68 | Map editing: bad bush position. |
| Map_add_wall_bad_position | 69 | Map editing: bad wall position. |
| Map_remove_wall_bad_position | 70 | Map editing: bad wall position. |
| Map_add_hole_bad_position | 71 | Map editing: bad hole position. |
| Map_remove_hole_bad_position | 72 | Map editing: bad hole position. |
| Map_add_altar_bad_position | 73 | Map editing: bad altar position. |
| Map_remove_altar_bad_position | 74 | Map editing: bad altar position. |
| Map_get_bush_bad_position | 75 | The bush query position is outside the map. |
| Map_get_wall_bad_position | 76 | The wall query position is outside the map. |
| Map_get_hole_bad_position | 77 | The hole query position is outside the map. |
| Map_get_altar_bad_position | 78 | The altar query position is outside the map. |
| Map_get_camp_handle_at_bad_position | 79 | The camp query position is outside the map. |
| Map_add_camp_bad_position | 80 | Map editing: bad camp position. |
| Map_set_camp_bad_position | 81 | Map editing: bad camp position. |
| Invalid_action_champion_teleport_bad_destination | 82 | The teleport destination is not a legal landing tile. |
| Invalid_action_respawn_group_blocked_spawn | 83 | A camp group's respawn tiles are blocked. |
| Invalid_action_camp_teleport_bad_destination | 84 | A camp teleport destination is not legal. |
| Timeline_bad_seek_position | 85 | Replay timeline: bad seek position. |
| Timeline_bad_seek_substep | 86 | Replay timeline: bad seek substep. |
| Api_no_map | 87 | No map is loaded. |
| Managed_resources_bad_position | 88 | A bitboard or distance-field position is outside the map. |
| Managed_resources_bad_radius | 89 | A radius argument is invalid. |
| Managed_resources_aliasing | 90 | Input and output buffers alias where they must not. |
| Managed_resources_metadata_mismatch | 91 | A buffer was built for different map dimensions. |
| Managed_resources_opaque_origin | 92 | A buffer was not created by the engine. |
| Api_invalid_team | 93 | The team is invalid. |
| Api_invalid_perspective | 94 | The query is not allowed from this bot's perspective. |
| Api_not_initialized | 95 | The API is not initialised. |
| Api_bad_position | 96 | The position is outside the map. |
| Api_not_in_vision | 97 | The target is not in this champion's vision. |
| Api_not_found | 98 | Nothing matches the query. |
| Api_invalid_camp_group | 99 | The camp group is invalid. |
| Api_invalid_camp_info | 100 | The camp information is invalid. |
| Api_invalid_camp | 101 | The camp is invalid. |
| Api_invalid_champion | 102 | The champion is invalid. |
| Api_invalid_ward | 103 | The ward is invalid. |
| Api_invalid_ability | 104 | The ability is invalid. |
| Api_not_teammate | 105 | The champion is not on this bot's team. |
| Api_camp_group_not_waiting_to_respawn | 106 | The camp group is not waiting to respawn. |
| Api_champion_alive | 107 | The champion is alive, so it has no respawn timer. |
| Api_invalid_champion_type | 108 | The champion type is invalid. |
| Api_invalid_camp_type | 109 | The camp type is invalid. |
| Api_value_out_of_range | 110 | A value is out of range. |
| Api_buffer_too_small | 111 | The output buffer is too small. |
| Api_not_owner | 112 | Only the champion running this bot may act for it. |
| Invalid_action_recall_already_used | 113 | A recall has already been started this turn. |
| Invalid_action_submit_gems_already_used | 114 | A tribute has already been started this turn. |
| Invalid_action_cancel_channel_not_channeling | 115 | The champion is not channelling. |
| Invalid_action_cancel_channel_already_used | 116 | A channel has already been cancelled this turn. |
| Invalid_action_place_ward_ally_ward_present | 117 | An allied ward already occupies the tile. |
| Invalid_action_altar_lock_bad_altar | 118 | The position is not an altar. |
| Invalid_action_altar_lock_out_of_range | 119 | The altar is out of altar-lock range. |
| Invalid_action_altar_lock_already_locked | 120 | The altar is already locked. |
| Invalid_action_is_teleporting | 123 | The action is not allowed while teleporting. |
| Invalid_action_cancel_channel_not_cancellable | 124 | This channel cannot be cancelled. |
| Invalid_action_submit_gems_altar_locked | 125 | The altar is locked by the enemy. |
| Invalid_action_spell_cast_already_moved | 126 | This ability cannot be cast after moving. |
| Invalid_action_move_exclusive_spell_cast | 127 | The champion cannot move after casting this ability. |
| Invalid_action_sell_not_tavi | 128 | Only Tavi can sell items. |
| Invalid_action_sell_invalid_item | 129 | The item does not exist. |
| Invalid_action_sell_not_owned | 130 | The champion does not own that item. |
| Invalid_action_sell_already_sold | 131 | An item has already been sold this turn. |
| Invalid_action_sell_gold_overflow | 132 | The sale would overflow gold. |
| Invalid_action_sell_not_on_spawn | 133 | Items can only be sold on spawn. |
| Draft_already_picked | 134 | A champion has already been selected this draft turn. |
| Draft_no_champion_selected | 135 | Select a champion before ending the draft turn. |

← PreviousWASM API reference←→ turn pagesNext → · ReferenceAgents.md