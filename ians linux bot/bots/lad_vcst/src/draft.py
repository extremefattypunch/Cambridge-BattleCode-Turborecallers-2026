"""Draft: deterministic priority list of strong solo camp farmers.

Picks are simultaneous and duplicates with the enemy are allowed, so we simply
take the best champion we have not picked yet.  Dash champions come early so
hole-separated maps can be crossed without TP crystals.
"""
import cambc

D = cambc.ChampionDraft
# Vendetta: 70 str melee + dash; Varg: splash + shield (wolves do ~0 net dmg);
# Ryth: 1200 hp + area stun; Vesper Vale: +33% gold + dash; Marcella: 1200 hp;
# Heart of Ruin: shield + damaging dash; Tavi/Ren as fallbacks.
PRIORITY = [D.VENDETTA, D.VARG, D.RYTH, D.VESPER_VALE, D.MARCELLA,
            D.HEART_OF_RUIN, D.TAVI, D.REN, D.WILLOW, D.STELLAR, D.PRISM,
            D.CASSI_AND_ISSAC]
# sf_draft: top-20 meta core (INSIGHTS 2.1): all 20 top teams draft HoR, Marcella,
# Vendetta and Vesper; Ryth (or Tavi) fifth.  Carries (Vesper, Marcella) and the
# dash champions come first so 3-pick maps still get two dashes.
# imitation (ladder-common draft); everything else identical to tb_merge_b
PRIORITY = [D.VARG, D.CASSI_AND_ISSAC, D.STELLAR, D.TAVI, D.REN, D.RYTH, D.VESPER_VALE, D.VENDETTA, D.MARCELLA, D.HEART_OF_RUIN, D.WILLOW, D.PRISM]


def play():
    chosen = set(int(c) for c in cambc.draft.current_draft(cambc.Team.ALLY))
    try:
        cambc.draft_memory.submit(b"tb_splitfarm v1")
    except Exception:
        pass
    for pick in PRIORITY:
        if int(pick) in chosen:
            continue
        try:
            cambc.draft.pick(pick)
            return
        except Exception as error:
            print("draft pick failed", int(pick), error, flush=True)
            continue
