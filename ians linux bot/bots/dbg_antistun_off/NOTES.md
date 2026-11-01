# dbg_antistun_off: logging-only control for the h_antistun analysis (1 Nov 2026)

Copy of `bots/h_antistun` with `ANTISTUN = False`, so `stun_blocked()` always returns False and
`recall_safe()` returns True as in tb_merge_b. The decisions are tb_merge_b's; only the CHLOG
instrumentation stays (CHS = channel start with the ready-stunner tag `thr`, CHX = outcome).
Purpose: measure how often the champion's tributes/recalls/teleports start within reach of a
ready enemy stunner and how often they are actually cut, i.e. the "before" side of Q15/T19.
Not a candidate. Safe to delete after the h_antistun report.
