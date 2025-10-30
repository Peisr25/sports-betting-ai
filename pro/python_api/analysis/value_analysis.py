"""
Análise de Valor Esperado (Expected Value - EV) para apostas
"""
from typing import Dict, List


class ValueAnalyzer:
    """
    Calcula o valor esperado de apostas

    EV = (Probabilidade de Vitória × Retorno) - (Probabilidade de Perda × Stake)

    Apostas com EV positivo são teoricamente lucrativas no longo prazo.
    """

    def __init__(self, min_ev: float = 0.05, min_probability: float = 0.10):
        """
        Args:
            min_ev: EV mínimo para considerar aposta com valor (5%)
            min_probability: Probabilidade mínima para considerar (10%)
        """
        self.min_ev = min_ev
        self.min_probability = min_probability

    def calculate_ev(
        self,
        probability: float,
        odds: float,
        stake: float = 100
    ) -> Dict:
        """
        Calcula valor esperado de uma aposta

        Args:
            probability: Probabilidade real do evento (0-1)
            odds: Odd decimal da casa de apostas
            stake: Valor apostado

        Returns:
            Análise de EV
        """
        # Retorno se ganhar (inclui stake de volta)
        potential_return = odds * stake

        # Lucro se ganhar
        profit_if_win = potential_return - stake

        # Valor esperado
        ev = (probability * profit_if_win) - ((1 - probability) * stake)

        # EV percentual
        ev_percentage = (ev / stake) * 100 if stake > 0 else 0

        # Probabilidade implícita da odd
        implied_probability = 1 / odds if odds > 0 else 0

        # Margem de valor
        value_margin = probability - implied_probability

        return {
            "probability": round(probability, 4),
            "odds": round(odds, 2),
            "implied_probability": round(implied_probability, 4),
            "value_margin": round(value_margin, 4),
            "ev": round(ev, 2),
            "ev_percentage": round(ev_percentage, 2),
            "has_value": ev > 0,
            "is_good_bet": ev_percentage >= (self.min_ev * 100),
            "potential_return": round(potential_return, 2),
            "profit_if_win": round(profit_if_win, 2)
        }

    def analyze_match(
        self,
        predictions: Dict,
        odds: Dict,
        stake: float = 100
    ) -> List[Dict]:
        """
        Analisa todas as apostas de uma partida

        Args:
            predictions: Predições do modelo
            odds: Odds das casas de apostas
            stake: Valor a apostar

        Returns:
            Lista de análises ordenadas por EV
        """
        analyses = []

        # Resultado (1X2)
        result_odds = odds.get("result", {})
        result_probs = predictions.get("result", {})

        if result_odds and result_probs:
            for outcome, prob in result_probs.items():
                odd = result_odds.get(outcome)

                if odd and prob >= self.min_probability:
                    analysis = self.calculate_ev(prob, odd, stake)
                    analysis["market"] = "Resultado (1X2)"
                    analysis["bet"] = outcome
                    analyses.append(analysis)

        # Gols
        goals_odds = odds.get("goals", {})
        goals_probs = predictions.get("goals", {})

        if goals_odds and goals_probs:
            for outcome, prob in goals_probs.items():
                odd = goals_odds.get(outcome)

                if odd and prob >= self.min_probability:
                    analysis = self.calculate_ev(prob, odd, stake)
                    analysis["market"] = "Total de Gols"
                    analysis["bet"] = outcome
                    analyses.append(analysis)

        # BTTS
        btts_odds = odds.get("btts", {})
        btts_probs = predictions.get("both_teams_score", {})

        if btts_odds and btts_probs:
            for outcome, prob in btts_probs.items():
                odd = btts_odds.get(outcome)

                if odd and prob >= self.min_probability:
                    analysis = self.calculate_ev(prob, odd, stake)
                    analysis["market"] = "Ambos Marcam"
                    analysis["bet"] = outcome
                    analyses.append(analysis)

        # Ordena por EV
        analyses.sort(key=lambda x: x["ev"], reverse=True)

        return analyses

    def get_best_bets(
        self,
        analyses: List[Dict],
        top_n: int = 5
    ) -> List[Dict]:
        """
        Retorna as melhores apostas

        Args:
            analyses: Lista de análises
            top_n: Número de apostas a retornar

        Returns:
            Top N apostas por EV
        """
        # Filtra apenas apostas com valor
        good_bets = [a for a in analyses if a.get("is_good_bet", False)]

        # Ordena por EV percentual
        good_bets.sort(key=lambda x: x["ev_percentage"], reverse=True)

        return good_bets[:top_n]

    def calculate_kelly_criterion(
        self,
        probability: float,
        odds: float,
        bankroll: float = 1000,
        fractional_kelly: float = 0.25
    ) -> Dict:
        """
        Calcula stake usando Critério de Kelly

        Kelly % = (odds * probability - 1) / (odds - 1)

        Args:
            probability: Probabilidade real do evento
            odds: Odd decimal
            bankroll: Banca total
            fractional_kelly: Fração do Kelly a usar (0.25 = 25%)

        Returns:
            Análise de Kelly
        """
        if odds <= 1:
            return {
                "kelly_percentage": 0,
                "recommended_stake": 0,
                "note": "Odds inválidas"
            }

        # Calcula Kelly
        kelly_percentage = ((odds * probability) - 1) / (odds - 1)

        # Aplica fração (conservador)
        adjusted_kelly = kelly_percentage * fractional_kelly

        # Garante que não seja negativo
        adjusted_kelly = max(adjusted_kelly, 0)

        # Limita a 10% da banca
        adjusted_kelly = min(adjusted_kelly, 0.10)

        # Calcula stake recomendado
        recommended_stake = bankroll * adjusted_kelly

        return {
            "kelly_percentage": round(kelly_percentage * 100, 2),
            "adjusted_kelly_percentage": round(adjusted_kelly * 100, 2),
            "recommended_stake": round(recommended_stake, 2),
            "fraction_used": fractional_kelly,
            "bankroll": bankroll
        }


if __name__ == "__main__":
    print("=== Análise de Valor Esperado ===\n")

    analyzer = ValueAnalyzer()

    # Exemplo: Arsenal vs Chelsea
    print("Exemplo: Arsenal vs Chelsea\n")

    # Predições do modelo
    probability = 0.55  # 55% de chance do Arsenal ganhar

    # Odd da casa de apostas
    odds = 1.80  # Arsenal @1.80

    # Análise
    analysis = analyzer.calculate_ev(probability, odds, stake=100)

    print(f"Probabilidade Real: {analysis['probability']:.1%}")
    print(f"Odd: {analysis['odds']}")
    print(f"Probabilidade Implícita: {analysis['implied_probability']:.1%}")
    print(f"Margem de Valor: {analysis['value_margin']:.1%}")
    print(f"\nEV: ${analysis['ev']}")
    print(f"EV%: {analysis['ev_percentage']:.2f}%")
    print(f"Tem Valor? {'✓ SIM' if analysis['has_value'] else '✗ NÃO'}")
    print(f"Boa Aposta? {'✓ SIM' if analysis['is_good_bet'] else '✗ NÃO'}")

    # Kelly Criterion
    print("\n--- Critério de Kelly ---")
    kelly = analyzer.calculate_kelly_criterion(
        probability=probability,
        odds=odds,
        bankroll=1000,
        fractional_kelly=0.25
    )

    print(f"Kelly Original: {kelly['kelly_percentage']:.2f}%")
    print(f"Kelly Ajustado (25%): {kelly['adjusted_kelly_percentage']:.2f}%")
    print(f"Stake Recomendado: ${kelly['recommended_stake']:.2f}")
