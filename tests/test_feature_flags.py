from min_tokenization_translator.config import FeatureFlag, FeatureFlags


def test_feature_flags_roundtrip():
    flags = FeatureFlags()
    flags.enable(
        FeatureFlag.ASCII_CORE,
        FeatureFlag.UNICODE_OVERLAY,
        FeatureFlag.SERIALIZATION,
        FeatureFlag.DYNAMIC_PACKS,
    )
    payload = flags.as_payload()
    decoded = FeatureFlags.from_payload(payload, params=flags.params)
    assert decoded.enabled == flags.enabled


def test_requires_helpers():
    flags = FeatureFlags()
    assert flags.requires_unicode_support() is False
    assert flags.requires_serialization() is False
    flags.enable(FeatureFlag.UNICODE_OVERLAY, FeatureFlag.SERIALIZATION)
    assert flags.requires_unicode_support() is True
    assert flags.requires_serialization() is True
