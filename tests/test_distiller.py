from mrconductor.distiller import PromptDistiller


def test_distiller_extracts_graph_and_lexicon():
    distiller = PromptDistiller()
    prompt = "Diagnosis: pneumonia. dosage=500mg. Return plan -> taper antibiotics."
    distilled = distiller.distill(prompt, context={"priority": "high"})

    assert distilled.metrics["segments_analyzed"] >= 3
    assert distilled.metrics["graph_size"] >= 3
    assert "diag pneumonia" in distilled.lexicon
    canonical_keys = {entry["canonical"] for entry in distilled.graph}
    assert "diag pneumonia" in canonical_keys
    assert any(entry["type"] == "context" for entry in distilled.graph)
