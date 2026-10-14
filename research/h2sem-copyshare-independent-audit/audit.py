#!/usr/bin/env python3
"""Code-separated exact PR1805 audit. Ross Richardson / OpenAI Codex, Apache-2.0.

No predecessor or producer implementation is imported. Submitted numerical
claims are comparison targets, not inputs to reconstruction.
"""
import argparse
import copy
import gzip
import hashlib
import json
import math
from pathlib import Path
import random
from collections import Counter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
BASE = '0b1cccf86e2f5132ed286a26ef0a681a495740ea'
INPUTS = {WORD, 'research/e8-bit-p111-tuned/code/xcheck_p.py',
          'research/r439-copy-path-sharing-barrier/verify.py',
          'research/r439-semantic-d-contract-seed10/PROOF.md'}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def unique(items):
    out = {}
    for k,v in items:
        need(k not in out, 'duplicate JSON key')
        out[k] = v
    return out


def read(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()


def pins():
    s = read(HERE/'SOURCES.json')
    need(s['base_commit'] == BASE, 'base pin')
    live = [i for i in s['files'] if i['usage'] == 'input']
    need(len(live) == len(INPUTS) and {i['path'] for i in live} == INPUTS, 'source inventory')
    for i in live:
        need(hashlib.sha256((ROOT/i['path']).read_bytes()).hexdigest() == i['sha256'], 'source bytes '+i['path'])
    archived = read(HERE/'PINS.json')['files']
    names = {'inputs/pr1805/'+n for n in ('verify.py','README.md','CERTIFICATE.json','SOURCES.json','VERIFY.json','TASK.json','test_package.py')}
    names |= {'inputs/context/selected-result.json','inputs/context/agent-task-catalog.json'}
    need(len(archived) == len(names) and {i['path'] for i in archived} == names, 'archive inventory')
    for i in archived:
        need(hashlib.sha256((HERE/i['path']).read_bytes()).hexdigest() == i['sha256'], 'archive bytes '+i['path'])


def load_word():
    return json.loads(gzip.decompress((ROOT/WORD).read_bytes()))


def nominate(w):
    # Independent incidence-column formula: saving=2|Ia intersect Ib|-|Ia|-2.
    incidence = {}
    for t,(f,d,ss) in enumerate(w['D']):
        need(f == 0 and d == w['v']+t and len(ss) == len(set(ss)), 'baseline D layout')
        for s in ss:
            incidence[s] = incidence.get(s,0) | (1<<t)
    pool = sorted(set(incidence)-set(w['ret']))
    need(all(s >= 2*w['v'] for s in pool), 'nonhelper source')
    scores = []
    for a in pool:
        for b in pool:
            if a != b:
                saving = 2*(incidence[a]&incidence[b]).bit_count()-incidence[a].bit_count()-2
                if saving > 0:
                    scores.append((saving,a,b))
    # This declared predecessor tie rule is intentionally retained.
    random.Random(42).shuffle(scores)
    scores.sort(key=lambda x:-x[0])
    chosen,used,total = [],set(),0
    for saving,a,b in scores:
        if not ({a,b}&used):
            chosen.append([a,b]);used.update((a,b));total += saving
    census = dict(operands=len(pool),oriented_pairs=len(pool)*(len(pool)-1),positive_pairs=len(scores),
                  best_saving=scores[0][0],best_pair=list(scores[0][1:]),matching_pairs=len(chosen),matching_saving=total)
    return chosen,census


def construct(w, pairs):
    # Inverse disjoint helper-basis substitution, on coefficient bit masks.
    flat = [r for pair in pairs for r in pair]
    need(len(flat) == len(set(flat)), 'overlapping pairs')
    need(all(2*w['v'] <= r < 2*w['v']+w['R'] for r in flat), 'pair range')
    out = copy.deepcopy(w)
    prep = [[0,a,[b]] for a,b in pairs]
    body = []
    for frame,d,ss in w['D']:
        mask = sum(1<<s for s in ss)
        for a,b in pairs:
            if mask & (1<<a):
                mask ^= 1<<b
        body.append([frame,d,[r for r in range(2*w['v'],2*w['v']+w['R']) if mask&(1<<r)]])
    out['D'] = prep+body+list(reversed(prep))
    return out


def events(w, reverse=False, d_only=False):
    out = []
    for section in ('D',) if d_only else ('D','A'):
        out.extend(('add',d,s) for _,d,ss in w[section] for s in ss)
    if not d_only:
        temp = 2*w['v']+w['R']
        for slot,r in enumerate(w['ret']):
            out.append(('copy',temp,r))
            out.extend(('add',w['v']+t,temp) for t,slots in enumerate(w['scatter']) if slot in slots)
            out.append(('erase',temp,r))
        for section in ('B','C'):
            out.extend(('add',d,s) for _,d,ss in w[section] for s in ss)
    return [({'copy':'erase','erase':'copy'}.get(k,k),d,s) for k,d,s in reversed(out)] if reverse else out


def columns(w, reverse=False, d_only=False):
    # Each basis input is executed separately, packed by OUTPUT register.
    n = 2*w['v']+w['R']
    ops = [(k,1<<d,1<<s) for k,d,s in events(w,reverse,d_only)]
    result = []
    for i in range(n):
        state = 1<<i
        for k,d,s in ops:
            if k == 'add':
                if state&s: state ^= d
            elif k == 'copy':
                need(not(state&d), 'copy overwrites live temp')
                if state&s: state |= d
            else:
                need(bool(state&d) == bool(state&s), 'erase changed temp')
                state &= ~d
        need(not(state>>n), 'live final temporary')
        result.append(state)
    return result


def envelope(w, reverse):
    values = [1]*(2*w['v']+w['R'])+[0]
    peak = 1
    for k,d,s in events(w,reverse):
        if k == 'add': values[d] += values[s]
        elif k == 'copy':
            need(values[d] == 0, 'positive COPY lifetime')
            values[d] = values[s]
        else: values[d] = 0
        peak = max(peak,values[d])
    need(values[-1] == 0, 'positive temp not cleared')
    return peak


def rank(rows):
    # Exact primitive-integer elimination over Q, not modular rank.
    pivots = {}
    for row in rows:
        a = list(row)
        for j in sorted(pivots):
            if a[j]:
                b = pivots[j]; aj,bj = a[j],b[j]
                a = [bj*x-aj*y for x,y in zip(a,b)]
                divisor = math.gcd(*a)
                if divisor: a = [x//divisor for x in a]
        if any(a):
            j = next(j for j,x in enumerate(a) if x)
            divisor = math.gcd(*a)
            pivots[j] = [x//divisor for x in a]
    return len(pivots)


def paid(w):
    frames = [set(f) for f in w['frames']]
    dims = [rank(w['lines'][i] for i in f) for f in w['frames']]
    paths = [[f] for f in w['start']]
    profile,copies = Counter(),[]
    def visit(r,f):
        old = paths[r][-1]
        if old != f:
            need(frames[old] < frames[f] and dims[old] < dims[f], 'nonmonotone frame')
            profile[dims[f]-dims[old]] += 1
            paths[r].append(f)
    for sec in ('D','A','B','C'):
        for f,d,ss in w[sec]:
            for r in [d]+ss: visit(r,f)
        if sec == 'A':
            copies = [dims[paths[r][-1]] for r in w['ret']]
            profile.update(copies)
    for r,f in enumerate(w['final']): visit(r,f)
    return dict(profile={str(k):v for k,v in sorted(profile.items())},rank_mass=sum(k*v for k,v in profile.items()),
                copy_ranks=copies,frame_paths_sha256=digest(paths),frame_dimensions_sha256=digest(dims))


def bill(w):
    f,b = envelope(w,False),envelope(w,True)
    local,nine = 64*f**3*b**2,(1<<18)*f**5*b**4
    need(local < 1<<104 and nine < 1<<192, 'strict precision guard')
    return dict(native_ADDs=sum(k=='add' for k,_,_ in events(w)),D_adds=sum(len(ss) for _,_,ss in w['D']),
                F=f,B=b,local_bits=local.bit_length(),nine_stage_bits=nine.bit_length(),
                local_integer=local,nine_stage_integer=nine,local_slack=(1<<104)-local,nine_stage_slack=(1<<192)-nine,
                COPY=len(w['ret']),ERASE=len(w['ret']))


def compute():
    pins()
    base = load_word()
    matching,census = nominate(base)
    variants = {'base':base,'single':construct(base,[matching[0]]),'match':construct(base,matching)}
    claim = read(HERE/'inputs/pr1805/CERTIFICATE.json')
    need(census == claim['census'], 'independent census mismatch')
    d0,paid0 = columns(base,d_only=True),paid(base)
    n,v = 2*base['v']+base['R'],base['v']
    want = [(1<<i) | ((1<<(v+i)) if i<v else 0) for i in range(n)]
    bills = {}
    for name,w in variants.items():
        need(columns(w,d_only=True) == d0, name+' D/A boundary')
        for backwards in (False,True):
            need(columns(w,reverse=backwards) == want, name+' complete dirty endpoint')
        b = bill(w)
        need({k:b[k] for k in claim['bills'][name]} == claim['bills'][name],name+' invoice discrepancy')
        need(paid(w) == paid0,name+' frame/COPY invoice')
        bills[name] = b
    need(paid0['profile'] == claim['paid_profile'] and paid0['rank_mass'] == claim['rank_mass'], 'paid claim')
    controls = []
    for name,w in [('single',variants['single']),('two_pair',construct(base,matching[:2]))]:
        bad = copy.deepcopy(w);bad['D'].pop()
        need(columns(bad,d_only=True) != d0,'unrestored control accepted')
        controls.append(name+'_missing_restoration')
    bad = copy.deepcopy(variants['single']);restore = bad['D'].pop();bad['D'].insert(2,restore)
    need(columns(bad,d_only=True) != d0,'early restoration control');controls.append('early_restoration')
    bad = copy.deepcopy(base);bad['D'][0][2].pop()
    need(columns(bad,d_only=True) != d0,'body source control');controls.append('missing_body_source')
    return dict(scope='Independent finite invoice and dirty-boundary audit; no new kappa',
                predecessor_head='b34e0620bd92af49c9095e0eeb885f601fffd137',columns=n,
                pair_census=census,matching=matching,matching_sha256=digest(matching),
                D_columns_sha256=digest(d0),bills=bills,paid=paid0,controls=controls,new_kappa=False)


def main():
    ap = argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args = ap.parse_args()
    result = compute();path = HERE/'RESULT.json'
    if args.write: path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    else: need(canonical(result) == canonical(read(path)), 'typed receipt mismatch')
    print('PASS_COPYSHARE_INDEPENDENT_AUDIT columns=661 words=3 directions=2 controls=4 no_new_kappa')


if __name__ == '__main__':
    main()
