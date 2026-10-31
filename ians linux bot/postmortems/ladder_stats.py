import json, sys, itertools, collections, math, re
ROOT = sys.argv[1]
M = json.load(open(ROOT + '/matches/ladder/matches.json'))
G = json.load(open(ROOT + '/matches/ladder/raw/match_groups.json'))
NAMES = {0:'Ryth',1:'Vesper',2:'Vendetta',3:'Cassi&Issac',4:'Stellar',5:'Prism',6:'Marcella',7:'Willow',8:'Ren',9:'Varg',10:'Tavi',11:'HoR'}

# side + rating per match from raw
side = {}; grp = {}
for g in G:
    gr = g['group']
    us = [x for x in gr['sides'] if x['teamName'] == 'Turbo Recallers'][0]
    th = [x for x in gr['sides'] if x['teamName'] != 'Turbo Recallers'][0]
    for m in g['matches']:
        side[m['id']] = us['side']
        grp[m['id']] = (gr['id'], th['teamName'], th['ratingBefore'], us['ratingBefore'])
for r in M:
    r['side'] = side.get(r['id'], '?')
    r['orating'] = grp[r['id']][2]
    r['gid'] = grp[r['id']][0]
    r['n'] = len(r['udraft'].split(','))
    r['w'] = 1 if r['res'] == 'win' else 0
    r['od'] = r['odraft'].split(',')

def wl(rows):
    w = sum(r['w'] for r in rows); return w, len(rows) - w
def pct(rows):
    w, l = wl(rows); return f"{w}W-{l}L ({100*w/max(1,w+l):.0f}%)"
def ci(w, n):  # Wilson 95%
    if n == 0: return (0, 0)
    p = w / n; z = 1.96
    d = 1 + z*z/n; c = (p + z*z/(2*n)) / d; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return (100*(c-h), 100*(c+h))
def mean(xs): xs = list(xs); return sum(xs)/len(xs) if xs else float('nan')

out = []
P = out.append
for v in (1, 2):
    rows = [r for r in M if r['v'] == v]
    w, l = wl(rows); lo, hi = ci(w, w+l)
    P(f"V{v}: {pct(rows)} CI95 {lo:.0f}-{hi:.0f}%  avg gems us {mean(r['us'] for r in rows):.0f} them {mean(r['them'] for r in rows):.0f}  avg opp rating {mean(r['orating'] for r in rows):.0f}  rounds {mean(r['rounds'] for r in rows):.0f}")
P('')
P('BY TEAM SIZE')
for v in (1, 2):
    for n in (3, 4, 5):
        rows = [r for r in M if r['v'] == v and r['n'] == n]
        P(f"  v{v} {n}-pick: {pct(rows)}  gems {mean(r['us'] for r in rows):.0f}-{mean(r['them'] for r in rows):.0f}")
P('BY SIDE (v1)')
for s in 'ab':
    rows = [r for r in M if r['v'] == 1 and r['side'] == s]
    P(f"  v1 side {s}: {pct(rows)}")
P('BY END REASON')
for v in (1, 2):
    for e in sorted(set(r['end'] for r in M)):
        rows = [r for r in M if r['v'] == v and r['end'] == e]
        if rows: P(f"  v{v} {e}: {pct(rows)}  rounds {mean(r['rounds'] for r in rows):.0f}  gems {mean(r['us'] for r in rows):.0f}-{mean(r['them'] for r in rows):.0f}")
P('LOSS DETAIL v1 (end, rounds, us-them)')
L = [r for r in M if r['v'] == 1 and not r['w']]
early = [r for r in L if r['end'] == 'gems' and r['rounds'] < 1000]
mid = [r for r in L if r['end'] == 'gems' and 1000 <= r['rounds'] < 1600]
late = [r for r in L if r['end'] == 'gems' and r['rounds'] >= 1600]
tb = [r for r in L if r['end'] != 'gems']
P(f"  losses {len(L)}: opp hit 1000 <r1000: {len(early)} (our gems {mean(r['us'] for r in early):.0f}), r1000-1599: {len(mid)} (our {mean(r['us'] for r in mid):.0f}), r1600+: {len(late)} (our {mean(r['us'] for r in late):.0f}), tiebreak: {len(tb)} (our {mean(r['us'] for r in tb):.0f} vs {mean(r['them'] for r in tb):.0f})")
blow = [r for r in L if r['us'] < 0.4 * r['them']]
close = [r for r in L if r['us'] >= 0.7 * r['them']]
P(f"  blowouts (us<40% of them): {len(blow)}; close (us>=70% of them): {len(close)}")
P(f"  rounds hist of v1 losses ending by gems: {sorted(r['rounds'] for r in L if r['end']=='gems')}")
P(f"  v1 wins rounds: {sorted(r['rounds'] for r in M if r['v']==1 and r['w'])}")
P('ALL V2 GAMES')
for r in M:
    if r['v'] == 2: P(f"  {r['opp'][:14]:14} {r['map']:22} {r['res']:4} {r['us']:5}-{r['them']:<5} r{r['rounds']:<5} {r['end']:14} opp: {r['odraft']}")

