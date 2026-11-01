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
                cambc.debug_block(bot.trace_pre)
                bot.play_turn()
                cambc.debug_block(bot.trace)
                bot.build_static_fields()
        except Exception as error:
            print(f"bot error: {error}", flush=True)

        cambc.end_turn()


if __name__ == "__main__":
    main()
