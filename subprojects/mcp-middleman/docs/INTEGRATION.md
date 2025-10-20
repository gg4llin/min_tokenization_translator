# MCP Integration Notes

## Tool Surface

- `handshake`: negotiates feature flags and returns session lexicon seed.
- `distill`: runs PromptDistiller and returns structured graph + lexicon.
- `encode`: invokes SymbolEncoder with session dictionary context.
- `decode`: (future) reconstructs human-readable payloads for auditing.

## Session Handling

- Use deterministic session IDs provided by clients.
- Cache lexicons per session for reuse across encode/decode calls.
- Expose health checks to verify tokenizer compatibility.

## Security Considerations

- Authenticate clients via API keys or mutual TLS.
- Rate-limit encode/decode to protect resources.
- Log events with obfuscated payloads for compliance audits.
