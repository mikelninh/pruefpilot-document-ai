from app.storage import SQLiteStore


def test_feedback_becomes_eval_case(tmp_path):
    store = SQLiteStore(str(tmp_path / "test.db"))
    feedback_id, eval_case = store.save_feedback({
        "case_id": "GF-2026-014",
        "document_id": "D05",
        "field_name": "document_type",
        "previous_value": "verwendungsnachweis",
        "corrected_value": "zahlenmaessiger_verwendungsnachweis",
        "note": "Fachlich präziser",
    })
    assert feedback_id.startswith("fb_")
    assert eval_case["expected"] == "zahlenmaessiger_verwendungsnachweis"
    assert len(store.list_feedback()) == 1
