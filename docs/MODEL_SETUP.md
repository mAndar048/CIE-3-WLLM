# Optional pretrained model setup

## A. AI4Bharat IndicXlit (real neural transliteration)

Verified API shape according to the official IndicXlit app README:
```python
from ai4bharat.transliteration import XlitEngine
model = XlitEngine("hi", beam_width=5, rescore=True)
result = model.translit_word("namaste", topk=1)
```

Preferred deployment: separate Linux Python 3.9/3.10 virtual environment (older Fairseq dependencies can fail on newest Python environments). Try:

```bash
pip install -r requirements-indicxlit.txt
streamlit run app.py
```

In the sidebar choose **AI4Bharat IndicXlit**. Its first run may download network model assets; offline first run will not succeed. If installation fails, read the [official repo](https://github.com/AI4Bharat/IndicXlit/tree/master/app) for up-to-date version compatibility. This project will show an error, not silently switch to a mock model.

## B. AI4Bharat IndicTrans2 (neural English translation)

On a Linux/macOS Python 3.10+ environment with enough disk/memory, install:

```bash
pip install -r requirements-translation.txt
```

Default checkpoint: `ai4bharat/indictrans2-indic-en-dist-200M` (distilled 200M, smaller than 1B). In UI tick **Translate to English with IndicTrans2**. A checkpoint is downloaded on first use and may be slow on CPU. Some versions of the toolkit import `IndicProcessor` through a different path; adjust per official current docs if required. The model uses `trust_remote_code=True`; review model code and only load a trusted checkpoint. More details: https://github.com/VarunGumma/IndicTransToolkit

## C. BharatGen Param-1-2.9B-Instruct (Hindi phrasing)

The public model card shows OpenAI-compatible vLLM serving. A GPU-backed environment is recommended. BharatGen lists 8 GB as a starting GPU memory guide for Param1-2.9B; practical needs depend on inference settings and concurrency.

```bash
# On a suitable Linux GPU machine with vLLM installed:
vllm serve "bharatgenai/Param-1-2.9B-Instruct"
```

In another terminal, set:
```bash
export PARAM1_API_URL=http://localhost:8000/v1/chat/completions
export PARAM1_MODEL=bharatgenai/Param-1-2.9B-Instruct
export PARAM1_API_KEY=EMPTY
streamlit run app.py
```

The app's **Improve phrasing with BharatGen Param1** switch is **Hindi only**, as specified for the instruction-tuned checkpoint. A user-controlled HTTPS model endpoint is also supported, but choose it only after checking privacy and credentials. Source: https://huggingface.co/bharatgenai/Param-1-2.9B-Instruct

## Model verification checklist
- [ ] Confirm checkpoint identifier and current model card access/licensing.
- [ ] Confirm language support and sample words for Hindi/Kannada/Tamil.
- [ ] Capture model ID, exact installed library versions, CPU/GPU and latency.
- [ ] Run and save `python evaluation/run_eval.py --mode indicxlit` output.
- [ ] Report real CER separately from offline/demo CER.
- [ ] Verify quality of edited text with a bilingual human before demo.
