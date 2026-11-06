"""CS3235: Streamlit frontend for Hinglish Smart Writing Assistant."""
from pathlib import Path
import io
import streamlit as st
import pandas as pd

from core.lexicon import LANGUAGES, EXAMPLES
from core.metrics import character_error_rate, word_accuracy
from core.pipeline import process, MAX_CHARS
from core.providers import ModelUnavailable

st.set_page_config(page_title="BhashaWrite | Hinglish Smart Writer", page_icon="✍️",
                   layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>
.block-container {max-width: 1160px; padding-top: 2rem}
.stApp {background: linear-gradient(165deg,#f8f9fc 0%,#fffaf1 100%)}
.hero {background:#17344d; padding:24px 28px; border-radius:18px;color:#fff; margin-bottom:22px}
.hero h1 {color:#fff; margin:0;font-size:2.0rem}
.hero p {color:#dfeffb;margin:9px 0 0}
.box {background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:14px}
.small {color:#6b7280;font-size:0.85rem}
</style>""", unsafe_allow_html=True)
st.markdown('''<div class="hero"><h1>✍️ BhashaWrite</h1>
<p>Roman-script Indian language → native script → clearer writing → optional English translation<br>
CS3235 Mini Project 4 · AI4Bharat IndicXlit + IndicTrans2 · Optional BharatGen Param1</p></div>''',
unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Settings")
    language = st.selectbox("Target language", list(LANGUAGES))
    engine = st.radio("Transliteration provider", ["Offline demo lexicon", "AI4Bharat IndicXlit"],
                      help="Offline demo works without downloads. Select IndicXlit for real AI4Bharat inference.")
    preserve = st.checkbox("Keep common English technical terms", value=True)
    refine = st.checkbox("Improve phrasing with BharatGen Param1", value=False,
                         help="Hindi/English only. Requires a separately running Param1 vLLM endpoint and PARAM1_API_URL.")
    translate = st.checkbox("Translate to English with IndicTrans2", value=False,
                            help="Requires local IndicTrans2 model dependencies and checkpoint download.")
    st.divider()
    st.caption("**Provider transparency:** Offline demo uses only a small manually curated lexicon and punctuation rules. It is not a trained model. Neural features use actual checkpoints when installed.")
    st.caption("No user text is stored by this app. External endpoints may have their own data policies.")

converter, testing, architecture = st.tabs(["✍️ Writer", "📊 Evaluation", "📚 Project info"])
with converter:
    st.subheader("Write naturally in Roman script")
    example = EXAMPLES[LANGUAGES[language][0]]
    text = st.text_area("Input", value=example, height=130, max_chars=MAX_CHARS,
                        placeholder="Example: namaste mujhe kal class jaana hai")
    col_run, col_count = st.columns([1,5])
    with col_run:
        clicked = st.button("✨ Convert text", use_container_width=True, type="primary")
    with col_count:
        st.caption(f"{len(text)} / {MAX_CHARS} characters")
    if clicked:
        try:
            with st.spinner("Processing with the selected backend..."):
                st.session_state["last_result"] = process(text, language, engine,
                                                         advanced_refine=refine,
                                                         translate=translate,
                                                         preserve_english=preserve)
        except (ModelUnavailable, ValueError) as exc:
            st.error(str(exc))
            st.session_state.pop("last_result", None)
        except Exception as exc:
            st.error(f"Unexpected processing error: {type(exc).__name__}: {exc}")
            st.session_state.pop("last_result", None)
    if "last_result" in st.session_state:
        result = st.session_state["last_result"]
        st.caption(f"Backend used: **{result.provider}**")
        left, right = st.columns(2, gap="large")
        with left:
            st.markdown("#### Native-script transliteration")
            st.code(result.native, language=None)
        with right:
            st.markdown("#### Polished text")
            st.code(result.polished, language=None)
        if result.english is not None:
            st.markdown("#### English translation")
            st.info(result.english)
        for msg in result.warnings:
            st.warning(msg)
        st.download_button("⬇️ Download result (.txt)",
                           data=("Source: " + result.source + "\nNative: " + result.native +
                                 "\nPolished: " + result.polished +
                                 "\nEnglish: " + (result.english or "not available") + "\n"),
                           file_name="bhashawrite_output.txt", mime="text/plain")

with testing:
    st.subheader("45 curated test cases & reproducible metrics")
    st.markdown("Compare generated native-script text with a human-authored reference. "
                "**CER** = character edits ÷ reference length; **word accuracy** uses position-aligned exact tokens.")
    dataset = Path(__file__).parent / "evaluation" / "cases.csv"
    if dataset.exists():
        df = pd.read_csv(dataset).fillna("")
        st.dataframe(df[["case_id", "language", "category", "source", "reference"]],
                     hide_index=True, use_container_width=True, height=300)
        st.download_button("Download reference test cases", dataset.read_bytes(),
                           file_name="cases.csv", mime="text/csv")
        mode = st.selectbox("Evaluate", ["Offline demo lexicon", "AI4Bharat IndicXlit"], key="ev_mode")
        if st.button("Run all 45 test cases"):
            reports = []
            try:
                with st.spinner("Evaluating..."):
                    for _, case in df.iterrows():
                        pred = process(case.source, case.language, mode).native
                        reports.append({"case_id":case.case_id, "language":case.language,
                                        "category":case.category, "source":case.source,
                                        "reference":case.reference, "prediction":pred,
                                        "cer":character_error_rate(pred, case.reference),
                                        "word_accuracy":word_accuracy(pred, case.reference),
                                        "exact":int(pred == case.reference)})
                res_df = pd.DataFrame(reports)
                st.session_state["evaluation"] = res_df
            except ModelUnavailable as exc:
                st.error(str(exc))
        if "evaluation" in st.session_state:
            res_df = st.session_state["evaluation"]
            c1,c2,c3 = st.columns(3)
            c1.metric("Mean CER ↓", f"{res_df.cer.mean():.3f}")
            c2.metric("Word accuracy ↑", f"{res_df.word_accuracy.mean():.1%}")
            c3.metric("Exact match ↑", f"{res_df.exact.mean():.1%}")
            st.dataframe(res_df, hide_index=True, use_container_width=True, height=350)
            st.download_button("⬇️ Download scored results",res_df.to_csv(index=False).encode("utf-8-sig"),
                               file_name="evaluation_results.csv", mime="text/csv")
    else:
        st.error("Missing evaluation/cases.csv")

with architecture:
    st.subheader("Architecture and evaluation design")
    st.markdown('''
**Task:** Preserve a user's meaning while transliterating Romanized Hindi, Kannada or Tamil into native script.

**Pipeline:** Roman input → tokenize / preserve URLs & codes → AI4Bharat IndicXlit (or clearly labeled offline demo) → punctuation cleanup → optional BharatGen Param1 rewriting (Hindi only) → optional AI4Bharat IndicTrans2 English translation → result & download.

**AI4Bharat integration:** IndicXlit `XlitEngine.translit_word`; IndicTrans2 `IndicProcessor`, tokenizer and encoder-decoder. **BharatGen integration:** Param1-2.9B-Instruct via local vLLM server. All models are optional installs; the app explicitly reports when unavailable.

**Assessment:** 45 test cases, mean CER, word accuracy, exact match, per-language breakdown, failure analysis. `pytest` unit and security/boundary tests.

**Limitations:** Roman-script ambiguity, code-switching, unseen words, inflection errors, language mixing, domain terminology, CPU/GPU resources. Offline demo is intentionally limited.

See README.md, docs/REPORT.md, docs/FAILURE_ANALYSIS.md, docs/MODEL_SETUP.md.
''')
