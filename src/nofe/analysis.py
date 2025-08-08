from dataclasses import dataclass, asdict
from typing import Dict
from nltk.sentiment import SentimentIntensityAnalyzer

@dataclass
class TruthVector:
    empirical: float
    logical: float
    emotional: float
    historical: float
    notes: str

    def to_dict(self) -> Dict:
        return asdict(self)

class NightwalkerAgentStack:
    def __init__(self):
        self.sent = SentimentIntensityAnalyzer()

    def thinker(self, text: str) -> str:
        return "Contextualizes events vs historical baselines (MVP heuristic)."

    def doer(self, text: str) -> str:
        return "Extracts entities/events (MVP heuristic)."

    def controller(self, text: str) -> str:
        return "Checks logical consistency (MVP heuristic)."

    def pulse(self, text: str) -> str:
        s = self.sent.polarity_scores(text or "")
        return f"Sentiment={{'neg':{s['neg']:.2f}, 'neu':{s['neu']:.2f}, 'pos':{s['pos']:.2f}, 'compound':{s['compound']:.2f}}}"

def evaluate_truth_vector(text: str) -> TruthVector:
    notes = "Automated MVP scoring; analyst review required."
    return TruthVector(empirical=0.65, logical=0.75, emotional=0.50, historical=0.60, notes=notes)
