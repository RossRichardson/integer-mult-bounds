#!/usr/bin/env python3
"""Artifact and relocation controls for the new audit, not the predecessor.

Ross Richardson with OpenAI Codex assistance. Apache-2.0.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0,str(Path(__file__).resolve().parent))
import audit


def run(root,pkg,success,reason=''):
    p = subprocess.run([sys.executable,'-I','-O','-B',str(pkg/'audit.py')],cwd=root,
                       capture_output=True,text=True,encoding='utf-8',timeout=120)
    audit.need((p.returncode == 0) == success and reason in p.stdout+p.stderr,
               'unexpected own-audit test '+str((p.returncode,p.stdout[-300:],p.stderr[-600:])))


def main():
    audit.pins()
    with tempfile.TemporaryDirectory(prefix='copyshare-own-controls-') as temp:
        root = Path(temp)/'read only repo'
        pkg = root/'research'/audit.HERE.name
        shutil.copytree(audit.HERE,pkg)
        for rel in audit.INPUTS:
            dst = root/rel;dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(audit.ROOT/rel,dst)
        # Read-only relocated optimized positive control.
        files = [p for p in root.rglob('*') if p.is_file()]
        try:
            for p in files:p.chmod(0o444)
            run(root,pkg,True,'PASS_COPYSHARE_INDEPENDENT_AUDIT')
        finally:
            for p in files:p.chmod(0o644)
        cert = pkg/'RESULT.json';frozen = cert.read_bytes()
        bad = json.loads(frozen);bad['bills']['match']['F'] += 1
        cert.write_text(json.dumps(bad),encoding='utf-8')
        run(root,pkg,False,'typed receipt mismatch')
        bad = json.loads(frozen);bad['new_kappa'] = 0
        cert.write_text(json.dumps(bad),encoding='utf-8')
        run(root,pkg,False,'typed receipt mismatch')
        cert.unlink()
        run(root,pkg,False,'RESULT.json')
        audit.need(not cert.exists(),'missing receipt was silently regenerated')
        cert.write_bytes(frozen)
        word = root/audit.WORD;raw = word.read_bytes();word.write_bytes(b'!'+raw[1:])
        run(root,pkg,False,'source bytes')
        word.write_bytes(raw)
        manifest = pkg/'SOURCES.json';bad = json.loads(manifest.read_bytes())
        bad['files'] = [i for i in bad['files'] if i['path'] != audit.WORD]
        manifest.write_text(json.dumps(bad),encoding='utf-8')
        run(root,pkg,False,'source inventory')
    print('PASS_COPYSHARE_AUDIT_PACKAGE_CONTROLS optimized_readonly_relocation=1 corruptions=5')


if __name__ == '__main__':main()
