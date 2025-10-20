from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from .config import FeatureFlags
from .distiller import DistilledPrompt


@dataclass
class EncodedResult:
    """Holds the compressed payload and supporting metadata."""

    payload: str
    dictionary: Dict[str, str] = field(default_factory=dict)
    feature_header: str = ""


class SymbolEncoder:
    """
    Builds a compact symbol stream from a distilled prompt.

    The encoder assigns single-byte ASCII symbols to high-value phrases,
    falling back to prefixed identifiers when the symbol pool is exhausted.
    """

    _SYMBOL_POOL = [
        "!", "@", "#", "$", "%", "&", "*", "+", "-", "/", ":", ";", "<", ">", "?", "[", "]", "{", "}",
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S",
        "T", "U", "V", "W", "X", "Y", "Z",
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s",
        "t", "u", "v", "w", "x", "y", "z",
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    ]

    def __init__(self, feature_flags: FeatureFlags | None = None) -> None:
        self.feature_flags = feature_flags
        self._token_to_symbol: Dict[str, str] = {}
        self._symbol_to_token: Dict[str, str] = {}
        self._pool_index = 0

    def encode(self, distilled: DistilledPrompt) -> EncodedResult:
        self._token_to_symbol.clear()
        self._symbol_to_token.clear()
        self._pool_index = 0

        tokens = self._collect_tokens(distilled)
        ordered_tokens = sorted(tokens, key=lambda item: (-item[1], len(item[0])))
        for token, _count in ordered_tokens:
            self._register_token(token)

        symbol_stream = []
        for entry in distilled.graph:
            parts = []
            for key in ("type", "key", "value", "source", "target", "lhs", "rhs", "canonical"):
                value = entry.get(key)
                if value:
                    parts.append(self._encode_token(value))
            if parts:
                symbol_stream.append("".join(parts))
        if distilled.residual_note:
            symbol_stream.append(self._encode_token(distilled.residual_note))

        feature_header = ""
        if self.feature_flags:
            feature_header = self.feature_flags.as_payload()
            symbol_stream.insert(0, feature_header)

        payload = "|".join(symbol_stream)
        return EncodedResult(payload=payload, dictionary=dict(self._symbol_to_token), feature_header=feature_header)

    def _collect_tokens(self, distilled: DistilledPrompt) -> List[tuple[str, int]]:
        counts: Dict[str, int] = {}

        def bump(text: str, weight: int = 1) -> None:
            if not text:
                return
            counts[text] = counts.get(text, 0) + weight

        for entry in distilled.graph:
            for value in entry.values():
                bump(str(value), 2)
        for canonical, surface in distilled.lexicon.items():
            bump(canonical, 3)
            bump(surface, 1)
        if distilled.residual_note:
            bump(distilled.residual_note, 1)
        return list(counts.items())

    def _register_token(self, token: str) -> None:
        if token in self._token_to_symbol:
            return
        if self._pool_index < len(self._SYMBOL_POOL):
            symbol = self._SYMBOL_POOL[self._pool_index]
            self._pool_index += 1
        else:
            symbol = f"~{len(self._token_to_symbol)}"
        self._token_to_symbol[token] = symbol
        self._symbol_to_token[symbol] = token

    def _encode_token(self, token: str) -> str:
        if token not in self._token_to_symbol:
            self._register_token(token)
        return self._token_to_symbol[token]
