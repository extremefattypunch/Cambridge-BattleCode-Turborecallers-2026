#!/usr/bin/env python3
"""Keep match notes in one folder per match, and keep every link to them pointing at the right place.

Layout (see the repo README):
    results/real-matches/<YYYY-MM-DD>_<HHMM>_<opponent>_<group8>/notes.md   one 5-game ladder match vs one team
    results/real-matches/studies/<YYYY-MM-DD>_<HHMM>_<name>/notes.md         studies across many real matches
    results/real-matches/{INSIGHTS,WEAKNESSES,INDEX}.md                       synthesis, ledger, index
    results/simulated-matches/<YYYY-MM-DD>_<HHMM>_<candidate>/notes.md       one simulated match (experiment or gate)
    results/simulated-matches/INDEX.md                                        index, oldest first
Times are UTC: a real match's first game; a simulated note's last change.

Usage:
    python3 tools/organize_notes.py            move notes left in the old places, fix links, rebuild both indexes
    python3 tools/organize_notes.py --dry-run  only print what would move

Old places: results/experiments/*.md (one file per experiment) and results/ladder/scouting/*.md (named
<date>-<group8>-<opponent>.md), plus results/ladder/{INSIGHTS,WEAKNESSES}.md. Compatibility symlinks
(left for workflows that were started before the move) are skipped.
"""
import argparse
import datetime
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
REAL = os.path.join(RES, "real-matches")
SIM = os.path.join(RES, "simulated-matches")
OLD_EXP = os.path.join(RES, "experiments")
OLD_SCOUT = os.path.join(RES, "ladder", "scouting")
LOG = os.path.join(RES, "ladder-games.jsonl")
SITE = "https://2026a.battlecode.co.uk/game/match-groups/"
# Notes that analyse many real matches rather than one simulated match.
STUDIES = {"2026-10-31-ladder-learning.md", "2026-11-01-v3-ladder-study.md"}


def slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:30] or "team"


def utc_stamp(path):
    """When the note was written: its first commit if tracked (checkouts reset mtimes), else its mtime."""
    out = subprocess.run(["git", "log", "--diff-filter=A", "--format=%at", "--", path], cwd=ROOT,
                         capture_output=True, text=True).stdout.split()
    ts = int(out[-1]) if out else os.path.getmtime(path)
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%d_%H%M")


def ladder_sets():
    sets = {}
    if os.path.exists(LOG):
        for line in open(LOG):
            if line.strip():
                r = json.loads(line)
                sets.setdefault(r["group"][:8], []).append(r)
    return sets


def plan_moves():
    moves = []  # (old path, new path)
    if os.path.isdir(OLD_EXP):
        for f in sorted(os.listdir(OLD_EXP)):
            p = os.path.join(OLD_EXP, f)
            if not f.endswith(".md") or os.path.islink(p) or f == "TEMPLATE.md":
                continue
            name = f[len("2026-11-01-"):-3] if re.match(r"\d{4}-\d\d-\d\d-", f) else f[:-3]
            base = REAL + "/studies" if f in STUDIES else SIM
            moves.append((p, os.path.join(base, f"{utc_stamp(p)}_{name}", "notes.md")))
    sets = ladder_sets()
    if os.path.isdir(OLD_SCOUT):
        for f in sorted(os.listdir(OLD_SCOUT)):
            p = os.path.join(OLD_SCOUT, f)
            if not f.endswith(".md") or os.path.islink(p):
                continue
            m = re.match(r"\d{4}-\d\d-\d\d-([0-9a-f]{8})", f)
            rows = sets.get(m.group(1)) if m else None
            if not rows:
                continue
            t = min(r["time"] for r in rows)
            folder = f"{t[:10]}_{t[11:13]}{t[14:16]}_{slug(rows[0]['opp'])}_{m.group(1)}"
            moves.append((p, os.path.join(REAL, folder, "notes.md")))
    for f in ("INSIGHTS.md", "WEAKNESSES.md"):
        p = os.path.join(RES, "ladder", f)
        if os.path.exists(p) and not os.path.islink(p):
            moves.append((p, os.path.join(REAL, f)))
    old = os.path.join(RES, "ladder-analysis-2026-10-31.md")
    if os.path.exists(old) and not os.path.islink(old):
        moves.append((old, os.path.join(REAL, "studies", "2026-10-31_2340_ladder-analysis", "notes.md")))
    return moves


def tracked(path):
    return subprocess.run(["git", "ls-files", "--error-unmatch", path], cwd=ROOT,
                          capture_output=True).returncode == 0


