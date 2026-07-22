from __future__ import annotations
from dataclasses import dataclass
import re

PATTERNS = {
    "document_prompt_injection": re.compile(
        r"(ignore|vergiss|ignoriere).{0,35}(previous|vorher|system|instruction|anweisung)",
        re.IGNORECASE,
    ),
    "credential_request": re.compile(r"(api[-_ ]?key|passwort|token|zugangsdaten)", re.IGNORECASE),
    "external_action_instruction": re.compile(
        r"(send|sende|überweise|delete|lösche|notify|benachrichtige)", re.IGNORECASE
    ),
}

@dataclass(frozen=True)
class SecurityFinding:
    code: str
    severity: str
    message: str


def scan_untrusted_document(text: str) -> list[SecurityFinding]:
    findings: list[SecurityFinding] = []
    for code, pattern in PATTERNS.items():
        if pattern.search(text):
            severity = "high" if code == "document_prompt_injection" else "medium"
            findings.append(
                SecurityFinding(
                    code=code,
                    severity=severity,
                    message="Untrusted document content was isolated from agent instructions.",
                )
            )
    return findings
