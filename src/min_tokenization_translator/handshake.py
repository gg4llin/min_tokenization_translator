from __future__ import annotations

import base64
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from .config import FeatureFlags


@dataclass
class HandshakeConfig:
    """Configuration for securing session handshakes."""

    protocol_version: str = "1.0"
    tokenizer_fingerprint: str = "gpt-4o-mini"
    key_dir: Path = Path.home() / ".min_tokenization_translator" / "keys"
    ssh_key_type: str = "ed25519"


@dataclass
class HandshakeArtifacts:
    """Artifacts produced during handshake preparation."""

    public_key: str
    private_key_path: Path
    feature_payload: str
    nonce: str


class HandshakeManager:
    """
    Manages secure handshake negotiation using SSH key pairs.

    Defaults to per-session keys but can reuse encrypted keys when requested.
    """

    def __init__(self, config: HandshakeConfig, feature_flags: FeatureFlags):
        self.config = config
        self.feature_flags = feature_flags

    def prepare_handshake(self) -> HandshakeArtifacts:
        """Generate keys, nonce, and feature payload for a session."""
        key_path = self._generate_keypair()
        public_key = self._read_public_key(key_path)
        feature_payload = self.feature_flags.as_payload()
        nonce = base64.urlsafe_b64encode(os.urandom(12)).decode("ascii").rstrip("=")
        return HandshakeArtifacts(
            public_key=public_key,
            private_key_path=key_path,
            feature_payload=feature_payload,
            nonce=nonce,
        )

    def _generate_keypair(self) -> Path:
        """Create an SSH keypair, honoring reusable-key requests when set."""
        key_dir = self.config.key_dir
        key_dir.mkdir(parents=True, exist_ok=True)
        if self.feature_flags.wants_reusable_keys():
            key_path = key_dir / f"reusable_{self.config.ssh_key_type}"
            if key_path.exists():
                return key_path
        else:
            key_path = key_dir / f"session_{os.getpid()}_{os.urandom(4).hex()}"

        if key_path.exists():
            key_path.unlink()
        public_path = key_path.with_suffix(".pub")
        if public_path.exists():
            public_path.unlink()

        cmd = [
            "ssh-keygen",
            "-t",
            self.config.ssh_key_type,
            "-f",
            str(key_path),
            "-N",
            "",
            "-C",
            "min-tokenization-translator-session",
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError as exc:
            raise RuntimeError("ssh-keygen is required for handshake key generation.") from exc
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"ssh-keygen failed: {exc.stderr.decode('utf-8', errors='ignore')}") from exc
        if self.feature_flags.wants_reusable_keys():
            key_path.chmod(0o600)
        return key_path

    def _read_public_key(self, key_path: Path) -> str:
        public_path = key_path.with_suffix(".pub")
        return public_path.read_text(encoding="utf-8").strip()

    def build_handshake_packet(self, artifacts: HandshakeArtifacts) -> str:
        """Serialize handshake data into compact packet ready for transport."""
        components = [
            f"v={self.config.protocol_version}",
            f"tok={self.config.tokenizer_fingerprint}",
            f"feat={artifacts.feature_payload}",
            f"nonce={artifacts.nonce}",
            f"pub={artifacts.public_key}",
        ]
        return "|".join(components)

    def parse_remote_packet(self, packet: str) -> Tuple[str, str, FeatureFlags]:
        """Parse remote handshake packet and return useful components."""
        fields = dict(part.split("=", 1) for part in packet.split("|") if "=" in part)
        protocol_version = fields.get("v", "")
        tokenizer = fields.get("tok", "")
        feature_payload = fields.get("feat", "")
        flags = FeatureFlags.from_payload(feature_payload, self.feature_flags.params)
        return protocol_version, tokenizer, flags
