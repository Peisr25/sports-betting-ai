"""
Configurações do sistema de apostas esportivas
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configurações gerais do sistema"""
    
    # API Football
    API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY", "")
    API_FOOTBALL_BASE_URL = "https://v3.football.api-sports.io"
    
    # Banco de dados
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database/sports_betting.db")
    
    # Servidor
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))
    
    # Modelo
    MODEL_PATH = "./models/trained_model.pkl"
    MIN_MATCHES_FOR_PREDICTION = 5  # Mínimo de jogos históricos necessários
    
    # Features para o modelo
    FEATURES = [
        "home_goals_avg",
        "away_goals_avg",
        "home_goals_conceded_avg",
        "away_goals_conceded_avg",
        "home_shots_avg",
        "away_shots_avg",
        "home_shots_on_target_avg",
        "away_shots_on_target_avg",
        "home_corners_avg",
        "away_corners_avg",
        "home_fouls_avg",
        "away_fouls_avg",
        "home_yellow_cards_avg",
        "away_yellow_cards_avg",
        "home_red_cards_avg",
        "away_red_cards_avg",
        "home_form",  # Pontos nos últimos 5 jogos
        "away_form",
        "head_to_head_home_wins",
        "head_to_head_draws",
        "head_to_head_away_wins"
    ]
    
    # Ligas suportadas (ID da API Football)
    SUPPORTED_LEAGUES = {
        "brasileirao_a": 71,
        "premier_league": 39,
        "la_liga": 140,
        "bundesliga": 78,
        "serie_a": 135,
        "ligue_1": 61
    }
    
    # Thresholds para recomendações
    HIGH_CONFIDENCE_THRESHOLD = 0.65
    MEDIUM_CONFIDENCE_THRESHOLD = 0.55
    
    # Limites de requisições API
    API_RATE_LIMIT_PER_DAY = 100  # Plano gratuito
    
config = Config()

