#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from min_tokenization_translator.benchmark import BenchmarkConfig, BenchmarkRunner
from min_tokenization_translator.config import FeatureFlag, FeatureFlags


def load_corpus(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        data = json.loads(text)
        if isinstance(data, list):
            return [str(item) for item in data]
        raise ValueError("JSON corpus must be a list of strings")
    return [line.strip() for line in text.splitlines() if line.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run compression benchmarks.")
    parser.add_argument("--corpus", type=Path, required=True, help="Path to corpus file (.txt or .json list).")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--unicode", action="store_true")
    parser.add_argument("--serialization", action="store_true")
    parser.add_argument("--dynamic-packs", action="store_true")
    parser.add_argument("--relational-context", action="store_true")
    parser.add_argument("--checksums", action="store_true")
    parser.add_argument("--mcp", action="store_true")
    parser.add_argument("--reuse-keys", action="store_true")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    corpus = load_corpus(args.corpus)
    feature_flags = FeatureFlags()
    feature_flags.enable(FeatureFlag.ASCII_CORE)

    if args.dynamic_packs:
        feature_flags.enable(FeatureFlag.DYNAMIC_PACKS)
    if args.relational_context:
        feature_flags.enable(FeatureFlag.RELATIONAL_CONTEXT)
    if args.checksums:
        feature_flags.enable(FeatureFlag.CHECKSUM_BLOCKS)
    if args.unicode:
        feature_flags.enable(FeatureFlag.UNICODE_OVERLAY)
    if args.serialization:
        feature_flags.enable(FeatureFlag.SERIALIZATION)
    if args.mcp:
        feature_flags.enable(FeatureFlag.MCP_TOOLING)
    if args.reuse_keys:
        feature_flags.enable(FeatureFlag.REUSABLE_KEYS)

    runner = BenchmarkRunner(
        BenchmarkConfig(
            corpus=corpus,
            feature_flags=feature_flags,
            runs=args.runs,
        )
    )
    result = runner.run()

    print("Baseline tokens:", result.baseline_tokens)
    print("Compressed tokens:", result.compressed_tokens)
    print("Token savings (%):", f"{result.token_savings_pct:.2f}")
    print("Average latency (ms):", f"{result.average_latency_ms:.4f}")
    print("Latency stddev (ms):", f"{result.stddev_latency_ms:.4f}")


if __name__ == "__main__":
    main()
