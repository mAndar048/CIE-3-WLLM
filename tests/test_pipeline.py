import pytest
from core.pipeline import process, normalize_input, polish_rules
from core.metrics import character_error_rate, word_accuracy, sentence_accuracy, edit_distance

@pytest.mark.parametrize("language,input_,expected", [
 ("Hindi","namaste","नमस्ते"),
 ("Kannada","namaskara","ನಮಸ್ಕಾರ"),
 ("Tamil","vanakkam","வணக்கம்"),
 ("Hindi","namaste, 123!","नमस्ते, 123!"),
 ("Hindi","aaj class hai","आज क्लास है"),
 ("Kannada","nanna hesaru","ನನ್ನ ಹೆಸರು"),
 ("Tamil","enakku thanni venum","எனக்கு தண்ணி வேணும்")
])
def test_transliteration(language, input_, expected):
    assert process(input_, language).native == expected

def test_protect_email_url_digits():
    s = "namaste x@y.com https://example.com/test?x=4 9:30"
    result = process(s, "Hindi")
    assert "x@y.com" in result.native
    assert "https://example.com/test?x=4" in result.native
    assert "9:30" in result.native

def test_keep_technical_english():
    assert "GitHub" in process("GitHub project hai", "Hindi").native

def test_unknown_word_is_not_fabricated():
    r = process("xyzzystuff", "Hindi")
    assert r.native == "xyzzystuff"
    assert "xyzzystuff" in r.unknown_words

def test_empty_input():
    assert process("   ").native == ""

def test_long_input_rejected():
    with pytest.raises(ValueError):
        process("x" * 1801)

def test_invalid_language():
    with pytest.raises(ValueError):
        process("test", "Martian")

def test_invalid_engine():
    with pytest.raises(ValueError):
        process("test", engine="FakeAI")

def test_local_polishing():
    assert polish_rules("नमस्ते  ,दुनिया!!!") == "नमस्ते, दुनिया!"

def test_metrics():
    assert edit_distance("abc", "adc") == 1
    assert character_error_rate("abc", "abc") == 0
    assert character_error_rate("abc", "abx") == pytest.approx(1/3)
    assert word_accuracy("a b", "a c") == .5
    assert sentence_accuracy("नमस्ते", "नमस्ते") == 1

def test_limited_translation_warns_and_does_not_hallucinate(monkeypatch):
    import core.pipeline as pipe
    def missing(*args, **kwargs):
        from core.providers import ModelUnavailable
        raise ModelUnavailable("no model")
    monkeypatch.setattr(pipe, "translate_to_english", missing)
    r = pipe.process("namaste", translate=True)
    assert r.english is None
    assert "no model" in r.warnings[0]

def test_param1_kannada_explicit_not_supported():
    from core.providers import refine_with_param1, ModelUnavailable
    with pytest.raises(ModelUnavailable):
        refine_with_param1("ನಮಸ್ಕಾರ", "kn")
