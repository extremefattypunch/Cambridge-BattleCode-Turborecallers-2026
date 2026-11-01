"""Dispatch draft and gameplay; a failed turn is logged and still yields."""
import cambc
import draft
from bot import Bot


def main():
    bot = Bot()
    while True:
        try:
            if cambc.is_draft():
                draft.play()
            else:
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
