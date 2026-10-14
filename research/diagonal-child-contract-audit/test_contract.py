#!/usr/bin/env python3
"""Semantic/source/certificate corruption and portable replay controls. Apache-2.0."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('contract_audit', HERE/'verify.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = audit.read_inputs()
        cls.cert = json.loads((HERE/'CERTIFICATE.json').read_text())

    def run_engine(self, engine, *args, ok=True, cwd=ROOT):
        p = subprocess.run([sys.executable,'-I','-O','-B',str(HERE/engine),*map(str,args)],
                           cwd=cwd,capture_output=True,text=True,timeout=20)
        self.assertEqual(p.returncode == 0,ok,p.stdout+p.stderr)
        return p

    def test_positive_both_engines(self):
        for engine in ['verify.py','oracle.py']:
            self.run_engine(engine)

    def test_six_certificate_corruptions_both_engines(self):
        def drop_batch(c): c['source']['batches'].pop()
        def wrong_support(c): c['obstruction']['rank16_row_support']=16
        def wrong_padding(c): c['obstruction']['padded_target_row_support']['1']-=1
        def bad_coefficient(c): c['source']['first_selected_column']['output'][0][1]*=-1
        def false_equivalence(c): c['controls']['minimal_counterexample']['rank_two_child']=c['controls']['minimal_counterexample']['direct_sum']
        def missing_recipe(c): c['source']['exact_recipe_columns']-=512
        with tempfile.TemporaryDirectory(prefix='diagonal-contract-mutants-') as tmp:
            file=Path(tmp)/'certificate.json'
            for mutation in [drop_batch,wrong_support,wrong_padding,bad_coefficient,false_equivalence,missing_recipe]:
                with self.subTest(mutation=mutation.__name__):
                    changed=copy.deepcopy(self.cert);mutation(changed)
                    file.write_text(json.dumps(changed))
                    for engine in ['verify.py','oracle.py']:
                        self.run_engine(engine,'--certificate',file,ok=False)

    def test_semantic_source_mutants(self):
        # Bypass only immutable hash checking to exercise the actual semantic checks.
        changed=copy.deepcopy(self.inputs)
        changed['LOCAL-PROGRAMS.json.gz']['forward'][17006][5]=16
        with self.assertRaisesRegex(audit.Reject,'paid profile'):
            audit.source_census(changed)
        changed=copy.deepcopy(self.inputs)
        events=changed['LOCAL-PROGRAMS.json.gz']['forward']
        events[17006][2]=events[17007][2]
        with self.assertRaisesRegex(audit.Reject,'independent registers'):
            audit.source_census(changed)
        rec=copy.deepcopy(next(r for r in self.inputs['CLIFFORD-RECIPES.json']['children']
                              if (r['old'],r['new'])==(855,1)))
        rec['rank']=16
        with self.assertRaisesRegex(audit.Reject,'ambient dimension'):
            audit.child_columns(rec,9)
        rec['rank']=1
        rec['left']['matrix_rows'][0]=0
        with self.assertRaisesRegex(audit.Reject,'singular monomial'):
            audit.child_columns(rec,9)

    def test_read_only_relocation_and_real_source_corruption(self):
        with tempfile.TemporaryDirectory(prefix='diagonal-contract-relocation-') as tmp:
            relocated=Path(tmp)
            package=relocated/'research/diagonal-child-contract-audit'
            shutil.copytree(HERE,package,ignore=shutil.ignore_patterns('__pycache__'))
            pins=json.loads((HERE/'SOURCES.json').read_text())['files']
            for pin in pins:
                if pin['usage']=='input':
                    dest=relocated/pin['path'];dest.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copyfile(ROOT/pin['path'],dest)
            files=[p for p in relocated.rglob('*') if p.is_file()]
            before={str(p.relative_to(relocated)):audit.sha(p.read_bytes()) for p in files}
            for p in files:p.chmod(0o444)
            for engine in ['verify.py','oracle.py']:
                result=subprocess.run([sys.executable,'-I','-O','-B',str(package/engine)],
                    cwd=tmp,capture_output=True,text=True,timeout=20,
                    env=dict(os.environ,PYTHONOPTIMIZE='2'))
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            after={str(p.relative_to(relocated)):audit.sha(p.read_bytes()) for p in relocated.rglob('*') if p.is_file()}
            self.assertEqual(before,after)
            source=relocated/audit.ARCHIVE;source.chmod(0o644)
            raw=bytearray(source.read_bytes());raw[-1]^=1;source.write_bytes(raw)
            for engine in ['verify.py','oracle.py']:
                self.run_engine(engine,'--root',relocated,ok=False)

if __name__=='__main__':
    unittest.main()
