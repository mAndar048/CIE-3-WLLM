"""A small, inspectable text processing pipeline with explainable provider state."""
from dataclasses import dataclass, field
import re
import unicodedata
from .lexicon import WORDS, ENGLISH_KEEP, LANGUAGES
from .providers import indicxlit_word, refine_with_param1, translate_to_english, ModelUnavailable

# Protect email addresses, links and neutral numbers; preserve punctuation verbatim.
TOKEN = re.compile(r"https?://\S+|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|[A-Za-z]+(?:'[A-Za-z]+)?|\d+(?:[.:/-]\d+)*|[^A-Za-z\d]+|.", re.UNICODE)
ROMAN_WORD = re.compile(r"^[A-Za-z]+(?:'[A-Za-z]+)?$")
PROTECTED = re.compile(r"^(?:https?://|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,})")
MAX_CHARS = 1800

@dataclass
class Result:
    source: str
    language: str
    native: str
    polished: str
    english: str | None = None
    provider: str = ""
    warnings: list[str] = field(default_factory=list)
    unknown_words: list[str] = field(default_factory=list)


def normalize_input(text: str) -> str:
    if not isinstance(text, str):
        raise ValueError("Input must be text")
    text = unicodedata.normalize("NFC", text).replace("\r\n", "\n").strip()
    if len(text) > MAX_CHARS:
        raise ValueError(f"Maximum {MAX_CHARS} characters are supported per request")
    return text


def polish_rules(text: str) -> str:
    """Local, deterministic whitespace/punctuation polishing (not an LLM)."""
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\s+([,;:!?।])", r"\1", text)
    text = re.sub(r"([,;:!?।])(?=[^\s,;:!?।\n])", r"\1 ", text)
    text = re.sub(r"([!?])\1{2,}", r"\1", text)
    # Avoid accidentally adding sentence-ending marks to URL / file / fragment input.
    return text.strip()


def _to_native(text: str, lang: str, engine: str, preserve_english: bool):
    output = []
    unknown = []
    provider = "AI4Bharat IndicXlit" if engine == "AI4Bharat IndicXlit" else "Offline demo lexicon"
    for token in TOKEN.findall(text):
        if not ROMAN_WORD.match(token):
            output.append(token)
            continue
        if preserve_english and token.lower() in ENGLISH_KEEP:
            output.append(token)
            continue
        if engine == "AI4Bharat IndicXlit":
            output.append(indicxlit_word(token, lang))
        else:
            match = WORDS[lang].get(token.lower())
            if match is None:
                unknown.append(token)
                output.append(token)  # explicitly preserves OOV, doesn't hallucinate conversion
            else:
                output.append(match)
    return "".join(output), provider, sorted(set(unknown), key=str.casefold)


def process(text: str, language: str="Hindi", engine: str="Offline demo lexicon",
            advanced_refine: bool=False, translate: bool=False, preserve_english: bool=True) -> Result:
    text = normalize_input(text)
    if language not in LANGUAGES:
        raise ValueError("Choose Hindi, Kannada or Tamil")
    if engine not in ("Offline demo lexicon", "AI4Bharat IndicXlit"):
        raise ValueError("Unsupported transliteration backend")
    lang = LANGUAGES[language][0]
    if not text:
        return Result(source="", language=language, native="", polished="", provider=engine)
    native, provider, unknown = _to_native(text, lang, engine, preserve_english)
    polished = polish_rules(native)
    warnings = []
    if unknown:
        warnings.append(f"{len(unknown)} out-of-vocabulary Roman word(s) were left unchanged in offline demo mode.")
    if advanced_refine:
        try:
            polished = refine_with_param1(polished, lang)
        except ModelUnavailable as exc:
            warnings.append(str(exc) + " Rule-based polish remains available.")
    english = None
    if translate:
        try:
            english = translate_to_english(polished, lang)
        except ModelUnavailable as exc:
            warnings.append(str(exc) + " English translation was not fabricated.")
    return Result(source=text, language=language, native=native,
                  polished=polished, english=english, provider=provider,
                  warnings=warnings, unknown_words=unknown)
