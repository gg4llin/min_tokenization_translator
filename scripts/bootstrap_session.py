#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from mrconductor.bootstrap import BootstrapConfig, bootstrap_environment


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bootstrap a MrConductor session workspace.")
    parser.add_argument("--workspace-dir", type=Path, default=Path("./workspace"))
    parser.add_argument("--packs-dir", type=Path, default=Path("./workspace/packs"))
    parser.add_argument("--reuse-keys", action="store_true")
    parser.add_argument("--unicode", action="store_true")
    parser.add_argument("--serialization", action="store_true")
    parser.add_argument("--no-dynamic-packs", action="store_true")
    parser.add_argument("--no-relational-context", action="store_true")
    parser.add_argument("--no-checksums", action="store_true")
    parser.add_argument("--enable-mcp", action="store_true")
    parser.add_argument("--tokenizer", type=str, default=None)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    config = BootstrapConfig(
        workspace_dir=args.workspace_dir,
        packs_dir=args.packs_dir,
        allow_reusable_keys=args.reuse_keys,
        preload_unicode_overlay=args.unicode,
        preload_serialization=args.serialization,
        enable_dynamic_packs=not args.no_dynamic_packs,
        enable_relational_context=not args.no_relational_context,
        enable_checksums=not args.no_checksums,
        enable_mcp_tooling=args.enable_mcp,
        override_tokenizer_fingerprint=args.tokenizer,
    )

    result = bootstrap_environment(config)

    print("Workspace:", result.workspace_dir)
    print("Packs:", result.packs_dir)
    print("Feature Flags:", sorted(flag.name for flag in result.feature_flags.enabled))
    print("Handshake Packet:", result.handshake_packet)


if __name__ == "__main__":
    main()
