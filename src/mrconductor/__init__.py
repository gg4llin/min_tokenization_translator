"""
MrConductor compression stack.

Provides modular components for feature flag negotiation, secure handshakes,
bootstrap utilities, and benchmarking harnesses that implement the protocol
described in ``prompt.md``.
"""

from .config import FeatureFlag, FeatureFlags, FeatureParamSet
from .handshake import HandshakeConfig, HandshakeManager
from .bootstrap import BootstrapConfig, BootstrapResult, bootstrap_environment
from .benchmark import BenchmarkConfig, BenchmarkResult, BenchmarkRunner
from .distiller import DistilledPrompt, PromptDistiller
from .encoder import EncodedResult, SymbolEncoder

__all__ = [
    "FeatureFlag",
    "FeatureFlags",
    "FeatureParamSet",
    "HandshakeConfig",
    "HandshakeManager",
    "BootstrapConfig",
    "BootstrapResult",
    "bootstrap_environment",
    "BenchmarkConfig",
    "BenchmarkResult",
    "BenchmarkRunner",
    "DistilledPrompt",
    "PromptDistiller",
    "EncodedResult",
    "SymbolEncoder",
]
