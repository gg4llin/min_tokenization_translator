from min_tokenization_translator.benchmark import BenchmarkConfig, BenchmarkRunner
from min_tokenization_translator.config import FeatureFlag, FeatureFlags


def test_benchmark_runs_with_feature_flags():
    feature_flags = FeatureFlags()
    feature_flags.enable(
        FeatureFlag.ASCII_CORE,
        FeatureFlag.DYNAMIC_PACKS,
        FeatureFlag.UNICODE_OVERLAY,
        FeatureFlag.SERIALIZATION,
    )
    config = BenchmarkConfig(
        corpus=["Diagnose patient with pneumonia.", "Return dosage plan: azithromycin 500mg -> taper."],
        feature_flags=feature_flags,
        runs=1,
    )
    result = BenchmarkRunner(config).run()
    assert result.baseline_tokens >= result.compressed_tokens
    assert result.token_savings_pct >= 0.0
