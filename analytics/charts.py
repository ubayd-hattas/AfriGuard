"""
Charts Module

Generates publication-quality figures for the Mzansi Code-Switching
Safety Benchmark. All figures saved to outputs/figures/ at 300 DPI.

Usage:
    from data_loader import load_evaluation
    from metrics import MetricsEngine
    from charts import ChartGenerator

    df = load_evaluation("evaluation.csv")
    engine = MetricsEngine(df)
    charts = ChartGenerator(df, engine)
    charts.generate_all()
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Style Configuration
# ---------------------------------------------------------------------------

plt.rcParams.update({
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "figure.figsize": (10, 6),
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#2D3436",
    "axes.labelcolor": "#2D3436",
    "xtick.color": "#2D3436",
    "ytick.color": "#2D3436",
    "text.color": "#2D3436",
    "font.size": 10,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "legend.fontsize": 9,
})

COLORS = {
    "refusal": "#1D9E75",
    "partial": "#EF9F27",
    "jailbreak": "#D85A30",
    "english": "#534AB7",
    "highlight": "#D85A30",
    "grid": "#E8E8E8",
    "text": "#2D3436",
}

MODEL_COLORS = {
    "Gemini": "#534AB7",
    "Llama": "#0F6E56",
    "OpenRouter model": "#D85A30",
}

LANG_ORDER = ["English", "Afrikaans", "isiZulu", "isiXhosa", "Tsonga"]
CAT_ORDER = [
    "Financial Fraud",
    "Xenophobic Incitement",
    "Political Disinformation",
    "Gang / Criminal Facilitation",
]
MODEL_ORDER = ["Gemini", "Llama", "OpenRouter model"]

OUTPUT_DIR = Path("outputs/figures")


# ---------------------------------------------------------------------------
# Chart Generator
# ---------------------------------------------------------------------------

class ChartGenerator:
    """Generate all publication-quality figures."""

    def __init__(self, df: pd.DataFrame, engine):
        self.df = df
        self.engine = engine
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Figure 1: Hero ASR Heatmap
    # ------------------------------------------------------------------

    def generate_asr_heatmap(self) -> Path:
        """
        Figure 1: Hero ASR Heatmap
        Rows: languages
        Columns: harm categories
        Cell: ASR %
        """
        pivot = self.df.groupby(["language", "harm_category"], observed=True)["is_jailbreak"].mean().unstack()
        pivot = pivot.reindex(LANG_ORDER)
        pivot.columns = [str(c) for c in pivot.columns]

        fig, ax = plt.subplots(figsize=(12, 6))

        sns.heatmap(
            pivot,
            annot=True,
            fmt=".0%",
            cmap="RdYlGn_r",
            vmin=0,
            vmax=1,
            linewidths=1.5,
            linecolor="white",
            ax=ax,
            cbar_kws={
                "label": "Attack Success Rate",
                "shrink": 0.8,
                "format": "%.0f%%",
            },
        )

        ax.set_title(
            "Attack Success Rate by Language and Harm Category",
            fontsize=14,
            fontweight="bold",
            pad=20,
        )
        ax.set_xlabel("Harm Category", fontsize=11, labelpad=10)
        ax.set_ylabel("Language", fontsize=11, labelpad=10)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

        # Add subtle border
        for _, spine in ax.spines.items():
            spine.set_visible(True)
            spine.set_linewidth(0.5)
            spine.set_color("#CCCCCC")

        plt.tight_layout()
        filepath = OUTPUT_DIR / "01_asr_heatmap.png"
        fig.savefig(filepath, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print(f"[SAVED] {filepath}")
        return filepath

    # ------------------------------------------------------------------
    # Figure 2: Model Comparison Bar Chart
    # ------------------------------------------------------------------

    def generate_model_comparison(self) -> Path:
        """
        Figure 2: Model vs ASR bar chart.
        """
        model_asr = self.engine.attack_success_rate(by="model")

        fig, ax = plt.subplots(figsize=(8, 5))

        bars = ax.bar(
            model_asr["model"].astype(str),
            model_asr["asr"] * 100,
            color=[MODEL_COLORS.get(str(m), "#888888") for m in model_asr["model"]],
            edgecolor="white",
            linewidth=1.5,
            width=0.6,
        )

        # Value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 1,
                f"{height:.1f}%",
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold",
            )

        ax.set_ylim(0, max(model_asr["asr"] * 100) * 1.2)
        ax.set_ylabel("Attack Success Rate (%)", fontsize=11)
        ax.set_xlabel("")
        ax.set_title(
            "Model Comparison: Attack Success Rate",
            fontsize=14,
            fontweight="bold",
            pad=15,
        )

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#CCCCCC")
        ax.spines["bottom"].set_color("#CCCCCC")
        ax.yaxis.grid(True, color=COLORS["grid"], linewidth=0.5)
        ax.set_axisbelow(True)

        plt.tight_layout()
        filepath = OUTPUT_DIR / "02_model_comparison.png"
        fig.savefig(filepath, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print(f"[SAVED] {filepath}")
        return filepath

    # ------------------------------------------------------------------
    # Figure 3: Language Safety Gap Chart
    # ------------------------------------------------------------------

    def generate_language_gap(self) -> Path:
        """
        Figure 3: Language vs Gap from English baseline.
        Horizontal bar chart.
        """
        gap_df = self.engine.language_safety_gap()
        gap_df = gap_df[gap_df["language"] != "English"].copy()
        gap_df = gap_df.sort_values("gap", ascending=True)

        fig, ax = plt.subplots(figsize=(9, 5))

        colors = [COLORS["highlight"] if g > 0 else COLORS["refusal"] for g in gap_df["gap"]]

        bars = ax.barh(
            gap_df["language"].astype(str),
            gap_df["gap"] * 100,
            color=colors,
            edgecolor="white",
            linewidth=1.5,
            height=0.6,
        )

        # Value labels
        for bar in bars:
            width = bar.get_width()
            ax.text(
                width + 0.5 if width >= 0 else width - 0.5,
                bar.get_y() + bar.get_height() / 2.0,
                f"{width:+.1f}pp",
                ha="left" if width >= 0 else "right",
                va="center",
                fontsize=10,
                fontweight="bold",
            )

        ax.axvline(x=0, color="#2D3436", linewidth=0.8, linestyle="-")
        ax.set_xlabel("Safety Gap vs English Baseline (percentage points)", fontsize=11)
        ax.set_title(
            "Language Safety Gap: Non-English vs English Baseline",
            fontsize=14,
            fontweight="bold",
            pad=15,
        )

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#CCCCCC")
        ax.spines["bottom"].set_color("#CCCCCC")
        ax.xaxis.grid(True, color=COLORS["grid"], linewidth=0.5)
        ax.set_axisbelow(True)

        plt.tight_layout()
        filepath = OUTPUT_DIR / "03_language_safety_gap.png"
        fig.savefig(filepath, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print(f"[SAVED] {filepath}")
        return filepath

    # ------------------------------------------------------------------
    # Figure 4: Harm Category Risk Chart
    # ------------------------------------------------------------------

    def generate_harm_risk(self) -> Path:
        """
        Figure 4: Harm category vs risk score.
        Horizontal bar chart sorted by risk.
        """
        risk_df = self.engine.harm_category_risk()
        risk_df = risk_df.sort_values("risk_score", ascending=True)

        fig, ax = plt.subplots(figsize=(9, 5))

        bars = ax.barh(
            risk_df["harm_category"].astype(str),
            risk_df["risk_pct"],
            color=COLORS["jailbreak"],
            edgecolor="white",
            linewidth=1.5,
            height=0.6,
        )

        for bar in bars:
            width = bar.get_width()
            ax.text(
                width + 0.5,
                bar.get_y() + bar.get_height() / 2.0,
                f"{width:.1f}%",
                ha="left",
                va="center",
                fontsize=10,
                fontweight="bold",
            )

        ax.set_xlabel("Risk Score (% ASR)", fontsize=11)
        ax.set_title(
            "Harm Category Risk Ranking",
            fontsize=14,
            fontweight="bold",
            pad=15,
        )

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#CCCCCC")
        ax.spines["bottom"].set_color("#CCCCCC")
        ax.xaxis.grid(True, color=COLORS["grid"], linewidth=0.5)
        ax.set_axisbelow(True)

        plt.tight_layout()
        filepath = OUTPUT_DIR / "04_harm_category_risk.png"
        fig.savefig(filepath, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print(f"[SAVED] {filepath}")
        return filepath

    # ------------------------------------------------------------------
    # Figure 5: Refusal Distribution (Stacked Bar)
    # ------------------------------------------------------------------

    def generate_refusal_distribution(self) -> Path:
        """
        Figure 5: 100% stacked bar showing refusal/partial/jailbreak by language.
        """
        dist = self.df.groupby("language", observed=True)[
            ["is_refusal", "is_partial", "is_jailbreak"]
        ].mean()
        dist = dist.reindex(LANG_ORDER)
        dist *= 100  # Convert to percentages

        fig, ax = plt.subplots(figsize=(10, 6))

        p1 = ax.bar(
            [str(l) for l in dist.index],
            dist["is_refusal"],
            color=COLORS["refusal"],
            edgecolor="white",
            linewidth=1.5,
            label="Refusal",
            width=0.65,
        )
        p2 = ax.bar(
            [str(l) for l in dist.index],
            dist["is_partial"],
            bottom=dist["is_refusal"],
            color=COLORS["partial"],
            edgecolor="white",
            linewidth=1.5,
            label="Partial Compliance",
            width=0.65,
        )
        p3 = ax.bar(
            [str(l) for l in dist.index],
            dist["is_jailbreak"],
            bottom=dist["is_refusal"] + dist["is_partial"],
            color=COLORS["jailbreak"],
            edgecolor="white",
            linewidth=1.5,
            label="Harmful Compliance",
            width=0.65,
        )

        # Percentage labels on segments
        for i, lang in enumerate(dist.index):
            r = dist.loc[lang, "is_refusal"]
            p = dist.loc[lang, "is_partial"]
            j = dist.loc[lang, "is_jailbreak"]

            if r > 8:
                ax.text(i, r / 2, f"{r:.0f}%", ha="center", va="center",
                       fontsize=9, fontweight="bold", color="white")
            if p > 8:
                ax.text(i, r + p / 2, f"{p:.0f}%", ha="center", va="center",
                       fontsize=9, fontweight="bold", color="white")
            if j > 8:
                ax.text(i, r + p + j / 2, f"{j:.0f}%", ha="center", va="center",
                       fontsize=9, fontweight="bold", color="white")

        ax.set_ylim(0, 100)
        ax.set_ylabel("Percentage of Responses (%)", fontsize=11)
        ax.set_title(
            "Response Distribution by Language",
            fontsize=14,
            fontweight="bold",
            pad=15,
        )

        ax.legend(
            loc="upper right",
            frameon=True,
            fancybox=True,
            framealpha=0.95,
            edgecolor="#CCCCCC",
        )

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#CCCCCC")
        ax.spines["bottom"].set_color("#CCCCCC")
        ax.yaxis.grid(True, color=COLORS["grid"], linewidth=0.5)
        ax.set_axisbelow(True)

        plt.tight_layout()
        filepath = OUTPUT_DIR / "05_refusal_distribution.png"
        fig.savefig(filepath, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print(f"[SAVED] {filepath}")
        return filepath

    # ------------------------------------------------------------------
    # Figure 6: Safety Consistency Chart
    # ------------------------------------------------------------------

    def generate_consistency_chart(self) -> Path:
        """
        Figure 6: Model safety consistency (variance of ASR across languages).
        """
        cons_df = self.engine.safety_consistency()

        fig, ax = plt.subplots(figsize=(8, 5))

        bars = ax.bar(
            cons_df["model"].astype(str),
            cons_df["consistency_score"],
            color=[MODEL_COLORS.get(str(m), "#888888") for m in cons_df["model"]],
            edgecolor="white",
            linewidth=1.5,
            width=0.6,
        )

        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 1,
                f"{height:.1f}",
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold",
            )

        ax.set_ylim(0, 105)
        ax.set_ylabel("Consistency Score (0-100)", fontsize=11)
        ax.set_xlabel("")
        ax.set_title(
            "Safety Consistency: Variance of ASR Across Languages",
            fontsize=14,
            fontweight="bold",
            pad=15,
        )

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#CCCCCC")
        ax.spines["bottom"].set_color("#CCCCCC")
        ax.yaxis.grid(True, color=COLORS["grid"], linewidth=0.5)
        ax.set_axisbelow(True)

        plt.tight_layout()
        filepath = OUTPUT_DIR / "06_safety_consistency.png"
        fig.savefig(filepath, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print(f"[SAVED] {filepath}")
        return filepath

    # ------------------------------------------------------------------
    # Bonus Figure 7: Language × Model Grid
    # ------------------------------------------------------------------

    def generate_language_model_grid(self) -> Path:
        """
        Bonus: Faceted heatmap showing ASR for each language-model combination.
        """
        pivot = self.df.groupby(["language", "model"], observed=True)["is_jailbreak"].mean().unstack()
        pivot = pivot.reindex(LANG_ORDER)

        fig, ax = plt.subplots(figsize=(8, 6))

        sns.heatmap(
            pivot,
            annot=True,
            fmt=".0%",
            cmap="RdYlGn_r",
            vmin=0,
            vmax=1,
            linewidths=1.5,
            linecolor="white",
            ax=ax,
            cbar_kws={
                "label": "ASR",
                "shrink": 0.8,
                "format": "%.0f%%",
            },
        )

        ax.set_title(
            "Attack Success Rate: Language × Model",
            fontsize=14,
            fontweight="bold",
            pad=20,
        )
        ax.set_xlabel("Model", fontsize=11)
        ax.set_ylabel("Language", fontsize=11)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

        for _, spine in ax.spines.items():
            spine.set_visible(True)
            spine.set_linewidth(0.5)
            spine.set_color("#CCCCCC")

        plt.tight_layout()
        filepath = OUTPUT_DIR / "07_language_model_grid.png"
        fig.savefig(filepath, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print(f"[SAVED] {filepath}")
        return filepath

    # ------------------------------------------------------------------
    # Generate All
    # ------------------------------------------------------------------

    def generate_all(self) -> list[Path]:
        """Generate all figures and return list of file paths."""
        print("[INFO] Generating all figures...")

        paths = [
            self.generate_asr_heatmap(),
            self.generate_model_comparison(),
            self.generate_language_gap(),
            self.generate_harm_risk(),
            self.generate_refusal_distribution(),
            self.generate_consistency_chart(),
            self.generate_language_model_grid(),
        ]

        print(f"[INFO] {len(paths)} figures saved to {OUTPUT_DIR}/")
        return paths


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    from data_loader import load_evaluation
    from metrics import MetricsEngine

    parser = argparse.ArgumentParser(description="Generate all figures")
    parser.add_argument("filepath", nargs="?", default="evaluation.csv", help="Path to evaluation.csv")
    args = parser.parse_args()

    df = load_evaluation(args.filepath)
    engine = MetricsEngine(df)
    charts = ChartGenerator(df, engine)
    charts.generate_all()
