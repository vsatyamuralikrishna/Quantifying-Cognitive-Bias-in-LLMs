import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Get project root directory (2 levels up from this file)
ROOT = Path(__file__).parent.parent.parent

# Default directory for saving plots
IMAGES_DIR = ROOT / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def sanitize_filename(name: str) -> str:
    """
    Replaces invalid characters for filenames.
    """
    return name.replace("/", "__").replace(":", "-")


def plot_prompt_result(prompt_id: str, model_slug: str, implicate: float, silent: float):
    """
    Plot a single prompt result showing implicate vs. silent responses.
    """
    # Build figure + axis
    fig, ax = plt.subplots(figsize=(8, 6))

    # Data
    labels = ["Implicate", "Silent"]
    values = [implicate, silent]
    colors = ["#ff9999", "#66b3ff"]

    # Create bars
    bars = ax.bar(labels, values, color=colors, width=0.5)

    # Calculate dynamic y-limit (max value + 10% headroom)
    ymax = max(values) * 1.1
    ax.set_ylim(0, ymax)

    # Annotate each bar
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + ymax * 0.02,  # 2% of y-axis above the bar
            f"{height:.1f}%",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
        )

    # Labels & title
    ax.set_ylabel("Percentage", fontsize=14, labelpad=10)
    ax.set_title(f"Prompt Result\n{model_slug} | {prompt_id}",
                 fontsize=16, pad=20, fontweight="bold")

    # Grid, layout & save
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    fig.tight_layout()
    # still tuck in a tiny bit more margin just in case
    fig.subplots_adjust(top=0.88, bottom=0.12, left=0.12, right=0.96)

    filename = f"{sanitize_filename(model_slug)}__{sanitize_filename(prompt_id)}.png"
    fig.savefig(IMAGES_DIR / filename, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_model_summary(model_slug: str, summaries: list):
    """
    Plot a summary chart of all prompt results for a given model,
    with percentage labels inside each bar for better readability.
    """
    prompts     = [s["prompt_id"]        for s in summaries]
    implicates  = [s["implicate_percent"] for s in summaries]
    silents     = [s["silent_percent"]    for s in summaries]
    n = len(prompts)

    # Dynamic figure sizing
    fig_w = max(12, n * 0.4)
    fig_h = max(6, n * 0.15)  # grow height if many prompts
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    x     = np.arange(n)
    width = 0.35

    bars1 = ax.bar(x - width/2, implicates, width, label="Implicate", color="#ff9999", alpha=0.9)
    bars2 = ax.bar(x + width/2, silents,    width, label="Silent",    color="#66b3ff", alpha=0.9)

    # Dynamic y-limit with 10% headroom
    ymax = max(max(implicates), max(silents)) * 1.1
    ax.set_ylim(0, ymax)

    # **Place labels INSIDE** each bar
    for bar in (*bars1, *bars2):
        h = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            h / 2,                      # halfway up the bar
            f"{h:.1f}%",
            ha="center",
            va="center",
            fontsize=8,
            fontweight="bold",
            color="black"
        )

    # Axis labels & title
    ax.set_xlabel("Prompt ID", fontsize=14, labelpad=10)
    ax.set_ylabel("Percentage", fontsize=14, labelpad=10)
    ax.set_title(f"Model Summary — {model_slug}",
                 fontsize=16, pad=20, fontweight="bold")

    # Ticks & grid
    ax.set_xticks(x)
    ax.set_xticklabels(prompts, rotation=45, ha="right", fontsize=8)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.legend(fontsize=12, loc="upper right")

    # Tight layout + extra bottom margin for rotated labels
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.3, top=0.88, left=0.08, right=0.97)

    # Save
    filename = f"{sanitize_filename(model_slug)}__summary.png"
    fig.savefig(IMAGES_DIR / filename, dpi=300, bbox_inches="tight")
    plt.close(fig)