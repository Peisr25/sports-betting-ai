"""
Modelo de Distribuição de Poisson para previsão de gols em partidas de futebol
"""
import numpy as np
from scipy.stats import poisson
from typing import Dict, Tuple


class PoissonModel:
    """
    Implementa o modelo de Poisson para previsão de resultados de futebol.
    
    O modelo calcula a probabilidade de diferentes placares com base em:
    - Força ofensiva e defensiva dos times
    - Média de gols da liga
    - Vantagem de jogar em casa
    """
    
    def __init__(self, home_advantage: float = 1.3):
        """
        Inicializa o modelo de Poisson
        
        Args:
            home_advantage: Fator de vantagem de jogar em casa (padrão 1.3)
        """
        self.home_advantage = home_advantage
        
    def calculate_team_strength(
        self,
        team_goals_scored: float,
        team_goals_conceded: float,
        league_avg_goals: float
    ) -> Tuple[float, float]:
        """
        Calcula a força ofensiva e defensiva de um time
        
        Args:
            team_goals_scored: Média de gols marcados pelo time
            team_goals_conceded: Média de gols sofridos pelo time
            league_avg_goals: Média de gols da liga
            
        Returns:
            Tupla (força_ofensiva, força_defensiva)
        """
        attack_strength = team_goals_scored / league_avg_goals
        defense_strength = team_goals_conceded / league_avg_goals
        
        return attack_strength, defense_strength
    
    def predict_goals_expectancy(
        self,
        home_attack: float,
        home_defense: float,
        away_attack: float,
        away_defense: float,
        league_avg_goals: float
    ) -> Tuple[float, float]:
        """
        Calcula a expectativa de gols para cada time
        
        Args:
            home_attack: Força ofensiva do time da casa
            home_defense: Força defensiva do time da casa
            away_attack: Força ofensiva do time visitante
            away_defense: Força defensiva do time visitante
            league_avg_goals: Média de gols da liga
            
        Returns:
            Tupla (expectativa_gols_casa, expectativa_gols_fora)
        """
        home_goals_expectancy = (
            home_attack * away_defense * league_avg_goals * self.home_advantage
        )
        away_goals_expectancy = (
            away_attack * home_defense * league_avg_goals
        )
        
        return home_goals_expectancy, away_goals_expectancy
    
    def calculate_match_probabilities(
        self,
        home_goals_exp: float,
        away_goals_exp: float,
        max_goals: int = 10
    ) -> Dict[str, float]:
        """
        Calcula probabilidades de diferentes resultados
        
        Args:
            home_goals_exp: Expectativa de gols do time da casa
            away_goals_exp: Expectativa de gols do time visitante
            max_goals: Número máximo de gols a considerar
            
        Returns:
            Dicionário com probabilidades de diferentes mercados
        """
        # Matriz de probabilidades de placares
        score_matrix = np.zeros((max_goals + 1, max_goals + 1))
        
        for home_goals in range(max_goals + 1):
            for away_goals in range(max_goals + 1):
                score_matrix[home_goals, away_goals] = (
                    poisson.pmf(home_goals, home_goals_exp) *
                    poisson.pmf(away_goals, away_goals_exp)
                )
        
        # Probabilidades de resultado (1x2)
        home_win = np.sum(np.tril(score_matrix, -1))
        draw = np.sum(np.diag(score_matrix))
        away_win = np.sum(np.triu(score_matrix, 1))
        
        # Over/Under 2.5 gols
        over_2_5 = 0
        under_2_5 = 0
        for home_goals in range(max_goals + 1):
            for away_goals in range(max_goals + 1):
                total_goals = home_goals + away_goals
                if total_goals > 2.5:
                    over_2_5 += score_matrix[home_goals, away_goals]
                else:
                    under_2_5 += score_matrix[home_goals, away_goals]
        
        # Over/Under 1.5 gols
        over_1_5 = 0
        under_1_5 = 0
        for home_goals in range(max_goals + 1):
            for away_goals in range(max_goals + 1):
                total_goals = home_goals + away_goals
                if total_goals > 1.5:
                    over_1_5 += score_matrix[home_goals, away_goals]
                else:
                    under_1_5 += score_matrix[home_goals, away_goals]
        
        # Over/Under 3.5 gols
        over_3_5 = 0
        under_3_5 = 0
        for home_goals in range(max_goals + 1):
            for away_goals in range(max_goals + 1):
                total_goals = home_goals + away_goals
                if total_goals > 3.5:
                    over_3_5 += score_matrix[home_goals, away_goals]
                else:
                    under_3_5 += score_matrix[home_goals, away_goals]
        
        # Ambos marcam (BTTS)
        btts_yes = 0
        btts_no = 0
        for home_goals in range(max_goals + 1):
            for away_goals in range(max_goals + 1):
                if home_goals > 0 and away_goals > 0:
                    btts_yes += score_matrix[home_goals, away_goals]
                else:
                    btts_no += score_matrix[home_goals, away_goals]
        
        # Placar mais provável
        most_likely_score = np.unravel_index(
            score_matrix.argmax(), score_matrix.shape
        )
        
        return {
            "result": {
                "home_win": float(home_win),
                "draw": float(draw),
                "away_win": float(away_win)
            },
            "goals": {
                "over_1_5": float(over_1_5),
                "under_1_5": float(under_1_5),
                "over_2_5": float(over_2_5),
                "under_2_5": float(under_2_5),
                "over_3_5": float(over_3_5),
                "under_3_5": float(under_3_5),
                "btts_yes": float(btts_yes),
                "btts_no": float(btts_no)
            },
            "most_likely_score": {
                "home": int(most_likely_score[0]),
                "away": int(most_likely_score[1]),
                "probability": float(score_matrix[most_likely_score])
            },
            "expected_goals": {
                "home": float(home_goals_exp),
                "away": float(away_goals_exp),
                "total": float(home_goals_exp + away_goals_exp)
            }
        }
    
    def predict(
        self,
        home_stats: Dict[str, float],
        away_stats: Dict[str, float],
        league_avg_goals: float = 2.7
    ) -> Dict[str, float]:
        """
        Faz predição completa para uma partida
        
        Args:
            home_stats: Estatísticas do time da casa
                {
                    "goals_scored_avg": float,
                    "goals_conceded_avg": float
                }
            away_stats: Estatísticas do time visitante
                {
                    "goals_scored_avg": float,
                    "goals_conceded_avg": float
                }
            league_avg_goals: Média de gols da liga
            
        Returns:
            Dicionário com todas as probabilidades
        """
        # Calcula forças dos times
        home_attack, home_defense = self.calculate_team_strength(
            home_stats["goals_scored_avg"],
            home_stats["goals_conceded_avg"],
            league_avg_goals
        )
        
        away_attack, away_defense = self.calculate_team_strength(
            away_stats["goals_scored_avg"],
            away_stats["goals_conceded_avg"],
            league_avg_goals
        )
        
        # Calcula expectativa de gols
        home_goals_exp, away_goals_exp = self.predict_goals_expectancy(
            home_attack, home_defense,
            away_attack, away_defense,
            league_avg_goals
        )
        
        # Calcula probabilidades
        probabilities = self.calculate_match_probabilities(
            home_goals_exp, away_goals_exp
        )
        
        return probabilities


# Exemplo de uso
if __name__ == "__main__":
    model = PoissonModel()
    
    # Exemplo: Flamengo vs Palmeiras
    home_stats = {
        "goals_scored_avg": 2.1,
        "goals_conceded_avg": 0.9
    }
    
    away_stats = {
        "goals_scored_avg": 1.8,
        "goals_conceded_avg": 1.0
    }
    
    predictions = model.predict(home_stats, away_stats)
    
    print("Predições:")
    print(f"Vitória Casa: {predictions['result']['home_win']:.2%}")
    print(f"Empate: {predictions['result']['draw']:.2%}")
    print(f"Vitória Fora: {predictions['result']['away_win']:.2%}")
    print(f"\nOver 2.5 gols: {predictions['goals']['over_2_5']:.2%}")
    print(f"Ambos marcam: {predictions['goals']['btts_yes']:.2%}")
    print(f"\nPlacar mais provável: {predictions['most_likely_score']['home']}-{predictions['most_likely_score']['away']}")

