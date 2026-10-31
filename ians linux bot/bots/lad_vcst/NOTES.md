# lad_vcst: draft-only imitation of tb_merge_b

Copy of bots/tb_merge_b (Sprint 3 / website v2). The ONLY change is the second PRIORITY list in src/draft.py:

    PRIORITY = [D.VARG, D.CASSI_AND_ISSAC, D.STELLAR, D.TAVI, D.REN, D.RYTH, D.VESPER_VALE, D.VENDETTA, D.MARCELLA, D.HEART_OF_RUIN, D.WILLOW, D.PRISM]

Purpose: test whether ladder-common drafts beat tb_merge_b's meta draft (Vesper, Vendetta, Marcella, HoR, Ryth) under identical bot logic.
Caveat: champions without a BRUISER_PLAN entry (Varg, Stellar, Cassi, Issac, Ren, Prism) fall back to the default jungle/monster Strength item build.
Results vs tb_merge_b: see matches/tb_merge_b-vs-lad_vcst*.
