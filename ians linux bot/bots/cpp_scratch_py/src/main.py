import cambc
from cambc import game_map

D = cambc.ChampionDraft
PRI = [D.HEART_OF_RUIN, D.RYTH, D.VESPER_VALE, D.VENDETTA, D.MARCELLA, D.TAVI, D.VARG, D.REN, D.WILLOW, D.STELLAR, D.PRISM, D.CASSI_AND_ISSAC]

def main():
    done = False
    while True:
        try:
            if cambc.is_draft():
                chosen = set(int(c) for c in cambc.draft.current_draft(cambc.Team.ALLY))
                for p in PRI:
                    if int(p) in chosen:
                        continue
                    try:
                        cambc.draft.pick(p)
                        break
                    except Exception:
                        continue
            elif not done:
                done = True
                me = cambc.me()
                print("CHAMP", me.champion_name(), flush=True)
                for ab in me.abilities():
                    try:
                        info = ab.info()
                        print("AB", ab.slot(), type(info).__name__, info, flush=True)
                        if hasattr(info, "radius"):
                            print("RADIUS_TYPE", type(info.radius).__name__, info.radius, flush=True)
                            try:
                                for _ in range(info.radius):
                                    pass
                                print("RANGE_OK", flush=True)
                            except Exception as e:
                                print("RANGE_ERR", repr(e), flush=True)
                    except Exception as e:
                        print("ABERR", repr(e), flush=True)
                b = cambc.Bitboard()
                b.draw_chebyshev(cambc.Vec2(8, 8), 1)
                print("POS", [(p.x, p.y) for p in b.positions()], flush=True)
                b2 = cambc.Bitboard()
                b2.draw_chebyshev(cambc.Vec2(5, 3), 1)
                print("POS2", [(p.x, p.y) for p in b2.positions()], flush=True)
        except Exception as error:
            print(f"bot error: {error}", flush=True)
        cambc.end_turn()

if __name__ == "__main__":
    main()
