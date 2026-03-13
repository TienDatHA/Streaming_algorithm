from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt


def _save_bar_chart(
    labels: List[str],
    values: List[float],
    ylabel: str,
    title: str,
    output_path: Path,
    color: str,
) -> None:
    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values, color=color, alpha=0.85)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(axis="y", linestyle="--", alpha=0.25)

    for bar, value in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.3f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def generate_plots(results: List[Dict], output_dir: str = ".") -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    labels = [r["algorithm"] for r in results]

    _save_bar_chart(
        labels=labels,
        values=[r["time_s"] for r in results],
        ylabel="Time (seconds)",
        title="Runtime Comparison",
        output_path=out / "runtime.png",
        color="#4C78A8",
    )

    _save_bar_chart(
        labels=labels,
        values=[r["memory_mb"] for r in results],
        ylabel="Memory (MB)",
        title="Memory Usage Comparison",
        output_path=out / "memory.png",
        color="#F58518",
    )

    _save_bar_chart(
        labels=labels,
        values=[r["error_pct"] for r in results],
        ylabel="Error (%)",
        title="Estimation Error Comparison",
        output_path=out / "error.png",
        color="#54A24B",
    )
