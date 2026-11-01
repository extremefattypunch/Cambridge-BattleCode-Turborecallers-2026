#!/usr/bin/env python3.12
"""Keep match notes in one folder per match, and keep every link to them pointing at the right place.

Layout (see the repo README):
    results/real-matches/<YYYY-MM-DD>_<HHMM>_<opponent>_<group8>/notes.md   one 5-game ladder match vs one team
    results/real-matches/studies/<YYYY-MM-DD>_<HHMM>_<name>/notes.md         studies across many real matches
    results/real-matches/{INSIGHTS,WEAKNESSES,INDEX}.md                       synthesis, ledger, index (+ index/<day>.md)
    results/simulated-matches/<YYYY-MM-DD>_<HHMM>_<candidate>/notes.md       one simulated match (experiment or gate)
    results/simulated-matches/INDEX.md                                        index, oldest first
Times are UTC: a real match's first game; a simulated match's launch (for reports moved from the old
place, their first commit).

Usage:
    python3.12 tools/organize_notes.py            move notes left in old places, fix links, rebuild the indexes
    python3.12 tools/organize_notes.py --dry-run  only print what would move

Old places: results/experiments/*.md (one file per experiment) and results/ladder/scouting/*.md (named
<date>-<group8>-<opponent>.md), plus results/ladder/{INSIGHTS,WEAKNESSES}.md. Compatibility symlinks
(left for workflows that were started before the move) are skipped. A move never overwrites an existing
note (except a "Being generated" placeholder); such a case is reported for a manual merge. Untracked notes
changed in the last 15 minutes are left alone, since an agent may still be writing them.
"""
import argparse
import collections
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
KEEP_DAYS = 2  # days of real matches listed in INDEX.md itself; older days go to index/<day>.md
PLACEHOLDER = "**Being generated.**"
SETTLE = 15 * 60  # an untracked note changed more recently than this may still be being written: leave it


def slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:30].strip("-") or "team"


def real_folder(rows):
    """Folder name of a real match from its ladder-games.jsonl rows."""
    t = min(r["time"] for r in rows)
    return f"{t[:10]}_{t[11:13]}{t[14:16]}_{slug(rows[0]['opp'])}_{rows[0]['group'][:8]}"


def run(args):
    return subprocess.run(args, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          universal_newlines=True)


def utc_stamp(path):
    """When the note was written: its first commit if tracked (checkouts reset mtimes), else its mtime."""
    out = run(["git", "log", "--diff-filter=A", "--format=%at", "--", path]).stdout.split()
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


def settled(path):
    return tracked(path) or os.path.getmtime(path) < __import__("time").time() - SETTLE


def plan_moves():
    moves = []  # (old path, new path)
    if os.path.isdir(OLD_EXP):
        for f in sorted(os.listdir(OLD_EXP)):
            p = os.path.join(OLD_EXP, f)
            if not f.endswith(".md") or os.path.islink(p) or f == "TEMPLATE.md" or not settled(p):
                continue
            name = f[len("2026-11-01-"):-3] if re.match(r"\d{4}-\d\d-\d\d-", f) else f[:-3]
            base = REAL + "/studies" if f in STUDIES else SIM
            moves.append((p, os.path.join(base, f"{utc_stamp(p)}_{name}", "notes.md")))
    sets = ladder_sets()
    if os.path.isdir(OLD_SCOUT):
        for f in sorted(os.listdir(OLD_SCOUT)):
            p = os.path.join(OLD_SCOUT, f)
            if not f.endswith(".md") or os.path.islink(p) or not settled(p):
                continue
            m = re.match(r"\d{4}-\d\d-\d\d-([0-9a-f]{8})", f)
            rows = sets.get(m.group(1)) if m else None
            if not rows:
                print(f"WARN: {f}: group not in ladder-games.jsonl; left in place")
                continue
            moves.append((p, os.path.join(REAL, real_folder(rows), "notes.md")))
    for f in ("INSIGHTS.md", "WEAKNESSES.md"):
        p = os.path.join(RES, "ladder", f)
        if os.path.exists(p) and not os.path.islink(p) and settled(p):
            moves.append((p, os.path.join(REAL, f)))
    old = os.path.join(RES, "ladder-analysis-2026-10-31.md")
    if os.path.exists(old) and not os.path.islink(old):
        moves.append((old, os.path.join(REAL, "studies", "2026-10-31_2340_ladder-analysis", "notes.md")))
    return moves


def tracked(path):
    return run(["git", "ls-files", "--error-unmatch", path]).returncode == 0


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
            if os.path.basename(a) in ("INSIGHTS.md", "WEAKNESSES.md") and "/" not in a:
                continue  # bare INSIGHTS.md also names postmortems/INSIGHTS.md: only rewrite full paths
            new_text = re.sub(r"(?<![\w/.-])" + re.escape(a), b, new_text)
        if new_text != text:
            open(path, "w", encoding="utf-8").write(new_text)
            changed += 1
    return changed


def read(path):
    return open(path, encoding="utf-8").read()


def title(text):
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip().replace("|", "/")
    return ""


