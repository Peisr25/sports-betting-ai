"""
Módulo para processamento de dados e feature engineering
"""
import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime


class DataProcessor:
    """
    Processa dados brutos e cria features para os modelos
    """
    
    def __init__(self):
        """Inicializa o processador de dados"""
        pass
    
    def calculate_team_averages(
        self,
        matches: List[Dict],
        team_id: int,
        is_home: bool = True
    ) -> Dict[str, float]:
        """
        Calcula médias de estatísticas de um time
        
        Args:
            matches: Lista de partidas
            team_id: ID do time
            is_home: Se True, considera apenas jogos em casa
            
        Returns:
            Dicionário com médias
        """
        relevant_matches = []
        
        for match in matches:
            home_team_id = match.get("teams", {}).get("home", {}).get("id")
            away_team_id = match.get("teams", {}).get("away", {}).get("id")
            
            # Filtra por time e local
            if is_home and home_team_id == team_id:
                relevant_matches.append(match)
            elif not is_home and away_team_id == team_id:
                relevant_matches.append(match)
        
        if not relevant_matches:
            return self._get_default_averages()
        
        # Calcula médias
        goals_scored = []
        goals_conceded = []
        shots = []
        shots_on_target = []
        corners = []
        fouls = []
        yellow_cards = []
        red_cards = []
        
        for match in relevant_matches:
            if is_home:
                goals_scored.append(match.get("goals", {}).get("home", 0))
                goals_conceded.append(match.get("goals", {}).get("away", 0))
            else:
                goals_scored.append(match.get("goals", {}).get("away", 0))
                goals_conceded.append(match.get("goals", {}).get("home", 0))
            
            # Extrai estatísticas se disponíveis
            stats = match.get("statistics", {})
            if stats:
                side = "home" if is_home else "away"
                shots.append(stats.get(side, {}).get("total_shots", 0))
                shots_on_target.append(stats.get(side, {}).get("shots_on_goal", 0))
                corners.append(stats.get(side, {}).get("corners", 0))
                fouls.append(stats.get(side, {}).get("fouls", 0))
                yellow_cards.append(stats.get(side, {}).get("yellow_cards", 0))
                red_cards.append(stats.get(side, {}).get("red_cards", 0))
        
        return {
            "goals_scored_avg": np.mean(goals_scored) if goals_scored else 0,
            "goals_conceded_avg": np.mean(goals_conceded) if goals_conceded else 0,
            "shots_avg": np.mean(shots) if shots else 0,
            "shots_on_target_avg": np.mean(shots_on_target) if shots_on_target else 0,
            "corners_avg": np.mean(corners) if corners else 0,
            "fouls_avg": np.mean(fouls) if fouls else 0,
            "yellow_cards_avg": np.mean(yellow_cards) if yellow_cards else 0,
            "red_cards_avg": np.mean(red_cards) if red_cards else 0,
            "matches_played": len(relevant_matches)
        }
    
    def calculate_form(
        self,
        matches: List[Dict],
        team_id: int,
        last_n: int = 5
    ) -> int:
        """
        Calcula forma recente do time (pontos nos últimos N jogos)
        
        Args:
            matches: Lista de partidas
            team_id: ID do time
            last_n: Número de jogos a considerar
            
        Returns:
            Pontos nos últimos N jogos
        """
        points = 0
        count = 0
        
        # Ordena por data (mais recente primeiro)
        sorted_matches = sorted(
            matches,
            key=lambda x: x.get("fixture", {}).get("date", ""),
            reverse=True
        )
        
        for match in sorted_matches:
            if count >= last_n:
                break
            
            home_team_id = match.get("teams", {}).get("home", {}).get("id")
            away_team_id = match.get("teams", {}).get("away", {}).get("id")
            home_goals = match.get("goals", {}).get("home", 0)
            away_goals = match.get("goals", {}).get("away", 0)
            
            if home_team_id == team_id:
                if home_goals > away_goals:
                    points += 3
                elif home_goals == away_goals:
                    points += 1
                count += 1
            elif away_team_id == team_id:
                if away_goals > home_goals:
                    points += 3
                elif home_goals == away_goals:
                    points += 1
                count += 1
        
        return points
    
    def calculate_h2h_stats(
        self,
        h2h_matches: List[Dict],
        home_team_id: int,
        away_team_id: int
    ) -> Dict[str, int]:
        """
        Calcula estatísticas de confrontos diretos
        
        Args:
            h2h_matches: Lista de confrontos diretos
            home_team_id: ID do time da casa
            away_team_id: ID do time visitante
            
        Returns:
            Estatísticas de confrontos diretos
        """
        home_wins = 0
        draws = 0
        away_wins = 0
        
        for match in h2h_matches:
            match_home_id = match.get("teams", {}).get("home", {}).get("id")
            match_away_id = match.get("teams", {}).get("away", {}).get("id")
            home_goals = match.get("goals", {}).get("home", 0)
            away_goals = match.get("goals", {}).get("away", 0)
            
            # Determina vencedor considerando quem é casa/fora
            if match_home_id == home_team_id:
                if home_goals > away_goals:
                    home_wins += 1
                elif home_goals == away_goals:
                    draws += 1
                else:
                    away_wins += 1
            elif match_away_id == home_team_id:
                if away_goals > home_goals:
                    home_wins += 1
                elif home_goals == away_goals:
                    draws += 1
                else:
                    away_wins += 1
        
        return {
            "h2h_home_wins": home_wins,
            "h2h_draws": draws,
            "h2h_away_wins": away_wins,
            "h2h_total": len(h2h_matches)
        }
    
    def prepare_match_features(
        self,
        home_team_data: Dict,
        away_team_data: Dict,
        h2h_data: Dict
    ) -> Dict:
        """
        Prepara todas as features para uma partida
        
        Args:
            home_team_data: Dados do time da casa
            away_team_data: Dados do time visitante
            h2h_data: Dados de confrontos diretos
            
        Returns:
            Dicionário com todas as features
        """
        features = {}
        
        # Features do time da casa
        for key, value in home_team_data.items():
            features[f"home_{key}"] = value
        
        # Features do time visitante
        for key, value in away_team_data.items():
            features[f"away_{key}"] = value
        
        # Features de confronto direto
        features.update(h2h_data)
        
        return features
    
    def _get_default_averages(self) -> Dict[str, float]:
        """Retorna médias padrão quando não há dados"""
        return {
            "goals_scored_avg": 1.5,
            "goals_conceded_avg": 1.5,
            "shots_avg": 12.0,
            "shots_on_target_avg": 5.0,
            "corners_avg": 5.0,
            "fouls_avg": 12.0,
            "yellow_cards_avg": 2.0,
            "red_cards_avg": 0.1,
            "matches_played": 0
        }
    
    def calculate_league_averages(self, matches: List[Dict]) -> Dict[str, float]:
        """
        Calcula médias da liga
        
        Args:
            matches: Lista de todas as partidas da liga
            
        Returns:
            Médias da liga
        """
        total_goals = 0
        total_matches = len(matches)
        
        for match in matches:
            home_goals = match.get("goals", {}).get("home", 0)
            away_goals = match.get("goals", {}).get("away", 0)
            total_goals += home_goals + away_goals
        
        avg_goals = total_goals / total_matches if total_matches > 0 else 2.7
        
        return {
            "avg_goals_per_match": avg_goals,
            "total_matches": total_matches
        }
    
    def validate_features(self, features: Dict) -> bool:
        """
        Valida se as features estão completas
        
        Args:
            features: Dicionário de features
            
        Returns:
            True se válido, False caso contrário
        """
        required_keys = [
            "home_goals_scored_avg",
            "away_goals_scored_avg",
            "home_goals_conceded_avg",
            "away_goals_conceded_avg"
        ]
        
        for key in required_keys:
            if key not in features:
                return False
        
        return True


# Exemplo de uso
if __name__ == "__main__":
    processor = DataProcessor()
    
    # Exemplo de dados simulados
    matches = [
        {
            "teams": {"home": {"id": 1}, "away": {"id": 2}},
            "goals": {"home": 2, "away": 1},
            "fixture": {"date": "2025-10-20"},
            "statistics": {
                "home": {"total_shots": 15, "shots_on_goal": 6, "corners": 5, "fouls": 12, "yellow_cards": 2, "red_cards": 0},
                "away": {"total_shots": 10, "shots_on_goal": 4, "corners": 3, "fouls": 14, "yellow_cards": 3, "red_cards": 0}
            }
        }
    ]
    
    home_stats = processor.calculate_team_averages(matches, team_id=1, is_home=True)
    print("Estatísticas do time da casa:")
    print(home_stats)
    
    form = processor.calculate_form(matches, team_id=1)
    print(f"\nForma recente: {form} pontos")

