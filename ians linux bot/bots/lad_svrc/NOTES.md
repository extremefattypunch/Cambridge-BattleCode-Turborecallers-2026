# lad_svrc: draft-only imitation of tb_merge_b

Copy of bots/tb_merge_b (Sprint 3 / website v2). The ONLY change is the second PRIORITY list in src/draft.py:

    PRIORITY = [D.STELLAR, D.VARG, D.RYTH, D.CASSI_AND_ISSAC, D.TAVI, D.PRISM, D.REN, D.VESPER_VALE, D.VENDETTA, D.MARCELLA, D.HEART_OF_RUIN, D.WILLOW]

Purpose: test whether ladder-common drafts beat tb_merge_b's meta draft (Vesper, Vendetta, Marcella, HoR, Ryth) under identical bot logic.
Caveat: champions without a BRUISER_PLAN entry (Varg, Stellar, Cassi, Issac, Ren, Prism) fall back to the default jungle/monster Strength item build.
Results vs tb_merge_b: see matches/tb_merge_b-vs-lad_svrc*.
