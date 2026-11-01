"""Trace wrapper (h_spawnheal analysis only): bot.py is byte-identical to its source bot.
Logs per champion: engage turns (handle_enemies picked a target, or a stand-and-strike) and
whether the target stood on / next to its own spawn; spawn_healed skips (if the bot has it).
Prints go through cambc.debug_block (fuel-free in debug builds)."""
import cambc
from cambc import game_map, Team
import draft
import bot as B
from bot import Bot

_S = {"esp": None, "near": None}
ST = {"eng": 0, "on": 0, "nr": 0, "skip": 0, "turns": 0}
TURN = {"f": None}


def flag(e):
    try:
        if _S["esp"] is None:
            _S["esp"] = game_map.spawn_region(Team.ENEMY).copy()
            _S["near"] = B.dilate(_S["esp"], 1)
        ep = e.position()
        if _S["esp"].is_set(ep):
            return 2
        if _S["near"].is_set(ep):
            return 1
    except Exception:
        pass
    return 0


def mark(e):
    if TURN["f"] is None:
        TURN["f"] = (flag(e), int(e.health()) if hasattr(e, "health") else -1)


_wf = Bot.write_focus
_st = Bot.strike


def write_focus(self, e):
    mark(e)
    return _wf(self, e)


def strike(self, me, target, incoming):
    mark(target)
    return _st(self, me, target, incoming)


Bot.write_focus = write_focus
Bot.strike = strike
if hasattr(Bot, "spawn_healed"):
    _sh = Bot.spawn_healed

    def spawn_healed(self, e, eh, burst):
        r = _sh(self, e, eh, burst)
        if r:
            ST["skip"] += 1
        return r

    Bot.spawn_healed = spawn_healed


def log(msg):
    cambc.debug_block(lambda: print(msg, flush=True))


def main():
    bot = Bot()
    last = -1
    while True:
        try:
            if cambc.is_draft():
                draft.play()
            else:
                TURN["f"] = None
                bot.play_turn()
                bot.pm_end("turn_end")
                bot.build_static_fields()
                bot.pm_end("sfields")
                bot.prof()
                rnd = cambc.round_number()
                ST["turns"] += 1
                f = TURN["f"]
                if f is not None:
                    ST["eng"] += 1
                    if f[0] == 2:
                        ST["on"] += 1
                    elif f[0] == 1:
                        ST["nr"] += 1
                    log("E %d %d %d %d" % (rnd, bot.slot, f[0], f[1]))
                if rnd // 50 != last:
                    last = rnd // 50
                    log("S %d %d eng=%d on=%d nr=%d skip=%d turns=%d tz=%d off=%d" % (
                        rnd, bot.slot, ST["eng"], ST["on"], ST["nr"], ST["skip"], ST["turns"],
                        int(getattr(bot, "turret_zone", None) is not None),
                        int(getattr(bot, "sh_off", False))))
        except Exception as error:
            print(f"bot error: {error}", flush=True)

        cambc.end_turn()


if __name__ == "__main__":
    main()
