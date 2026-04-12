import chess
from math import floor

def score_round(score: float) -> int:
    """Rounds [n.5, n+1) up to n+1; rounds (-(n+1), -n.5) down to -(n+1)"""
    return floor(score + 0.5)

def to_color(color_name: str) -> chess.Color:
    if color_name == "white":
        return chess.WHITE
    else:
        return chess.BLACK
    
def str_to_bool(string:str) -> bool:
    return string.lower() in ("true", "yes", "on", "1")