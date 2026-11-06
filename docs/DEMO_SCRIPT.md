# 3-minute live project presentation

**0:00-0:25: Problem** - Many students type in Roman Hindi/Kannada/Tamil. A direct transliteration tool needs to preserve code-mixed words and show measurable quality.

**0:25-0:55: Architecture** - Streamlit UI → secure normalization/tokenization → IndicXlit or clearly labeled offline demo → punctuation cleanup → optional Param1 Hindi editor → optional IndicTrans2 English translator.

**0:55-1:40: Live demo** - Start `streamlit run app.py`. Switch Hindi/Tamil/Kannada. Enter `mujhe paani chahiye`, `namaskara nanna hesaru`, and `enakku thanni venum`. Show output, warning behavior, and download. Explicitly mention which provider is selected.

**1:40-2:20: Evaluation** - Evaluation tab has 45 reference cases; run offline evaluation and show mean CER, word accuracy, exact match. Show OOV examples and explain why demo scores are not AI model benchmark scores.

**2:20-2:45: Limitations** - Roman spelling ambiguity, unseen words, loanwords, training distribution, data privacy, GPU constraints, unsupported Param1 languages.

**2:45-3:00: Conclusion** - Modular model adapters, exact measurable errors, repeatable tests, open source code, human-review recommendations.

**Quick viva answers:**
- Transliteration preserves approximate sound/script; translation changes language/meaning.
- CER = Levenshtein character edits / reference char length.
- IndicXlit handles transliteration, IndicTrans2 translation, Param1 editing (only Hindi/English checkpoint).
- `XlitEngine` word-level inference can produce sentence-level grammatical errors.
- Unseen terms are preserved in the offline demo so the app never invents a native result.
