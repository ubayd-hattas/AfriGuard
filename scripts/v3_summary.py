"""Generate the machine-readable final handoff from audit/QC evidence."""
import json
import subprocess
from v3_core import ROOT, save


def main():
    qc=json.loads((ROOT/'results/v3/final_qc-complete.json').read_text())
    added=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
    added=[p for p in added if not p.startswith('new feedback/')]
    added=sorted(set(added+['results/v3/final_summary.json','reports/V3_HANDOFF.md']))
    modified=subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()
    result={
      'A_repository_state':{'branch':qc['branch'],'baseline_commit':'2c17d33','version':'V3 pipeline 3.0; semantic benchmark incomplete',
          'commits_created':False,'files_added':added,'files_modified':modified,
          'files_preserved':sorted(qc['preserved_file_checks']),
          'historical_readme_archive':'reports/archive/README_V2_2c17d33.md',
          'user_feedback':'pre-existing untracked directory; read and left untouched'},
      'B_critical_findings':{'v2_criticism_applies':True,'legacy_method':'English regex and length; constant partial fallback',
          'v2_fix':'f8155c1 stopped dropping unclear rows; did not fix semantic validity',
          'newline_sensitive_rows':3,'repetition_truncated_apparent_successes':319,
          'v3_change':'Full-text multilingual structured judge; separate nonsense/refusal/unsafe/ambiguous; no lexical fallback'},
      'C_results':{'v1_reported_asr':.606,'v1_internally_inconsistent':True,
          'recovered_pre_correction_n':952,'recovered_pre_correction_asr':565/952,
          'recovered_missing_rows':168,'recovered_missing_status':'blocked',
          'v2_stored_asr':561/1120,'current_exact_legacy_replay_asr':564/1120,
          'v3_semantic_asr':None,'v3_difference_pp':None,'v3_relative_difference':None,
          'v3_scoring_coverage':0,'v3_unresolved_bounds':[0,1],
          'interpretation':'Historical heuristic rate reproduced/audited; no corrected semantic estimate available'},
      'D_translation_validation':{'attempted_inputs':240,'successful_back_translations':1,'semantic_comparisons':0,
          'successful_prompt_id':'11_nso','token_jaccard':.7333333333333333,
          'character_similarity':.9172932330827067,
          'findings':'Google HTML server error; alternative endpoint 429. No drift inference possible'},
      'E_interventions':{'matched_triplets_planned':96,'target_calls_completed':0,
          'effect_pp':None,'ci95':None,'reason':'No target API credential; 92/96 input-translation tasks also lack back-translations'},
      'F_novel_attack_families':{'families':['English wrapper / inter-sentential code-switch','lowercase orthographic variation'],
          'variant_tasks_planned':192,'tested_target_outcomes':0,'novelty_claim':False,
          'limitations':'Controlled plans only; existing prompts reused; four seed clusters'},
      'G_resource_prototype':{'benign_source_resources':4,'candidate_translations':24,'completed_round_trips':0,
          'evaluation_ready':0,'release_status':'quarantined pending semantic/native-speaker and safety validation'},
      'H_claim_changes':{'retained':['regional coverage','open raw response corpus','historical V2 label counts'],
          'weakened':['V2 correction means completeness only','gap and model rankings require semantic validation'],
          'corrected':['1120 responses not unique prompts','current LLM fallback is disabled','code-switch metric was monolingual gap'],
          'removed_from_current_claims':['human scoring','kappa 0.82','native-speaker validation','first discovery','causal morphology/MoE claims','validated catastrophic ASR'],
          'newly_supported':['952-row pre-correction artifact recovered; 953 includes header',
              '168 omitted rows all blocked; 11 shared labels changed in V2',
              'three CRLF-sensitive labels','319 apparent successes flagged repetition-truncated','22 passing contract tests']},
      'I_limitations':['No semantic model/API access','No human validation','168 provider-blocked historical rows',
          '239/240 back-translations failed','No target intervention outcomes','Mock tests do not validate language competence',
          'No original provider finish reasons or verified generation/translation settings'],
      'J_next_steps':['Validate multilingual judge on fixed sample with native speakers',
          'Recover original collection/truncation logs','Rescore 952 content-bearing responses and report unresolved bounds',
          'Complete authorized translation quality validation','Run fresh matched pilot before expanding scope'],
      'quality_control':{'tests_passed':22,'historical_evidence_preserved':qc['all_historical_evidence_preserved'],
          'archived_readme_matches':qc['archived_readme_matches_original'],
          'compile_passed':qc['compile_returncode']==0,'diff_check_passed':qc['diff_check_returncode']==0,
          'experiment_log':'results/v3/experiment_log.jsonl'},
      'overall_status':'Highest-priority audit and scoring infrastructure implemented; semantic results and efficacy experiments BLOCKED, not complete.'}
    save(ROOT/'results/v3/final_summary.json',result)


if __name__=='__main__':main()
