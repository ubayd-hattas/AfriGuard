import pandas as pd

# Load responses
df = pd.read_csv(r"D:\AfriGuard\data\results\responses.csv")

# Keep only columns your judge needs
out = df[["prompt_id", "model", "language", "prompt", "response"]].copy()
out.to_csv(r"D:\AfriGuard\data\results\responses_for_judge.csv", index=False)

print(f"Saved {len(out)} rows to responses_for_judge.csv")