import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from qcbai.games.game_config import GameConfig
from qcbai.analytics.types import ExperimentResult


def sanitize_filename(name: str) -> str:
    return name.replace("/", "__").replace(":", "-")


def plot_prompt_result(
    prompt_id: str,
    model_slug: str,
    game_config: GameConfig,
    result: ExperimentResult,
    images_dir: Path,
):
    """Plot a single prompt result. Adapts to binary vs amount games.

    Saves to: images/<game_key>/<model_slug>/<prompt_id>.png
    """
    # Create model-specific subdirectory for plots
    model_images_dir = images_dir / sanitize_filename(model_slug)
    model_images_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 6))

    if game_config.response_type == "binary":
        labels = [game_config.distrust_choice, game_config.trust_choice]
        values = [
            round(result.distrust_estimate_probability_distribution * 100, 1),
            round(result.trust_estimate_probability_distribution * 100, 1),
        ]
        colors = ["#ff9999", "#66b3ff"]
        ylabel = "Percentage"
    else:
        labels = ["Mean Amount", f"Max (${game_config.max_amount})"]
        mean_amt = result.mean_amount if result.mean_amount is not None else 0
        values = [mean_amt, game_config.max_amount]
        colors = ["#66b3ff", "#dddddd"]
        ylabel = "Dollar Amount"

    bars = ax.bar(labels, values, color=colors, width=0.5)

    ymax = max(values) * 1.15 if max(values) > 0 else 10
    ax.set_ylim(0, ymax)

    for bar in bars:
        height = bar.get_height()
        fmt = f"{height:.1f}%" if game_config.response_type == "binary" else f"${height:.1f}"
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + ymax * 0.02,
            fmt,
            ha="center", va="bottom", fontsize=12, fontweight="bold",
        )

    ax.set_ylabel(ylabel, fontsize=14, labelpad=10)
    ax.set_title(
        f"{game_config.name}\n{model_slug} | {prompt_id}",
        fontsize=14, pad=20, fontweight="bold",
    )
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    fig.tight_layout()

    filename = f"{sanitize_filename(prompt_id)}.png"
    fig.savefig(model_images_dir / filename, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_model_summary(
    model_slug: str,
    summaries: list,
    game_config: GameConfig,
    images_dir: Path,
):
    """Plot a summary chart of all prompt results for a given model.

    Saves to: images/<game_key>/<model_slug>/summary.png
    """
    # Create model-specific subdirectory for plots
    model_images_dir = images_dir / sanitize_filename(model_slug)
    model_images_dir.mkdir(parents=True, exist_ok=True)
    n = len(summaries)
    if n == 0:
        return

    fig_w = max(12, n * 0.4)
    fig_h = max(6, n * 0.15)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    prompts = [s["prompt_id"] for s in summaries]
    x = np.arange(n)

    if game_config.response_type == "binary":
        label_a = summaries[0].get("choice_a_label", "Trust")
        label_b = summaries[0].get("choice_b_label", "Distrust")
        vals_a = [s["choice_a_percent"] for s in summaries]
        vals_b = [s["choice_b_percent"] for s in summaries]
        width = 0.35

        bars1 = ax.bar(x - width / 2, vals_b, width, label=label_b, color="#ff9999", alpha=0.9)
        bars2 = ax.bar(x + width / 2, vals_a, width, label=label_a, color="#66b3ff", alpha=0.9)

        highest = max(max(vals_a), max(vals_b)) if vals_a and vals_b else 100
        ymax = highest * 1.15
        ax.set_ylim(0, ymax)
        ax.set_ylabel("Percentage", fontsize=14, labelpad=10)

        for bar_set in (bars1, bars2):
            for bar in bar_set:
                h = bar.get_height()
                if h >= highest * 0.15:
                    ax.text(bar.get_x() + bar.get_width() / 2, h / 2,
                            f"{h:.1f}%", ha="center", va="center",
                            fontsize=8, fontweight="bold", color="black")
                else:
                    ax.text(bar.get_x() + bar.get_width() / 2, h + highest * 0.02,
                            f"{h:.1f}%", ha="center", va="bottom",
                            fontsize=8, color="black")
    else:
        means = [s.get("mean_amount", 0) or 0 for s in summaries]
        max_amt = game_config.max_amount or 10
        bars = ax.bar(x, means, 0.6, label="Mean Amount", color="#66b3ff", alpha=0.9)
        ax.axhline(y=max_amt, color="#ff9999", linestyle="--", alpha=0.7, label=f"Max (${max_amt})")
        ax.axhline(y=max_amt / 2, color="#aaaaaa", linestyle=":", alpha=0.5, label=f"Midpoint (${max_amt / 2:.0f})")

        ymax = max_amt * 1.25
        ax.set_ylim(0, ymax)
        ax.set_ylabel("Dollar Amount", fontsize=14, labelpad=10)

        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + max_amt * 0.02,
                    f"${h:.1f}", ha="center", va="bottom",
                    fontsize=8, fontweight="bold", color="black")

    ax.set_xlabel("Prompt ID", fontsize=14, labelpad=10)
    ax.set_title(f"{game_config.name} \u2014 {model_slug}", fontsize=16, pad=20, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(prompts, rotation=90, ha="center", fontsize=8)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.legend(fontsize=12, loc="upper right")

    fig.tight_layout()
    fig.subplots_adjust(bottom=0.40, top=0.88, left=0.08, right=0.97)

    filename = "summary.png"
    fig.savefig(model_images_dir / filename, dpi=300, bbox_inches="tight")
    plt.close(fig)
