from pydantic import BaseModel

class Match(BaseModel):
    match_id: int
    competition_id: int = None
    season_id: int = None

class Player(BaseModel):
    player_id: int
    match_id: int
    player_data: dict