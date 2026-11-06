"""Run 45 human-authored sentence-pair cases; output metrics and failure rows."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from core.pipeline import process
from core.metrics import character_error_rate, word_accuracy, sentence_accuracy

DATA = Path(__file__).resolve().with_name("cases.csv")

def run(mode="demo", output=None):
    engine = "AI4Bharat IndicXlit" if mode == "indicxlit" else "Offline demo lexicon"
    with DATA.open(encoding="utf-8-sig", newline="") as f:
        cases = list(csv.DictReader(f))
    rows = []
    for c in cases:
        pred = process(c["source"], c["language"], engine).native
        rows.append({**c,"prediction":pred,
                     "cer":round(character_error_rate(pred, c["reference"]), 5),
                     "word_accuracy":round(word_accuracy(pred, c["reference"]),5),
                     "exact_match":int(sentence_accuracy(pred,c["reference"]))})
    if output:
        dest = Path(output)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f,fieldnames=list(rows[0]))
            writer.writeheader();writer.writerows(rows)
    by_lang=defaultdict(list)
    for row in rows:
        by_lang[row["language"]].append(row)
    def summary(group):
        return {"n":len(group), "mean_CER":round(sum(x["cer"] for x in group)/len(group),4),
                "word_accuracy":round(sum(x["word_accuracy"] for x in group)/len(group),4),
                "exact_match":round(sum(x["exact_match"] for x in group)/len(group),4)}
    report={"mode":mode, "timestamp_utc":datetime.now(timezone.utc).isoformat(),
            "test_set":"45 manually authored phrase/sentence cases, not a standardized Aksharantar benchmark",
            "all":summary(rows),"by_language":{k:summary(v) for k,v in sorted(by_lang.items())},
            "failures":[{"case_id":x["case_id"],"source":x["source"],"expected":x["reference"],
                         "predicted":x["prediction"],"cer":x["cer"]} for x in rows if not x["exact_match"]]}
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return report

if __name__ == "__main__":
    p=argparse.ArgumentParser();p.add_argument("--mode",choices=["demo","indicxlit"],default="demo")
    p.add_argument("--output",default="evaluation/results-demo.csv")
    a=p.parse_args();run(a.mode,a.output)
