"""
Modelo Ensemble que combina Poisson e ML para melhores predições
"""
from typing import Dict
import numpy as np
from .poisson import PoissonModel
from .ml_model import MLBettingModel


class EnsembleModel:
    """
    Combina predições de Poisson e ML para obter resultados mais robustos
    """
    
    def __init__(
        self,
        poisson_weight: float = 0.4,
        ml_weight: float = 0.6
    ):
        """
        Inicializa o modelo ensemble
        
        Args:
            poisson_weight: Peso do modelo Poisson (0-1)
            ml_weight: Peso do modelo ML (0-1)
        """
        if abs(poisson_weight + ml_weight - 1.0) > 0.001:
            raise ValueError("Pesos devem somar 1.0")
        
        self.poisson_weight = poisson_weight
        self.ml_weight = ml_weight
        
        self.poisson_model = PoissonModel()
        self.ml_model = MLBettingModel()
    
    def combine_probabilities(
        self,
        poisson_probs: Dict,
        ml_probs: Dict
    ) -> Dict:
        """
        Combina probabilidades dos dois modelos
        
        Args:
            poisson_probs: Probabilidades do modelo Poisson
            ml_probs: Probabilidades do modelo ML
            
        Returns:
            Probabilidades combinadas
        """
        combined = {}
        
        # Combina resultado (1x2)
        if "result" in poisson_probs and "result" in ml_probs:
            combined["result"] = {
                "home_win": (
                    self.poisson_weight * poisson_probs["result"]["home_win"] +
                    self.ml_weight * ml_probs["result"]["home_win"]
                ),
                "draw": (
                    self.poisson_weight * poisson_probs["result"]["draw"] +
                    self.ml_weight * ml_probs["result"]["draw"]
                ),
                "away_win": (
                    self.poisson_weight * poisson_probs["result"]["away_win"] +
                    self.ml_weight * ml_probs["result"]["away_win"]
                )
            }
        
        # Combina Over/Under 2.5
        if "goals" in poisson_probs and "over_2_5" in ml_probs:
            combined["over_2_5"] = (
                self.poisson_weight * poisson_probs["goals"]["over_2_5"] +
                self.ml_weight * ml_probs["over_2_5"]
            )
            combined["under_2_5"] = (
                self.poisson_weight * poisson_probs["goals"]["under_2_5"] +
                self.ml_weight * ml_probs.get("under_2_5", 1 - ml_probs["over_2_5"])
            )
        
        # Combina BTTS
        if "goals" in poisson_probs and "btts_yes" in ml_probs:
            combined["btts_yes"] = (
                self.poisson_weight * poisson_probs["goals"]["btts_yes"] +
                self.ml_weight * ml_probs["btts_yes"]
            )
            combined["btts_no"] = (
                self.poisson_weight * poisson_probs["goals"]["btts_no"] +
                self.ml_weight * ml_probs.get("btts_no", 1 - ml_probs["btts_yes"])
            )
        
        # Adiciona predições exclusivas do ML
        ml_only_markets = [
            "over_3_5_cards", "under_3_5_cards",
            "over_9_5_corners", "under_9_5_corners",
            "over_25_fouls", "under_25_fouls"
        ]
        
        for market in ml_only_markets:
            if market in ml_probs:
                combined[market] = ml_probs[market]
        
        # Adiciona informações do Poisson
        if "expected_goals" in poisson_probs:
            combined["expected_goals"] = poisson_probs["expected_goals"]
        
        if "most_likely_score" in poisson_probs:
            combined["most_likely_score"] = poisson_probs["most_likely_score"]
        
        return combined
    
    def predict(
        self,
        home_stats: Dict,
        away_stats: Dict,
        match_data: Dict,
        league_avg_goals: float = 2.7
    ) -> Dict:
        """
        Faz predição usando ensemble
        
        Args:
            home_stats: Estatísticas do time da casa para Poisson
            away_stats: Estatísticas do time visitante para Poisson
            match_data: Dados completos da partida para ML
            league_avg_goals: Média de gols da liga
            
        Returns:
            Predições combinadas
        """
        # Predições Poisson
        poisson_predictions = self.poisson_model.predict(
            home_stats, away_stats, league_avg_goals
        )
        
        # Predições ML (se modelo estiver treinado)
        ml_predictions = {}
        try:
            ml_predictions = self.ml_model.predict_all_markets(match_data)
        except ValueError:
            # Se ML não estiver treinado, usa apenas Poisson
            print("Aviso: Modelo ML não treinado, usando apenas Poisson")
            return poisson_predictions
        
        # Combina predições
        combined_predictions = self.combine_probabilities(
            poisson_predictions,
            ml_predictions
        )
        
        # Adiciona metadados
        combined_predictions["model_info"] = {
            "poisson_weight": self.poisson_weight,
            "ml_weight": self.ml_weight,
            "models_used": ["poisson", "ml"]
        }
        
        return combined_predictions
    
    def load_ml_models(self, directory: str):
        """
        Carrega modelos ML treinados
        
        Args:
            directory: Diretório dos modelos
        """
        self.ml_model.load_models(directory)
    
    def get_confidence_level(self, probability: float) -> str:
        """
        Retorna nível de confiança baseado na probabilidade
        
        Args:
            probability: Probabilidade (0-1)
            
        Returns:
            Nível de confiança (Muito Alta, Alta, Média, Baixa)
        """
        if probability >= 0.70:
            return "Muito Alta"
        elif probability >= 0.60:
            return "Alta"
        elif probability >= 0.50:
            return "Média"
        else:
            return "Baixa"
    
    def generate_recommendations(
        self,
        predictions: Dict,
        min_confidence: float = 0.55
    ) -> list:
        """
        Gera recomendações de apostas baseadas nas predições
        
        Args:
            predictions: Predições do ensemble
            min_confidence: Confiança mínima para recomendar
            
        Returns:
            Lista de recomendações
        """
        recommendations = []
        
        # Analisa resultado
        if "result" in predictions:
            result = predictions["result"]
            max_prob = max(result.values())
            if max_prob >= min_confidence:
                outcome = max(result, key=result.get)
                outcome_names = {
                    "home_win": "Vitória do Time da Casa",
                    "draw": "Empate",
                    "away_win": "Vitória do Time Visitante"
                }
                recommendations.append({
                    "market": "Resultado Final (1x2)",
                    "bet": outcome_names[outcome],
                    "probability": result[outcome],
                    "confidence": self.get_confidence_level(result[outcome]),
                    "reasoning": f"Probabilidade de {result[outcome]:.1%}"
                })
        
        # Analisa Over/Under 2.5
        if "over_2_5" in predictions and predictions["over_2_5"] >= min_confidence:
            recommendations.append({
                "market": "Total de Gols",
                "bet": "Over 2.5 Gols",
                "probability": predictions["over_2_5"],
                "confidence": self.get_confidence_level(predictions["over_2_5"]),
                "reasoning": f"Expectativa de {predictions.get('expected_goals', {}).get('total', 0):.1f} gols"
            })
        elif "under_2_5" in predictions and predictions["under_2_5"] >= min_confidence:
            recommendations.append({
                "market": "Total de Gols",
                "bet": "Under 2.5 Gols",
                "probability": predictions["under_2_5"],
                "confidence": self.get_confidence_level(predictions["under_2_5"]),
                "reasoning": f"Expectativa de {predictions.get('expected_goals', {}).get('total', 0):.1f} gols"
            })
        
        # Analisa BTTS
        if "btts_yes" in predictions and predictions["btts_yes"] >= min_confidence:
            recommendations.append({
                "market": "Ambos Marcam",
                "bet": "Sim",
                "probability": predictions["btts_yes"],
                "confidence": self.get_confidence_level(predictions["btts_yes"]),
                "reasoning": "Ambos times têm bom ataque"
            })
        
        # Analisa Cartões
        if "over_3_5_cards" in predictions and predictions["over_3_5_cards"] >= min_confidence:
            recommendations.append({
                "market": "Total de Cartões",
                "bet": "Over 3.5 Cartões",
                "probability": predictions["over_3_5_cards"],
                "confidence": self.get_confidence_level(predictions["over_3_5_cards"]),
                "reasoning": "Histórico de muitos cartões"
            })
        
        # Analisa Escanteios
        if "over_9_5_corners" in predictions and predictions["over_9_5_corners"] >= min_confidence:
            recommendations.append({
                "market": "Total de Escanteios",
                "bet": "Over 9.5 Escanteios",
                "probability": predictions["over_9_5_corners"],
                "confidence": self.get_confidence_level(predictions["over_9_5_corners"]),
                "reasoning": "Times com alta média de escanteios"
            })
        
        # Analisa Faltas
        if "over_25_fouls" in predictions and predictions["over_25_fouls"] >= min_confidence:
            recommendations.append({
                "market": "Total de Faltas",
                "bet": "Over 25 Faltas",
                "probability": predictions["over_25_fouls"],
                "confidence": self.get_confidence_level(predictions["over_25_fouls"]),
                "reasoning": "Jogo com tendência a muitas faltas"
            })
        
        # Ordena por probabilidade
        recommendations.sort(key=lambda x: x["probability"], reverse=True)
        
        return recommendations


