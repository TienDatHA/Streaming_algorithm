from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from typing import List


@dataclass
class CountMinSketch:
    epsilon: float = 0.001
    delta: float = 0.01
    width: int = field(init=False)
    depth: int = field(init=False)
    table: List[List[int]] = field(init=False)
    total_count: int = 0

    def __post_init__(self) -> None:
        if self.epsilon <= 0 or self.delta <= 0 or self.delta >= 1:
            raise ValueError("epsilon must be > 0 and 0 < delta < 1")

        self.width = math.ceil(math.e / self.epsilon)
        self.depth = math.ceil(math.log(1 / self.delta))
        self.table = [[0] * self.width for _ in range(self.depth)]

    def _hash(self, item: str, i: int) -> int:
        digest = hashlib.blake2b(f"{i}:{item}".encode("utf-8"), digest_size=8).digest()
        return int.from_bytes(digest, "big") % self.width

    def update(self, item: str, count: int = 1) -> None:
        self.total_count += count
        for i in range(self.depth):
            idx = self._hash(item, i)
            self.table[i][idx] += count

    def estimate(self, item: str) -> int:
        return min(self.table[i][self._hash(item, i)] for i in range(self.depth))

    def process_stream(self, stream) -> None:
        for item in stream:
            self.update(item)

    def memory_bytes(self) -> int:
        # Integer counters in table.
        return self.depth * self.width * 8
