from __future__ import annotations

from typing import Any


CASES: dict[str, dict[str, Any]] = {
    "glasfaser-sonnenhain": {
        "id": "glasfaser-sonnenhain",
        "internal_id": "GF-2026-014",
        "title": "Glasfaser-Ausbau Sonnenhain",
        "question": "Kann die Schlusszahlung vorbereitet werden?",
        "domain": "Fördermittelprüfung",
        "user": "Fördermittelprüfer:in",
        "goal": "Fehlende Unterlagen, Zahlendifferenzen und unbelegte Aussagen vor der menschlichen Freigabe erkennen.",
        "status": "Prüfung erforderlich",
        "documents": [
            {"name": "Bewilligungsbescheid.pdf", "status": "vorhanden", "excerpt": "Bewilligungszeitraum: 01.09.2025 bis 30.06.2026."},
            {"name": "Rechnungspaket_R001-R007.pdf", "status": "vorhanden", "excerpt": "Rechnungssumme 734.280 EUR; R-007 ohne Leistungszeitraum."},
            {"name": "Zahlenmaessiger_Verwendungsnachweis.pdf", "status": "vorhanden", "excerpt": "Beantragte Erstattung: 730.000 EUR."},
            {"name": "Abnahmeprotokoll.pdf", "status": "fehlt", "excerpt": "Pflichtunterlage liegt nicht vor."},
            {"name": "GPS-Fotodokumentation.zip", "status": "fehlt", "excerpt": "Pflichtunterlage liegt nicht vor."},
            {"name": "Lieferantenhinweis.pdf", "status": "quarantaene", "excerpt": "Enthält eine dokumentbasierte Prompt-Injection-Anweisung."},
        ],
        "metrics": [
            {"value": "7/9", "label": "Pflichtunterlagen"},
            {"value": "4.280 €", "label": "ungeklärte Differenz"},
            {"value": "1", "label": "Quarantänefall"},
        ],
        "confirmed": [
            "Bewilligungsbescheid, Sachbericht und Kernnachweise liegen vor.",
            "R-001 bis R-006 sind formal dem Projektzeitraum zuordenbar.",
        ],
        "open": [
            "Abnahmeprotokoll fehlt.",
            "GPS-Fotodokumentation fehlt.",
            "Rechnung R-007 enthält keinen eindeutigen Leistungszeitraum.",
            "Rechnungssumme und beantragte Erstattung weichen um 4.280 EUR ab.",
        ],
        "next_action": "Abnahmeprotokoll und GPS-Fotos nachfordern; R-007 und die Differenz von 4.280 EUR klären.",
        "suggested_questions": [
            "Welche Unterlagen fehlen?",
            "Welche Beträge stimmen nicht überein?",
            "Kann die Schlusszahlung freigegeben werden?",
            "Warum wurde ein Dokument quarantänisiert?",
        ],
        "sources": [
            {"title": "Bewilligungsbescheid Sonnenhain", "version": "12.08.2025", "page": 3, "section": "Nebenbestimmungen 4.2", "url": "https://pruefpilot-document-ai.vercel.app/api/docs"},
            {"title": "BNBest-Gigabit", "version": "26.06.2026", "page": 4, "section": "4.2.1", "url": "https://pruefpilot-document-ai.vercel.app/api/docs"},
        ],
        "tech": {
            "mode": "live-api",
            "tools": ["classify_documents", "check_completeness", "reconcile_amounts", "scan_prompt_injection", "draft_review_memo"],
            "domain_pack": ["required_documents.yaml", "funding_rules.json", "amount_checks.py", "review_memo_template.md"],
        },
    },
    "wohngeld-vollstaendigkeit": {
        "id": "wohngeld-vollstaendigkeit",
        "internal_id": "WG-DEMO-041",
        "title": "Wohngeldantrag einer vierköpfigen Familie",
        "question": "Welche Unterlagen fehlen noch?",
        "domain": "Bürgerdienst",
        "user": "Sachbearbeiter:in / Bürgerberatung",
        "goal": "Die Vollständigkeit erklären und gezielte Nachforderungen vorbereiten, ohne über den Anspruch zu entscheiden.",
        "status": "Nachforderung vorbereiten",
        "documents": [
            {"name": "Wohngeldantrag.pdf", "status": "vorhanden", "excerpt": "Vier Personen; Bruttokaltmiete 1.120 EUR."},
            {"name": "Mietvertrag.pdf", "status": "vorhanden", "excerpt": "Bruttokaltmiete stimmt mit dem Antrag überein."},
            {"name": "Einkommensnachweise_Eltern.pdf", "status": "pruefen", "excerpt": "130 EUR Abweichung zur Antragsangabe."},
            {"name": "Meldebescheinigung.pdf", "status": "vorhanden", "excerpt": "Vier Haushaltsmitglieder an derselben Anschrift."},
            {"name": "Nebenkostenabrechnung_aktuell.pdf", "status": "fehlt", "excerpt": "Aktueller Nachweis fehlt."},
            {"name": "Unterhaltsnachweis.pdf", "status": "fehlt", "excerpt": "Unterhaltszahlung ist nicht belegt."},
        ],
        "metrics": [
            {"value": "4/6", "label": "Kernunterlagen"},
            {"value": "130 €", "label": "Einkommensabweichung"},
            {"value": "2", "label": "gezielte Nachforderungen"},
        ],
        "confirmed": [
            "Antrag, Mietvertrag und Meldebescheinigung liegen vor.",
            "Die angegebene Bruttokaltmiete stimmt mit dem Mietvertrag überein.",
        ],
        "open": [
            "Aktueller Nebenkostennachweis fehlt.",
            "Unterhaltszahlung ist nicht belegt.",
            "Einkommensangabe weicht um 130 EUR von den Nachweisen ab.",
        ],
        "next_action": "Nebenkostennachweis und Unterhaltsbeleg anfordern; Einkommensangabe mit der Familie klären.",
        "suggested_questions": [
            "Welche Unterlagen fehlen?",
            "Welche Angaben widersprechen sich?",
            "Ist der Antrag vollständig?",
            "Was sollte die Sachbearbeitung als Nächstes tun?",
        ],
        "sources": [
            {"title": "Synthetische Prüfliste Wohngeldantrag", "version": "Demo 1.0", "page": 1, "section": "Unterlagenprüfung", "url": "https://github.com/mikelninh/pruefpilot-document-ai"},
            {"title": "Synthetischer Antragsdatensatz", "version": "WG-DEMO-041", "page": 2, "section": "Einkommen und Miete", "url": "https://github.com/mikelninh/pruefpilot-document-ai"},
        ],
        "tech": {
            "mode": "domain-pack-preview",
            "tools": ["classify_documents", "check_required_documents", "compare_declared_income", "prepare_request_for_information"],
            "domain_pack": ["wohngeld_case_schema.json", "required_documents.yaml", "consistency_checks.py", "request_template.md"],
        },
    },
    "vergaberegel-schul-it": {
        "id": "vergaberegel-schul-it",
        "internal_id": "VR-DEMO-2027",
        "title": "Neue Vergaberegel für kommunale Schul-IT",
        "question": "Welche laufenden Projekte sind betroffen?",
        "domain": "Rechtsänderung & Vergabe",
        "user": "Verwaltungsjurist:in / Projektleitung",
        "goal": "Eine Regeländerung versioniert verstehen und auf laufende Vorgänge anwenden.",
        "status": "Drei Vorgänge prüfen",
        "documents": [
            {"name": "Vergaberegel_2026.pdf", "status": "vorhanden", "excerpt": "Bisherige Begründungsanforderungen für Direktvergaben."},
            {"name": "Vergaberegel_2027.pdf", "status": "vorhanden", "excerpt": "Neue Pflicht zur dokumentierten Marktpreisprüfung ab 01.01.2027."},
            {"name": "Projektliste_Schul-IT.xlsx", "status": "vorhanden", "excerpt": "Acht laufende Beschaffungsprojekte."},
            {"name": "Vergabevermerk_Schulcampus_Nord.pdf", "status": "pruefen", "excerpt": "Keine dokumentierte Marktpreisprüfung."},
            {"name": "Vergabevermerk_Tablets_West.pdf", "status": "vorhanden", "excerpt": "Marktpreisprüfung und Begründung dokumentiert."},
        ],
        "metrics": [
            {"value": "2", "label": "Regelversionen"},
            {"value": "3", "label": "mögliche Treffer"},
            {"value": "1", "label": "hoher Handlungsbedarf"},
        ],
        "confirmed": [
            "Die neue Regel gilt ab 01.01.2027.",
            "Projekt Tablets West enthält bereits die erforderliche Marktpreisprüfung.",
        ],
        "open": [
            "Schulcampus Nord enthält keine dokumentierte Marktpreisprüfung.",
            "Bei zwei weiteren Vorgängen ist der Startzeitpunkt der Vergabe unklar.",
        ],
        "next_action": "Schulcampus Nord priorisiert prüfen; bei zwei Vorgängen den maßgeblichen Vergabestart klären.",
        "suggested_questions": [
            "Was hat sich 2027 geändert?",
            "Welche Projekte sind betroffen?",
            "Welches Projekt hat den größten Handlungsbedarf?",
            "Wie hängt das mit GitLaw zusammen?",
        ],
        "sources": [
            {"title": "Synthetische Vergaberegel 2027", "version": "01.01.2027", "page": 6, "section": "§ 8 Marktpreisprüfung", "url": "https://github.com/mikelninh/pruefpilot-document-ai"},
            {"title": "Projektliste Schul-IT", "version": "15.12.2026", "page": 1, "section": "Laufende Vorgänge", "url": "https://github.com/mikelninh/pruefpilot-document-ai"},
        ],
        "tech": {
            "mode": "gitlaw-bridge-preview",
            "tools": ["compare_rule_versions", "find_effective_date", "match_projects_to_rule", "draft_impact_note"],
            "domain_pack": ["versioned_rules.json", "project_schema.json", "impact_checks.py", "legal_change_summary.md"],
        },
    },
}


