from __future__ import annotations

import statistics
import time
from dataclasses import dataclass
from typing import List, Sequence

from .config import FeatureFlags
from .distiller import PromptDistiller
from .encoder import SymbolEncoder


@dataclass
class BenchmarkConfig:
    """Configuration for benchmarking compression pipeline."""

    corpus: Sequence[str]
    feature_flags: FeatureFlags
    runs: int = 3


@dataclass
class BenchmarkResult:
    """Summary metrics gathered during benchmarking."""

    baseline_tokens: int
    compressed_tokens: int
    token_savings_pct: float
    average_latency_ms: float
    stddev_latency_ms: float


class BenchmarkRunner:
    """Simulates compression runs to measure savings and latency."""

    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self._distiller = PromptDistiller()
        self._encoder = SymbolEncoder(config.feature_flags)

    def _mock_token_count(self, text: str) -> int:
        """
        Stand-in tokenizer; replace with actual tokenizer API during integration.
        """
        return max(1, len(text.split()))

    def _compress_prompt(self, prompt: str) -> str:
        """
        Placeholder compression logic.
        Actual implementation should call distiller and encoder modules.
        """
        distilled = self._distiller.distill(prompt)
        encoded = self._encoder.encode(distilled)
        return encoded.payload

    def run(self) -> BenchmarkResult:
        baseline_tokens = 0
        compressed_tokens = 0
        latencies: List[float] = []

        for _ in range(self.config.runs):
            for prompt in self.config.corpus:
                baseline_tokens += self._mock_token_count(prompt)
                start = time.perf_counter()
                compressed = self._compress_prompt(prompt)
                latencies.append((time.perf_counter() - start) * 1000.0)
                compressed_tokens += self._mock_token_count(compressed)

        runs_completed = max(1, self.config.runs * len(self.config.corpus))
        avg_latency = statistics.mean(latencies) if latencies else 0.0
        std_latency = statistics.pstdev(latencies) if len(latencies) > 1 else 0.0
        savings_pct = 0.0
        if baseline_tokens:
            savings_pct = 100.0 * (1 - (compressed_tokens / baseline_tokens))

        return BenchmarkResult(
            baseline_tokens=baseline_tokens // runs_completed,
            compressed_tokens=compressed_tokens // runs_completed,
            token_savings_pct=savings_pct,
            average_latency_ms=avg_latency,
            stddev_latency_ms=std_latency,
        )
