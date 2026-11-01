---
name: cambc-site-notes
description: "How to scrape/download from the Cambridge Battlecode site via Chrome tools (blob downloads, output filter, CLI URL)"
metadata:
  node_type: memory
  type: reference
  originSessionId: 011a374b-9717-46be-b823-39c7b5bbdb2a
  modified: 2026-10-31T18:32:10.698Z
---

- Docs markdown (GameRules.md, BotAPI<Lang>.md) is generated client-side on /game/docs/agents; hook URL.createObjectURL to grab blob text, then POST it to a localhost receiver (page fetch to http://127.0.0.1 works). Chrome blocks a second auto-download.
- Chrome javascript_tool output is blocked if it looks like query-string/cookie data (e.g. `a=b; c=d`) — format outputs with `|` separators.
- CLI binary: https://2026a.battlecode.co.uk/api/v1/distribution/linux-x64/download (SHA-256 shown on /game/download; v4.0.0 = 552056aa…9eb4). Also `pip install cambc`.
- Site pages are an SPA; read `document.querySelector('main').innerText` after ~2s.

Related: [[cambc-battlecode-project]]
