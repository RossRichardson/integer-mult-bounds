"""Bounded registered replay; the complete cold release remains separate."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,tempfile
from fractions import Fraction as Q
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
def need(v,m):
 if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 for rel,digest in json.loads((P/'ARTIFACTS.json').read_bytes()).items():
  q=P/rel;need(q.is_file() and not q.is_symlink() and sha(q)==digest,'immutable package input '+rel)
 # ARTIFACTS.json is the package's generated output manifest. The outer
 # registered runner checks its committed bytes before launch; permit this
 # verifier to refresh it after checking every listed input.
 before={str(p.relative_to(P)):sha(p) for p in P.rglob('*') if p.is_file() and p.name!='ARTIFACTS.json'}
 with tempfile.TemporaryDirectory(prefix='staged-owner-moment-') as t:
  out=Path(t)/'replay';env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPYCACHEPREFIX=str(Path(t)/'pycache'))
  for k in ('PYTHONOPTIMIZE','PYTHONPATH'):env.pop(k,None)
  r=subprocess.run([sys.executable,'-B',str(P/'check_owners_and_moment.py'),'--repo',str(ROOT),'--word-package',str(ROOT/'research/staged-644-660-width-reduction'),'--out',str(out)],env=env)
  need(r.returncode==0,'fresh owner and moment replay failed')
  result=json.loads((out/'RESULT.json').read_bytes())
  need(result['status']=='PASS_FRESH_FINITE_OWNER_MOMENT_AND_OUTER' and result['roles']==2717280,'fresh full owner check result')
  claim=json.loads((P/'CLAIM.json').read_bytes())
  precision=P/claim['precision_refinement_receipt']
  need(precision.is_file() and sha(precision)==claim['precision_refinement_receipt_sha256'],'60-digit refinement receipt pin')
  receipt=json.loads(precision.read_bytes())
  need(receipt['status']=='PASS_FRESH_60_DIGIT_CONDITIONAL_ENDPOINT_REFINEMENT','refinement receipt status')
  need(receipt['inherited_full_release_receipt_sha256']==sha(P/'evidence/RELEASE-RECEIPT.json'),'inherited complete release pin')
  need(Q(receipt['kappa'])==Q(claim['kappa']) and Q(receipt['strict_gain'])==Q(claim['strict_gain']),'refined claim and exact gain bind receipt')
  need(receipt['profile']==claim['profile'] and receipt['root_interval_rational']==claim['root_interval'],'refined profile/root bind receipt')
  need(result['profile']==claim['profile'] and result['root_interval']==claim['root_interval'],'fresh complete histogram and root bind claim')
  need(Q(result['kappa'])==Q(claim['kappa'])==Q(claim['kappa_decimal'])>Q('0.00173'),'fresh exact conditional arithmetic binds claim')
  need(Q(claim['kappa'])-Q(claim['predecessor_kappa'])==Q(claim['strict_gain']),'strict improvement over pinned predecessor')
 need(all((P/rel).is_file() and sha(P/rel)==digest for rel,digest in before.items()),'package input drift')
 files={str(p.relative_to(P)):sha(p) for p in P.rglob('*') if p.is_file() and p.name!='ARTIFACTS.json'}
 (P/'ARTIFACTS.json').write_text(json.dumps(dict(sorted(files.items())),indent=2)+'\n')
 print('PASS_STAGED_PAIR_REGISTERED_OWNER_MOMENT_OUTER')
if __name__=='__main__':main()
