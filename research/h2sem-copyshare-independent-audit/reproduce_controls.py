#!/usr/bin/env python3
"""Reproduce PR1805 control gaps and a proposed repair in disposable exports.

These are mutation tests of the original implementation, not independent
mathematical checks. Only audit.py supplies the separate mathematical replay.
Ross Richardson with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import difflib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0,str(Path(__file__).resolve().parent))
import audit

HERE = audit.HERE
CHECK = '        semantic_n(drop["D"], word["v"], word["R"])'
ORIGINAL_CONTROL = '''    try:
        semantic_n(drop["D"], word["v"], word["R"])
        raise ValueError("partial matching unrestored accepted")
    except ValueError:
        rejected.append("partial_matching_unrestored")
'''
REPAIRED_CONTROL = '''    try:
        semantic_n(drop["D"], word["v"], word["R"])
    except ValueError as exc:
        need("helper restoration" in str(exc), "unexpected partial-matching failure: " + str(exc))
        rejected.append("partial_matching_unrestored")
    else:
        raise ValueError("partial matching unrestored accepted")
'''
ORIGINAL_CERT = '''    certificate = HERE / "CERTIFICATE.json"
    if certificate.exists():
        need(report == json.loads(certificate.read_text(encoding="utf-8")),
             "certificate mismatch")
    else:
        certificate.write_text(json.dumps(report, indent=2) + "\\n", encoding="utf-8")
'''
REPAIRED_CERT = '''    certificate = HERE / "CERTIFICATE.json"
    if args.write:
        certificate.write_text(json.dumps(report, indent=2) + "\\n", encoding="utf-8")
    else:
        need(report == json.loads(certificate.read_text(encoding="utf-8")),
             "certificate mismatch")
'''


def repaired_source(original):
    for block in (ORIGINAL_CONTROL,ORIGINAL_CERT,'def main():\n    check_pins()'):
        audit.need(original.count(block) == 1,'unique patch anchor')
    result = original.replace('import copy\n','import argparse\nimport copy\n',1)
    result = result.replace(ORIGINAL_CONTROL,REPAIRED_CONTROL)
    result = result.replace(ORIGINAL_CERT,REPAIRED_CERT)
    return result.replace('def main():\n    check_pins()', '''def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="explicitly regenerate CERTIFICATE.json")
    args = parser.parse_args()
    need(args.write or (HERE / "CERTIFICATE.json").is_file(),
         "missing certificate; use --write only for intentional regeneration")
    check_pins()''')


def materialize(root):
    pkg = root/'research/h2sem-copyshare-priced'
    shutil.copytree(HERE/'inputs/pr1805',pkg)
    pins = audit.read(pkg/'SOURCES.json')
    for i in pins['files']:
        src = (HERE/'inputs/context'/Path(i['path']).name) if i['usage'] == 'provenance' else audit.ROOT/i['path']
        dst = root/i['path'];dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(src.read_bytes())
    return pkg


def run(root,pkg,entry='verify.py',extra=(),optimized=False):
    argv = [sys.executable,'-I','-B']+(['-O'] if optimized else [])+[str(pkg/entry),*extra]
    p = subprocess.run(argv,cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=180,
                       env={k:v for k,v in os.environ.items() if k != 'PYTHONOPTIMIZE'})
    return p.returncode,p.stdout,p.stderr


def expect(result,passed,substring):
    code,out,err = result
    audit.need((code == 0) == passed and substring in out+err,
               'unexpected replay outcome '+str((code,out[-600:],err[-600:])))


def compute():
    audit.pins()
    original = (HERE/'inputs/pr1805/verify.py').read_text(encoding='utf-8')
    repaired = repaired_source(original)
    audit.need(original.count(CHECK) == repaired.count(CHECK) == 1,'unique mutation')
    patch = ''.join(difflib.unified_diff(original.splitlines(keepends=True),repaired.splitlines(keepends=True),
                                       fromfile='a/research/h2sem-copyshare-priced/verify.py',
                                       tofile='b/research/h2sem-copyshare-priced/verify.py'))
    audit.need((HERE/'repair.patch').read_text(encoding='utf-8') == patch,'repair patch mismatch')
    rows = []
    with tempfile.TemporaryDirectory(prefix='copyshare-audit-') as temp:
        root = Path(temp)/'repo with spaces';pkg = materialize(root)
        source = pkg/'verify.py';certificate = pkg/'CERTIFICATE.json';frozen = certificate.read_bytes()
        expect(run(root,pkg),True,'PASS_H2SEM_COPYSHARE_PRICED')
        audit.need(certificate.read_bytes() == frozen,'original baseline mutated certificate')
        rows.append('original positive replay passes')
        # Actual fault injection: remove only the named two-pair negative probe.
        # All real candidate checks, other controls and frozen certificate stay intact.
        source.write_text(original.replace(CHECK,'        pass  # AUDIT: defect detector removed'),encoding='utf-8')
        for optimized in (False,True):
            expect(run(root,pkg,optimized=optimized),True,'PASS_H2SEM_COPYSHARE_PRICED')
        expect(run(root,pkg,entry='test_package.py'),True,'PASS_H2SEM_COPYSHARE_PRICED_PACKAGE_CONTROLS')
        rows.append('omitted two-pair probe passes normal optimized and all original package tests')
        source.write_text(original,encoding='utf-8');certificate.unlink()
        expect(run(root,pkg),True,'PASS_H2SEM_COPYSHARE_PRICED')
        audit.need(certificate.read_bytes() == frozen,'regenerated certificate differs')
        rows.append('original default replay recreates missing certificate and passes')
        # Positive repair control uses the exact same committed numerical receipt.
        source.write_text(repaired,encoding='utf-8')
        expect(run(root,pkg),True,'PASS_H2SEM_COPYSHARE_PRICED')
        audit.need(certificate.read_bytes() == frozen,'repair changed numeric receipt')
        rows.append('repair passes unchanged numerical certificate')
        source.write_text(repaired.replace(CHECK,'        pass  # AUDIT: defect detector removed'),encoding='utf-8')
        for optimized in (False,True):
            expect(run(root,pkg,optimized=optimized),False,'partial matching unrestored accepted')
        rows.append('repair rejects omitted probe normally and under optimization')
        source.write_text(repaired,encoding='utf-8');certificate.unlink()
        expect(run(root,pkg),False,'missing certificate')
        audit.need(not certificate.exists(),'missing-certificate failure wrote an artifact')
        rows.append('repair rejects missing certificate without writing')
        expect(run(root,pkg,extra=('--write',)),True,'PASS_H2SEM_COPYSHARE_PRICED')
        audit.need(certificate.read_bytes() == frozen,'explicit regeneration changed receipt')
        rows.append('explicit write recreates identical certificate')
    return dict(predecessor_head='b34e0620bd92af49c9095e0eeb885f601fffd137',checks=rows,
                mathematics_refuted=False,repair_applied_upstream=False)


def main():
    ap = argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args = ap.parse_args()
    report = compute();path = HERE/'CONTROL-RESULT.json'
    if args.write:path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    else:audit.need(audit.canonical(report) == audit.canonical(audit.read(path)),'control receipt mismatch')
    print('PASS_COPYSHARE_CONTROL_AUDIT original_gaps=2 repaired_checks=4 no_mathematical_counterexample')


if __name__ == '__main__':main()
