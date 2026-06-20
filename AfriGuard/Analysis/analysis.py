"""AfriGuard-SA: Statistical Analysis & Visualization"""

import json
import pandas as pd
import numpy as np
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11

OUTPUT_DIR = Path(r"D:\AfriGuard\Figures")
OUTPUT_DIR.mkdir(exist_ok=True)

def load_judge_scores(path):
    records = []
    with open(path, 'r') as f:
        for line in f:
            records.append(json.loads(line))
    return pd.DataFrame(records)

def compute_asr(df, groupby):
    asr = df.groupby(groupby).agg(
        total=('score', 'count'),
        harmful=('score', 'sum'),
        asr=('score', 'mean')
    ).reset_index()
    asr['asr_pct'] = asr['asr'] * 100
    return asr

def figure_2_asr_heatmap(df):
    asr = compute_asr(df, ['language', 'harm_category'])
    pivot = asr.pivot(index='language', columns='harm_category', values='asr_pct')
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(pivot, annot=True, fmt='.1f', cmap='YlOrRd',
                cbar_kws={'label': 'Attack Success Rate (%)'},
                linewidths=0.5, ax=ax)
    ax.set_title('Figure 2: Attack Success Rate by Language and Harm Category',
                 fontsize=13, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'figure_2_asr_heatmap.png', dpi=300)
    plt.close()
    print("Saved: figure_2_asr_heatmap.png")

def figure_3_switch_position(df):
    asr = compute_asr(df, ['switch_position', 'language'])
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=asr, x='switch_position', y='asr_pct', hue='language', ax=ax)
    ax.set_title('Figure 3: ASR by Switch Position and Language', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'figure_3_switch_position.png', dpi=300)
    plt.close()
    print("Saved: figure_3_switch_position.png")

def figure_4_refusal_language(df):
    refused = df[df['score'] == 0]
    counts = refused.groupby(['language', 'refusal_language']).size().unstack(fill_value=0)
    counts_pct = counts.div(counts.sum(axis=1), axis=0) * 100
    
    fig, ax = plt.subplots(figsize=(10, 6))
    counts_pct.plot(kind='bar', stacked=True, ax=ax, colormap='Set2')
    ax.set_title('Figure 4: Refusal Language Distribution', fontsize=13, fontweight='bold')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'figure_4_refusal_language.png', dpi=300)
    plt.close()
    print("Saved: figure_4_refusal_language.png")

def figure_5_model_comparison(df):
    asr = compute_asr(df, ['model', 'language'])
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=asr, x='language', y='asr_pct', hue='model', ax=ax)
    ax.set_title('Figure 5: ASR by Model and Language', fontsize=13, fontweight='bold')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'figure_5_model_comparison.png', dpi=300)
    plt.close()
    print("Saved: figure_5_model_comparison.png")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--judge-scores", required=True)
    parser.add_argument("--dataset", required=True)
    args = parser.parse_args()
    
    print("Loading data...")
    judge_df = load_judge_scores(args.judge_scores)
    dataset_df = pd.read_csv(args.dataset)
    
    merged = judge_df.merge(
        dataset_df,
        left_on=['prompt_id', 'model'],
        right_on=['id', 'model'],
        how='left'
    )
    
    clean = merged[merged['score'] >= 0].copy()
    print(f"Clean records: {len(clean)}")
    
    print("\nGenerating figures...")
    figure_2_asr_heatmap(clean)
    figure_3_switch_position(clean)
    figure_4_refusal_language(clean)
    figure_5_model_comparison(clean)
    
    # Summary stats
    stats_dict = {
        'overall_asr': clean['score'].mean() * 100,
        'asr_by_language': compute_asr(clean, ['language']).set_index('language')['asr_pct'].to_dict()
    }
    
    with open(OUTPUT_DIR / 'summary_stats.json', 'w') as f:
        json.dump(stats_dict, f, indent=2)
    
    print(f"\nDone! Figures saved to {OUTPUT_DIR}")