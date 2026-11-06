# Failure analysis and responsible deployment

## Test design
45 authored reference sentences across 3 languages, including code-mixed technical vocabulary, numeral/time preservation, punctuation, user requests, and OOV loanwords. The offline demo intentionally exposes limited vocabulary coverage, so low/uneven metrics are expected on unseen words. The real model must be assessed separately on the same references.

## Typical failure categories

| Category | Example | Root cause | Mitigation |
|---|---|---|---|
| Unseen English loanword | `mujhe certificate chahiye` | 'certificate' missing in demo lexicon | Use IndicXlit, enlarge benchmark/lexicon with provenance |
| Mixed protected terms | `mujhe Email chahiye` | Email intentionally preserved as English technical term, while gold transliterates it | Offer user-toggle or token-level editor |
| Orthographic alternatives | `namasthe` vs `namaste` | Roman spelling ambiguity | Top-k candidate selection and human override |
| Names | Person/place transliteration | Ambiguous pronunciation, language-specific spelling | Ask user to confirm named entities |
| Colloquial-to-formal shift | spoken Tamil `irukku` | Transliteration does not rewrite register | Separate verified language-aware editor |
| Punctuation/spacing | `namaste , duniya!!!` | Inconsistent user punctuation | Rules stage and user-editable result |
| Hallucination by LLM | Unrequested additions after polishing | Generative model may add content | Constrain prompts and review numbers/entities manually |
| Unsupported language model | Param1 for Kannada/Tamil | Model primarily Hindi/English | Guardrail disallows Param1 for other languages |
| First-run failure | No internet / incompatible Fairseq | Model downloads and transitive dependencies | Show error and document supported environment |
| Privacy / prompt injection | User embeds instructions in text to be edited | Untrusted content can redirect LLM | Structured prompting, endpoint isolation and human review |

## What the metrics mean
CER is at character level and can be >1.0; a semantic paraphrase may score badly even if useful. Word accuracy is strict position-by-position matching and is not equivalent to word error rate. Exact sentence accuracy is harsh under valid spelling variations. For an academic evaluation, report results by language/category and collect human acceptability ratings in addition to CER.

## Model-comparison protocol
1. Freeze `evaluation/cases.csv` before comparison; do not adapt the lexicon to test examples after viewing outcomes.
2. Run `--mode demo` and record mean CER/word accuracy/exact match and failed IDs.
3. Set up actual IndicXlit, run `--mode indicxlit`, and repeat.
4. Review at least five low-scoring cases per language with a fluent annotator.
5. Discuss model weaknesses without claiming the example dataset is an official corpus or representative of all dialects.
6. Only compare equally configured runs; note the default `preserve_english=True` switch.

## Ethics, security and limitations
- Do not upload private student, university or government data to an endpoint without consent.
- In the UI, a provider status identifies whether a real model or demo was used.
- There is no persistent user database or login; public deployments need rate limiting and access control.
- Translation may alter sentiment, named entities, honorifics or technical meaning. Verify consequential text manually.
- This project has a tiny, authored evaluation set rather than large-scale training/fine-tuning, which is a limitation rather than evidence of universal quality.
