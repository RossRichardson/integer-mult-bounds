#!/usr/bin/env python3
"""Separate reverse-incidence check and rational dense-matrix control oracle.

Same assisted author as verify.py; code-separated, not independent human review.
No import of verify.py or the native compiler. Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
Z = (F(0), F(0))
ONE = (F(1), F(0))

def require(test, label):
    if not test:
        raise ValueError('oracle: '+label)

def plus(x,y):
    return (x[0]+y[0],x[1]+y[1])

def times(x,y):
    return (x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0])

def mm(a,b):
    return [[tuple(sum(times(a[i][k],b[k][j])[d] for k in range(len(b))) for d in (0,1))
             for j in range(len(b[0]))] for i in range(len(a))]

def identity(n):
    return [[ONE if i==j else Z for j in range(n)] for i in range(n)]

def c_axis(vector,axis,inverse=False):
    sign = -1 if inverse else 1
    a,b = (F(1,2),F(sign,2)),(F(1,2),F(-sign,2))
    return [plus(times(a,vector[i]),times(b,vector[i^(1<<axis)])) for i in range(len(vector))]

def c_matrix(ambient,axes):
    columns = []
    for j in range(1<<ambient):
        column = [ONE if i==j else Z for i in range(1<<ambient)]
        for axis in axes:
            column = c_axis(column,axis)
        columns.append(column)
    return [list(row) for row in zip(*columns)]

def matrix_controls(cert):
    direct = c_matrix(2,[0])
    tensor = c_matrix(2,[0,1])
    expected = cert['controls']['minimal_counterexample']
    require(expected == dict(dimension=4,denominator=4,input=[1,0,0,0],
        direct_sum=[[int(4*v) for v in row[0]] for row in direct],
        rank_two_child=[[int(4*v) for v in row[0]] for row in tensor]),'exact counterexample')
    require(direct != tensor,'semantic mutant')
    require(all(tuple(sum(z[d] for z in row) for d in (0,1)) == ONE for row in direct+tensor),
            'all-ones control')
    require(cert['controls']['all_ones_blind_control'] is True,'blind-control receipt')
    require(cert['controls']['tensor_dimensions_checked'] == [2,4,8,16,32,64],'finite tensor domain')
    for r in range(1,7):
        # A literal sequential butterfly, rather than the closed product formula.
        v = [ONE]+[Z]*((1<<r)-1)
        for axis in range(r):
            v = c_axis(v,axis)
        require(all(x != Z for x in v),'tensor support r='+str(r))
    # Exhaust all 4! by 4! row/column permutations, with nontrivial phases.
    permutations = 0
    phase = [ONE,(F(0),F(1)),(F(-1),F(0)),(F(0),F(-1))]
    for p in itertools.permutations(range(4)):
        for q in itertools.permutations(range(4)):
            candidate = [[times(times(phase[i],tensor[p[i]][q[j]]),phase[j])
                          for j in range(4)] for i in range(4)]
            require(all(sum(z != Z for z in row)==4 for row in candidate),'monomial support invariant')
            require(candidate != direct,'permuted invalid child')
            permutations += 1
    # Dropping monomiality breaks the obstruction: D C2* is a valid dense adapter.
    inverse = [[(tensor[j][i][0],-tensor[j][i][1]) for j in range(4)] for i in range(4)]
    adapter = mm(direct,inverse)
    require(mm(adapter,tensor) == direct,'nonmonomial positive escape')
    require(any(sum(z != Z for z in row)>1 for row in adapter),'escape really changes hypothesis')
    require(mm(c_matrix(2,[1]),direct) == tensor,'tensor product positive control')
    require(direct == [[c_matrix(1,[0])[i%2][j%2] if i//2==j//2 else Z
                       for j in range(4)] for i in range(4)],'selector/direct-sum positive control')
    require(cert['controls']['credited_pr679_selector_repair']==dict(lanes=16,active_rank=1,
            joined_rank=5,inverse_selector_rank=4,complete_matrix_entries=1024),'selector repair scope')
    for x in range(32):
        initial=[ONE if j==x else Z for j in range(32)]
        value=initial
        for axis in range(5):value=c_axis(value,axis)
        for axis in range(1,5):value=c_axis(value,axis,inverse=True)
        require(value==c_axis(initial,0),'literal paid selector repair on all columns')
    return permutations

def perm_image(rec,x):
    value = rec['offset']
    for output_bit,row in enumerate(rec['matrix_rows']):
        if bin(row & x).count('1') % 2:
            value ^= 1<<output_bit
    return value

def phase_at(rec,x):
    bits = [i for i in range(9) if x & (1<<i)]
    exponent = rec['phase']+sum(rec['linear_Z4'][i] for i in bits)
    for i,j in itertools.combinations(bits,2):
        exponent += 2*((rec['quadratic_rows'][i]>>j)&1)
    return [ONE,(F(0),F(1)),(F(-1),F(0)),(F(0),F(-1))][exponent%4]

def check(cert_path,root):
    cert = json.loads(cert_path.read_text())
    require(cert['status']=='PASS_DIAGONAL_CHILD_CONTRACT_AUDIT' and cert['no_new_kappa'] is True,'scope')
    for pin in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if pin['usage']=='input':
            require(hashlib.sha256((root/pin['path']).read_bytes()).hexdigest()==pin['sha256'],'source '+pin['path'])
    names = ['LOCAL-PROGRAMS.json.gz','CANONICAL-WORD.json.gz','CLIFFORD-RECIPES.json']
    loaded = {}
    with tarfile.open(root/'research/community-frontier1094-audit/selected-replay.tar.gz') as tar:
        for name in names:
            raw = tar.extractfile('candidate/strict/global/base/providers/gauge44/'+name).read()
            loaded[name] = json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)
    programs,word,recipe_doc = (loaded[n] for n in names)
    require(word['h']==9 and word['v']==112 and word['R']==480,'native dimension')
    recipes = {(r['old'],r['new']):r for r in recipe_doc['children']}
    require(len(recipes)==len(recipe_doc['children']),'recipe keys')
    wanted_pairs,expected_batches = set(),[]
    for orientation in ['forward','backward']:
        events = programs[orientation]
        counts = Counter()
        run = []
        groups = []
        def finish_run():
            for start in range(0,len(run)-15,16):
                block=run[start:start+16]
                if len({e[1][2] for e in block})==16:
                    groups.append(block)
        for i,event in enumerate(events):
            if event[0]=='climb': counts[event[5]]+=1
            if event[0]=='center': counts[event[4]]+=1
            if event[0]=='phase': continue
            if event[0]=='climb' and event[5]==1:
                run.append((i,event))
            else:
                finish_run();run=[]
        finish_run()
        require(dict(counts)=={1:2412,2:418,3:432,4:142,5:82,8:8},'profile')
        require(cert['source']['rank_one_counts'][orientation]==counts[1],'rank-one count')
        require(len(groups)==8,'complete original batch census')
        for block in groups:
            for _,e in block:
                pair=(e[3],e[4]);wanted_pairs.add(pair)
                require(recipes[pair]['rank']==1,'recipe rank')
                require(len(word['frames'][pair[1]])-len(word['frames'][pair[0]])==1,'frame rank')
            expected_batches.append(dict(orientation=orientation,first_event=block[0][0],last_event=block[-1][0],
                registers=[e[2] for _,e in block],row_support={'2':8192}))
    require(cert['source']['batches']==expected_batches,'batch binding')
    require(cert['source']['unique_recipes']==len(wanted_pairs),'distinct recipe coverage')
    require(cert['source']['exact_recipe_columns']==512*len(wanted_pairs),'column coverage')
    reverse_rows = 0
    for pair in wanted_pairs:
        rec=recipes[pair]
        inverse_maps=[]
        for side in ['left','right']:
            mapping={perm_image(rec[side],x):x for x in range(512)}
            require(set(mapping)==set(range(512)),'monomial is a permutation')
            inverse_maps.append(mapping)
        il,ir=inverse_maps
        # For each output row, undo L, choose either C1 input, then undo R.
        for row in range(512):
            u=il[row]
            require(len({ir[u],ir[u^1]})==2,'two source coordinates in every row')
            reverse_rows+=1
    rec=recipes[855,1]
    x=perm_image(rec['right'],0)
    rphase=phase_at(rec['right'],0)
    witness=[]
    for u,c in [(x,(F(1,2),F(1,2))),(x^1,(F(1,2),F(-1,2)))]:
        value=times(times(c,rphase),phase_at(rec['left'],u))
        witness.append([perm_image(rec['left'],u),int(value[0]*2),int(value[1]*2)])
    require(cert['source']['first_selected_column']==dict(register=456,event=17006,old=855,new=1,
            input_coordinate=0,denominator=2,output=sorted(witness)),'selected coefficient witness')
    ob=cert['obstruction']
    require(ob==dict(original_batch_dimension=16*(1<<9),minimum_rank16_dimension=1<<16,
        batch_row_support=2,rank16_row_support=1<<16,
        padded_target_row_support={'1':(1<<16)-16*(1<<9),'2':16*(1<<9)},
        padded_candidate_row_support={'65536':1<<16},
        quantified_scope='One C_r child, r>=2, with arbitrary invertible monomial pre/post maps; independent arbitrary inputs including dirty spectators.'),'padded obstruction')
    permutations=matrix_controls(cert)
    print('PASS_INDEPENDENT_DIAGONAL_CONTRACT_ORACLE','reverse_rows='+str(reverse_rows),
          'permutation_pairs='+str(permutations),'no_new_kappa')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate',type=Path,default=HERE/'CERTIFICATE.json')
    parser.add_argument('--root',type=Path,default=ROOT)
    args=parser.parse_args()
    check(args.certificate,args.root)
