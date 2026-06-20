#!/usr/bin/env python3
"""
run_groq_only.py
----------------
Run all working prompts (English + isiZulu + Afrikaans + Tsonga) through Groq Llama.
Filters out Swati failures automatically.
"""

import os
import time
import pandas as pd
from groq import Groq
from tqdm import tqdm

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

# ── Load and filter prompts ──────────────────────────────────────────────────
df = pd.read_csv(r"D:\AfriGuard\data\benchmark_prompts.csv")

# Filter out Swati failures
working = df[~df["prompt"].str.startswith("[TRANSLATION_FAILED", na=False)].copy()
print(f"Total: {len(df)} | Working: {len(working)} | Skipped Swati failures: {len(df) - len(working)}")
print(working["language_name"].value_counts())

# ── Load existing progress ─────────────────────────────────────────────────
output_path = r"D:\AfriGuard\data\results\responses.csv"
if os.path.exists(output_path):
    existing = pd.read_csv(output_path)
    done = set(zip(existing["prompt_id"], existing["model"]))
    print(f"\nResuming from {len(existing)} existing responses")
else:
    existing = pd.DataFrame()
    done = set()
    print("\nStarting fresh")

# ── Run prompts ─────────────────────────────────────────────────────────────
results = []

for _, row in tqdm(working.iterrows(), total=len(working)):
    key = (row["prompt_id"], "groq_llama")
    if key in done:
        continue
    
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": row["prompt"]},
            ],
            temperature=0.0,
            max_tokens=512,
        )
        response = completion.choices[0].message.content.strip()
    except Exception as e:
        response = f"[API_ERROR: {e}]"
    
    results.append({
        "prompt_id": row["prompt_id"],
        "seed_id": row["seed_id"],
        "language": row["language"],
        "language_name": row["language_name"],
        "harm_category": row["harm_category"],
        "model": "groq_llama",
        "prompt": row["prompt"],
        "response": response,
    })
    
    # Save every 10
    if len(results) % 10 == 0:
        combined = pd.concat([existing, pd.DataFrame(results)], ignore_index=True) if not existing.empty else pd.DataFrame(results)
        combined.to_csv(output_path, index=False)
        print(f"  Saved {len(combined)} total")
    
    time.sleep(0.1)

# Final save
combined = pd.concat([existing, pd.DataFrame(results)], ignore_index=True) if not existing.empty else pd.DataFrame(results)
combined.to_csv(output_path, index=False)
print(f"\n{'='*60}")
print(f"Done! {len(combined)} responses saved to {output_path}")
print(f"{'='*60}")