# Exemplo de uso
if __name__ == "__main__":
    ensemble = EnsembleModel()
    
    # Dados para Poisson
    home_stats = {
        "goals_scored_avg": 2.1,
        "goals_conceded_avg": 0.9
    }
    
    away_stats = {
        "goals_scored_avg": 1.8,
        "goals_conceded_avg": 1.0
    }
    
    # Dados completos para ML
    match_data = {
        "home_goals_avg": 2.1,
        "away_goals_avg": 1.8,
        "home_goals_conceded_avg": 0.9,
        "away_goals_conceded_avg": 1.0,
        "home_shots_avg": 15.2,
        "away_shots_avg": 13.5,
        "home_shots_on_target_avg": 6.1,
        "away_shots_on_target_avg": 5.3,
        "home_corners_avg": 5.8,
        "away_corners_avg": 5.2,
        "home_fouls_avg": 12.3,
        "away_fouls_avg": 13.1,
        "home_yellow_cards_avg": 2.1,
        "away_yellow_cards_avg": 2.3,
        "home_red_cards_avg": 0.1,
        "away_red_cards_avg": 0.1,
        "home_form": 12,
        "away_form": 10,
        "h2h_home_wins": 3,
        "h2h_draws": 1,
        "h2h_away_wins": 1
    }
    
    # Predição (usará apenas Poisson se ML não estiver treinado)
    predictions = ensemble.predict(home_stats, away_stats, match_data)
    
    print("Predições Ensemble:")
    print(f"Vitória Casa: {predictions['result']['home_win']:.2%}")
    print(f"Empate: {predictions['result']['draw']:.2%}")
    print(f"Vitória Fora: {predictions['result']['away_win']:.2%}")
    
    # Gera recomendações
    recommendations = ensemble.generate_recommendations(predictions)
    
    print("\nRecomendações:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['market']} - {rec['bet']}")
        print(f"   Probabilidade: {rec['probability']:.1%}")
        print(f"   Confiança: {rec['confidence']}")
        print(f"   Motivo: {rec['reasoning']}\n")