def fix_links(moves):
    """Rewrite references to moved notes in every markdown file of the bot folder and the repo root."""
    rel = lambda p: os.path.relpath(p, ROOT)
    repl = []
    for old, new in moves:
        repl.append((rel(old), rel(new)))                    # results/experiments/x.md
        repl.append((os.path.basename(old), rel(new)))       # bare x.md in tables
    files = [os.path.join(dp, f) for dp, _, fs in os.walk(ROOT) for f in fs
             if f.endswith(".md") and "/.git" not in dp and "/matches" not in dp]
    files.append(os.path.join(os.path.dirname(ROOT), "CLAUDE.md"))
    files.append(os.path.join(os.path.dirname(ROOT), "README.md"))
    changed = 0
    for path in files:
        if not os.path.isfile(path) or os.path.islink(path):
            continue
        text = open(path, encoding="utf-8").read()
        new_text = text
        for a, b in sorted(repl, key=lambda ab: -len(ab[0])):
            new_text = re.sub(r"(?<![\w/.-])" + re.escape(a), b, new_text)
        if new_text != text:
            open(path, "w", encoding="utf-8").write(new_text)
            changed += 1
    return changed


def title(path):
    for line in open(path, encoding="utf-8"):
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def rebuild_indexes():
    os.makedirs(SIM, exist_ok=True)
    os.makedirs(REAL, exist_ok=True)
    sims = sorted(d for d in os.listdir(SIM) if os.path.isfile(os.path.join(SIM, d, "notes.md")))
    with open(os.path.join(SIM, "INDEX.md"), "w") as f:
        f.write("# Simulated matches (the testing pipeline), oldest first\n\n"
                "Generated by `tools/organize_notes.py`. Each folder holds one `notes.md`; the format is in "
                "`TEMPLATE.md` and the workflow in the repo README. Notes before 1 Nov ~06:00 UTC use the older "
                "report format (no 'previous simulated match' section).\n\n"
                "| # | Folder (UTC) | Title |\n|---|---|---|\n")
        for i, d in enumerate(sims, 1):
            f.write(f"| S{i:03d} | [{d}]({d}/notes.md) | {title(os.path.join(SIM, d, 'notes.md'))} |\n")
    sets = ladder_sets()
    reals = sorted((d for d in os.listdir(REAL) if os.path.isfile(os.path.join(REAL, d, "notes.md"))), reverse=True)
    with open(os.path.join(REAL, "INDEX.md"), "w") as f:
        f.write("# Real ladder matches, newest first\n\n"
                "Generated by `tools/organize_notes.py`. One folder per 5-game ladder match against one team, each "
                "with a `notes.md` (format in `TEMPLATE.md`). The synthesis is `INSIGHTS.md`; the ranked weakness "
                "ledger is `WEAKNESSES.md`; cross-match studies are in `studies/`.\n\n"
                "| Folder (UTC) | Our version | Opponent | Record | Site |\n|---|---|---|---|---|\n")
        for d in reals:
            rows = sets.get(d.rsplit("_", 1)[-1], [])
            if rows:
                w = sum(r["res"] == "win" for r in rows)
                f.write(f"| [{d}]({d}/notes.md) | v{rows[0]['v']} | {rows[0]['opp']} ({rows[0]['opp_rating']}) | "
                        f"{w}-{len(rows) - w} | [match group]({SITE}{rows[0]['group']}) |\n")
            else:
                f.write(f"| [{d}]({d}/notes.md) | | | | |\n")
        studies = os.path.join(REAL, "studies")
        if os.path.isdir(studies):
            f.write("\n## Studies across many real matches\n\n")
            for d in sorted(os.listdir(studies)):
                if os.path.isfile(os.path.join(studies, d, "notes.md")):
                    f.write(f"- [{d}](studies/{d}/notes.md): {title(os.path.join(studies, d, 'notes.md'))}\n")
    return len(sims), len(reals)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    moves = plan_moves()
    for old, new in moves:
        print(f"{os.path.relpath(old, ROOT)} -> {os.path.relpath(new, ROOT)}")
    if args.dry_run:
        return
    for old, new in moves:
        os.makedirs(os.path.dirname(new), exist_ok=True)
        if tracked(old):
            subprocess.run(["git", "mv", "-f", old, new], cwd=ROOT, check=True)
        else:
            os.replace(old, new)
    n = fix_links(moves) if moves else 0
    sims, reals = rebuild_indexes()
    print(f"moved {len(moves)}, rewrote links in {n} files; indexes: {sims} simulated, {reals} real")


if __name__ == "__main__":
    main()
