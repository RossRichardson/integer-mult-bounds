#!/usr/bin/env python3
"""Exact direct-sum versus retained Fourier-child contract audit.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
No supplier implementation is imported. Gaussian integer numerators are exact.
"""
from __future__ import annotations
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
PREFIX = 'candidate/strict/global/base/providers/gauge44/'
MEMBERS = {
    'LOCAL-PROGRAMS.json.gz': '241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a',
    'CANONICAL-WORD.json.gz': '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219',
    'CLIFFORD-RECIPES.json': 'd0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731',
}
BASE_PROFILE = {1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}
BATCHES = [(17006,17021)] + [(17106+16*j,17121+16*j) for j in range(7)]

class Reject(ValueError):
    pass

def need(ok, message):
    if not ok:
        raise Reject(message)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def read_inputs(root=ROOT):
    pins = json.loads((HERE/'SOURCES.json').read_text())
    for item in pins['files']:
        if item['usage'] == 'input':
            need(sha((root/item['path']).read_bytes()) == item['sha256'], 'source pin: '+item['path'])
    out = {}
    with tarfile.open(root/ARCHIVE, 'r:gz') as stream:
        for name, digest in MEMBERS.items():
            hits = [m for m in stream.getmembers() if m.name == PREFIX+name]
            need(len(hits) == 1 and hits[0].isfile(), 'unique archive member: '+name)
            raw = stream.extractfile(hits[0]).read()
            need(sha(raw) == digest, 'archive member hash: '+name)
            out[name] = json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)
    return out

def mul(a,b):
    return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])

def ipow(k):
    return ((1,0),(0,1),(-1,0),(0,-1))[k%4]

def monomial(record,n):
    """Decode diagonal phase, linear permutation, translation and global phase."""
    rows,q,linear = (record[k] for k in ('matrix_rows','quadratic_rows','linear_Z4'))
    need(len(rows) == len(q) == len(linear) == n, 'monomial dimensions')
    need(all(type(v) is int for v in rows+q+linear), 'integer monomial')
    need(all(0 <= v < 1<<n for v in rows+q), 'monomial row range')
    need(all(0 <= v < 4 for v in linear), 'monomial phase range')
    need(all(((q[i]>>j)&1) == ((q[j]>>i)&1) for i in range(n) for j in range(n)), 'symmetric quadratic form')
    need(all(linear[i]%2 == ((q[i]>>i)&1) for i in range(n)), 'quadratic phase parity')
    offset,phase = record['offset'],record['phase']
    need(type(offset) is int and 0 <= offset < 1<<n, 'monomial offset')
    need(type(phase) is int and 0 <= phase < 4, 'monomial global phase')
    images,factors = [],[]
    for x in range(1<<n):
        images.append(sum(((row&x).bit_count()%2)<<j for j,row in enumerate(rows)) ^ offset)
        exponent = phase + sum(linear[j] for j in range(n) if x>>j&1)
        exponent += 2*sum(1 for j in range(n) for k in range(j+1,n)
                          if (x>>j&1) and (x>>k&1) and (q[j]>>k&1))
        factors.append(ipow(exponent))
    need(len(set(images)) == 1<<n, 'singular monomial')
    return images,factors

def child_columns(recipe,n):
    """Literal L(C_r tensor I)R columns; integer numerators over 2**r."""
    r = recipe['rank']
    need(type(r) is int and 0 < r <= n, 'child rank outside ambient dimension')
    right,rp = monomial(recipe['right'],n)
    left,lp = monomial(recipe['left'],n)
    columns = []
    for x in range(1<<n):
        column = {}
        for mask in range(1<<r):
            value = rp[x]
            for bit in range(r):
                value = mul(value,(1,-1) if mask>>bit&1 else (1,1))
            at = right[x]^mask
            row = left[at]
            need(row not in column, 'unexpected child-path collision')
            column[row] = mul(value,lp[at])
            need(column[row] != (0,0), 'zero Fourier factor')
        columns.append(column)
    return columns,1<<r

def signature(columns,size):
    rows = [0]*size
    for column in columns:
        for i,value in column.items():
            if value != (0,0):
                rows[i] += 1
    return {str(k):v for k,v in sorted(Counter(rows).items())}

