"""
Módulo de coleta e processamento de dados
"""
from .collector import FootballDataCollector
from .processor import DataProcessor
from .database import DatabaseManager, League, Team, Match, Prediction

__all__ = [
    "FootballDataCollector",
    "DataProcessor",
    "DatabaseManager",
    "League",
    "Team",
    "Match",
    "Prediction"
]

