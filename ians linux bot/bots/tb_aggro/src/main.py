"""Dispatch draft and gameplay; a failed turn is logged and still yields."""
import cambc
import draft
from bot import Bot

_errors = 0


def main():
    global _errors
    bot = Bot()
    while True:
        try:
            if cambc.is_draft():
                draft.play()
            else:
                bot.play_turn()
        except Exception as error:
            _errors += 1
            if _errors <= 20:
                try:
                    import traceback
                    traceback.print_exc()
                except Exception:
                    print(f"bot error: {error}", flush=True)

        cambc.end_turn()


if __name__ == "__main__":
    main()