P('')
P('OPPONENT CHAMPION PRESENCE (our record when opp drafted X)  v1 | v2 | all')
cnt = collections.Counter(c for r in M for c in r['od'])
for c, k in cnt.most_common():
    a = [r for r in M if c in r['od']]
    b = [r for r in M if c not in r['od']]
    a1 = [r for r in a if r['v'] == 1]; a2 = [r for r in a if r['v'] == 2]
    b1 = [r for r in b if r['v'] == 1]
    P(f"  {c:12} picks {k:2}  v1 with: {pct(a1):16} v1 without: {pct(b1):16} v2 with: {pct(a2)}")
# first pick of opp
P('OPP FIRST PICK (v1)')
fp = collections.Counter(r['od'][0] for r in M if r['v'] == 1)
for c, k in fp.most_common():
    P(f"  {c:12} {pct([r for r in M if r['v']==1 and r['od'][0]==c])}")
P('OPP PAIRS (v1, n>=6) sorted by our win%')
pc = collections.defaultdict(list)
for r in M:
    if r['v'] != 1: continue
    for a, b in itertools.combinations(sorted(set(r['od'])), 2):
        pc[(a, b)].append(r)
for (a, b), rows in sorted(pc.items(), key=lambda kv: sum(r['w'] for r in kv[1]) / len(kv[1])):
    if len(rows) >= 6: P(f"  {a}+{b}: {pct(rows)}")
# opponent draft overlap with top-20 core
CORE = {'HoR', 'Vesper', 'Vendetta', 'Marcella', 'Ryth', 'Tavi'}
P('OPP #CORE CHAMPS (HoR/Vesper/Vendetta/Marcella/Ryth/Tavi) -> our record v1')
for k in range(0, 6):
    rows = [r for r in M if r['v'] == 1 and len(CORE & set(r['od'])) == k]
    if rows: P(f"  {k} core: {pct(rows)}")
P('OPP TEAM-LEVEL DRAFT (most common opp pick set per team) + our result')
byteam = collections.defaultdict(list)
for r in M: byteam[(r['v'], r['opp'])].append(r)
for (v, t), rows in byteam.items():
    c = collections.Counter(x for r in rows for x in r['od'])
    P(f"  v{v} {t[:22]:22} r{rows[0]['orating']:.0f} side {rows[0]['side']} {pct(rows):14} gems {mean(r['us'] for r in rows):.0f}-{mean(r['them'] for r in rows):.0f}  opp champs: {', '.join(f'{x}{n}' for x, n in c.most_common())}")

P('')
P('BY MAP (all versions)')
bymap = collections.defaultdict(list)
for r in M: bymap[r['map']].append(r)
for mp, rows in sorted(bymap.items(), key=lambda kv: (sum(r['w'] for r in kv[1]) / len(kv[1]), kv[0])):
    P(f"  {mp:24} n{rows[0]['n']} " + ' '.join(f"v{r['v']}:{'W' if r['w'] else 'L'}({r['us']}-{r['them']})" for r in rows))
# map prefix families
P('BY MAP PREFIX (v1)')
fam = collections.defaultdict(list)
for r in M:
    if r['v'] == 1: fam[re.match(r'(\d\d|adgato|[a-z]+)', r['map']).group(1)].append(r)
for f, rows in fam.items(): P(f"  {f}: {pct(rows)}")

# local per-map: v2 vs sf_bank on all 70 maps, sf_bank vs sf_base sprint
def parse(fn):
    d = {}
    for line in open(fn):
        p = line.split()
        if len(p) >= 6 and p[1] in ('A', 'B') and p[2] in ('WIN', 'loss'):
            d.setdefault(p[0], []).append((p[1], p[2] == 'WIN', int(p[3]), int(p[4])))
    return d
loc2 = parse(ROOT + '/matches/final-mergeb-all.log')
loc1 = parse(ROOT + '/matches/sf_bank-final.log')
P('')
P('LOCAL vs LADDER per map')
for r in M:
    lm = r['map'].replace('_', '-')
    if r['v'] == 2:
        lr = loc2.get(lm)
        P(f"  v2 {lm:22} ladder {r['res']:4}  local tb_merge_b vs sf_bank: {lr}")
# v1: sf_base results = inverse of sf_bank rows
agree = []
for r in M:
    if r['v'] != 1: continue
    lm = r['map'].replace('_', '-')
    if lm in loc1:
        base_w = sum(1 for x in loc1[lm] if not x[1])
        agree.append((lm, r['w'], base_w, len(loc1[lm])))
P(f"  v1 ladder games on maps in sf_bank-final (sprint set): {len(agree)}")
for x in agree: P(f"    {x}")
# mergeb local loss maps vs ladder
lossmaps2 = {m for m, rs in loc2.items() if any(not x[1] for x in rs)}
P(f"  tb_merge_b local loss maps (vs sf_bank): {sorted(lossmaps2)}")
# v1 ladder record on maps where tb_merge_b lost locally vs elsewhere
a = [r for r in M if r['v'] == 1 and r['map'].replace('_', '-') in lossmaps2]
b = [r for r in M if r['v'] == 1 and r['map'].replace('_', '-') not in lossmaps2]
P(f"  v1 ladder on mergeb-local-loss maps: {pct(a)}; elsewhere {pct(b)}")
print('\n'.join(out))
