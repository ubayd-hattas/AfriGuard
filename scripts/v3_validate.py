"""Independent translated-view scorer cross-check; NOT human agreement.
Translate prompt AND response for evaluation only, never target input intervention.
"""
import argparse
from pathlib import Path
from v3_core import ROOT, Blocked, Router, digest, read_jsonl, save, save_jsonl
from v3_score import score_record
from v3_translation import Translator


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sample',type=Path,default=ROOT/'results/v3/audit/validation_sample.jsonl')
    p.add_argument('--primary',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--secondary-judge')
    p.add_argument('--max-calls',type=int,default=0)
    p.add_argument('--live-translation',action='store_true')
    args=p.parse_args()
    primary={r['record_hash']:r for r in read_jsonl(args.primary)}
    sample=read_jsonl(args.sample)
    router=Router(ROOT/'results/v3/cache/validation_judge',args.max_calls)
    translator=Translator(ROOT/'results/v3/cache/validation_translation') if args.live_translation else None
    results=[]
    failures=0
    for r in sample:
        a=primary[r['record_hash']]
        out={'record_hash':r['record_hash'],'prompt_id':r['prompt_id'],'model':r['model'],
             'language':r['language'],'primary_class':a['final_class'],
             'secondary':None,'status':'pending','agreement':None}
        if a['scoring_status']!='scored':
            out['reason']='primary_judgment_unavailable'
        elif not args.secondary_judge or args.secondary_judge==a['scorer_model']:
            out['reason']='independent_secondary_judge_required'
        else:
            try:
                translated=dict(r)
                if r['language']!='en':
                    if not translator or failures>=3:
                        raise Blocked('translation_offline_or_circuit_breaker')
                    translated['prompt']=translator.translate(r['prompt'],r['language'],'en')['translation']
                    translated['response']=translator.translate(r['response'],r['language'],'en')['translation']
                translated['language']='en'
                translated['record_hash']=digest(translated)
                b=score_record(translated,router,args.secondary_judge)
                out.update(secondary=b,status='cross_checked' if b['scoring_status']=='scored' else 'pending',
                           intermediate_translation={k:translated[k] for k in ('prompt','response')})
                if b['scoring_status']=='scored':
                    out['agreement']=a['final_class']==b['final_class']
            except Blocked as exc:
                failures+=1
                out['reason']=str(exc)
        results.append(out)
    paired=[r for r in results if r['agreement'] is not None]
    save_jsonl(args.out/'cross_checks.jsonl',results)
    save(args.out/'summary.json',{'sample_n':len(sample),'paired_n':len(paired),
        'agreement':sum(r['agreement'] for r in paired)/len(paired) if paired else None,
        'human_annotation':False,'sampling':'one per model x language x category; seed 20260912',
        'warning':'Automated cross-view agreement is not accuracy; translation may repair gibberish or erase harm. Disagreements require adjudication.'})


if __name__=='__main__':
    main()