def list_cases() -> list[dict[str, Any]]:
    return [
        {
            "id": case["id"],
            "internal_id": case["internal_id"],
            "title": case["title"],
            "question": case["question"],
            "domain": case["domain"],
            "user": case["user"],
            "status": case["status"],
            "metrics": case["metrics"],
            "tech_mode": case["tech"]["mode"],
        }
        for case in CASES.values()
    ]


def get_case(case_id: str) -> dict[str, Any] | None:
    return CASES.get(case_id)


def _citation(case: dict[str, Any], index: int = 0) -> dict[str, Any]:
    source = case["sources"][min(index, len(case["sources"]) - 1)]
    return {
        "source_id": f'{case["id"]}-source-{index + 1}',
        "title": source["title"],
        "version": source["version"],
        "page": source["page"],
        "section": source["section"],
        "source_url": source["url"],
        "confidence": 0.94 if index == 0 else 0.89,
    }


def answer(case_id: str, question: str) -> dict[str, Any] | None:
    case = get_case(case_id)
    if not case:
        return None
    q = question.lower().strip()
    trace = [
        {"tool": "select_domain_pack", "status": "ok", "detail": case["domain"], "duration_ms": 0.2},
        {"tool": "retrieve_case_and_rules", "status": "ok", "detail": "Fallakte und versionierte Quellen abgeglichen", "duration_ms": 0.7},
    ]

    if any(word in q for word in ("fehl", "vollständig", "unterlagen")):
        response = f"Offen sind: {' '.join(case['open'])} Empfohlene nächste Aktion: {case['next_action']}"
    elif any(word in q for word in ("nächst", "aktion", "tun", "schritt")):
        response = case["next_action"]
    elif any(word in q for word in ("betrag", "summe", "einkommen", "widerspruch", "abweich")):
        if case_id == "glasfaser-sonnenhain":
            response = "Die Rechnungssumme beträgt 734.280 EUR, beantragt wurden 730.000 EUR. Die Differenz von 4.280 EUR ist vor einer Freigabe zu klären."
        elif case_id == "wohngeld-vollstaendigkeit":
            response = "Die Einkommensangabe im Antrag liegt 130 EUR unter der Summe der Nachweise. Diese Abweichung muss geklärt werden."
        else:
            response = "Hier steht keine Betragsprüfung im Vordergrund, sondern die neue Pflicht zur dokumentierten Marktpreisprüfung."
    elif any(word in q for word in ("freig", "entscheid", "anspruch")):
        response = f"PrüfPilot trifft keine abschließende Entscheidung. Status: {case['status']}. Für die menschliche Prüfung gilt: {case['next_action']}"
    elif any(word in q for word in ("geändert", "änderung", "2027", "betroffen", "projekt")) and case_id == "vergaberegel-schul-it":
        response = "Ab 01.01.2027 muss eine dokumentierte Marktpreisprüfung vorliegen. Drei laufende Projekte können betroffen sein; Schulcampus Nord hat den höchsten Handlungsbedarf."
    elif "gitlaw" in q:
        response = "GitLaw liefert die versionierte Regel-Ebene: Was gilt wann und was hat sich geändert? PrüfPilot verbindet diese Regel mit einer konkreten Akte."
    elif any(word in q for word in ("quarant", "prompt", "sicherheit")):
        response = "Dokumentinhalte werden als untrusted content behandelt. Die Demo-Prompt-Injection wird isoliert und als Quarantänefall markiert."
    else:
        response = f"Bestätigt: {' '.join(case['confirmed'])} Offen: {' '.join(case['open'])} Nächste Aktion: {case['next_action']}"

    trace.extend(
        [
            {"tool": "compose_grounded_answer", "status": "ok", "detail": "Antwort aus synthetischer Fallakte und Quellen erzeugt", "duration_ms": 0.5},
            {"tool": "human_boundary_check", "status": "ok", "detail": "Keine autonome Verwaltungsentscheidung", "duration_ms": 0.1},
        ]
    )
    return {
        "answer": response,
        "grounded": True,
        "uncertainty": "low",
        "citations": [_citation(case, 0), _citation(case, 1)],
        "trace": trace,
        "case_id": case_id,
        "tech_mode": case["tech"]["mode"],
    }


