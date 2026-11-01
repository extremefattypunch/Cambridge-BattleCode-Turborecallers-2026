# h_shortcut_off: control for h_shortcut

Byte-identical to `bots/h_shortcut` except `SHORTCUT_FIX = False` (same module size, so the same fuel until the patched branch is reached; with the flag off the logic is c2_respawn's). Used to isolate the fix from module-size fuel chaos (report: results/simulated-matches/2026-11-01_0531_h_shortcut/notes.md).
