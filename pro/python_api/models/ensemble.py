"""
Sistema Ensemble - Combina múltiplos modelos de predição
NOVO: Suporta predições da API-Football!
"""
from typing import Dict, List, Optional
import numpy as np
from .poisson import PoissonModel
from .xgboost_model import XGBoostModel


class APIFootballModel:
    """
    Wrapper para predições da API-Football
    Permite usar predições da API como um "modelo" no ensemble
    """

    def __init__(self, database):
        """
        Args:
            database: Instância do Database (database_v2.py)
        """
        self.db = database
        self.is_trained = True  # Sempre "treinado" (usa dados da API)

    def predict(self, match_id: int) -> Optional[Dict]:
        """
        Busca predição da API-Football para uma partida

        Args:
            match_id: ID da partida no banco de dados

        Returns:
            Predição no formato padrão, ou None se não houver
        """
        predictions = self.db.get_predictions(match_id=match_id)

        # Filtrar apenas predições da api-football
        api_predictions = [p for p in predictions if p.model_name == "api-football"]

        if not api_predictions:
            return None

        # Pegar a predição mais recente
        api_pred = api_predictions[-1]

        return {
            "model": "API-Football",
            "result": {
                "home_win": float(api_pred.home_win_prob or 0.33),
                "draw": float(api_pred.draw_prob or 0.33),
                "away_win": float(api_pred.away_win_prob or 0.33)
            },
            "source": "api-football-predictions"
        }


