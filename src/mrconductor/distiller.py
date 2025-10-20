from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Dict, List, Optional, Tuple


@dataclass
class DistilledPrompt:
    """Structured representation of a prompt after preprocessing."""

    graph: List[Dict[str, str]]
    residual_note: str
    lexicon: Dict[str, str] = field(default_factory=dict)
    metrics: Dict[str, int] = field(default_factory=dict)


class PromptDistiller:
    """
    Strips redundant context while preserving semantic intent.
    """

    _STOP_WORDS = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "to",
        "for",
        "of",
        "with",
        "please",
        "ensure",
        "make",
        "that",
    }

    _SYNONYMS = {
        "dosage": "dose",
        "medication": "med",
        "meds": "med",
        "diagnosis": "diag",
        "diagnose": "diag",
        "patient": "pt",
        "temperature": "temp",
        "pressure": "bp",
        "analysis": "analyze",
        "analyse": "analyze",
    }

    def __init__(self) -> None:
        self._statement_pattern = re.compile(r"[:=\-]>?|\breturns?\b|\binclude\b", re.IGNORECASE)

    def distill(self, raw_prompt: str, context: Optional[Dict[str, str]] = None) -> DistilledPrompt:
        context = context or {}
        cleaned = re.sub(r"\s+", " ", raw_prompt).strip()
        segments = self._split_segments(cleaned)

        graph: List[Dict[str, str]] = []
        residual_parts: List[str] = []
        lexicon: Dict[str, str] = {}

        seen_canonicals = set()
        analyzed = 0
        deduplicated = 0
        for segment in segments:
            analyzed += 1
            canonical, entry = self._normalize_segment(segment)
            if not canonical:
                residual_parts.append(segment)
                continue
            if canonical in seen_canonicals:
                deduplicated += 1
                continue
            seen_canonicals.add(canonical)
            lexicon[canonical] = segment
            graph.append(entry)

        for name, value in context.items():
            canonical = self._canonicalize(f"{name}:{value}")
            if canonical not in seen_canonicals:
                seen_canonicals.add(canonical)
                lexicon[canonical] = f"{name}:{value}"
                graph.append(
                    {
                        "type": "context",
                        "key": self._canonicalize(name),
                        "value": value.strip(),
                        "canonical": canonical,
                    }
                )

        metrics = {
            "segments_analyzed": analyzed,
            "segments_deduplicated": deduplicated,
            "graph_size": len(graph),
            "residual_segments": len(residual_parts),
        }

        residual_note = ". ".join(residual_parts)
        return DistilledPrompt(graph=graph, residual_note=residual_note, lexicon=lexicon, metrics=metrics)

    def _split_segments(self, text: str) -> List[str]:
        candidates = re.split(r"[.;\n]|(?:\s-\s)|(?:\s\*\s)", text)
        segments: List[str] = []
        for candidate in candidates:
            segment = candidate.strip(" -*")
            if segment:
                segments.append(segment)
        return segments

    def _normalize_segment(self, segment: str) -> Tuple[str, Dict[str, str]]:
        lowered = segment.lower()
        if ":" in segment:
            key, value = segment.split(":", 1)
            return self._canonicalize(key + ":" + value), {
                "type": "kv",
                "key": self._canonicalize(key),
                "value": value.strip(),
                "canonical": self._canonicalize(key + ":" + value),
            }
        arrow_match = re.search(r"(.*?)->(.*)", segment)
        if arrow_match:
            left = arrow_match.group(1).strip()
            right = arrow_match.group(2).strip()
            canonical = self._canonicalize(left + "->" + right)
            return canonical, {
                "type": "flow",
                "source": self._canonicalize(left),
                "target": self._canonicalize(right),
                "canonical": canonical,
            }
        equal_match = re.search(r"(.*?)=(.*)", segment)
        if equal_match:
            left = equal_match.group(1).strip()
            right = equal_match.group(2).strip()
            canonical = self._canonicalize(left + "=" + right)
            return canonical, {
                "type": "assign",
                "lhs": self._canonicalize(left),
                "rhs": right.strip(),
                "canonical": canonical,
            }
        if self._statement_pattern.search(segment):
            canonical = self._canonicalize(segment)
            return canonical, {
                "type": "statement",
                "value": segment.strip(),
                "canonical": canonical,
            }
        canonical = self._canonicalize(segment)
        if not canonical:
            return "", {}
        return canonical, {
            "type": "statement",
            "value": segment.strip(),
            "canonical": canonical,
        }

    def _canonicalize(self, text: str) -> str:
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        normalized = []
        for token in tokens:
            token = self._SYNONYMS.get(token, token)
            if token in self._STOP_WORDS:
                continue
            normalized.append(token)
        return " ".join(normalized)
