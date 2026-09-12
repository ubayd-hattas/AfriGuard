"""Recover relevant deleted pre-correction evidence, without modifying Git history."""
import ast
import csv
import hashlib
import io
import json
import os
import subprocess
from collections import Counter
from v3_core import ROOT, MODELS, dataset, save, save_jsonl, save_text

REV='5e52f94'
PATHS=['analytics/evaluation.csv','AUDIT_REPORT.md','data/benchmark_prompts.csv',
       'AfriGuard/Judge/judge.py','AfriGuard/Tests/test_judge.py']


def blob(path):
    return subprocess.check_output(['git','show',REV+':'+path],cwd=ROOT)


def main():
    out=ROOT/'results/v3/history'
    manifest={}
    for path in PATHS:
        data=blob(path)
        target=out/'recovered'/path
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=data:
            raise FileExistsError(target)
        if not target.exists():target.write_bytes(data)
        manifest[path]={'git_revision':REV,'sha256':hashlib.sha256(data).hexdigest(),
                        'archive':target.relative_to(ROOT).as_posix()}
    old=list(csv.DictReader(io.StringIO(blob('analytics/evaluation.csv').decode('utf-8-sig'))))
    current={(r['model_short'],r['prompt_id']):r for r in dataset()}
    old_keys={(r['model'],r['prompt_id']) for r in old}
    missing=[r for k,r in current.items() if k not in old_keys]
    transitions=Counter()
    changes=[]
    for r in old:
        new=current[r['model'],r['prompt_id']]
        transitions[r['label']+' -> '+new['historical_label']]+=1
        if r['label']!=new['historical_label']:
            changes.append({'model':r['model'],'prompt_id':r['prompt_id'],
                            'pre_correction_label':r['label'],'v2_label':new['historical_label']})
    benchmark=list(csv.DictReader(io.StringIO(blob('data/benchmark_prompts.csv').decode('utf-8-sig'))))
    bench_keys={r['prompt_id']:r for r in benchmark}
    unique={r['prompt_id']:r for r in dataset()}
    shared=set(bench_keys)&set(unique)
    summary={'revision':REV,'recovered_evaluation_n':len(old),
       'label_counts':dict(Counter(r['label'] for r in old)),
       'historical_micro_asr':sum(r['label']=='compliance' for r in old)/len(old),
       'judging_methods':dict(Counter(r['judging_method'] for r in old)),
       'missing_relative_to_v2_n':len(missing),'missing_statuses':dict(Counter(r['status'] for r in missing)),
       'shared_label_transitions':dict(transitions),'shared_label_changes':changes,
       'benchmark_n':len(benchmark),'benchmark_languages':dict(Counter(r['language'] for r in benchmark)),
       'benchmark_shared_ids_with_current':len(shared),
       'benchmark_identical_prompts_with_current':sum(bench_keys[k]['prompt']==unique[k]['prompt'] for k in shared),
       'archived_live_test_cases':4,'archived_live_test_execution':'blocked: KIMI_API_KEY unavailable; requires removed OpenAI SDK and Windows-specific path',
       'kimi_key_available':bool(os.getenv('KIMI_API_KEY')),
       'interpretation':'Recovered pre-correction artifact is 952 records (953 physical lines including header), not a matching reconstruction of the reported V1 60.6% headline.'}
    save(out/'manifest.json',manifest)
    save(out/'summary.json',summary)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
