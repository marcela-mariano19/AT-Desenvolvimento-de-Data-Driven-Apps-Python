from fastapi import APIRouter
from ..models.football import Match, Player
from fastapi import HTTPException
from statsbombpy import sb
import google.generativeai as genai
import orjson
import os
from dotenv import load_dotenv
import json

router = APIRouter()

load_dotenv('keys.env')

@router.get("/")
async def read_root():
    return {"message": "Bem-vindo ao Football Stats!"}

@router.post("/match/raw")
async def read_raw_match(body: Match):
    try:
        events = sb.events(match_id=body.match_id)
        return orjson.loads(events.to_json(orient="records")) #Foi necessário declarar assim para conseguir exibir valores NAN
    except:
        raise HTTPException(status_code=404, detail="Partida não encontrada")
    
@router.post("/match/stats")
async def read_match_stats(body: Match):
    """
    Recebe um objeto Match e retorna um dicionário com estatísticas da partida
    """
    try:
        events = sb.events(match_id=body.match_id)
    except:
        raise HTTPException(status_code=404, detail="Partida não encontrada")
    events = sb.events(match_id=body.match_id)

    match = sb.matches(competition_id=body.competition_id, season_id=body.season_id)
    match = match[match['match_id'] == body.match_id]

    home_team = match['home_team'].values[0]
    home_score = match['home_score'].values[0]
    away_team = match['away_team'].values[0]
    away_score = match['away_score'].values[0] 
    event_goals = events[events['shot_outcome'] == 'Goal']
    list_players_goals = event_goals[['player', 'team']].to_dict('records')
    try:
        event_passes = events[events['pass_goal_assist'] == True]
        list_players_passes = event_passes[['player', 'team']].to_dict('records')
    except:
        list_players_passes = []

    
    passes = events[events['type'] == 'Pass'].shape[0]
    shots = events[events['type'] == 'Shot'].shape[0]
    dribbles = events[events['type'] == 'Dribble'].shape[0]
    ball_recoveries = events[events['type'] == 'Ball Recovery'].shape[0]
    try:
        yellow_cards = events[events['bad_behaviour_card'] == 'Yellow Card'].shape[0]
    
    except KeyError:
        yellow_cards = 0

    try:
        red_cards = events[events['bad_behaviour_card'] == 'Red Card'].shape[0]
    
    except KeyError:
        red_cards = 0

    stats = {
        "home_team": home_team,
        "home_score": int(home_score),
        "away_team": away_team,
        "away_score": int(away_score),
        "passes": int(passes),
        "shots": int(shots),
        "dribbles": int(dribbles),
        "ball_recoveries": int(ball_recoveries),
        "players_goals": list_players_goals,
        "players_passes": list_players_passes,
        "yellow_cards": int(yellow_cards),
        "red_cards": int(red_cards)
    }

    return stats




@router.post("/match/match_summary")
async def read_match(body: Match):
    """
    Recebe um objeto Match e retorna um texto com a análise da partida
    """
    if body.competition_id is None:
        raise HTTPException(status_code=400, detail="ID da competição é obrigatório")
    if body.season_id is None:
        raise HTTPException(status_code=400, detail="ID da temporada é obrigatório")
    try:
        events = sb.events(match_id=body.match_id)
    except:
        raise HTTPException(status_code=404, detail="Partida não encontrada")
    
    passes = events[events['type'] == 'Pass'].shape[0]
    
    try:
        yellow_cards = events[events['bad_behaviour_card'] == 'Yellow Card'].shape[0]
    
    except KeyError:
        yellow_cards = 0
    match = sb.matches(competition_id=body.competition_id, season_id=body.season_id)
    match = match[match['match_id'] == body.match_id]

    home_team = match['home_team'].values[0]
    home_score = match['home_score'].values[0]
    away_team = match['away_team'].values[0]
    away_score = match['away_score'].values[0] 
    event_goals = events[events['shot_outcome'] == 'Goal']
    list_players_goals = event_goals[['player', 'team']].to_dict('records')
    try:
        event_passes = events[events['pass_goal_assist'] == True]
        list_players_passes = event_passes[['player', 'team']].to_dict('records')
    except:
        list_players_passes = []

    prompt = f"""
    Você é um jornalista que precisa falar sobre a partida entre o time da casa {home_team} que fez {home_score} goals e o time visitante {away_team} que fez {away_score} goals.
    A partida teve {passes} passes e {yellow_cards} cartões amarelos. Os jogadores que fizeram gols foram: {list_players_goals}.
    Os jogadores que deram assistências foram: {list_players_passes}. Use apenas os dados fornecidos para criar um texto sobre a partida.

    Exemplo de retorno esperado:
    'O time A venceu o time B por 3 a 1. Os destaques foram os gols de João e Lucas, além de uma assistência de Ana.'
    """


    # Definir a chave de API do Gemini (use a chave fornecida pela sua conta)
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    return response.text

@router.post("/match/player_profile")
async def read_player_profile(body: Player):
    """
    Recebe um objeto Player e retorna um texto com o perfil do jogador com estatísticas como número de passes, finalizações, desarmes e minutos jogados.
    """
    #Carregando dados para uso na função
    events = sb.events(match_id=body.match_id)
    player_data = body.player_data

    player_events = events[events['player_id'] == body.player_id]

    goals = player_events[player_events['shot_outcome'] == 'Goal'].shape[0]
    passes = player_events[player_events['type'] == 'Pass'].shape[0]
    shots = player_events[player_events['type'] == 'Shot'].shape[0]
    dribbles = player_events[player_events['type'] == 'Dribble'].shape[0]
    ball_recoveries = player_events[player_events['type'] == 'Ball Recovery'].shape[0]
    try:
        yellow_cards = events[events['bad_behaviour_card'] == 'Yellow Card'].shape[0]
    except KeyError:
        yellow_cards = 0

    try:
        red_cards = events[events['bad_behaviour_card'] == 'Red Card'].shape[0]
    
    except KeyError:
        red_cards = 0



    stats_player = {
        "player_name": player_data['player_name'],
        "country": player_data['country'],
        "passes": int(passes),
        "goals": int(goals),
        "shots": int(shots),
        "dribbles": int(dribbles),
        "ball_recoveries": int(ball_recoveries),
        "yellow_cards": int(yellow_cards),
        "red_cards": int(red_cards)
    }

    return stats_player