class EnsembleModel:
    """
    Sistema Ensemble que combina predições de múltiplos modelos

    Estratégias:
    - weighted_average: Média ponderada por pesos
    - voting: Votação majoritária
    - confidence: Baseado em confiança de cada modelo

    NOVO: Suporta predições da API-Football no ensemble!
    """

    def __init__(
        self,
        models: Dict[str, any] = None,
        weights: Dict[str, float] = None,
        strategy: str = "weighted_average",
        database = None,
        include_api_predictions: bool = False
    ):
        """
        Inicializa o ensemble

        Args:
            models: Dicionário de modelos {nome: modelo}
            weights: Dicionário de pesos {nome: peso}
            strategy: Estratégia de combinação
            database: Instância do Database (para buscar predições da API)
            include_api_predictions: Se deve incluir predições da API-Football
        """
        self.models = models or {}
        self.weights = weights or {}
        self.strategy = strategy
        self.database = database
        self.include_api_predictions = include_api_predictions

        # Modelos padrão
        if not self.models:
            self.models = {
                "poisson": PoissonModel(),
                # XGBoost será adicionado quando treinado
            }

        # Adiciona modelo da API-Football se solicitado
        if include_api_predictions and database:
            self.models["api-football"] = APIFootballModel(database)

        # Pesos padrão
        if not self.weights:
            self.weights = {
                "poisson": 0.5,
                "xgboost": 0.3,
                "api-football": 0.2
            }

    def add_model(self, name: str, model: any, weight: float = 1.0):
        """
        Adiciona um modelo ao ensemble

        Args:
            name: Nome do modelo
            model: Instância do modelo
            weight: Peso do modelo
        """
        self.models[name] = model
        self.weights[name] = weight

    def normalize_weights(self):
        """Normaliza pesos para somarem 1.0"""
        total = sum(self.weights.values())
        if total > 0:
            self.weights = {k: v / total for k, v in self.weights.items()}

    def predict(self, match_stats: Dict, match_id: int = None) -> Dict:
        """
        Faz predição combinada de todos os modelos

        Args:
            match_stats: Estatísticas da partida
            match_id: ID da partida (necessário para API-Football e features)

        Returns:
            Predições combinadas
        """
        predictions = {}

        # Coleta predições de cada modelo
        for name, model in self.models.items():
            try:
                if name == "poisson":
                    pred = model.predict_match(
                        home_attack=match_stats["home"]["goals_scored_avg"],
                        away_attack=match_stats["away"]["goals_scored_avg"],
                        home_defense=match_stats["home"].get("goals_conceded_avg"),
                        away_defense=match_stats["away"].get("goals_conceded_avg")
                    )
                    predictions[name] = pred

                elif name == "xgboost":
                    if model.is_trained:
                        # Passa match_id para XGBoost poder usar features da API
                        pred = model.predict(match_stats, match_id=match_id)
                        predictions[name] = pred
                    else:
                        print(f"Modelo {name} não treinado, pulando...")

                elif name == "api-football":
                    if match_id:
                        pred = model.predict(match_id)
                        if pred:
                            predictions[name] = pred
                        else:
                            print(f"Predição da API-Football não disponível para match_id={match_id}")
                    else:
                        print("match_id necessário para buscar predições da API-Football")

            except Exception as e:
                print(f"Erro ao obter predição de {name}: {e}")

        if not predictions:
            raise Exception("Nenhum modelo disponível para predição")

        # Combina predições
        if self.strategy == "weighted_average":
            combined = self._weighted_average(predictions)
        elif self.strategy == "voting":
            combined = self._voting(predictions)
        elif self.strategy == "confidence":
            combined = self._confidence_based(predictions)
        else:
            combined = self._weighted_average(predictions)

        combined["models_used"] = list(predictions.keys())
        combined["strategy"] = self.strategy

        return combined

    def _weighted_average(self, predictions: Dict) -> Dict:
        """Combina predições usando média ponderada"""
        # Normaliza pesos dos modelos ativos
        active_weights = {k: v for k, v in self.weights.items() if k in predictions}
        total_weight = sum(active_weights.values())

        if total_weight == 0:
            active_weights = {k: 1.0 / len(predictions) for k in predictions}
            total_weight = 1.0

        normalized_weights = {k: v / total_weight for k, v in active_weights.items()}

        # Combina resultados
        combined_result = {
            "home_win": 0.0,
            "draw": 0.0,
            "away_win": 0.0
        }

        for model_name, pred in predictions.items():
            weight = normalized_weights.get(model_name, 0.0)
            result = pred.get("result", {})

            combined_result["home_win"] += result.get("home_win", 0.0) * weight
            combined_result["draw"] += result.get("draw", 0.0) * weight
            combined_result["away_win"] += result.get("away_win", 0.0) * weight

        # Combina gols (se disponível)
        combined_goals = {}
        poisson_pred = predictions.get("poisson", {})

        if "goals" in poisson_pred:
            combined_goals = poisson_pred["goals"]

        # Combina BTTS
        combined_btts = {}
        if "both_teams_score" in poisson_pred:
            combined_btts = poisson_pred["both_teams_score"]

        # Combina escanteios
        combined_corners = {}
        if "corners" in poisson_pred:
            combined_corners = poisson_pred["corners"]

        # Combina cartões
        combined_cards = {}
        if "cards" in poisson_pred:
            combined_cards = poisson_pred["cards"]

        # Placar mais provável
        most_likely_score = poisson_pred.get("most_likely_score", {})

        return {
            "model": "Ensemble (Weighted Average)",
            "weights": normalized_weights,
            "result": {
                "home_win": round(combined_result["home_win"], 3),
                "draw": round(combined_result["draw"], 3),
                "away_win": round(combined_result["away_win"], 3)
            },
            "goals": combined_goals,
            "both_teams_score": combined_btts,
            "corners": combined_corners,
            "cards": combined_cards,
            "most_likely_score": most_likely_score
        }

    def _voting(self, predictions: Dict) -> Dict:
        """Combina usando votação majoritária"""
        votes = {"home_win": 0, "draw": 0, "away_win": 0}

        for model_name, pred in predictions.items():
            result = pred.get("result", {})
            winner = max(result, key=result.get)
            votes[winner] += 1

        total_votes = sum(votes.values())

        return {
            "model": "Ensemble (Voting)",
            "result": {
                "home_win": round(votes["home_win"] / total_votes, 3),
                "draw": round(votes["draw"] / total_votes, 3),
                "away_win": round(votes["away_win"] / total_votes, 3)
            },
            "votes": votes
        }

    def _confidence_based(self, predictions: Dict) -> Dict:
        """Combina baseado em confiança de cada modelo"""
        # Calcula confiança como a probabilidade máxima
        confidences = {}

        for model_name, pred in predictions.items():
            result = pred.get("result", {})
            max_prob = max(result.values())
            confidences[model_name] = max_prob

        # Usa confiança como peso
        total_conf = sum(confidences.values())

        if total_conf == 0:
            return self._weighted_average(predictions)

        combined_result = {
            "home_win": 0.0,
            "draw": 0.0,
            "away_win": 0.0
        }

        for model_name, pred in predictions.items():
            conf = confidences[model_name] / total_conf
            result = pred.get("result", {})

            combined_result["home_win"] += result.get("home_win", 0.0) * conf
            combined_result["draw"] += result.get("draw", 0.0) * conf
            combined_result["away_win"] += result.get("away_win", 0.0) * conf

        return {
            "model": "Ensemble (Confidence-Based)",
            "confidences": confidences,
            "result": {
                "home_win": round(combined_result["home_win"], 3),
                "draw": round(combined_result["draw"], 3),
                "away_win": round(combined_result["away_win"], 3)
            }
        }

    def get_model_predictions(self, match_stats: Dict, match_id: int = None) -> Dict:
        """
        Retorna predições individuais de cada modelo

        Args:
            match_stats: Estatísticas da partida
            match_id: ID da partida (necessário para API-Football)

        Returns:
            Dicionário com predições de cada modelo
        """
        individual_predictions = {}

        for name, model in self.models.items():
            try:
                if name == "poisson":
                    pred = model.predict_match(
                        home_attack=match_stats["home"]["goals_scored_avg"],
                        away_attack=match_stats["away"]["goals_scored_avg"],
                        home_defense=match_stats["home"].get("goals_conceded_avg"),
                        away_defense=match_stats["away"].get("goals_conceded_avg")
                    )
                    individual_predictions[name] = pred

                elif name == "xgboost":
                    if model.is_trained:
                        pred = model.predict(match_stats, match_id=match_id)
                        individual_predictions[name] = pred

                elif name == "api-football":
                    if match_id:
                        pred = model.predict(match_id)
                        if pred:
                            individual_predictions[name] = pred

            except Exception as e:
                print(f"Erro em {name}: {e}")

        return individual_predictions


# Exemplo de uso
if __name__ == "__main__":
    print("=== Sistema Ensemble - Exemplo ===\n")

    # Cria ensemble com Poisson
    ensemble = EnsembleModel()

    # Estatísticas de exemplo
    match_stats = {
        "home": {
            "goals_scored_avg": 2.0,
            "goals_conceded_avg": 1.0,
            "wins": 7,
            "draws": 2,
            "losses": 1,
            "matches_played": 10
        },
        "away": {
            "goals_scored_avg": 1.5,
            "goals_conceded_avg": 1.5,
            "wins": 5,
            "draws": 3,
            "losses": 2,
            "matches_played": 10
        }
    }

    # Predição
    print("Predição com Ensemble:")
    prediction = ensemble.predict(match_stats)

    print(f"Modelo: {prediction['model']}")
    print(f"Modelos usados: {prediction['models_used']}")
    print(f"\nResultado:")
    print(f"  Casa: {prediction['result']['home_win']:.1%}")
    print(f"  Empate: {prediction['result']['draw']:.1%}")
    print(f"  Fora: {prediction['result']['away_win']:.1%}")

    if "weights" in prediction:
        print(f"\nPesos:")
        for model, weight in prediction["weights"].items():
            print(f"  {model}: {weight:.2f}")
