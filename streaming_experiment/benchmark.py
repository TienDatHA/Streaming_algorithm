from __future__ import annotations

import time
import tracemalloc
from collections import Counter
from statistics import mean
from typing import Any, Dict, Iterable, List, Sequence

from streaming_experiment.count_min_sketch import CountMinSketch
from streaming_experiment.dataset_loader import stream_items
from streaming_experiment.hyperloglog import HyperLogLog
from streaming_experiment.reservoir_sampling import ReservoirSampler


def _with_peak_memory(run_fn):
    tracemalloc.start()
    t0 = time.perf_counter()
    result = run_fn()
    elapsed = time.perf_counter() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, elapsed, peak / (1024 * 1024)


def exact_stats(file_paths: Sequence[str], stream_config: Dict[str, Any]) -> Dict[str, Any]:
    counter = Counter()
    total = 0
    for item in stream_items(file_paths, **stream_config):
        counter[item] += 1
        total += 1

    return {
        "counter": counter,
        "total": total,
        "true_unique": len(counter),
    }


def benchmark_reservoir(
    file_paths: Sequence[str],
    stream_config: Dict[str, Any],
    *,
    true_unique: int,
    k: int = 5000,
) -> Dict[str, Any]:
    sampler = ReservoirSampler(k=k, seed=42)

    def _run():
        sampler.process_stream(stream_items(file_paths, **stream_config))
        return sampler

    _, elapsed, peak_mem_mb = _with_peak_memory(_run)
    est_unique = sampler.estimate_unique_count()
    err_pct = (abs(est_unique - true_unique) / max(1, true_unique)) * 100

    return {
        "algorithm": "Reservoir",
        "time_s": elapsed,
        "memory_mb": peak_mem_mb,
        "error_pct": err_pct,
        "estimate": est_unique,
    }


def benchmark_cms(
    file_paths: Sequence[str],
    stream_config: Dict[str, Any],
    *,
    true_counter: Counter,
    epsilon: float = 0.001,
    delta: float = 0.01,
    eval_top_k: int = 100,
) -> Dict[str, Any]:
    cms = CountMinSketch(epsilon=epsilon, delta=delta)

    def _run():
        cms.process_stream(stream_items(file_paths, **stream_config))
        return cms

    _, elapsed, peak_mem_mb = _with_peak_memory(_run)

    top_items = true_counter.most_common(eval_top_k)
    over_errors = []
    for key, true_freq in top_items:
        est = cms.estimate(key)
        over_errors.append(max(0, est - true_freq) / max(1, true_freq))

    err_pct = mean(over_errors) * 100 if over_errors else 0.0

    return {
        "algorithm": "CountMinSketch",
        "time_s": elapsed,
        "memory_mb": peak_mem_mb,
        "error_pct": err_pct,
        "estimate": None,
    }


def benchmark_hll(
    file_paths: Sequence[str],
    stream_config: Dict[str, Any],
    *,
    true_unique: int,
    p: int = 12,
) -> Dict[str, Any]:
    hll = HyperLogLog(p=p)

    def _run():
        hll.process_stream(stream_items(file_paths, **stream_config))
        return hll

    _, elapsed, peak_mem_mb = _with_peak_memory(_run)

    est_unique = hll.count()
    err_pct = (abs(est_unique - true_unique) / max(1, true_unique)) * 100

    return {
        "algorithm": "HyperLogLog",
        "time_s": elapsed,
        "memory_mb": peak_mem_mb,
        "error_pct": err_pct,
        "estimate": est_unique,
    }


def run_all_benchmarks(file_paths: Sequence[str], stream_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    truth = exact_stats(file_paths, stream_config)

    results = [
        benchmark_reservoir(
            file_paths,
            stream_config,
            true_unique=truth["true_unique"],
            k=5000,
        ),
        benchmark_cms(
            file_paths,
            stream_config,
            true_counter=truth["counter"],
            epsilon=0.002,
            delta=0.01,
            eval_top_k=100,
        ),
        benchmark_hll(
            file_paths,
            stream_config,
            true_unique=truth["true_unique"],
            p=12,
        ),
    ]

    return results
