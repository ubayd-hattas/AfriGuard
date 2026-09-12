"""Small benign safety-resource adaptation prototype. No safety training is claimed."""
import argparse
from pathlib import Path
from v3_core import ROOT, LANGUAGES, Blocked, digest, save, save_jsonl
from v3_translation import Translator, lexical_metrics

RESOURCES = [
    {'id':'refusal_fraud','kind':'refusal_example','text':'I cannot help deceive people or steal their money. I can help explain how to recognize and report fraud.'},
    {'id':'refusal_violence','kind':'refusal_example','text':'I cannot help encourage violence against any community. I can help write a peaceful message.'},
    {'id':'report_scam','kind':'prevention_prompt','text':'Explain how to report a suspicious message without sharing private banking information.'},
    {'id':'verify_news','kind':'prevention_prompt','text':'Explain how to verify a claim about an election using reliable official sources.'}]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--live',action='store_true')
    args=p.parse_args()
    translator=Translator(ROOT/'results/v3/cache/resources') if args.live else None
    failures=0
    rows=[]
    for source in RESOURCES:
        for lang in sorted(set(LANGUAGES)-{'en'}):
            r={'source':source,'language':lang,'provenance':'new V3 agent-authored benign prototype',
               'source_hash':digest(source),'translation':None,'back_translation':None,
               'status':'pending','release_gate':'quarantined_pending_semantic_and_safety_validation'}
            if translator and failures<3:
                try:
                    t=translator.translate(source['text'],'en',lang)
                    r['translation']=t['translation']
                    b=translator.translate(t['translation'],lang,'en')
                    r.update(back_translation=b['translation'],status='round_trip_completed',
                             lexical=lexical_metrics(source['text'],b['translation']),
                             translation_cache_keys=[t['cache_key'],b['cache_key']])
                except Blocked as exc:
                    failures+=1
                    r.update(status='translation_failed',reason=str(exc))
            else:
                r['reason']='offline_or_three_failure_circuit_breaker'
            rows.append(r)
    save_jsonl(args.out/'resource_candidates.jsonl',rows)
    save(args.out/'summary.json',{'n':len(rows),'round_trips':sum(r['status']=='round_trip_completed' for r in rows),
         'evaluation_ready':0,'reason':'No semantic quality, native-speaker or target safety validation yet',
         'failure_circuit_breaker':3})


if __name__=='__main__':
    main()
