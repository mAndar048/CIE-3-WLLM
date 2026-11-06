# BhashaWrite - Hinglish Smart Writing Assistant
**CS3235 | Mini Project 4 | CIE3 Lab | Individual submission**

> **Status:** The Streamlit app, offline demo engine, metrics, test dataset, and test suite are runnable. The real pretrained AI4Bharat/BharatGen paths are implemented as **optional integrations**; checkpoint weights are not included in this repository and have **not** been tested in the delivery environment. Offline-demo scores must not be presented as pretrained-model scores.

## Problem statement
People frequently type Hindi, Kannada, and Tamil using Roman letters. General-purpose editors are poor at converting informal spellings to native script, protecting code-mixed technical vocabulary, and providing an auditable quality measure. **BhashaWrite** accepts Roman-script text, returns native-script text, performs transparent punctuation cleanup, and can optionally improve Hindi wording with BharatGen Param1 or translate Indian-language text into English with AI4Bharat IndicTrans2.

## One-minute start (works without model downloads)

```bash
python -m venv .venv
# Linux / macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501`. Select **Offline demo lexicon**, choose language, enter text, select **Convert text**. The demo is a small hand-curated dictionary and rules, *not a learned model*. Unknown words are preserved and reported, rather than being invented.

### Command line demo & tests
```bash
python scripts/demo_cli.py "mujhe paani chahiye" --language Hindi
python -m pytest -q
python evaluation/run_eval.py --mode demo --output evaluation/results-demo.csv
```

## Actual pretrained models

| Function | Real checkpoint / library | Hardware and status |
|---|---|---|
| Native transliteration | AI4Bharat **IndicXlit** via `ai4bharat-transliteration` + `XlitEngine` | Model download on first use. Package may require a compatible Python/Fairseq environment. |
| Hindi phrasing | BharatGen **Param-1-2.9B-Instruct** | Requires local vLLM HTTP server; ~8 GB GPU listed by BharatGen. *Hindi and English* only for this instruction-tuned checkpoint. |
| English translation | AI4Bharat **IndicTrans2 Indic-English distilled 200M** | Requires extra libraries and checkpoint download; CPU possible but slow. |

**IMPORTANT:** BharatGen Param1-2.9B-Instruct is **not** advertised as a Kannada/Tamil writing model. The app disables its use for these languages rather than claiming unsupported coverage. See [Model setup](docs/MODEL_SETUP.md) for the exact optional commands and caveats. The three integrations are independently toggled.

## App capabilities
- Roman-script Hindi, Kannada, Tamil → native script.
- Preserves URLs, email addresses, times and common English technical vocabulary.
- Optional Hindi phrasing cleanup with actual BharatGen endpoint (no fabricated result when disabled).
- Optional English translation with actual IndicTrans2 checkpoint (no fabricated translation when disabled).
- Realistic provider status, warnings about OOV/installation problems, downloadable outputs.
- Built-in evaluation dashboard, CSV download, per-language test references.

## Data & reproducible evaluation
`evaluation/cases.csv` contains **45 manually composed reference cases** (15 each Hindi, Kannada, Tamil) covering greetings, education, requests, questions, code mixing, numbers, punctuation and unseen words. These are small illustrative cases, *not the official Aksharantar test corpus*. To replace them with benchmark pairs, maintain the same column schema and cite your source/license.

Metrics implemented in `core/metrics.py`:
- **CER** = Levenshtein character edit distance / reference character count (lower is better).
- **Word accuracy** = position-aligned exact token matches / max(reference token count, predicted token count) (higher is better; not WER).
- **Sentence exact match** = 1 if full normalized string equals gold string, else 0.

```
python evaluation/run_eval.py --mode demo --output evaluation/results-demo.csv
python evaluation/run_eval.py --mode indicxlit --output evaluation/results-indicxlit.csv
```

**Model evaluation is a separate procedure**: install IndicXlit, run the second command, and compare the two CSVs. Never copy demo metrics into neural performance results. The app's Evaluation tab performs the same comparison interactively.

## High-level architecture
```
Input (Streamlit)
  └── validate, normalize, tokenize
      ├── preserve English terms, email, URL and numbers
      └── [AI4Bharat IndicXlit OR explicitly named offline demo lexicon]
          └── rule-based punctuation polish
              ├── [optional BharatGen Param1-Instruct (Hindi only)]
              ├── [optional AI4Bharat IndicTrans2 -> English]
              └── UI + downloadable text + assessment CSV
```

## Repository map
```
app.py                       Streamlit interface & dashboard
core/pipeline.py             deterministic pipeline/orchestration & validation
core/providers.py            actual AI4Bharat and BharatGen integrations
core/lexicon.py              explicitly non-AI fallback
core/metrics.py              CER, word accuracy, exact match
evaluation/cases.csv         45 reference examples
evaluation/run_eval.py       reusable evaluator; writes per-case CSV
tests/                       pytest unit/integration-style validation
.github/workflows/tests.yml  continuous integration
requirements*.txt            separate lightweight & heavy model dependencies
docs/REPORT.md               structured project/report draft
docs/FAILURE_ANALYSIS.md     limitations, vulnerabilities, mitigations
docs/MODEL_SETUP.md          exact model installation instructions
docs/DEMO_SCRIPT.md          live presentation script
docs/SUBMISSION_CHECKLIST.md steps before submission
```

## Testing and what has actually been verified
- The standard-library pipeline/metrics and 45 example cases have automated tests.
- The repository includes a `pytest` suite and GitHub Actions workflow; local execution results are recorded in `docs/TEST_RUN.txt` when produced.
- **Not yet verified**: end-to-end downloads/model inference for IndicXlit/IndicTrans2/Param1, hosted deployment, uploaded GitHub repository, human evaluation on held-out unseen text. Do these before claiming fully deployed AI functionality.

## Privacy and security
Inputs are not persisted to a database. App limits each request to 1,800 characters, preserves URLs/emails as tokens, and does not automatically send text to third-party services. If a BharatGen endpoint is configured, user text is sent there by design; configure endpoint/data retention and authentication deliberately. Model prompt uses user text as untrusted content; it is *not* a guarantee against prompt injection. Do not enter confidential documents on public deployments.

## Limitations / future work
Word-level IndicXlit may produce incorrect grammar for code-mixed sentences; transliteration does not equal semantic translation. Colloquial spellings are ambiguous. Better corpus coverage requires Aksharantar; blind automatic correction can distort intent. Next steps: manual verification, benchmark expansion, caching + timeouts, higher quality morphological handling, rate limiting for public endpoints, multiple annotators.

## Research / official sources
1. [AI4Bharat IndicXlit repository and API](https://github.com/AI4Bharat/IndicXlit/tree/master/app)
2. [Aksharantar corpus](https://huggingface.co/datasets/ai4bharat/Aksharantar)
3. [AI4Bharat IndicTrans2](https://github.com/AI4Bharat/IndicTrans2)
4. [IndicTransToolkit](https://github.com/VarunGumma/IndicTransToolkit)
5. [BharatGen Param-1-2.9B-Instruct model card](https://huggingface.co/bharatgenai/Param-1-2.9B-Instruct)
6. [BharatGen model requirements](https://bharatgen.com/models/)

**Licensing:** This original project code is MIT licensed. Pretrained models, packages and datasets have **separate** respective licenses/terms; users must check those before redistributing or deploying them. No model weights or dataset assets from those sources are redistributed here.
