# h_shortcut_off2: control for h_shortcut (v2)

Byte-identical to `bots/h_shortcut` (v2) except `SHORTCUT_FIX = False`: same module size and the same fuel until the patched branch runs, where the logic is then c2_respawn's. Isolates the fix from module-size fuel chaos (report: results/experiments/2026-11-01-h_shortcut.md).
