"""Offline-only checkpoint from preserved access attempts and QC; no network code."""
import hashlib
import json
from pathlib import Path
from v3_core import ROOT, digest, read_jsonl
from v3_score import SYSTEM, validate_judgment

BASE = ROOT / 'results/v3/offline-closeout'
GATE = ROOT / 'results/v3/judge-access-gate-corrected'


def checkpoint():
    cases = read_jsonl(GATE / 'fixtures.jsonl')
    protocol = json.loads((GATE / 'protocol.json').read_text())
    if digest(cases) != protocol['fixtures_hash'] or digest(SYSTEM) != protocol['rubric_hash']:
        raise ValueError('Frozen diagnostics or rubric changed')
    if digest(read_jsonl(ROOT / 'results/v3/audit/validation_sample.jsonl')) != protocol['fixed_sample_hash']:
        raise ValueError('Fixed sample changed')
    attempts = []
    for name in ('00-1', '00-2', '99-access-only'):
        request = json.loads((GATE / 'attempts' / (name + '.request.json')).read_text(encoding='utf-8'))
        result = json.loads((GATE / 'attempts' / (name + '.result.json')).read_text(encoding='utf-8'))
        if digest(request['request']) != request['request_hash'] or result['request_hash'] != request['request_hash']:
            raise ValueError('Diagnostic request identity mismatch')
        attempts.append(result)
    first, repeat, access = attempts
    if first['request_hash'] != repeat['request_hash']:
        raise ValueError('Reproducibility requests were not identical')
    judged = validate_judgment(first['content'], cases[0]['response'])
    if judged != first['judgment'] or judged['final_class'] != 'SAFE_REFUSAL':
        raise ValueError('Saved accepted control altered')
    if any(r['error_classification'] != 'TRANSPORT' or r['actual_class'] is not None or
           r['judgment'] is not None for r in (repeat, access)):
        raise ValueError('Transport failure acquired a scientific label')
    if not first['control_pass'] or repeat['control_pass'] is not None:
        raise ValueError('Control accounting changed')
    qc_path = BASE / 'final_qc.json'
    qc = json.loads(qc_path.read_text()) if qc_path.exists() else None
    qc_passed = bool(qc and all(qc[k] == 0 for k in ('tests_returncode', 'compile_returncode', 'diff_check_returncode'))
                     and qc['all_historical_evidence_preserved'] and qc['accounting_passed']
                     and not qc['common_api_secret_pattern_matches'])
    return {
        'scope': 'Current offline closeout; top-level sample counts remain the prior local experiment',
        'remote_judge': 'BLOCKED — NOT REPRODUCIBLE',
        'semantic_judge_validation': 'BLOCKED', 'native_speaker_validation': 'NOT AVAILABLE',
        'historical_semantic_rescore': 'NOT RUN', 'corrected_semantic_asr': None,
        'remote_calls_during_offline_closeout': 0,
        'prior_corrected_access_gate': {
            'structured_attempted': 2, 'schema_accepted': 1, 'schema_invalid': 0,
            'timed_out': 0, 'transport_blocked': 1, 'control_pass': 1, 'control_fail': 0,
            'control_unavailable': 1, 'remaining_planned_calls_not_run': 28,
            'websocket_access_only_attempted': 1, 'websocket_access_only_blocked': 1,
            'identical_request_hash': first['request_hash'],
            'semantic_consistency': None, 'multilingual_accuracy': None,
            'evidence': GATE.relative_to(ROOT).as_posix()},
        'pre_fix_adapter_attempt': {
            'attempted': 1, 'schema_evaluated': 0, 'status': 'BLOCKED',
            'reason': 'Pre-schema wrapper rejection; original artifact lacks block-type evidence',
            'evidence': 'results/v3/judge-access-gate'},
        'completed': ['engineering recovery', 'offline scorer infrastructure',
                      'cached evidence verification', 'access diagnostic stage'] +
                     (['offline validation/QC'] if qc_passed else []),
        'blocked': ['reliable remote semantic judge', 'multilingual judge approval',
                    'native-speaker validation', 'corrected historical semantic rescore',
                    'intervention efficacy', 'translation reliability validation'],
        'not_run': ['remaining remote multilingual controls', 'remote 112-record validation sample',
                    '952-record historical semantic rescore', 'full intervention matrix',
                    'new large translation campaign', 'novel attack semantic evaluation',
                    'resource adaptation evaluation'],
        'offline_qc': 'COMPLETED' if qc_passed else 'NOT RUN',
        'offline_qc_location': qc_path.relative_to(ROOT).as_posix(),
        'scientific_accuracy_threshold': 'UNRESOLVED; synthetic expectations are not a population accuracy threshold',
        'next_action': 'After independently established stable authorized access, run frozen multilingual controls '
                       'and the unchanged 112-record validation sample; document approval before any historical rescore',
        'prohibited_shortcut': 'No English lexical/length heuristic or missing-to-zero substitution',
    }


def extend_ledger(report):
    """Preserve original artifact timestamps; append current scope, never redate history."""
    archive = BASE / 'prior-nextstage'
    manifest = json.loads((archive / 'manifest.json').read_text())['sha256']
    for name, expected in manifest.items():
        if hashlib.sha256((archive / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Archived checkpoint changed')
    rows = read_jsonl(archive / 'experiment_log.jsonl')
    # Keep separately scoped observed attempts, including the initial adapter rejection.
    for run in (ROOT / 'results/v3/judge-access-gate', GATE):
        for item in read_jsonl(run / 'experiment_log.jsonl'):
            rows.append({**item, 'ledger_scope': run.relative_to(ROOT).as_posix()})
    state = report['current_execution_checkpoint']
    from datetime import datetime, timezone
    qc_path = BASE / 'final_qc.json'
    stamp_path = qc_path if qc_path.exists() else GATE / 'summary.json'
    rows.append({'experiment_id': 'V3-OFFLINE-CLOSEOUT',
                 'timestamp': datetime.fromtimestamp(stamp_path.stat().st_mtime, timezone.utc).isoformat(),
                 'timestamp_kind': 'QC/result artifact mtime, not an experiment start',
                 'sample_unit': 'engineering checkpoint; not response records',
                 'status': state['offline_qc'], 'remote_calls': 0,
                 'purpose': 'Verify cached evidence and preserve explicit blocked/not-run states',
                 'result_location': state['offline_qc_location'],
                 'completed': state['completed'], 'blocked': state['blocked'], 'not_run': state['not_run'],
                 'corrected_semantic_asr': None, 'native_speaker_validation': 'NOT AVAILABLE'})
    return rows
