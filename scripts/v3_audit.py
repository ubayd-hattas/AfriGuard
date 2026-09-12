"""Reproduce the legacy baseline without executing its I/O or importing dependencies."""
import ast
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from v3_core import ROOT, dataset, digest, save, save_jsonl


def legacy_function():
    tree = ast.parse((ROOT/'scripts/judge.py').read_text(encoding='utf-8'))
    names = {'REFUSAL_PATTERNS','COMPLIANCE_PATTERNS','BLOCKED_PATTERNS'}
    nodes = [n for n in tree.body if
        isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in n.targets)
        or isinstance(n, ast.FunctionDef) and n.name == 'heuristic_label']
    ns = {'re': re}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), 'audited_legacy_heuristic', 'exec'), ns)
    return ns['heuristic_label']


def main():
    rows = dataset()
    f = legacy_function()
    comparisons = []
    for r in rows:
        label = f(r['response']) or 'partial'
        comparisons.append({'record_hash':r['record_hash'], 'model':r['model_short'],
            'prompt_id':r['prompt_id'], 'seed_id':r['seed_id'], 'language':r['language'],
            'harm_category':r['harm_category'], 'status':r['status'],
            'stored_label':r['historical_label'], 'reproduced_label':label,
            'matches':label==r['historical_label']})
    groups = {}
    for field in ['model','language','harm_category','status']:
        groups[field] = {}
        for value in sorted({r[field] for r in comparisons}):
            group = [r for r in comparisons if r[field]==value]
            counts = Counter(r['stored_label'] for r in group)
            groups[field][value] = {'n':len(group),'counts':dict(counts),
                                   'historical_asr':counts['compliance']/len(group)}
    baseline = '2c17d33'
    files = subprocess.check_output(['git','ls-tree','-r','--name-only',baseline], cwd=ROOT, text=True).splitlines()
    import hashlib
    # Keep the PRE-UPGRADE manifest reproducible even after README/UI corrections.
    # Original checkout used CRLF for text; preserve the initial working-tree hashes
    # rather than pretending Git's LF blobs have identical bytes.
    manifest_path = ROOT/'results/v3/audit/historical_file_hashes.json'
    if manifest_path.exists():
        import json
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    else:
        manifest = {f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}
    out = ROOT/'results/v3/audit'
    save(out/'historical_file_hashes.json', manifest)
    save_jsonl(out/'legacy_reproduction.jsonl', comparisons)
    save(out/'baseline.json', {'n':len(rows), 'dataset_hash':digest(rows),
         'mismatches':sum(not r['matches'] for r in comparisons),
         'counts':dict(Counter(r['stored_label'] for r in comparisons)),
         'groups':groups, 'python':sys.version,
         'source_commit':subprocess.check_output(['git','rev-parse',baseline],cwd=ROOT,text=True).strip()})
    # Sampling is stratified across model/language/category, independent of outcome.
    import random
    rng = random.Random(20260912)
    strata = defaultdict(list)
    for r in rows:
        strata[(r['model'],r['language'],r['harm_category'])].append(r)
    sample = [rng.choice(sorted(v,key=lambda r:r['prompt_id'])) for _,v in sorted(strata.items())]
    save_jsonl(out/'validation_sample.jsonl', sample)
    print('Audited',len(rows),'rows; mismatches:',sum(not r['matches'] for r in comparisons))


if __name__ == '__main__':
    main()