def evidence(case_id: str, claim: str) -> dict[str, Any] | None:
    case = get_case(case_id)
    if not case:
        return None
    if case_id == "glasfaser-sonnenhain":
        status = "PARTIALLY_SUPPORTED"
        summary = "R-001 bis R-006 sind zuordenbar; für R-007 fehlt der Leistungszeitraum und das Abnahmeprotokoll liegt nicht vor."
    elif case_id == "wohngeld-vollstaendigkeit":
        status = "NOT_SUPPORTED" if "vollständig" in claim.lower() else "PARTIALLY_SUPPORTED"
        summary = "Antrag und Mietdaten sind belegt; Nebenkostennachweis, Unterhaltsbeleg und Einkommensklärung fehlen."
    else:
        status = "PARTIALLY_SUPPORTED"
        summary = "Regel und Inkrafttreten sind belegt; bei zwei Projekten ist der maßgebliche Vergabestart unklar."
    return {
        "status": status,
        "summary": summary,
        "supporting_evidence": case["confirmed"],
        "missing_evidence": case["open"],
        "trace": [
            {"tool": "parse_claim", "status": "ok", "detail": "Behauptung in Prüfkriterien zerlegt", "duration_ms": 0.2},
            {"tool": "compare_claim_to_evidence", "status": "warning", "detail": summary, "duration_ms": 0.8},
        ],
    }


def memo(case_id: str) -> dict[str, Any] | None:
    case = get_case(case_id)
    if not case:
        return None
    return {
        "case_id": case_id,
        "decision": "NEEDS_INFORMATION",
        "confirmed": case["confirmed"],
        "open_points": case["open"],
        "next_actions": [case["next_action"], "Anschließend menschliche Fachprüfung und Freigabe dokumentieren."],
        "citations": [_citation(case, 0), _citation(case, 1)],
        "human_approval_required": True,
        "trace": [
            {"tool": "summarize_case_state", "status": "ok", "detail": "Bestätigte und offene Punkte strukturiert", "duration_ms": 0.5},
            {"tool": "draft_review_memo", "status": "ok", "detail": "Nächste Aktion vorbereitet", "duration_ms": 0.4},
            {"tool": "human_approval_gate", "status": "ok", "detail": "Endentscheidung nicht automatisiert", "duration_ms": 0.1},
        ],
    }
