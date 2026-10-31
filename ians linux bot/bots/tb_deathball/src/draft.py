"""Deathball draft: tanky melee damage dealers first, a healer, then casters.

Picks are simultaneous and duplicates with the enemy are allowed, so we only
need to avoid our own previous picks.
"""
import cambc

# ChampionDraft ids: RYTH 0, VESPER_VALE 1, VENDETTA 2, CASSI_AND_ISSAC 3, STELLAR 4,
# PRISM 5, MARCELLA 6, WILLOW 7, REN 8, VARG 9, TAVI 10, HEART_OF_RUIN 11
PREFERENCE = (2, 9, 3, 7, 0, 6, 10, 8, 4, 1, 5)


def play():
    chosen = list(cambc.draft.current_draft(cambc.Team.ALLY))
    chosen_ints = set(int(c) for c in chosen)
    try:
        cambc.draft_memory.submit(b"deathball")
    except Exception:
        pass
    for pick in PREFERENCE:
        if pick not in chosen_ints:
            cambc.draft.pick(pick)
            return
    for pick in range(11):
        if pick not in chosen_ints:
            cambc.draft.pick(pick)
            return
