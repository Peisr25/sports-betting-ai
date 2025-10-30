"""
Modelo de predição usando distribuição de Poisson
"""
import math
from typing import Dict, List


class PoissonModel:
    """
    Modelo de predição baseado em distribuição de Poisson

    A distribuição de Poisson é ideal para modelar eventos raros e independentes,
    como gols em uma partida de futebol.

    P(X = k) = (λ^k * e^(-λ)) / k!

    Onde:
    - λ (lambda) é a média de gols esperados
    - k é o número de gols
    - e é a constante de Euler
    """

    def __init__(self):
        """Inicializa o modelo de Poisson"""
        self.max_goals = 10  # Máximo de gols a considerar nas probabilidades

    def poisson_probability(self, k: int, lambda_param: float) -> float:
        """
        Calcula a probabilidade de Poisson para k eventos

        Args:
            k: Número de eventos (gols)
            lambda_param: Taxa média de eventos

        Returns:
            Probabilidade de ocorrer exatamente k eventos
        """
        if lambda_param <= 0:
            return 0.0

        return (lambda_param ** k) * math.exp(-lambda_param) / math.factorial(k)

    def predict_match(
        self,
        home_attack: float,
        away_attack: float,
        home_defense: float = None,
        away_defense: float = None
    ) -> Dict:
        """
        Prediz resultado de uma partida usando Poisson

        Args:
            home_attack: Média de gols marcados pelo time da casa
            away_attack: Média de gols marcados pelo time visitante
            home_defense: Média de gols sofridos pelo time da casa (opcional)
            away_defense: Média de gols sofridos pelo time visitante (opcional)

        Returns:
            Dicionário com predições de todos os mercados
        """
        # Ajusta lambda considerando defesa se disponível
        if home_defense is not None and away_defense is not None:
            # Fator casa: time da casa tem vantagem de ~0.3 gols
            home_lambda = (home_attack + away_defense) / 2 + 0.15
            away_lambda = (away_attack + home_defense) / 2 - 0.15
        else:
            # Sem dados de defesa, usa apenas ataque com fator casa
            home_lambda = home_attack + 0.15
            away_lambda = away_attack - 0.15

        # Garante valores mínimos positivos
        home_lambda = max(home_lambda, 0.5)
        away_lambda = max(away_lambda, 0.5)

        # Calcula probabilidades de gols
        home_probs = [self.poisson_probability(i, home_lambda) for i in range(self.max_goals)]
        away_probs = [self.poisson_probability(i, away_lambda) for i in range(self.max_goals)]

        # Predições de resultado (1X2)
        result_probs = self._calculate_result_probabilities(home_probs, away_probs)

        # Predições de total de gols
        goals_probs = self._calculate_goals_probabilities(home_probs, away_probs)

        # Predições de ambos marcam
        btts_probs = self._calculate_btts_probabilities(home_probs, away_probs)

        # Predições de escanteios (estimativa baseada em gols)
        corners_probs = self._calculate_corners_probabilities(home_lambda, away_lambda)

        # Predições de cartões (estimativa baseada em gols)
        cards_probs = self._calculate_cards_probabilities(home_lambda, away_lambda)

        # Placar mais provável
        most_likely_score = self._calculate_most_likely_score(home_probs, away_probs)

        return {
            "model": "Poisson Distribution",
            "lambdas": {
                "home": round(home_lambda, 2),
                "away": round(away_lambda, 2)
            },
            "result": result_probs,
            "goals": goals_probs,
            "both_teams_score": btts_probs,
            "corners": corners_probs,
            "cards": cards_probs,
            "most_likely_score": most_likely_score
        }

    def _calculate_result_probabilities(
        self,
        home_probs: List[float],
        away_probs: List[float]
    ) -> Dict:
        """Calcula probabilidades de resultado (1X2)"""
        home_win = 0.0
        draw = 0.0
        away_win = 0.0

        for home_goals in range(self.max_goals):
            for away_goals in range(self.max_goals):
                prob = home_probs[home_goals] * away_probs[away_goals]

                if home_goals > away_goals:
                    home_win += prob
                elif home_goals == away_goals:
                    draw += prob
                else:
                    away_win += prob

        # Normaliza para somar 100%
        total = home_win + draw + away_win
        if total > 0:
            home_win /= total
            draw /= total
            away_win /= total

        return {
            "home_win": round(home_win, 3),
            "draw": round(draw, 3),
            "away_win": round(away_win, 3)
        }

    def _calculate_goals_probabilities(
        self,
        home_probs: List[float],
        away_probs: List[float]
    ) -> Dict:
        """Calcula probabilidades de total de gols"""
        over_05 = 0.0
        over_15 = 0.0
        over_25 = 0.0
        over_35 = 0.0
        over_45 = 0.0

        for home_goals in range(self.max_goals):
            for away_goals in range(self.max_goals):
                prob = home_probs[home_goals] * away_probs[away_goals]
                total_goals = home_goals + away_goals

                if total_goals > 0.5:
                    over_05 += prob
                if total_goals > 1.5:
                    over_15 += prob
                if total_goals > 2.5:
                    over_25 += prob
                if total_goals > 3.5:
                    over_35 += prob
                if total_goals > 4.5:
                    over_45 += prob

        return {
            "over_0.5": round(over_05, 3),
            "under_0.5": round(1 - over_05, 3),
            "over_1.5": round(over_15, 3),
            "under_1.5": round(1 - over_15, 3),
            "over_2.5": round(over_25, 3),
            "under_2.5": round(1 - over_25, 3),
            "over_3.5": round(over_35, 3),
            "under_3.5": round(1 - over_35, 3),
            "over_4.5": round(over_45, 3),
            "under_4.5": round(1 - over_45, 3),
        }

    def _calculate_btts_probabilities(
        self,
        home_probs: List[float],
        away_probs: List[float]
    ) -> Dict:
        """Calcula probabilidades de ambos marcam"""
        # P(Ambos marcam) = 1 - P(Casa não marca) - P(Fora não marca) + P(Ninguém marca)
        home_no_goal = home_probs[0]
        away_no_goal = away_probs[0]

        btts_no = home_no_goal + away_no_goal - (home_no_goal * away_no_goal)
        btts_yes = 1 - btts_no

        return {
            "yes": round(btts_yes, 3),
            "no": round(btts_no, 3)
        }

    def _calculate_corners_probabilities(
        self,
        home_lambda: float,
        away_lambda: float
    ) -> Dict:
        """
        Estima probabilidades de escanteios baseado em gols

        Correlação típica: ~10-11 escanteios por partida
        Times mais ofensivos geram mais escanteios
        """
        # Estima escanteios baseado em ataque (correlação aproximada)
        corners_lambda = (home_lambda + away_lambda) * 4.5

        over_75 = sum(self.poisson_probability(k, corners_lambda) for k in range(8, 20))
        over_85 = sum(self.poisson_probability(k, corners_lambda) for k in range(9, 20))
        over_95 = sum(self.poisson_probability(k, corners_lambda) for k in range(10, 20))
        over_105 = sum(self.poisson_probability(k, corners_lambda) for k in range(11, 20))

        return {
            "over_7.5": round(over_75, 3),
            "under_7.5": round(1 - over_75, 3),
            "over_8.5": round(over_85, 3),
            "under_8.5": round(1 - over_85, 3),
            "over_9.5": round(over_95, 3),
            "under_9.5": round(1 - over_95, 3),
            "over_10.5": round(over_105, 3),
            "under_10.5": round(1 - over_105, 3),
        }

    def _calculate_cards_probabilities(
        self,
        home_lambda: float,
        away_lambda: float
    ) -> Dict:
        """
        Estima probabilidades de cartões baseado em gols

        Correlação típica: ~3-4 cartões por partida
        Jogos mais intensos tendem a ter mais cartões
        """
        # Estima cartões baseado em intensidade do jogo
        cards_lambda = (home_lambda + away_lambda) * 1.5

        over_25 = sum(self.poisson_probability(k, cards_lambda) for k in range(3, 15))
        over_35 = sum(self.poisson_probability(k, cards_lambda) for k in range(4, 15))
        over_45 = sum(self.poisson_probability(k, cards_lambda) for k in range(5, 15))

        return {
            "over_2.5": round(over_25, 3),
            "under_2.5": round(1 - over_25, 3),
            "over_3.5": round(over_35, 3),
            "under_3.5": round(1 - over_35, 3),
            "over_4.5": round(over_45, 3),
            "under_4.5": round(1 - over_45, 3),
        }

    def _calculate_most_likely_score(
        self,
        home_probs: List[float],
        away_probs: List[float]
    ) -> Dict:
        """Calcula o placar mais provável"""
        max_prob = 0.0
        most_likely = {"home": 0, "away": 0}

        for home_goals in range(self.max_goals):
            for away_goals in range(self.max_goals):
                prob = home_probs[home_goals] * away_probs[away_goals]

                if prob > max_prob:
                    max_prob = prob
                    most_likely = {"home": home_goals, "away": away_goals}

        return {
            "score": f"{most_likely['home']}-{most_likely['away']}",
            "probability": round(max_prob, 3)
        }


