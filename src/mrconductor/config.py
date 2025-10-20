from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Iterable, List, Optional, Set, Tuple


class FeatureFlag(Enum):
    """Enumerates protocol features that can be toggled per session."""

    ASCII_CORE = auto()
    UNICODE_OVERLAY = auto()
    SERIALIZATION = auto()
    DYNAMIC_PACKS = auto()
    RELATIONAL_CONTEXT = auto()
    CHECKSUM_BLOCKS = auto()
    MCP_TOOLING = auto()
    REUSABLE_KEYS = auto()


@dataclass(frozen=True)
class FeatureParamSet:
    """
    String-level representation of feature toggles for handshake transmission.

    Each flag is serialized into a short token so the payload remains compact.
    """

    ascii_symbol: str = "~a"
    unicode_symbol: str = "~u"
    serialization_symbol: str = "~s"
    dynamic_packs_symbol: str = "~p"
    relational_context_symbol: str = "~r"
    checksum_symbol: str = "~c"
    mcp_symbol: str = "~m"
    reusable_keys_symbol: str = "~k"

    def encode_flags(self, flags: Iterable[FeatureFlag]) -> str:
        """Return a compressed string with the encoded feature set."""
        symbol_map = {
            FeatureFlag.ASCII_CORE: self.ascii_symbol,
            FeatureFlag.UNICODE_OVERLAY: self.unicode_symbol,
            FeatureFlag.SERIALIZATION: self.serialization_symbol,
            FeatureFlag.DYNAMIC_PACKS: self.dynamic_packs_symbol,
            FeatureFlag.RELATIONAL_CONTEXT: self.relational_context_symbol,
            FeatureFlag.CHECKSUM_BLOCKS: self.checksum_symbol,
            FeatureFlag.MCP_TOOLING: self.mcp_symbol,
            FeatureFlag.REUSABLE_KEYS: self.reusable_keys_symbol,
        }
        return "".join(symbol_map[flag] for flag in flags)

    def decode_flags(self, payload: str) -> Set[FeatureFlag]:
        """Parse feature flags from a compressed payload string."""
        reverse_map = {
            self.ascii_symbol: FeatureFlag.ASCII_CORE,
            self.unicode_symbol: FeatureFlag.UNICODE_OVERLAY,
            self.serialization_symbol: FeatureFlag.SERIALIZATION,
            self.dynamic_packs_symbol: FeatureFlag.DYNAMIC_PACKS,
            self.relational_context_symbol: FeatureFlag.RELATIONAL_CONTEXT,
            self.checksum_symbol: FeatureFlag.CHECKSUM_BLOCKS,
            self.mcp_symbol: FeatureFlag.MCP_TOOLING,
            self.reusable_keys_symbol: FeatureFlag.REUSABLE_KEYS,
        }
        flags: Set[FeatureFlag] = set()
        token = ""
        for char in payload:
            token += char
            if token in reverse_map:
                flags.add(reverse_map[token])
                token = ""
        if token:
            raise ValueError(f"Trailing token could not be decoded: {token!r}")
        return flags


@dataclass
class FeatureFlags:
    """
    High-level feature management used by orchestrator and bootstrap scripts.
    """

    enabled: Set[FeatureFlag] = field(default_factory=lambda: {FeatureFlag.ASCII_CORE})
    params: FeatureParamSet = field(default_factory=FeatureParamSet)

    def enable(self, *flags: FeatureFlag) -> None:
        for flag in flags:
            self.enabled.add(flag)

    def disable(self, *flags: FeatureFlag) -> None:
        for flag in flags:
            self.enabled.discard(flag)

    def as_payload(self) -> str:
        return self.params.encode_flags(sorted(self.enabled, key=lambda f: f.value))

    @classmethod
    def from_payload(cls, payload: str, params: Optional[FeatureParamSet] = None) -> "FeatureFlags":
        param_set = params or FeatureParamSet()
        flags = param_set.decode_flags(payload)
        return cls(enabled=flags, params=param_set)

    def requires_unicode_support(self) -> bool:
        return FeatureFlag.UNICODE_OVERLAY in self.enabled

    def requires_serialization(self) -> bool:
        return FeatureFlag.SERIALIZATION in self.enabled

    def wants_reusable_keys(self) -> bool:
        return FeatureFlag.REUSABLE_KEYS in self.enabled

    def summary(self) -> Dict[str, bool]:
        return {flag.name.lower(): flag in self.enabled for flag in FeatureFlag}
