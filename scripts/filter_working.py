# Save as D:\AfriGuard\Scripts\filter_working.py
import pandas as pd

df = pd.read_csv("data/benchmark_prompts.csv")
working = df[~df["prompt"].str.startswith("[TRANSLATION_FAILED", na=False)]
working.to_csv("data/benchmark_working.csv", index=False)

print(f"Total: {len(df)} | Working: {len(working)} | Failed: {len(df) - len(working)}")
print(working["language_name"].value_counts())