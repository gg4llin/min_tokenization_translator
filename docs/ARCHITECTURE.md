# Architecture Overview

The system is composed of modular services that align with the language specification in `prompt.md`. Each module can run inside a host application, an MCP server, or as a standalone CLI.

## Modules

### PromptDistiller
- Input: raw natural-language prompt and optional conversation context.
- Output: distilled semantic graph and residual natural-language note.
- Responsibilities: pruning redundant content, normalizing units, generating canonical tuples for encoding.
- Interfaces: `distill(raw_prompt: str, context: Optional[Dict]) -> DistilledPrompt`.

### DictionaryManager
- Curates static ASCII/Unicode symbols.
- Negotiates dynamic packs and maintains pack registries keyed by handshake seeds.
- Provides persistence hooks for cross-session reuse.

### SessionOrchestrator
- Conducts secure handshake, selecting protocol version, tokenizer fingerprints, serialization mode, and feature flags.
- Manages SSH key strategy (ephemeral by default, reusable when permitted).

### Encoder/Decoder
- Converts distilled graphs into ASCII/Unicode payloads via `SymbolEncoder`.
- Builds hierarchical dictionaries (core + session lexicon) to assign single-byte symbols to high-value phrases.
- Supports hybrid serialization where payloads are compressed prior to symbol mapping.
- Exposes integrity hooks (checksum, retransmit requests).

### TransportAdapter
- Abstracts API clients, ensuring UTF-8 fidelity, tracing, and observability.
- Optional MCP interface exposes `distill`, `encode`, `decode`, and `analyze_savings` commands.
- FastAPI host (`min_tokenization_translator.server`) wraps these adapters as REST endpoints for remote agents.

### MetricsMonitor
- Records token counts before and after compression.
- Flags regressions when savings fall below thresholds.
- Supplies benchmark data to adaptive tuning jobs.

## Handshake Security

1. Orchestrator generates ephemeral Ed25519 key pair.
2. Public key and protocol parameters are embedded in handshake message.
3. Remote endpoint replies with its public key and capability set.
4. Session keys are derived via ECDH; subsequent messages are authenticated.
5. Optional reusable keys can be loaded from encrypted storage when flagged.

When the FastAPI service is deployed, the `/handshake` route executes the same workflow and returns the compact handshake packet to remote clients.

## Benchmarking Flow

1. Load a corpus of baseline prompts with known token counts.
2. Run each prompt through the distiller, encoder, and transport pipeline.
3. Measure token count, latency, and fidelity against ground truth.
4. Produce comparative metrics versus standard prompting.

## Extensibility

- All modules rely on typed interfaces to enable language-porting.
- Feature flags advertised during handshake ensure backward compatibility.
- Serialization layer supports Protocol Buffers, Cap'n Proto, or JSON fallback.
