import matplotlib.pyplot as plt
from pathlib import Path

# Ensure this directory exists
IMAGES_DIR = Path("images")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def plot_prompt_result(prompt_id: str, model_slug: str, implicate: float, silent: float):
    """
    Plot a single prompt result with implicate vs silent percentages.
    """
    plt.figure(figsize=(6, 5))

    labels = ["Implicate", "Silent"]
    values = [implicate, silent]
    colors = ["#ff9999", "#66b3ff"]

    bars = plt.bar(labels, values, color=colors)

    for bar in bars:
        plt.text(bar.get_x() + bar.get_width() / 2.0, bar.get_height() + 1,
                 f"{bar.get_height():.1f}%", ha="center")

    plt.ylim(0, 100)
    plt.ylabel("Percentage")
    plt.title(f"Prompt Result — {model_slug} | {prompt_id}")
    plt.tight_layout()

    filename = f"{model_slug}__{prompt_id}.png"
    plt.savefig(IMAGES_DIR / filename)
    plt.close()


def plot_model_summary(model_slug: str, summaries: list):
    """
    Plot aggregate bar chart across all prompts for a given model.
    """
    prompts = [s["prompt_id"] for s in summaries]
    implicates = [s["implicate_percent"] for s in summaries]
    silents = [s["silent_percent"] for s in summaries]

    x = range(len(prompts))
    width = 0.35

    plt.figure(figsize=(12, 6))

    plt.bar(x, implicates, width=width, label="Implicate", color="#ff9999")
    plt.bar([i + width for i in x], silents, width=width, label="Silent", color="#66b3ff")

    plt.xlabel("Prompt ID")
    plt.ylabel("Percentage")
    plt.title(f"Model Summary — {model_slug}")
    plt.xticks([i + width / 2 for i in x], prompts, rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()

    filename = f"{model_slug}__summary.png"
    plt.savefig(IMAGES_DIR / filename)
    plt.close()