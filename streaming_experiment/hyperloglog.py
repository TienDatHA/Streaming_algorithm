from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from typing import List


@dataclass
class HyperLogLog:
    p: int = 12
    registers: List[int] = field(init=False)

    def __post_init__(self) -> None:
        if not (4 <= self.p <= 16):
            raise ValueError("p should be in [4, 16]")
        self.m = 1 << self.p
        self.registers = [0] * self.m

    def _hash64(self, item: str) -> int:
        digest = hashlib.sha1(item.encode("utf-8")).digest()[:8]
        return int.from_bytes(digest, byteorder="big", signed=False)

    @staticmethod
    def _rank(w: int, max_bits: int) -> int:
        if w == 0:
            return max_bits + 1
        return max_bits - w.bit_length() + 1

    def add(self, item: str) -> None:
        x = self._hash64(item)
        idx = x >> (64 - self.p)
        w = x & ((1 << (64 - self.p)) - 1)
        r = self._rank(w, 64 - self.p)
        if r > self.registers[idx]:
            self.registers[idx] = r

    def process_stream(self, stream) -> None:
        for item in stream:
            self.add(item)

    def count(self) -> float:
        m = self.m
        z = sum(2.0 ** (-r) for r in self.registers)

        if m == 16:
            alpha_m = 0.673
        elif m == 32:
            alpha_m = 0.697
        elif m == 64:
            alpha_m = 0.709
        else:
            alpha_m = 0.7213 / (1 + 1.079 / m)

        estimate = alpha_m * (m**2) / z

        # Small-range correction
        zeros = self.registers.count(0)
        if estimate <= 2.5 * m and zeros > 0:
            estimate = m * math.log(m / zeros)

        return estimate

    def memory_bytes(self) -> int:
        # One byte per register in a compact implementation (rough estimate).
        return self.m
