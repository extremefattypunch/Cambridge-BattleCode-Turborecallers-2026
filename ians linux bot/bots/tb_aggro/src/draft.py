import cambc

# Melee bruisers first: melee can walk and hit in the same turn (good for chasing
# and for camp farming), and they have the highest health/strength.
# ChampionDraft ids: RYTH 0, VESPER_VALE 1, VENDETTA 2, CASSI_AND_ISSAC 3, STELLAR 4,
# PRISM 5, MARCELLA 6, WILLOW 7, REN 8, VARG 9, TAVI 10, HEART_OF_RUIN 11
PREFERENCE = [2, 9, 0, 6, 10, 8, 1, 7, 4, 5, 3]


def play():
    chosen = cambc.draft.current_draft(cambc.Team.ALLY)
    for pick in PREFERENCE:
        if pick not in chosen:
            try:
                cambc.draft.pick(pick)
                return
            except Exception as error:  # unavailable pick: try the next one
                print("draft pick failed", pick, error)