# Exemplo de uso
if __name__ == "__main__":
    model = PoissonModel()

    print("=== Modelo de Poisson - Exemplo ===\n")

    # Exemplo: Arsenal (casa) vs Chelsea (fora)
    # Arsenal: 2.1 gols/jogo em casa, sofre 1.0 gols/jogo
    # Chelsea: 1.8 gols/jogo fora, sofre 1.2 gols/jogo
    print("Predição: Arsenal vs Chelsea\n")

    predictions = model.predict_match(
        home_attack=2.1,
        away_attack=1.8,
        home_defense=1.0,
        away_defense=1.2
    )

    print(f"Lambda Casa: {predictions['lambdas']['home']}")
    print(f"Lambda Fora: {predictions['lambdas']['away']}\n")

    print("Resultado (1X2):")
    print(f"  Casa: {predictions['result']['home_win']:.1%}")
    print(f"  Empate: {predictions['result']['draw']:.1%}")
    print(f"  Fora: {predictions['result']['away_win']:.1%}\n")

    print("Total de Gols:")
    print(f"  Over 2.5: {predictions['goals']['over_2.5']:.1%}")
    print(f"  Under 2.5: {predictions['goals']['under_2.5']:.1%}\n")

    print("Ambos Marcam:")
    print(f"  Sim: {predictions['both_teams_score']['yes']:.1%}")
    print(f"  Não: {predictions['both_teams_score']['no']:.1%}\n")

    print(f"Placar Mais Provável: {predictions['most_likely_score']['score']}")
    print(f"Probabilidade: {predictions['most_likely_score']['probability']:.1%}")
