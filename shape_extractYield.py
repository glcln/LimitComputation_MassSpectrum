#!/usr/bin/env python3
import os, re, glob

BASEDIR = 'MyNewDataCards'
LABEL = 'etaRebinPerso_Oldfit__PUppiMETcut'

def read_rate(path):
    with open(path) as f:
        lines = f.readlines()
    bins = procs = rates = None
    for l in lines:
        toks = l.split()
        if not toks:
            continue
        if toks[0] == 'bin' and len(toks) > 3:
            bins = toks[1:]
        elif toks[0] == 'process' and not toks[1].lstrip('-').isdigit():
            procs = toks[1:]
        elif toks[0] == 'rate':
            rates = toks[1:]
    return bins, procs, rates

def mass_key(fn):
    m = re.search(r'(\d+)', os.path.basename(fn))
    return int(m.group(1)) if m else 0

for d in sorted(glob.glob(os.path.join(BASEDIR, '*'))):
    name = os.path.basename(d)
    if not os.path.isdir(d) or not name.startswith('datacards_') or not name.endswith(LABEL):
        continue
    print('=' * 80)
    print(d)
    print('=' * 80)
    txts = glob.glob(os.path.join(d, '*_cutandcount.txt'))
    for txt in sorted(txts, key=mass_key):
        bins, procs, rates = read_rate(txt)
        print(f'\n{os.path.basename(txt)}')
        if rates is None:
            print('  (ligne rate introuvable)')
            continue
        if bins and procs and len(bins) == len(procs) == len(rates):
            for b, p, r in zip(bins, procs, rates):
                print(f'  {b:20s} {p:12s} rate = {r}')
        else:
            print('  rate =', '  '.join(rates))
    print()