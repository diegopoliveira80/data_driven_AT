from pydantic import BaseModel
from typing import Dict,List

class PlayerRequest(BaseModel):
    match_id: int
    player_name: str

class PlayerResponse(BaseModel):
    passes_completed: int
    passes_attempted: int
    shots: int
    shots_on_target: int
    fouls_committed: int
    fouls_won: int
    tackles: int
    interceptions: int
    dribbles_successful: int
    dribbles_attempted: int
    Goal: int
    Cartao_Amarelo: int
    Cartao_Vermelho: int
    

class Summaryrequest(BaseModel):
    stats_jogador1: Dict
    stats_jogador2: Dict
    escalacao: Dict
    agent_prompt: str
    
    
class SummaryResponse(BaseModel):
    result: str
    
    
class SummaryMatchRequest(BaseModel):
    partida: List
    statist: List
    escalacao: Dict
    agent_prompt: str