"""V3 immutable I/O, strict dataset joins, cached OpenRouter calls and statistics.
Standard library only. Historical scripts are intentionally not imported.
"""
import csv
import hashlib
import json
import os
import random
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = {'en': 'English', 'af': 'Afrikaans', 'zu': 'isiZulu', 'xh': 'isiXhosa',
             'st': 'Sesotho', 'nso': 'Sepedi', 'ts': 'Tsonga / Xitsonga'}
MODELS = {'GPT': 'openai/gpt-oss-20b', 'Kimi': 'moonshotai/kimi-k2.6',
          'Llama': 'meta-llama/llama-3.3-70b-instruct', 'Qwen': 'qwen/qwen3-32b'}


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     allow_nan=False).encode('utf-8')).hexdigest()


def read_jsonl(path):
    with Path(path).open(encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def save(path, value):
    """Atomic immutable artifact: identical rerun allowed; changed output needs new path."""
    path = Path(path)
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n'
    save_text(path, text)


def save_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text(encoding='utf-8') != text:
            raise FileExistsError(f'Refusing to overwrite evidence: {path}; use a new run directory')
        return
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(text, encoding='utf-8')
    temp.replace(path)


def save_jsonl(path, rows):
    save_text(path, ''.join(json.dumps(r, ensure_ascii=False, sort_keys=True, allow_nan=False) + '\n'
                            for r in rows))


def csv_rows(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def dataset():
    seeds = {r['prompt_id']: r for r in csv_rows(ROOT / 'data/seed_prompts.csv')}
    if len(seeds) != 40:
        raise ValueError('Expected 40 unique seeds')
    old = csv_rows(ROOT / 'data/results/evaluation.csv')
    old_keys = {(r['model'], r['prompt_id']): r for r in old}
    if len(old_keys) != len(old):
        raise ValueError('Duplicate historical evaluations')
    rows, seen, prompts = [], set(), {}
    for short, model in MODELS.items():
        path = ROOT / f'data/results/{short}responses.csv'
        for index, r in enumerate(csv_rows(path), 2):
            if r['model'] != model or r['language'] not in LANGUAGES:
                raise ValueError('Unknown model/language')
            key = (short, r['prompt_id'])
            if key in seen or key not in old_keys:
                raise ValueError('Duplicate or unmatched response')
            seen.add(key)
            if r['prompt_id'] != f"{r['seed_id']}_{r['language']}":
                raise ValueError('Prompt identity mismatch')
            s = seeds[r['seed_id']]
            if r['harm_category'] != s['harm_category']:
                raise ValueError('Category mismatch')
            for field in ('seed_id', 'language', 'harm_category'):
                if old_keys[key][field] != r[field]:
                    raise ValueError('Historical metadata mismatch')
            if r['prompt_id'] in prompts and prompts[r['prompt_id']] != r['prompt']:
                raise ValueError('Different prompt text across models')
            prompts[r['prompt_id']] = r['prompt']
            r.update(source_file=path.relative_to(ROOT).as_posix(), source_record=index,
                     model_short=short, english_source=s['english_prompt'],
                     historical_label=old_keys[key]['label'],
                     historical_method=old_keys[key]['judging_method'])
            r['record_hash'] = digest(r)
            rows.append(r)
    expected = {(m, f'{s}_{l}') for m in MODELS for s in seeds for l in LANGUAGES}
    if seen != expected or seen != set(old_keys):
        raise ValueError('Incomplete or unexpected factorial design')
    return rows


class Blocked(RuntimeError):
    pass


class Router:
    """Bounded live calls; cache keys include complete request, model and rubric text.

    No API payload or exception body is printed. Successful raw provider envelopes
    are preserved (without request credentials). No cached failure masquerades as data.
    """
    def __init__(self, cache, max_calls=0):
        self.cache = Path(cache)
        self.max_calls = max_calls
        self.calls = 0

    def call(self, model, system, payload, max_tokens=1600):
        request = {'model': model, 'messages': [
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False)}],
            'temperature': 0, 'max_tokens': max_tokens}
        key = digest(request)
        path = self.cache / (key + '.json')
        if path.exists():
            entry = json.loads(path.read_text(encoding='utf-8'))
            if entry['request'] != request:
                raise ValueError('Cache request mismatch')
            return entry
        if self.calls >= self.max_calls:
            raise Blocked('call_budget_exhausted_or_offline')
        api_key = os.getenv('OPENROUTER_API_KEY', '').strip()
        if not api_key:
            raise Blocked('missing_OPENROUTER_API_KEY')
        self.calls += 1
        req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',
            data=json.dumps(request).encode(), headers={
                'Authorization': 'Bearer ' + api_key, 'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                envelope = json.load(response)
        except urllib.error.HTTPError as exc:
            raise Blocked(f'provider_http_{exc.code}') from None
        except (urllib.error.URLError, TimeoutError):
            raise Blocked('provider_connection_error') from None
        choice = envelope.get('choices', [{}])[0]
        content = choice.get('message', {}).get('content')
        if choice.get('finish_reason') != 'stop' or not isinstance(content, str) or not content.strip():
            # Preserve incomplete envelopes separately; never treat these as valid judgments.
            save(self.cache / ('incomplete-' + key + '.json'),
                 {'request': request, 'envelope': envelope})
            raise Blocked('incomplete_provider_output')
        entry = {'request': request, 'envelope': envelope, 'content': content,
                 'cache_key': key, 'timestamp': now()}
        save(path, entry)
        return entry


def cluster_interval(rows, value, seed=20260912, draws=2000):
    """Percentile CI resampling seed IDs, retaining all within-seed dependencies."""
    groups = defaultdict(list)
    for r in rows:
        groups[r['seed_id']].append(value(r))
    keys = sorted(groups)
    if len(keys) < 2:
        return None
    rng = random.Random(seed)
    samples = []
    for _ in range(draws):
        vals = [v for k in rng.choices(keys, k=len(keys)) for v in groups[k]]
        samples.append(sum(vals) / len(vals))
    samples.sort()
    return [samples[int(.025 * draws)], samples[int(.975 * draws)]]


def summarize(rows):
    counts = Counter(r['final_class'] for r in rows)
    n = len(rows)
    pending = sum(r['scoring_status'] != 'scored' for r in rows)
    uncertain = counts['AMBIGUOUS']
    unsafe = counts['UNSAFE']
    complete = n > 0 and pending == 0
    return {'n': n, 'counts': dict(counts), 'pending': pending,
            'coverage': (n-pending)/n if n else None,
            'asr': unsafe/n if complete else None,
            'unresolved_bounds': [unsafe/n, (unsafe+uncertain)/n] if n else None,
            'seed_cluster_ci95': cluster_interval(rows, lambda r: int(r['final_class']=='UNSAFE'))
                if complete else None,
            'interpretation': 'automated provisional; not human validated'}
