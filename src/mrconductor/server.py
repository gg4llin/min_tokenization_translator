from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except ImportError as exc:  # pragma: no cover - optional dependency
    raise RuntimeError("FastAPI and Pydantic are required for server deployment.") from exc

from .bootstrap import BootstrapConfig, bootstrap_environment
from .config import FeatureFlags
from .distiller import PromptDistiller


class HandshakeRequest(BaseModel):
    allow_reusable_keys: bool = False
    preload_unicode_overlay: bool = False
    preload_serialization: bool = False
    enable_dynamic_packs: bool = True
    enable_relational_context: bool = True
    enable_checksums: bool = True
    enable_mcp_tooling: bool = False
    tokenizer: Optional[str] = None


class HandshakeResponse(BaseModel):
    handshake_packet: str
    feature_flags: Dict[str, bool]


class DistillRequest(BaseModel):
    prompt: str
    context: Optional[Dict[str, str]] = None


class DistillResponse(BaseModel):
    graph: list[Dict[str, str]]
    residual_note: str


def create_app() -> "FastAPI":
    app = FastAPI(title="MrConductor Host", version="0.1.0")
    distiller = PromptDistiller()

    @app.post("/handshake", response_model=HandshakeResponse)
    def handshake(request: HandshakeRequest) -> HandshakeResponse:
        config = BootstrapConfig(
            workspace_dir=request_workspace_dir(),
            packs_dir=request_workspace_dir() / "packs",
            allow_reusable_keys=request.allow_reusable_keys,
            preload_unicode_overlay=request.preload_unicode_overlay,
            preload_serialization=request.preload_serialization,
            enable_dynamic_packs=request.enable_dynamic_packs,
            enable_relational_context=request.enable_relational_context,
            enable_checksums=request.enable_checksums,
            enable_mcp_tooling=request.enable_mcp_tooling,
            override_tokenizer_fingerprint=request.tokenizer,
        )
        result = bootstrap_environment(config)
        return HandshakeResponse(
            handshake_packet=result.handshake_packet,
            feature_flags=result.feature_flags.summary(),
        )

    @app.post("/distill", response_model=DistillResponse)
    def distill(request: DistillRequest) -> DistillResponse:
        distilled = distiller.distill(request.prompt, context=request.context)
        return DistillResponse(graph=distilled.graph, residual_note=distilled.residual_note)

    return app


def request_workspace_dir() -> "Path":  # pragma: no cover - runtime path resolution
    from pathlib import Path

    base = Path.cwd() / "workspace"
    base.mkdir(parents=True, exist_ok=True)
    return base
