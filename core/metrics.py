"""Dependency-free transliteration metrics."""
import unicodedata


def _normalize(text: str) -> str:
    return unicodedata.normalize("NFC", str(text)).strip()


def edit_distance(a: str, b: str) -> int:
    """Levenshtein edit distance in O(len(a)*len(b)) time, O(min len) memory."""
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            curr.append(min(curr[-1] + 1, prev[j] + 1, prev[j-1] + (ca != cb)))
        prev = curr
    return prev[-1]


def character_error_rate(pred: str, gold: str) -> float:
    """Levenshtein distance divided by reference character count."""
    pred, gold = _normalize(pred), _normalize(gold)
    return edit_distance(pred, gold) / max(1, len(gold))


def word_accuracy(pred: str, gold: str) -> float:
    """Aligned position exact-match rate; penalizes missing/extra tokens."""
    p, g = _normalize(pred).split(), _normalize(gold).split()
    total = max(len(p), len(g), 1)
    return sum(x == y for x, y in zip(p, g)) / total


def sentence_accuracy(pred: str, gold: str) -> float:
    return float(_normalize(pred) == _normalize(gold))
