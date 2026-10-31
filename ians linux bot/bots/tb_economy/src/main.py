"""Dispatch draft and gameplay; a failed turn is logged and still yields."""
import cambc
import draft
from bot import Bot

try:
    import traceback
except Exception:  # pragma: no cover
    traceback = None


def main():
    bot = Bot()
    errors = 0
    while True:
        try:
            if cambc.is_draft():
                draft.play()
            else:
                bot.play_turn()
        except Exception as error:
            errors += 1
            if errors <= 20:
                if traceback is not None:
                    try:
                        print("bot error:", traceback.format_exc(), flush=True)
                    except Exception:
                        print(f"bot error: {error}", flush=True)
                else:
                    print(f"bot error: {error}", flush=True)

        cambc.end_turn()


if __name__ == "__main__":
    main()
