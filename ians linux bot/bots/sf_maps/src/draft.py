"""Draft: deterministic priority list of strong solo camp farmers.

Picks are simultaneous and duplicates with the enemy are allowed, so we simply
take the best champion we have not picked yet.  Dash champions come early so
hole-separated maps can be crossed without TP crystals.
"""
import cambc
import mapprofile

D = cambc.ChampionDraft
# Vendetta: 70 str melee + dash; Varg: splash + shield (wolves do ~0 net dmg);
# Ryth: 1200 hp + area stun; Vesper Vale: +33% gold + dash; Marcella: 1200 hp;
# Heart of Ruin: shield + damaging dash; Tavi/Ren as fallbacks.
PRIORITY = [D.VENDETTA, D.VARG, D.RYTH, D.VESPER_VALE, D.MARCELLA,
            D.HEART_OF_RUIN, D.TAVI, D.REN, D.WILLOW, D.STELLAR, D.PRISM,
            D.CASSI_AND_ISSAC]


_PROFILE_DONE = [False]
MAP_DEBUG = False


def submit_profile():
    """sf_maps: map-archetype profile -> draft memory (once per draft)."""
    if _PROFILE_DONE[0]:
        return
    _PROFILE_DONE[0] = True
    try:
        prof = mapprofile.compute()
        cambc.draft_memory.submit(prof.encode())
        if MAP_DEBUG:
            print("PROFILE", prof, flush=True)
            for i, g in enumerate(cambc.game_map.camp_groups()):
                print("G", i, [ (int(c.kind()), c.spawn_position()) for c in g.camps()][:4], len(g),
                      g.gem_value(), g.gold_value(), flush=True)
    except Exception as error:
        print("profile failed", error, flush=True)


def play():
    chosen = set(int(c) for c in cambc.draft.current_draft(cambc.Team.ALLY))
    submit_profile()
    for pick in PRIORITY:
        if int(pick) in chosen:
            continue
        try:
            cambc.draft.pick(pick)
            return
        except Exception as error:
            print("draft pick failed", int(pick), error, flush=True)
            continue
