"""Dispatch draft and gameplay; a failed turn is logged and still yields."""
import cambc
import draft
from bot import Bot

# placebo_a (noise-floor control, NOT a candidate): q24_combo plus one extra, discarded
# cambc.round_number() call at the start of every play turn (~2.5-3.2k fuel, ~0.1% of the
# 2.5M turn budget). It touches no state, so decisions can differ from q24_combo's only
# through fuel-dependent branches (FUEL_* floors, static-field pacing, suspensions).


def main():
    bot = Bot()
    while True:
        try:
            if cambc.is_draft():
                draft.play()
            else:
                cambc.round_number()  # placebo_a: one behaviour-free API read, discarded
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
