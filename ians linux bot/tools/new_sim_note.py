#!/usr/bin/env python3.12
"""Start the note for a new simulated match, BEFORE the test runs.

Usage:
    python3.12 tools/new_sim_note.py CANDIDATE --vs CHAMPION --prev PARENT_FOLDER [--tag TAG]

Creates results/simulated-matches/<YYYY-MM-DD>_<HHMM UTC now>_<CANDIDATE>/notes.md from the part of
results/simulated-matches/TEMPLATE.md below its '---' line, fills in the header (candidate, champion,
the parent simulated match it builds on, the games folder) and prints the note's path. The agent then
writes sections 1 (the parent match, analysed) and 2 (the hypothesis and its evidence) and commits them
before any game runs; sections 3-5 come after the test.
PARENT_FOLDER is a folder name under results/simulated-matches/ (usually the champion's gate match);
see results/simulated-matches/INDEX.md.
"""
import argparse
import datetime
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIM = os.path.join(ROOT, "results", "simulated-matches")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("candidate")
    ap.add_argument("--vs", required=True, help="the champion it is tested against")
    ap.add_argument("--prev", required=True, help="parent simulated-match folder")
    ap.add_argument("--tag", default=None, help="eval.py tag of the main test (default <candidate>-all)")
    args = ap.parse_args()
    for b in (args.candidate, args.vs):
        if not os.path.isdir(os.path.join(ROOT, "bots", b)):
            sys.exit(f"no such bot: bots/{b}")
    if not os.path.isfile(os.path.join(SIM, args.prev, "notes.md")):
        sys.exit(f"no such simulated match: results/simulated-matches/{args.prev}/notes.md")
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d_%H%M")
    folder = os.path.join(SIM, f"{stamp}_{args.candidate}")
    os.makedirs(folder, exist_ok=False)
    template = open(os.path.join(SIM, "TEMPLATE.md"), encoding="utf-8").read()
    body = template.split("\n---\n", 1)[1].lstrip("\n")
    date, hhmm = stamp.split("_")
    body = (body.replace("<candidate>", args.candidate).replace("<champion>", args.vs)
                .replace("<date> <HH:MM> UTC", f"{date} {hhmm[:2]}:{hhmm[2:]} UTC")
                .replace("[`<folder>`](../<folder>/notes.md)", f"[`{args.prev}`](../{args.prev}/notes.md)", 1)
                .replace("`matches/<tag>/`", f"`matches/{args.tag or args.candidate + '-all'}/`"))
    path = os.path.join(folder, "notes.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    print(os.path.relpath(path, ROOT))


if __name__ == "__main__":
    main()
