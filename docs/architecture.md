# Architecture

```mermaid
flowchart LR
    UI[Reviewer Workspace] --> API[FastAPI Gateway]
    API --> O[Bounded Orchestrator]
    O --> I[Intake + Security]
    O --> C[Completeness Agent]
    O --> E[Evidence Agent]
    O --> R[Grounded RAG]
    O --> M[Review Memo Agent]
    C --> T[Typed Tools / MCP Surface]
    E --> T
    R --> BM25[Version-aware Retrieval]
    I --> CASE[Synthetic Case Store]
    T --> CASE
    BM25 --> RULES[Official Rule Summaries]
    M --> H[Human Approval Gate]
    API --> OBS[Eval and observability boundary]
```

## Boundaries

- Maximum five logical tool calls per workflow.
- Structured Pydantic outputs.
- Version and page metadata on every rule citation.
- Untrusted document text is never treated as agent instruction.
- No external action, payment, notification or funding decision.
- Synthetic case data only.
- Deterministic fallback so the public demo runs without an API key.
