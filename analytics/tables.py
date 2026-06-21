"""
Tables Module

Generates publication-ready summary tables.
Exports both CSV and Markdown formats to outputs/tables/.

Usage:
    from data_loader import load_evaluation
    from metrics import MetricsEngine
    from tables import TableGenerator

    df = load_evaluation("evaluation.csv")
    engine = MetricsEngine(df)
    tables = TableGenerator(df, engine)
    tables.generate_all()
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List

OUTPUT_DIR = Path("outputs/tables")


class TableGenerator:
    """Generate all publication tables."""

    def __init__(self, df: pd.DataFrame, engine):
        self.df = df
        self.engine = engine
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Table 1: Language Summary
    # ------------------------------------------------------------------

    def generate_language_summary(self) -> Dict[str, Path]:
        """
        Table 1: Summary statistics per language.
        Columns: Language, Total, Refusal%, Partial%, Jailbreak%, ASR%, Gap vs English
        """
        dist = self.engine.full_distribution(by="language")

        # Get English (en) baseline for gap calculation
        english_row = dist[dist["language"] == "en"]
        english_asr = english_row["jailbreak_rate"].values[0] if len(english_row) > 0 else 0

        dist["gap_vs_english"] = dist["jailbreak_rate"] - english_asr
        dist["gap_vs_english_pct"] = (dist["gap_vs_english"] * 100).round(1)

        # Select and rename columns
        table = dist[[
            "language", "n_total", "n_refusal", "n_partial", "n_jailbreak",
            "refusal_pct", "partial_pct", "jailbreak_pct", "gap_vs_english_pct",
        ]].copy()

        table.columns = [
            "Language", "Total", "Refusals (n)", "Partial (n)", "Jailbreaks (n)",
            "Refusal %", "Partial %", "ASR %", "Gap vs Eng (pp)",
        ]

        # Save CSV
        csv_path = OUTPUT_DIR / "table1_language_summary.csv"
        table.to_csv(csv_path, index=False)

        # Save Markdown
        md_path = OUTPUT_DIR / "table1_language_summary.md"
        with open(md_path, "w") as f:
            f.write("# Table 1: Language Summary\n\n")
            f.write("Attack success rates and response distributions by language condition.\n\n")
            f.write(table.to_markdown(index=False, floatfmt=".1f"))
            f.write("\n\n**Note:** ASR % = Attack Success Rate (label == 2). ")
            f.write("Gap vs Eng = difference in ASR percentage points from English baseline.\n")

        print(f"[SAVED] {csv_path}")
        print(f"[SAVED] {md_path}")
        return {"csv": csv_path, "md": md_path}

    # ------------------------------------------------------------------
    # Table 2: Model Summary
    # ------------------------------------------------------------------

    def generate_model_summary(self) -> Dict[str, Path]:
        """
        Table 2: Summary statistics per model.
        Columns: Model, Total, Refusal%, Partial%, Jailbreak%, Robustness Score
        """
        dist = self.engine.full_distribution(by="model")
        robust = self.engine.model_robustness()

        # Merge robustness score
        dist = dist.merge(robust[["model", "robustness_score"]], on="model", how="left")

        table = dist[[
            "model", "n_total", "n_refusal", "n_partial", "n_jailbreak",
            "refusal_pct", "partial_pct", "jailbreak_pct", "robustness_score",
        ]].copy()

        table.columns = [
            "Model", "Total", "Refusals (n)", "Partial (n)", "Jailbreaks (n)",
            "Refusal %", "Partial %", "ASR %", "Robustness",
        ]

        csv_path = OUTPUT_DIR / "table2_model_summary.csv"
        table.to_csv(csv_path, index=False)

        md_path = OUTPUT_DIR / "table2_model_summary.md"
        with open(md_path, "w") as f:
            f.write("# Table 2: Model Summary\n\n")
            f.write("Performance comparison across tested language models.\n\n")
            f.write(table.to_markdown(index=False, floatfmt=".1f"))
            f.write("\n\n**Note:** Robustness = 100 - ASR%. Higher = safer.\n")

        print(f"[SAVED] {csv_path}")
        print(f"[SAVED] {md_path}")
        return {"csv": csv_path, "md": md_path}

    # ------------------------------------------------------------------
    # Table 3: Category Summary
    # ------------------------------------------------------------------

    def generate_category_summary(self) -> Dict[str, Path]:
        """
        Table 3: Summary statistics per harm category.
        """
        dist = self.engine.full_distribution(by="harm_category")
        risk = self.engine.harm_category_risk()

        dist = dist.merge(risk[["harm_category", "risk_score"]], on="harm_category", how="left")

        table = dist[[
            "harm_category", "n_total", "n_refusal", "n_partial", "n_jailbreak",
            "refusal_pct", "partial_pct", "jailbreak_pct", "risk_score",
        ]].copy()

        table.columns = [
            "Harm Category", "Total", "Refusals (n)", "Partial (n)", "Jailbreaks (n)",
            "Refusal %", "Partial %", "ASR %", "Risk Score",
        ]

        # Sort by risk score descending
        table = table.sort_values("Risk Score", ascending=False)

        csv_path = OUTPUT_DIR / "table3_category_summary.csv"
        table.to_csv(csv_path, index=False)

        md_path = OUTPUT_DIR / "table3_category_summary.md"
        with open(md_path, "w") as f:
            f.write("# Table 3: Harm Category Summary\n\n")
            f.write("Attack success rates by harm category, ranked by risk.\n\n")
            f.write(table.to_markdown(index=False, floatfmt=".1f"))
            f.write("\n\n**Note:** Risk Score = ASR weighted by severity.\n")

        print(f"[SAVED] {csv_path}")
        print(f"[SAVED] {md_path}")
        return {"csv": csv_path, "md": md_path}

    # ------------------------------------------------------------------
    # Table 4: Top Jailbreak Cases
    # ------------------------------------------------------------------

    def generate_top_jailbreaks(self, top_n: int = 10) -> Dict[str, Path]:
        """
        Table 4: Most successful jailbreak cases.
        Shows prompts that achieved label==2, grouped by language and category.
        """
        jb_df = self.df[self.df["label"] == 2].copy()

        if len(jb_df) == 0:
            # No jailbreaks found — create empty table with correct schema
            table = pd.DataFrame(columns=[
                "Language", "Harm Category", "Model", "Count",
                "% of Language", "% of Category",
            ])
        else:
            grouped = jb_df.groupby(["language", "harm_category", "model"], observed=True).size().reset_index(name="count")

            # Add percentage within language
            lang_totals = self.df.groupby("language", observed=True).size().to_dict()
            grouped["pct_of_language"] = grouped.apply(
                lambda r: round(r["count"] / lang_totals.get(r["language"], 1) * 100, 1),
                axis=1,
            )

            # Add percentage within category
            cat_totals = self.df.groupby("harm_category", observed=True).size().to_dict()
            grouped["pct_of_category"] = grouped.apply(
                lambda r: round(r["count"] / cat_totals.get(r["harm_category"], 1) * 100, 1),
                axis=1,
            )

            grouped = grouped.sort_values("count", ascending=False).head(top_n)

            table = grouped[[
                "language", "harm_category", "model", "count",
                "pct_of_language", "pct_of_category",
            ]].copy()

            table.columns = [
                "Language", "Harm Category", "Model", "Jailbreaks (n)",
                "% of Language", "% of Category",
            ]

        csv_path = OUTPUT_DIR / "table4_top_jailbreaks.csv"
        table.to_csv(csv_path, index=False)

        md_path = OUTPUT_DIR / "table4_top_jailbreaks.md"
        with open(md_path, "w") as f:
            f.write("# Table 4: Top Jailbreak Cases\n\n")
            f.write(f"Top {top_n} most successful jailbreak combinations.\n\n")
            if len(table) > 0:
                f.write(table.to_markdown(index=False, floatfmt=".1f"))
            else:
                f.write("*No jailbreak cases found in dataset.*\n")
            f.write("\n\n**Note:** Shows language-category-model combinations with highest jailbreak counts.\n")

        print(f"[SAVED] {csv_path}")
        print(f"[SAVED] {md_path}")
        return {"csv": csv_path, "md": md_path}

    # ------------------------------------------------------------------
    # Generate All
    # ------------------------------------------------------------------

    def generate_all(self) -> List[Dict[str, Path]]:
        """Generate all tables."""
        print("[INFO] Generating all tables...")

        results = [
            self.generate_language_summary(),
            self.generate_model_summary(),
            self.generate_category_summary(),
            self.generate_top_jailbreaks(),
        ]

        print(f"[INFO] {len(results)} tables saved to {OUTPUT_DIR}/")
        return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    from data_loader import load_evaluation
    from metrics import MetricsEngine

    parser = argparse.ArgumentParser(description="Generate all tables")
    parser.add_argument("filepath", nargs="?", default="evaluation.csv", help="Path to evaluation.csv")
    args = parser.parse_args()

    df = load_evaluation(args.filepath)
    engine = MetricsEngine(df)
    tables = TableGenerator(df, engine)
    tables.generate_all()