def rebuild_indexes():
    os.makedirs(SIM, exist_ok=True)
    os.makedirs(REAL, exist_ok=True)
    sims = sorted(d for d in os.listdir(SIM) if os.path.isfile(os.path.join(SIM, d, "notes.md")))
    with open(os.path.join(SIM, "INDEX.md"), "w") as f:
        f.write("# Simulated matches (the testing pipeline), oldest first\n\n"
                "Generated by `tools/organize_notes.py`; do not edit. Each folder holds one `notes.md`, in the "
                "format of `TEMPLATE.md` (\"new\") or the older report format (\"legacy\"). \"Builds on\" is the "
                "parent simulated match analysed in the note's section 1.\n\n"
                "| Folder (UTC) | Format | Builds on | Title |\n|---|---|---|---|\n")
        for d in sims:
            text = read(os.path.join(SIM, d, "notes.md"))
            fmt = "new" if "## 1. The previous simulated match" in text else "legacy"
            m = re.search(r"\*\*Previous simulated match:\*\*\s*\[`?([^`\]]+)`?\]", text)
            parent = f"[{m.group(1)}]({m.group(1)}/notes.md)" if m else ""
            f.write(f"| [{d}]({d}/notes.md) | {fmt} | {parent} | {title(text)} |\n")

    sets = ladder_sets()
    reals = sorted((d for d in os.listdir(REAL) if os.path.isfile(os.path.join(REAL, d, "notes.md"))), reverse=True)
    by_day = collections.OrderedDict()
    for d in reals:
        by_day.setdefault(d[:10], []).append(d)
    days = list(by_day)
    os.makedirs(os.path.join(REAL, "index"), exist_ok=True)

    def rows_for(day, prefix):
        out = []
        for d in by_day[day]:
            text = read(os.path.join(REAL, d, "notes.md"))
            fmt = "new" if "## 1. The games played" in text else "legacy"
            rows = sets.get(d.rsplit("_", 1)[-1], [])
            if rows:
                w = sum(r["res"] == "win" for r in rows)
                out.append(f"| [{d[11:]}]({prefix}{d}/notes.md) | v{rows[0]['v']} | {rows[0]['opp']} "
                           f"({rows[0]['opp_rating']}) | {w}-{len(rows) - w} | {fmt} | "
                           f"[match group]({SITE}{rows[0]['group']}) |")
            else:
                out.append(f"| [{d[11:]}]({prefix}{d}/notes.md) | | | | {fmt} | |")
        return out

    header = "| Folder (HHMM UTC) | Our version | Opponent (rating) | Record | Format | Site |\n|---|---|---|---|---|---|\n"
    for day in days[KEEP_DAYS:]:
        with open(os.path.join(REAL, "index", f"{day}.md"), "w") as f:
            f.write(f"# Real ladder matches on {day} (UTC), newest first\n\n" + header +
                    "\n".join(rows_for(day, "../")) + "\n")
    with open(os.path.join(REAL, "INDEX.md"), "w") as f:
        f.write("# Real ladder matches, newest first\n\n"
                "Generated by `tools/organize_notes.py`; do not edit. One folder per 5-game ladder match against "
                "one team, each with a `notes.md` (format in `TEMPLATE.md`). Start with `INSIGHTS.md` (the "
                "synthesis) and `WEAKNESSES.md` (the ranked ledger). Cross-match studies are in `studies/`.\n\n")
        per_v = collections.defaultdict(lambda: [0, 0, 0])
        for d in reals:
            rows = sets.get(d.rsplit("_", 1)[-1], [])
            if rows:
                v = per_v[rows[0]["v"]]
                v[0] += 1
                v[1] += sum(r["res"] == "win" for r in rows)
                v[2] += sum(r["res"] != "win" for r in rows)
        if per_v:
            f.write("## Analysed matches per bot version\n\n| Version | Matches | Games W-L |\n|---|---|---|\n")
            for v in sorted(per_v, key=lambda x: x or 0, reverse=True):
                n, w, l = per_v[v]
                f.write(f"| v{v} | {n} | {w}-{l} |\n")
            f.write("\n")
        for day in days[:KEEP_DAYS]:
            f.write(f"## {day}\n\n" + header + "\n".join(rows_for(day, "")) + "\n\n")
        if days[KEEP_DAYS:]:
            f.write("## Earlier days\n\n" + "".join(f"- [{day}](index/{day}.md)\n" for day in days[KEEP_DAYS:]) + "\n")
        studies = os.path.join(REAL, "studies")
        if os.path.isdir(studies):
            f.write("## Studies across many real matches\n\n")
            for d in sorted(os.listdir(studies)):
                if os.path.isfile(os.path.join(studies, d, "notes.md")):
                    f.write(f"- [{d}](studies/{d}/notes.md): {title(read(os.path.join(studies, d, 'notes.md')))}\n")
    return len(sims), len(reals)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    moves = plan_moves()
    applied = []
    for old, new in moves:
        if os.path.exists(new) and PLACEHOLDER not in read(new):
            print(f"SKIP (destination exists; merge by hand): {os.path.relpath(old, ROOT)} -> {os.path.relpath(new, ROOT)}")
            continue
        print(f"{os.path.relpath(old, ROOT)} -> {os.path.relpath(new, ROOT)}")
        if args.dry_run:
            continue
        os.makedirs(os.path.dirname(new), exist_ok=True)
        if tracked(old):
            run(["git", "mv", "-f", old, new])
        else:
            os.replace(old, new)
        applied.append((old, new))
    if args.dry_run:
        return
    n = fix_links(applied) if applied else 0
    sims, reals = rebuild_indexes()
    print(f"moved {len(applied)}, rewrote links in {n} files; indexes: {sims} simulated, {reals} real")


if __name__ == "__main__":
    main()
