#!/usr/bin/env python3
from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Min Tokenization Translator FastAPI server.")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    try:
        import uvicorn
        from min_tokenization_translator.server import create_app
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise SystemExit("Install fastapi and uvicorn extras to run the server.") from exc

    app = create_app()
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
