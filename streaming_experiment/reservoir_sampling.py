from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ReservoirSampler:
    k: int
    seed: Optional[int] = 42
    sample: List[str] = field(default_factory=list)
    seen: int = 0

    def __post_init__(self) -> None:
        if self.k <= 0:
            raise ValueError("Reservoir size k must be > 0")
        self._rng = random.Random(self.seed)

    def process(self, item: str) -> None:
        self.seen += 1
        if len(self.sample) < self.k:
            self.sample.append(item)
            return

        j = self._rng.randint(1, self.seen)
        if j <= self.k:
            self.sample[j - 1] = item

    def process_stream(self, stream) -> None:
        for item in stream:
            self.process(item)

    def estimate_unique_count(self) -> float:
        if not self.sample:
            return 0.0
        observed_unique_ratio = len(set(self.sample)) / len(self.sample)
        return observed_unique_ratio * self.seen

    def memory_bytes(self) -> int:
        # Rough estimate: pointers + average string payload in sample.
        ptr_size = 8
        avg_len = sum(len(s) for s in self.sample) / max(1, len(self.sample))
        return int(len(self.sample) * (ptr_size + avg_len))
