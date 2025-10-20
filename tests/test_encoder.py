from min_tokenization_translator.config import FeatureFlags, FeatureFlag
from min_tokenization_translator.distiller import PromptDistiller
from min_tokenization_translator.encoder import SymbolEncoder


def test_symbol_encoder_assigns_symbols():
    distiller = PromptDistiller()
    distilled = distiller.distill("Diagnosis: pneumonia. dosage=500mg.")
    flags = FeatureFlags(enabled={FeatureFlag.ASCII_CORE, FeatureFlag.DYNAMIC_PACKS})
    encoder = SymbolEncoder(flags)
    result = encoder.encode(distilled)

    assert result.payload
    # Feature payload should be present at the start.
    assert result.payload.split("|")[0] == flags.as_payload()
    assert len(result.dictionary) >= len(distilled.lexicon)