def source_census(inputs):
    programs = inputs['LOCAL-PROGRAMS.json.gz']
    word = inputs['CANONICAL-WORD.json.gz']
    need(word['h'] == 9 and word['R'] == 480 and word['v'] == 112, 'selected dimensions')
    recipes = inputs['CLIFFORD-RECIPES.json']['children']
    by_pair = {(r['old'],r['new']):r for r in recipes}
    need(len(by_pair) == len(recipes), 'duplicate recipe key')
    need(set(programs) == {'forward','backward'}, 'both orientations')
    pairs,blocks,rank_one_counts = set(),[],{}
    for orientation in ('forward','backward'):
        events = programs[orientation]
        paid = Counter(e[5] for e in events if e[0] == 'climb')
        paid.update(e[4] for e in events if e[0] == 'center')
        need(dict(paid) == BASE_PROFILE, 'selected paid profile')
        rank_one_counts[orientation] = sum(e[0] == 'climb' and e[5] == 1 for e in events)
        for start,end in BATCHES:
            block = events[start:end+1]
            need(len(block) == 16 and all(e[0] == 'climb' and e[5] == 1 for e in block), 'source batch rank-one tags')
            need(len({e[2] for e in block}) == 16, 'source batch independent registers')
            for e in block:
                pair = (e[3],e[4])
                need(pair in by_pair and by_pair[pair]['rank'] == 1, 'recipe/event rank binding')
                need(len(word['frames'][pair[1]])-len(word['frames'][pair[0]]) == 1, 'frame dimension increment')
                pairs.add(pair)
            blocks.append(dict(orientation=orientation,first_event=start,last_event=end,
                               registers=[e[2] for e in block],row_support={'2':16*512}))
    checked_columns,witness = 0,None
    for pair in sorted(pairs):
        columns,denominator = child_columns(by_pair[pair],9)
        need(signature(columns,512) == {'2':512}, 'literal recipe row support')
        need(all(len(c) == 2 for c in columns), 'literal recipe column support')
        checked_columns += len(columns)
        if pair == (855,1):
            witness = dict(register=456,event=17006,old=855,new=1,input_coordinate=0,
                denominator=denominator,output=[[row,*value] for row,value in sorted(columns[0].items())])
    need(witness is not None, 'first selected recipe witness')
    return dict(rank_one_counts=rank_one_counts,batches=blocks,unique_recipes=len(pairs),
                exact_recipe_columns=checked_columns,first_selected_column=witness)

def c_column(r,x):
    """Coordinate C_r column by its closed tensor-product formula."""
    result = []
    for y in range(1<<r):
        value = (1,0)
        for j in range(r):
            value = mul(value,(1,-1) if (x^y)>>j&1 else (1,1))
        result.append(value)
    return result

def finite_controls():
    direct = [[(0,0)]*4 for _ in range(4)]
    tensor = [c_column(2,x) for x in range(4)]
    for x in range(4):
        for y,value in enumerate(c_column(1,x%2)):
            direct[x][2*(x//2)+y] = (2*value[0],2*value[1])
    need(direct[0] == [(2,2),(2,-2),(0,0),(0,0)], 'direct-sum witness')
    need(tensor[0] == [(0,2),(2,0),(2,0),(0,-2)], 'tensor witness')
    need(direct != tensor, 'wrong child must fail RecipesExact')
    # A constant-vector-only test misses the failure on independent inputs.
    need([tuple(sum(direct[x][y][a] for x in range(4)) for a in (0,1)) for y in range(4)]
         == [tuple(sum(tensor[x][y][a] for x in range(4)) for a in (0,1)) for y in range(4)],
         'correlated-input blind spot')
    for r in range(1,7):
        need(all(all(z != (0,0) for z in c_column(r,x)) for x in range(1<<r)), 'full tensor support')
    # PR679's paid selector repair, specialized to sixteen rank-one lanes.
    # (C4* tensor I2) C5 = I16 tensor C1, denominator 2**9.
    selector_columns = [c_column(4,x) for x in range(16)]
    wide_columns = [c_column(5,x) for x in range(32)]
    for x in range(32):
        for y in range(32):
            terms = []
            for high in range(16):
                z = 2*high+(y%2)
                a,b = selector_columns[high][y//2]
                terms.append(mul((a,-b),wide_columns[x][z]))
            value = tuple(sum(v[i] for v in terms) for i in (0,1))
            target = c_column(1,x%2)[y%2] if x//2==y//2 else (0,0)
            need(value == (256*target[0],256*target[1]), 'paid sixteen-lane selector repair')
    return dict(minimal_counterexample=dict(dimension=4,denominator=4,input=[1,0,0,0],
                direct_sum=direct[0],rank_two_child=tensor[0]),
                all_ones_blind_control=True,tensor_dimensions_checked=[2**r for r in range(1,7)],
                credited_pr679_selector_repair=dict(lanes=16,active_rank=1,joined_rank=5,
                    inverse_selector_rank=4,complete_matrix_entries=1024))

def calculate(root=ROOT):
    source = source_census(read_inputs(root))
    return dict(status='PASS_DIAGONAL_CHILD_CONTRACT_AUDIT',no_new_kappa=True,
                source=source,controls=finite_controls(),
                obstruction=dict(original_batch_dimension=8192,minimum_rank16_dimension=65536,
                    batch_row_support=2,rank16_row_support=65536,
                    padded_target_row_support={'1':57344,'2':8192},
                    padded_candidate_row_support={'65536':65536},
                    quantified_scope='One C_r child, r>=2, with arbitrary invertible monomial pre/post maps; independent arbitrary inputs including dirty spectators.'))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',type=Path)
    parser.add_argument('--certificate',type=Path,default=HERE/'CERTIFICATE.json')
    parser.add_argument('--root',type=Path,default=ROOT)
    args = parser.parse_args()
    result = json.loads(json.dumps(calculate(args.root)))
    if args.write:
        args.write.write_text(json.dumps(result,indent=2)+'\n')
    else:
        need(result == json.loads(args.certificate.read_text()), 'certificate differs from exact replay')
    print(result['status'],'recipes='+str(result['source']['unique_recipes']),
          'columns='+str(result['source']['exact_recipe_columns']),'no_new_kappa')

if __name__ == '__main__':
    main()
