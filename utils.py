from math import floor

def score_round(score: float) -> int:
    """Rounds [n.5, n+1) up to n+1; rounds (-(n+1), -n.5) down to -(n+1)"""
    return floor(score + 0.5)