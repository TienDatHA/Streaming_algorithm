from __future__ import annotations

from pathlib import Path

from streaming_experiment.benchmark import run_all_benchmarks
from streaming_experiment.dataset_loader import resolve_data_files
from streaming_experiment.visualize import generate_plots


def print_results_table(results):
    header = f"{'Algorithm':<15} {'Time(s)':>10} {'Memory(MB)':>12} {'Error(%)':>10}"
    print(header)
    print("-" * len(header))
    for row in results:
        print(
            f"{row['algorithm']:<15} "
            f"{row['time_s']:>10.4f} "
            f"{row['memory_mb']:>12.3f} "
            f"{row['error_pct']:>10.3f}"
        )


def main() -> None:
    project_root = Path(__file__).resolve().parent
    data_dir = project_root / "data"

    files = resolve_data_files(data_dir)
    file_paths = [str(p) for p in files]

    # data.csv has headers and we extract `host`.
    # training.1600000.processed.noemoticon.csv has no headers;
    # index 4 corresponds to user id/username in Sentiment140 format.
    stream_config = {
        "column_name": "host",
        "file_column_indices": {
            "training.1600000.processed.noemoticon.csv": 4,
        },
        "has_header_map": {
            "data.csv": True,
            "training.1600000.processed.noemoticon.csv": False,
        },
    }

    results = run_all_benchmarks(file_paths, stream_config)
    print_results_table(results)
    plot_dir = project_root / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)

    # Save presentation-friendly charts in the plots folder.
    generate_plots(results, output_dir=str(plot_dir))

    print(f"\nSaved plots in: {plot_dir}")
    print("- runtime.png")
    print("- memory.png")
    print("- error.png")


if __name__ == "__main__":
    main()
