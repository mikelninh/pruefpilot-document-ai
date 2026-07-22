# PrüfPilot v3 — Live deployment

## Public surfaces

- Visual reviewer product: https://pruefpilot-aconium.vercel.app
- FastAPI service: https://pruefpilot-document-ai.vercel.app
- Interactive OpenAPI: https://pruefpilot-document-ai.vercel.app/api/docs
- Health: https://pruefpilot-document-ai.vercel.app/api/health
- Transparent benchmark: https://pruefpilot-document-ai.vercel.app/api/benchmark

## Implemented reviewer path

1. Open a prioritised funding case.
2. Upload a real PDF.
3. Extract text, classify the document and identify structured fields.
4. Treat document instructions as untrusted data and quarantine prompt injection.
5. Ask grounded questions with version, page and section citations.
6. Compare claims against case evidence.
7. Draft a review memo without making the final funding decision.
8. Turn reviewer corrections into regression evaluation cases.

## Verification

- Public health endpoint returned HTTP 200 after deployment.
- Public benchmark endpoint returned a measured deterministic baseline.
- OpenAI, Mistral and self-hosted providers remain unscored until a controlled run is executed with configured credentials.
- Local repository suite: 18/18 tests and 10/10 retrieval evaluations passed before deployment.

## Persistence boundary

The public Vercel function uses instance-local serverless state and exposes that limitation in response headers and the UI. Reviewer feedback is mirrored in browser storage for the public demonstration. The local Docker version uses SQLite; `db/schema.sql` defines the intended Postgres pilot schema.

This is a production-shaped application prototype, not a claim that SSO, RBAC, tenancy, durable object storage or a public-sector DMS integration are already complete.
