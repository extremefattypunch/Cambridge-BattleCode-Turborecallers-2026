#!/usr/bin/env python3
"""Create a new bot as a copy of an existing one: bots/SRC -> bots/DST (build cache excluded).

Usage:
    python3 tools/newbot.py SRC DST

Both names must be plain identifiers ([A-Za-z0-9_-]+), SRC must exist under bots/ and DST must not.
This exists so an unattended agent can fork bots without broad cp/rm permissions.
"""
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOTS = os.path.join(ROOT, "bots")
NAME = re.compile(r"^[A-Za-z0-9_-]+$")


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, dst = sys.argv[1], sys.argv[2]
    for name in (src, dst):
        if not NAME.match(name):
            sys.exit(f"invalid bot name: {name!r}")
    src_dir, dst_dir = os.path.join(BOTS, src), os.path.join(BOTS, dst)
    if not os.path.isdir(src_dir):
        sys.exit(f"no such bot: bots/{src}")
    if os.path.exists(dst_dir):
        sys.exit(f"already exists: bots/{dst}")
    shutil.copytree(src_dir, dst_dir, ignore=shutil.ignore_patterns(".cambc", "build", "target"))
    print(f"created bots/{dst} from bots/{src}")


if __name__ == "__main__":
    main()
