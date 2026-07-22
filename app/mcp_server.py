"""Optional MCP surface for the same bounded tools used by the API.

Run with:
    python -m app.mcp_server
"""
from __future__ import annotations
from .agents import PruefPilot

pilot = PruefPilot()

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install the optional MCP dependency: pip install 'mcp>=1.2'") from exc

mcp = FastMCP("PrüfPilot")

@mcp.tool()
def search_requirements(question: str) -> dict:
    """Return a grounded answer with versioned source references."""
    return pilot.ask(question).model_dump()

@mcp.tool()
def list_missing_documents() -> dict:
    """Compare the synthetic case file with its required document checklist."""
    return pilot.completeness().model_dump()

@mcp.tool()
def compare_claim_to_evidence(claim: str) -> dict:
    """Check a claim against case metadata and documents."""
    return pilot.evidence_check(claim).model_dump()

@mcp.tool()
def draft_review_memo() -> dict:
    """Draft a structured review memo. The tool never makes the final decision."""
    return pilot.review_memo().model_dump()

@mcp.tool()
def classify_case_documents() -> dict:
    """Classify, validate and security-scan the synthetic case uploads."""
    return pilot.intake().model_dump()

@mcp.tool()
def get_reviewer_queue() -> list[dict]:
    """Return prioritised synthetic cases for a reviewer workspace."""
    return [item.model_dump() for item in pilot.queue()]

if __name__ == "__main__":
    mcp.run()
