import csv
from pathlib import Path
from core.pipeline import process
from core.metrics import character_error_rate

DATA = Path(__file__).parents[1]/"evaluation"/"cases.csv"

def test_45_cases_and_categories():
    with open(DATA, encoding="utf-8-sig", newline="") as f:
        cases = list(csv.DictReader(f))
    assert len(cases) == 45
    assert {c["language"] for c in cases} == {"Hindi", "Kannada", "Tamil"}
    assert len({c["case_id"] for c in cases}) == len(cases)
    assert len({c["category"] for c in cases}) >= 5


def test_all_cases_can_be_scored_in_demo():
    with open(DATA, encoding="utf-8-sig", newline="") as f:
        cases = list(csv.DictReader(f))
    for c in cases:
        p = process(c["source"], c["language"]).native
        assert character_error_rate(p, c["reference"]) >= 0
