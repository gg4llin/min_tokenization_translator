from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .config import FeatureFlag, FeatureFlags
from .handshake import HandshakeConfig, HandshakeManager


@dataclass
class BootstrapConfig:
    """Configuration for provisioning a new MrConductor environment."""

    workspace_dir: Path
    packs_dir: Path
    key_dir: Optional[Path] = None
    allow_reusable_keys: bool = False
    enable_dynamic_packs: bool = True
    enable_relational_context: bool = True
    enable_checksums: bool = True
    preload_unicode_overlay: bool = False
    preload_serialization: bool = False
    enable_mcp_tooling: bool = False
    override_tokenizer_fingerprint: Optional[str] = None


@dataclass
class BootstrapResult:
    """Outcome of bootstrap routine."""

    workspace_dir: Path
    packs_dir: Path
    feature_flags: FeatureFlags
    handshake_packet: str


def bootstrap_environment(config: BootstrapConfig) -> BootstrapResult:
    """
    Prepare directories, feature flags, and initial handshake packet.
    """

    config.workspace_dir.mkdir(parents=True, exist_ok=True)
    config.packs_dir.mkdir(parents=True, exist_ok=True)

    feature_flags = FeatureFlags()
    feature_flags.enable(FeatureFlag.ASCII_CORE)

    if config.enable_dynamic_packs:
        feature_flags.enable(FeatureFlag.DYNAMIC_PACKS)

    if config.enable_relational_context:
        feature_flags.enable(FeatureFlag.RELATIONAL_CONTEXT)

    if config.enable_checksums:
        feature_flags.enable(FeatureFlag.CHECKSUM_BLOCKS)

    if config.preload_unicode_overlay:
        feature_flags.enable(FeatureFlag.UNICODE_OVERLAY)

    if config.preload_serialization:
        feature_flags.enable(FeatureFlag.SERIALIZATION)

    if config.allow_reusable_keys:
        feature_flags.enable(FeatureFlag.REUSABLE_KEYS)

    if config.enable_mcp_tooling:
        feature_flags.enable(FeatureFlag.MCP_TOOLING)

    key_dir = config.key_dir or (config.workspace_dir / ".keys")
    handshake_config = HandshakeConfig(key_dir=key_dir)
    if config.override_tokenizer_fingerprint:
        handshake_config.tokenizer_fingerprint = config.override_tokenizer_fingerprint

    manager = HandshakeManager(handshake_config, feature_flags)
    artifacts = manager.prepare_handshake()
    packet = manager.build_handshake_packet(artifacts)

    return BootstrapResult(
        workspace_dir=config.workspace_dir,
        packs_dir=config.packs_dir,
        feature_flags=feature_flags,
        handshake_packet=packet,
    )
