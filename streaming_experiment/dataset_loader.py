from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Union


PathLike = Union[str, Path]


def resolve_data_files(data_dir: PathLike) -> List[Path]:
    """Return CSV files under a directory in sorted order."""
    directory = Path(data_dir)
    files = sorted(directory.glob("*.csv"))
    if len(files) < 2:
        raise ValueError(f"Expected at least 2 CSV files in {directory}, found {len(files)}")
    return files


def stream_items(
    file_paths: Sequence[PathLike],
    column_name: Optional[str] = None,
    *,
    file_column_names: Optional[Dict[str, str]] = None,
    file_column_indices: Optional[Dict[str, int]] = None,
    default_column_index: Optional[int] = None,
    has_header_map: Optional[Dict[str, bool]] = None,
    encoding: str = "utf-8",
) -> Iterator[str]:
    """
    Iterate rows across multiple CSV files sequentially and yield one stream element at a time.

    Parameters
    ----------
    file_paths:
        Ordered list of files that forms a continuous stream.
    column_name:
        Default column name to extract when a file has headers.
    file_column_names:
        Per-file override for column name, keyed by file name.
    file_column_indices:
        Per-file override for column index, keyed by file name.
    default_column_index:
        Fallback column index for files without headers.
    has_header_map:
        Per-file flag indicating whether the file has header row.
    """
    file_column_names = file_column_names or {}
    file_column_indices = file_column_indices or {}
    has_header_map = has_header_map or {}

    for path_like in file_paths:
        path = Path(path_like)
        file_key = path.name
        has_header = has_header_map.get(file_key, True)

        with path.open("r", newline="", encoding=encoding, errors="replace") as csv_file:
            if has_header:
                reader = csv.DictReader(csv_file)
                selected_name = file_column_names.get(file_key, column_name)
                if not selected_name:
                    raise ValueError(f"No column name provided for header-based file: {file_key}")

                for row in reader:
                    value = row.get(selected_name)
                    if value is None or value == "":
                        continue
                    yield value
            else:
                reader = csv.reader(csv_file)
                selected_index = file_column_indices.get(file_key, default_column_index)
                if selected_index is None:
                    raise ValueError(
                        f"No column index configured for non-header file: {file_key}"
                    )

                for row in reader:
                    if not row or selected_index >= len(row):
                        continue
                    value = row[selected_index]
                    if value == "":
                        continue
                    yield value


def materialize_stream(stream: Iterable[str]) -> List[str]:
    """Utility helper for debugging/tests only."""
    return list(stream)
