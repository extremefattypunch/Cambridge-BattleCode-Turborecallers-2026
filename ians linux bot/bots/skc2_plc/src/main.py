"""Dispatch draft and gameplay; a failed turn is logged and still yields."""
import cambc
import draft
from bot import Bot

# skc2_plc (skeptic placebo replicate of c2_respawn, NOT a candidate): c2_respawn plus a fixed pure-Python fuel
# burn at the start of every play turn. The result is discarded and touches no state, so the
# bot's decisions can differ from q24_combo's only through fuel-dependent branches
# (FUEL_* floors in bot.py, static-field build pacing, fuel-exhaustion suspensions).
# Measured on 00anvil (31 Oct): _burn(100) costs ~67k fuel (~2.7% of the 2.5M turn budget);
# _burn(1000) ~0.98M and _burn(2000) ~2.07M, so "a few thousand" iterations would be a handicap.
PLACEBO_BURN = 100


def _burn(n):
    s = 0
    for i in range(n):
        s += i
    return s


def main():
    bot = Bot()
    while True:
        try:
            if cambc.is_draft():
                draft.play()
            else:
                _burn(PLACEBO_BURN)  # placebo_b: fuel only, result discarded
                bot.play_turn()
                bot.pm_end("turn_end")
                bot.build_static_fields()
                bot.pm_end("sfields")
                bot.prof()
        except Exception as error:
            print(f"bot error: {error}", flush=True)
            if getattr(bot, "debug_tb", False):
                import sys, traceback
                traceback.print_exc(file=sys.stdout)

        cambc.end_turn()


if __name__ == "__main__":
    main()
