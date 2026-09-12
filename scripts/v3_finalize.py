"""Reproducible final QC and evidence inventory; no model/network calls.
Writes final_qc.json; use --out for a new QC artifact after further changes.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from v3_core import ROOT, save


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=ROOT/'results/v3/final_qc.json')
    args=p.parse_args()
    manifest=json.loads((ROOT/'results/v3/audit/historical_file_hashes.json').read_text())
    intended={'README.md','analytics/dashboard.py'}
    checks={}
    for name,old_hash in manifest.items():
        if name not in intended:
            checks[name]=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==old_hash
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True)
    compile_result=subprocess.run([sys.executable,'-m','compileall','-q','scripts','analytics','tests'],cwd=ROOT,capture_output=True,text=True)
    diff=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True)
    # Verify case accounting in saved artifacts, without reclassifying missing data as zero.
    scores=[json.loads(l) for l in (ROOT/'results/v3/core-offline/scored_responses.jsonl').read_text(encoding='utf-8').splitlines()]
    metrics=json.loads((ROOT/'results/v3/core-offline/metrics.json').read_text())
    baseline=json.loads((ROOT/'results/v3/audit/baseline.json').read_text())
    accounting=len(scores)==1120 and metrics['overall']['asr'] is None and baseline['mismatches']==3
    import re
    candidate_paths = subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
    secret_matches=[]
    for name in candidate_paths:
        path=ROOT/name
        if path.is_file() and path.suffix.lower() in {'.py','.md','.json','.jsonl','.txt','.csv'}:
            if re.search(rb'sk-(?:or-v1-|proj-)?[A-Za-z0-9_-]{32,}',path.read_bytes()):
                secret_matches.append(name)
    archive_matches = hashlib.sha256((ROOT/'reports/archive/README_V2_2c17d33.md').read_bytes()).hexdigest()==manifest['README.md']
    result={'preserved_file_checks':checks,'all_historical_evidence_preserved':all(checks.values()),
            'archived_readme_matches_original':archive_matches,
            'common_api_secret_pattern_matches':secret_matches,
            'intentional_modifications':sorted(intended),
            'tests_returncode':tests.returncode,'test_output':tests.stdout+tests.stderr,
            'compile_returncode':compile_result.returncode,'diff_check_returncode':diff.returncode,
            'accounting_passed':accounting,
            'baseline_commit':'2c17d33','branch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
            'semantic_results_available':False,'human_validation_performed':False}
    save(args.out,result)
    print(json.dumps({k:v for k,v in result.items() if k not in {'test_output','preserved_file_checks'}},indent=2))
    if not all(checks.values()) or not archive_matches or secret_matches or tests.returncode or compile_result.returncode or diff.returncode or not accounting:
        raise SystemExit(1)


if __name__=='__main__':main()
