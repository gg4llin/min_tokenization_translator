from pathlib import Path
from unittest import mock

from mrconductor.config import FeatureFlag, FeatureFlags
from mrconductor.handshake import HandshakeConfig, HandshakeManager


def _fake_keypair(tmp_path: Path) -> Path:
    key_path = tmp_path / "key"
    key_path.write_text("PRIVATE", encoding="utf-8")
    key_path.with_suffix(".pub").write_text("ssh-ed25519 AAAACfakekey", encoding="utf-8")
    return key_path


def test_handshake_packet_roundtrip(tmp_path):
    flags = FeatureFlags()
    flags.enable(FeatureFlag.ASCII_CORE, FeatureFlag.DYNAMIC_PACKS, FeatureFlag.CHECKSUM_BLOCKS)
    config = HandshakeConfig(key_dir=tmp_path, tokenizer_fingerprint="unit-test-tokenizer")
    manager = HandshakeManager(config, flags)

    with mock.patch.object(manager, "_generate_keypair", return_value=_fake_keypair(tmp_path)):
        artifacts = manager.prepare_handshake()

    packet = manager.build_handshake_packet(artifacts)
    protocol_version, tokenizer, decoded_flags = manager.parse_remote_packet(packet)

    assert protocol_version == config.protocol_version
    assert tokenizer == "unit-test-tokenizer"
    assert decoded_flags.enabled == flags.enabled
