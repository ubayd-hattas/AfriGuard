"""Offline reproduction of next-stage validation evidence; NEVER emits corpus ASR.
Revalidates cached outputs against the frozen rubric/schema, sample and controls.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from v3_core import ROOT, digest, read_jsonl, save, save_jsonl
from v3_score import validate_judgment


def analyze(base):
    run=base/'local-qwen3-validation'
    sample=read_jsonl(ROOT/'results/v3/audit/validation_sample.jsonl')
    scores=read_jsonl(run/'sample_scores.jsonl')
    controls=read_jsonl(run/'stress_scores.jsonl')
    paired=read_jsonl(base/'refusal-crosscheck/paired_checks.jsonl')
    fixed={r['record_hash']:r for r in sample}
    if len(scores)!=112 or {r['record_hash'] for r in scores}!=set(fixed):
        raise ValueError('sample identities changed')
    composition=json.loads((run/'sample_composition.json').read_text())
    if composition['sample_hash']!=digest(sample):raise ValueError('fixed sample changed')
    fixtures=read_jsonl(ROOT/'configs/v3/semantic_stress_cases.jsonl')
    if fixtures!=read_jsonl(run/'stress_cases_snapshot.jsonl'):
        raise ValueError('control expectations changed after inference')
    errors=[]
    envelopes=[]
    for name,rows in [('sample',scores),('stress',controls)]:
        for r in rows:
            if name=='sample' and any(r[k]!=fixed[r['record_hash']][k] for k in ('response','prompt','language','harm_category')):
                raise ValueError('raw sample text changed')
            if r['judge_cache_key'] is None:
                if r['scoring_status']!='pending':raise ValueError('missing provenance')
                continue
            entry=json.loads((run/'cache'/(r['judge_cache_key']+'.json')).read_text(encoding='utf-8'))
            if entry['cache_key']!=digest({'request':entry['request'],'runtime_identity':entry['runtime_identity']}):
                raise ValueError('request cache integrity mismatch')
            payload=json.loads(entry['request']['messages'][1]['content'])
            if payload['response']!=r['response'] or payload['prompt']!=r['prompt']:
                raise ValueError('payload was not full original text')
            envelopes.append(entry['envelope'])
            try:
                j=validate_judgment(entry['content'],r['response'])
            except (ValueError,TypeError,KeyError) as exc:
                if r['scoring_status']!='invalid_judgment':raise ValueError('invalid judgment accepted')
                errors.append({'set':name,'record_hash':r['record_hash'],'reason':str(exc)})
            else:
                if r['scoring_status']!='scored' or j!=r['judgment']:
                    raise ValueError('accepted output altered')
    accepted=[r for r in scores if r['scoring_status']=='scored']
    protected=json.loads((ROOT/'results/v3/audit/historical_file_hashes.json').read_text())
    unchanged={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in protected.items()
               if p not in {'README.md','analytics/dashboard.py'}}
    transitions=Counter(r['historical_label']+' -> '+r['final_class'] for r in accepted)
    report={
      'experiment_id':'V3-NEXT-SEMANTIC-VALIDATION','status':'COMPLETED_VALIDATION_NOT_APPROVED',
      'model_identity':json.loads((run/'runtime.json').read_text()),
      'sample':composition,'accepted_candidate_classes':dict(Counter(r['final_class'] for r in accepted)),
      'accepted_sample_n':len(accepted),'invalid_sample_judgments':sum(r['scoring_status']=='invalid_judgment' for r in scores),
      'pending_blocked_sample_n':sum(r['scoring_status']=='pending' for r in scores),
      'semantic_ambiguous_accepted':sum(r['final_class']=='AMBIGUOUS' for r in accepted),
      'stress':{'n':len(controls),'schema_accepted':sum(r['scoring_status']=='scored' for r in controls),
         'expectations_met':sum(r['meets_expectation'] for r in controls),
         'gate_passed':all(r['meets_expectation'] for r in controls),
         'reference_type':'agent-authored synthetic expectations; no human/native-speaker certification'},
      'rejection_reasons_all_judgments':dict(Counter(r['reason'] for r in errors)),
      'candidate_historical_transitions_NOT_ground_truth':dict(transitions),
      'targeted_translation_check':{'n':len(paired),'class_changes':sum(r['original_score']['final_class']!=r['english_score']['final_class'] for r in paired),
          'sampling':'post-hoc two failed refusal controls','human_validated':False,'independent_judge':False},
      'main_run_usage':{'completed_requests':len(envelopes),
          'duration_seconds':sum(e['total_duration']/1e9 for e in envelopes),
          'input_tokens':sum(e['prompt_eval_count'] for e in envelopes),
          'output_tokens':sum(e['eval_count'] for e in envelopes)},
      'production_gate':'BLOCKED','language_competence':'NOT_ESTABLISHED',
      'corrected_corpus_asr':None,'corrected_corpus_breakdown':None,'confidence_intervals':None,
      'full_corpus_rescored':False,'target_inference_calls':0,
      'historical_metrics':{'v1_reported':{'n_reported':953,'definition':'reported heuristic headline; internally inconsistent','asr':.606},
          'recovered_pre_correction':{'n':952,'definition':'stored historical compliance / retained records','asr':565/952},
          'v2_stored':{'n':1120,'definition':'stored heuristic compliance / all records','asr':561/1120},
          'current_exact_replay':{'n':1120,'definition':'CRLF-sensitive current heuristic compliance / all records','asr':564/1120},
          'v3_semantic':{'n_intended_content':952,'n_rescored_after_gate':0,'definition':'validated semantic UNSAFE / content-bearing records; report missingness separately','asr':None}},
      'all_original_evidence_hashes_match':all(unchanged.values()),
      'fixed_sample_and_controls_unchanged':True,
      'translation_status':'two new response-control translations succeeded; no rerun of 240-prompt experiment',
      'intervention_status':'BLOCKED; zero target outcomes',
      'novel_attack_status':'not expanded; zero target outcomes',
      'resource_status':'quarantined; no candidates newly validated',
      'external_requirements':['Working independent multilingual judge (repair authorized CLI transport or configure reachable provider)',
          'Native-speaker review or strong independent validation of language competence, especially negation and broken/mixed text',
          'Provider/collection logs for 168 blocked historical records before interpreting all-attempt ASR'],
      'next_action':'Replace or independently validate the failed candidate before any full rescoring; do not tune to exposed controls and call that held-out validation.'}
    if not all(unchanged.values()):raise ValueError('historical evidence modified')
    # Add current engineering/access state without relabeling the prior local experiment.
    from v3_closeout import checkpoint
    report['current_execution_checkpoint'] = checkpoint()
    return report


def ledger(base,report):
    if 'current_execution_checkpoint' in report:
        from v3_closeout import extend_ledger
        return extend_ledger(report)
    main=base/'local-qwen3-validation'
    entries=[
      ('ACCESS','Determine available authorized judge access','Local/CLI access may exist without API-key environment variables',
       main/'runtime.json',1,1,'COMPLETED',
       'Existing local Qwen3 8B and 6 GB GPU found; a benign readiness completion succeeded; no model downloaded'),
      ('STRESS','Stress-test old scoring failure modes','A suitable judge must distinguish refusals, harm, nonsense and language mismatch semantically',
       main/'stress_scores.jsonl',12,12,'COMPLETED_CANDIDATE_NOT_APPROVED',
       '8/12 expectations met, 10 schema-valid outputs, two high-confidence African-language refusal errors'),
      ('FIXED-SAMPLE','Execute frozen validation sample','Full-text semantic judgments may differ from invalid legacy labels',
       main/'sample_scores.jsonl',112,95,'COMPLETED_VALIDATION_ONLY',
       '95 content-bearing calls; 83 schema-valid outputs, 12 rejected, 17 blocked records retained; no corpus metric'),
      ('TRANSLATION-CHECK','Diagnose two refusal errors using independent translation','Language negation errors may explain direct-versus-English inconsistency',
       base/'refusal-crosscheck/paired_checks.jsonl',2,2,'COMPLETED_DIAGNOSTIC',
       'Two Google response translations and two local English-view judgments completed; both UNSAFE to SAFE_REFUSAL'),
      ('REMOTE-ACCESS','Test existing subscription CLI without extracting credentials','Existing OAuth workflow may provide an independent judge',
       base/'cli_access_probe_sse.json',2,2,'BLOCKED',
       'Two CLI invocations (automatic and SSE) returned transport errors, no successful model response; Claude CLI not logged in'),
      ('CORE','Production semantic rescoring after validation gate','A defensible corrected ASR requires an approved judge',
       main/'summary.json',952,0,'BLOCKED',
       'Candidate did not pass gate; no full corpus rescoring, rates or intervals emitted'),
      ('DOWNSTREAM','Translation/intervention/attack/resource expansion only after valid scoring','Downstream efficacy requires trustworthy outcome measurement',
       base/'final_summary.json',None,0,'BLOCKED',
       'No 240-prompt retry, target-model intervention calls, novel-attack execution or resource release')]
    from datetime import datetime,timezone
    rows=[]
    for eid,purpose,hypothesis,path,n,executed,status,outcome in entries:
        rows.append({'experiment_id':'V3-NEXT-'+eid,'timestamp':datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat(),
            'timestamp_kind':'result artifact mtime, not inferred experiment start',
            'purpose':purpose,'hypothesis':hypothesis,'status':status,'n_planned':n,'n_executed':executed,
            'sample_unit':'CLI invocations' if eid=='REMOTE-ACCESS' else 'response records/control pairs',
            'data_version':'unchanged 2c17d33 response corpus and fixed 112-record V3 sample',
            'prompt_version':'V3 rubric unchanged; separately frozen synthetic stress fixtures',
            'models':['qwen3:8b'] if eid!='REMOTE-ACCESS' else ['openai-codex/gpt-6-astra','openai-codex/gpt-5.5'],
            'languages':['en','af','zu','xh','st','nso','ts'],
            'categories':['Financial Fraud','Gang/Criminal Facilitation','Political Disinformation','Xenophobic Incitement','scorer_validation'],
            'scorer_version':'v3.0 frozen rubric/schema','translation_system':'Google via deep-translator 1.11.4 for two diagnostic responses only',
            'configuration':{'temperature':0,'seed':20260912,'num_ctx':6144,'num_predict':512,
                'think':False,'kv_cache':'q8_0','num_gpu':99,'num_batch':128,'main_call_cap':107,'main_seconds_cap':1800}
                if eid!='REMOTE-ACCESS' else {'transports':['auto','sse'],'tools':False,'temperature':None,'retry_disabled_on_sse_probe':True},
            'random_seeds':[20260912] if eid!='REMOTE-ACCESS' else [],'result_location':path.relative_to(ROOT).as_posix(),'outcome':outcome,
            'compute_constraints':'6 GB GPU; no raw API keys; existing CLI completions failed; no native-speaker workflow',
            'assumptions':'Synthetic expectations are agent-authored, not human labels; independent translation is not independent-judge accuracy',
            'limitations':'Failed candidate cannot supply corrected corpus ASR; post-hoc translation diagnostic is not representative validation'} )
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base',type=Path,default=ROOT/'results/v3/next-stage')
    p.add_argument('--out',type=Path)
    args=p.parse_args()
    report=analyze(args.base)
    save(args.out or args.base/'final_summary.json',report)
    if args.out is None:
        save_jsonl(args.base/'experiment_log.jsonl',ledger(args.base,report))
    print(json.dumps({k:report[k] for k in ['status','accepted_sample_n','invalid_sample_judgments',
        'pending_blocked_sample_n','stress','production_gate','corrected_corpus_asr',
        'all_original_evidence_hashes_match']},indent=2))


if __name__=='__main__':main()
