import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_utils import DATA_DIR, BENCHMARK_PROMPTS_CSV

files = [
    DATA_DIR / "seed_prompts.csv",
    DATA_DIR / "bechmark_afrikaans.csv",  # Note the typo in the actual filename
    DATA_DIR / "benchmark_zulu.csv",
    DATA_DIR / "benchmark_sepedi.csv",
    DATA_DIR / "benchmark_xitsonga.csv",
]

# Verify all files exist
for f in files:
    if not f.exists():
        print(f"Error: Could not find {f}")
        sys.exit(1)

dfs = []
for f in files:
    try:
        df = pd.read_csv(f, encoding='utf-8', sep=None, engine='python')
    except UnicodeDecodeError:
        print(f"Warning: {f.name} is not UTF-8 encoded. Falling back to latin-1.")
        df = pd.read_csv(f, encoding='latin-1', sep=None, engine='python')
    dfs.append(df)

combined = pd.concat(dfs, ignore_index=True)

# Recreate benchmark IDs
combined["benchmark_id"] = [
    f"B{i:03d}" for i in range(1, len(combined) + 1)
]

combined.to_csv(
    BENCHMARK_PROMPTS_CSV,
    index=False,
    encoding="utf-8"
)

print(f"Created benchmark_prompts.csv with {len(combined)} rows")