"""Map-aware draft: pick strong camp-clearing / survivable champions.

ChampionDraft ids: RYTH 0, VESPER_VALE 1, VENDETTA 2, CASSI_AND_ISSAC 3, STELLAR 4,
PRISM 5, MARCELLA 6, WILLOW 7, REN 8, VARG 9, TAVI 10, HEART_OF_RUIN 11.
"""
import cambc
from cambc import game_map

D = cambc.ChampionDraft

# Core priority: high sustained damage + survivability against camps.
BASE_ORDER = [D.VENDETTA, D.VARG, D.CASSI_AND_ISSAC, D.RYTH, D.MARCELLA, D.TAVI,
              D.WILLOW, D.REN, D.VESPER_VALE, D.HEART_OF_RUIN, D.PRISM, D.STELLAR]

_failed = set()


def _map_profile():
    """Count camp kinds over the full map (draft has full map view)."""
    counts = [0] * 6
    groups = 0
    try:
        for group in game_map.camp_groups():
            groups += 1
            for camp in group.camps():
                try:
                    counts[int(camp.kind())] += 1
                except Exception:
                    pass
    except Exception:
        pass
    return counts, groups


def play():
    chosen = list(cambc.draft.current_draft(cambc.Team.ALLY))
    order = list(BASE_ORDER)
    counts, groups = _map_profile()
    holes = 0
    try:
        holes = game_map.holes().count()
    except Exception:
        pass
    # Hole-heavy maps: dash champions can cross gaps.
    if holes > 40:
        for pick in (D.VESPER_VALE, D.REN):
            if pick in order:
                order.remove(pick)
            order.insert(3, pick)
    try:
        if not chosen:
            cambc.draft_memory.submit(bytes([min(255, c) for c in counts]) + bytes([min(255, groups)]))
    except Exception:
        pass
    for pick in order:
        if pick in chosen or pick in _failed:
            continue
        try:
            cambc.draft.pick(pick)
            return
        except Exception as error:
            print("draft pick failed", pick, error, flush=True)
            _failed.add(pick)
    for pick in range(11):
        if pick not in chosen:
            try:
                cambc.draft.pick(pick)
                return
            except Exception:
                pass
