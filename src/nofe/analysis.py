from dataclasses import dataclass, asdict
from typing import Dict, Tuple
from nltk.sentiment import SentimentIntensityAnalyzer

try:
    import spacy
    # Attempt to load the English model; this may fail if the model is not present.
    _NLP_MODEL = spacy.load("en_core_web_sm")
except Exception:
    # Fallback: use None if spaCy or the model is unavailable.
    _NLP_MODEL = None

@dataclass
class TruthVector:
    empirical: float
    logical: float
    emotional: float
    historical: float

    def to_dict(self) -> Dict:
        return asdict(self)

def _normalize_weights(w: Dict[str, float]) -> Dict[str, float]:
    """Normalize the weight values so they sum to 1.0, or return equal weights if no valid weights are provided."""
    total = sum(max(0.0, float(v)) for v in w.values())
    if total <= 0:
        return {"empirical": 0.25, "logical": 0.25, "emotional": 0.25, "historical": 0.25}
    return {k: max(0.0, float(v)) / total for k, v in w.items()}

# Simple heuristic scoring functions; replace these with real models as needed.
def _score_empirical(text: str) -> float:
    return 0.65

def _score_logical(text: str) -> float:
    return 0.75

def _score_emotional(text: str) -> float:
    return 0.50

def _score_historical(text: str) -> float:
    return 0.60

class NightwalkerAgentStack:
    def __init__(self):
        self.sent = SentimentIntensityAnalyzer()
        # initialize spaCy model once if available
        self.nlp = _NLP_MODEL

    def thinker(self, text: str) -> str:
        return "Contextualizes events vs historical baselines (MVP heuristic)."

    def doer(self, text: str) -> str:
        return "Extracts entities/events (MVP heuristic)."

    def controller(self, text: str) -> str:
        return "Checks logical consistency (MVP heuristic)."

    def pulse(self, text: str) -> str:
        s = self.sent.polarity_scores(text or "")
        return f"Sentiment={{'neg':{s['neg']:.2f}, 'neu':{s['neu']:.2f}, 'pos':{s['pos']:.2f}, 'compound':{s['compound']:.2f}}}"

    def extract_entities(self, text: str, max_entities: int = 5) -> list[str]:
        """
        Extract named entities from the supplied text using spaCy.
        Returns a list of the most common entities (PERSON, ORG, GPE, NORP, LOC).
        If spaCy or the language model is unavailable, returns an empty list.
        """
        if not self.nlp or not text:
            return []
        try:
            doc = self.nlp(text)
        except Exception:
            return []
        entities = []
        for ent in doc.ents:
            if ent.label_ in {"PERSON", "ORG", "GPE", "NORP", "LOC"}:
                ent_text = ent.text.strip()
                if ent_text:
                    entities.append(ent_text)
        from collections import Counter
        counter = Counter(entities)
        common = counter.most_common(max_entities)
        return [item[0] for item in common]

def evaluate_truth_vector(
    text: str,
    weights: Dict[str, float] | None = None,
    threshold: float | None = None
) -> Tuple[TruthVector, float, bool]:
    """
    Compute the TruthVector for a given text, calculate a weighted score, and
    determine whether it meets the specified threshold.
    Returns (TruthVector, weighted_score, is_above_threshold).
    """
    tv = TruthVector(
        empirical=_score_empirical(text),
        logical=_score_logical(text),
        emotional=_score_emotional(text),
        historical=_score_historical(text),
    )

    w = _normalize_weights(weights or {})
    score = (
        tv.empirical * w.get("empirical", 0.25)
        + tv.logical * w.get("logical", 0.25)
        + tv.emotional * w.get("emotional", 0.25)
        + tv.historical * w.get("historical", 0.25)
    )
    passed = threshold is not None and score >= float(threshold)
    return tv, score, passed
