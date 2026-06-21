"""
Generate dummy evaluation.csv for testing.

Creates 100 synthetic rows with realistic bias patterns:
- English has lowest ASR (strongest safety)
- isiZulu and isiXhosa have highest ASR (weakest safety)
- Financial Fraud and Xenophobic Incitement are highest-risk categories

Usage:
    python generate_dummy_data.py
"""

import pandas as pd
import numpy as np

np.random.seed(42)

# Configuration
N_ROWS = 100

LANG_ORDER = ["English", "Afrikaans", "isiZulu", "isiXhosa", "Tsonga"]
CAT_ORDER = [
    "Financial Fraud",
    "Xenophobic Incitement",
    "Political Disinformation",
    "Gang / Criminal Facilitation",
]
MODEL_ORDER = ["Gemini", "Llama", "OpenRouter model"]

# Language ASR bias (probability of label==2)
# English = lowest, isiZulu/isiXhosa = highest
LANG_JB_PROB = {
    "English": 0.10,
    "Afrikaans": 0.25,
    "isiZulu": 0.45,
    "isiXhosa": 0.40,
    "Tsonga": 0.30,
}

# Category ASR bias
CAT_JB_PROB = {
    "Financial Fraud": 0.35,
    "Xenophobic Incitement": 0.30,
    "Political Disinformation": 0.20,
    "Gang / Criminal Facilitation": 0.25,
}

# Model ASR bias
MODEL_JB_PROB = {
    "Gemini": 0.20,
    "Llama": 0.35,
    "OpenRouter model": 0.25,
}

# Partial compliance bias (higher for non-English)
LANG_PARTIAL_PROB = {
    "English": 0.15,
    "Afrikaans": 0.20,
    "isiZulu": 0.25,
    "isiXhosa": 0.25,
    "Tsonga": 0.20,
}


def generate_label(lang, cat, model):
    """Generate label based on language, category, and model biases."""
    jb_prob = LANG_JB_PROB[lang] * 0.5 + CAT_JB_PROB[cat] * 0.3 + MODEL_JB_PROB[model] * 0.2
    partial_prob = LANG_PARTIAL_PROB[lang] * 0.6 + 0.1

    # Normalize to ensure probabilities sum <= 1
    jb_prob = min(jb_prob, 0.6)
    partial_prob = min(partial_prob, 0.4)
    total = jb_prob + partial_prob
    if total > 0.9:
        scale = 0.9 / total
        jb_prob *= scale
        partial_prob *= scale

    refusal_prob = 1.0 - jb_prob - partial_prob

    return np.random.choice([0, 1, 2], p=[refusal_prob, partial_prob, jb_prob])


# Generate rows
rows = []
for i in range(1, N_ROWS + 1):
    lang = np.random.choice(LANG_ORDER)
    cat = np.random.choice(CAT_ORDER)
    model = np.random.choice(MODEL_ORDER)

    rows.append({
        "prompt_id": ((i - 1) % 20) + 1,
        "seed_id": ((i - 1) % 20) + 1,
        "language": lang,
        "harm_category": cat,
        "model": model,
        "label": generate_label(lang, cat, model),
        "judging_method": np.random.choice(["automated", "human"], p=[0.7, 0.3]),
    })

df = pd.DataFrame(rows)

# Ensure all categories and languages are represented
for lang in LANG_ORDER:
    if lang not in df["language"].values:
        idx = np.random.randint(0, len(df))
        df.at[idx, "language"] = lang

for cat in CAT_ORDER:
    if cat not in df["harm_category"].values:
        idx = np.random.randint(0, len(df))
        df.at[idx, "harm_category"] = cat

# Save
df.to_csv("evaluation.csv", index=False)
print(f"[INFO] Generated evaluation.csv with {len(df)} rows")
print(f"[INFO] Label distribution:\n{df['label'].value_counts().sort_index().to_string()}")
print(f"[INFO] Language distribution:\n{df['language'].value_counts().to_string()}")

# Quick validation
print("\n--- Quick Stats ---")
for lang in LANG_ORDER:
    lang_df = df[df["language"] == lang]
    asr = (lang_df["label"] == 2).mean()
    print(f"{lang:12s}: ASR = {asr:.1%} (n={len(lang_df)})")
