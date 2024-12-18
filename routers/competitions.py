from statsbombpy import sb
from fastapi import APIRouter
import pandas as pd
import json
from copy import copy
import numpy as np
from routers.agent import get_sport_specialist_comments_about_match
from models.model import PlayerRequest, PlayerResponse
from pydantic import BaseModel


router = APIRouter()

@router.get('/competicoes/')
def get_competitions() -> str:
    return json.dumps(
        sb.competitions().to_dict(orient='records'))


@router.get('/partidas/')
def get_matches(competition_id: int, season_id: int) -> str:
    return json.dumps(
        sb.matches(competition_id=competition_id, season_id=season_id).to_dict(orient='records')
    )

    
@router.get('/escalacao/')
def get_Lineups(match_id: int):
    df = sb.lineups(match_id=match_id)
    df1=[{i: df[i].to_dict(orient='records')} for i in list(df.keys())]
    return json.dumps(df1, indent=2)


@router.get('/escalacao2/')
def get_lineups_stats(match_id: int) -> str:
    data = sb.lineups(match_id=match_id)
    data_final = copy(data)
    list_fields = ['cards', 'positions']
    for field in list_fields:
        for key, df in data.items():
            df[field] = df[field].apply(lambda v: {field: v})
            data_final[key] = df.to_dict(orient='records')
    return json.dumps(data_final, indent=2)


@router.get('/eventos/')
def get_matches(match_id: int) -> str:
    return json.dumps(
        sb.events(match_id=match_id).to_dict(orient='records'))

    
@router.get('/player_profile/')
def get_player_stats(match_id: int, player_name: str):
    events = sb.events(match_id=match_id)
    player_events = events[events['player'] == player_name]
    
    def safe_filter(df, column, condition):
        """Aplica um filtro seguro ao DataFrame, retornando False caso a coluna não exista."""
        if column in df.columns:
            return condition(df[column])
        return pd.Series([False] * len(df), index=df.index)

    stats = {
        "passes_completed": player_events[
            (safe_filter(player_events, 'type', lambda col: col == 'Pass')) &
            (safe_filter(player_events, 'pass_outcome', lambda col: col.isna()))
        ].shape[0],
        "passes_attempted": player_events[
            safe_filter(player_events, 'type', lambda col: col == 'Pass')
        ].shape[0],
        "shots": player_events[
            safe_filter(player_events, 'type', lambda col: col == 'Shot')
        ].shape[0],
        "shots_on_target": player_events[
            (safe_filter(player_events, 'type', lambda col: col == 'Shot')) &
            (safe_filter(player_events, 'shot_outcome', lambda col: col == 'On Target'))
        ].shape[0],
        "fouls_committed": player_events[
            safe_filter(player_events, 'type', lambda col: col == 'Foul Committed')
        ].shape[0],
        "fouls_won": player_events[
            safe_filter(player_events, 'type', lambda col: col == 'Foul Won')
        ].shape[0],
        "tackles": player_events[
            safe_filter(player_events, 'type', lambda col: col == 'Tackle')
        ].shape[0],
        "interceptions": player_events[
            safe_filter(player_events, 'type', lambda col: col == 'Interception')
        ].shape[0],
        "dribbles_successful": player_events[
            (safe_filter(player_events, 'type', lambda col: col == 'Dribble')) &
            (safe_filter(player_events, 'dribble_outcome', lambda col: col == 'Complete'))
        ].shape[0],
        "dribbles_attempted": player_events[
            safe_filter(player_events, 'type', lambda col: col == 'Dribble')
        ].shape[0],
        "Goal": player_events[
            safe_filter(player_events, 'shot_outcome', lambda col: col == 'Goal')
        ].shape[0],
        "Cartao Amarelo": player_events[
            safe_filter(player_events, 'foul_committed_card', lambda col: col == 'Yellow Card')
        ].shape[0],
        "Cartao Vermelho": player_events[
            safe_filter(player_events, 'foul_committed_card', lambda col: col == 'Red Card')
        ].shape[0],
    }

    return json.dumps(stats)


#@router.get('/match_summary/')
#def get_match_summary(match_details: dict, line_ups: list):
#    match_details_dict = json.loads(match_details)  # Converte match_details para uma lista de dicionários
#    line_ups_dict = json.loads(line_ups)  # Converte line_ups para um dicionário
#    return get_sport_specialist_comments_about_match(match_details_dict,line_ups_dict) 