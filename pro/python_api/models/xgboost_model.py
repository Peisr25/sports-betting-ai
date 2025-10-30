"""
Modelo XGBoost para predições de apostas esportivas
"""
import xgboost as xgb
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, log_loss
import joblib
import os


class XGBoostModel:
    """
    Modelo baseado em XGBoost para predições de partidas

    XGBoost (Extreme Gradient Boosting) é um algoritmo de machine learning
    de alta performance que usa ensemble de árvores de decisão.
    """

    def __init__(self, model_path: str = None):
        """
        Inicializa o modelo XGBoost

        Args:
            model_path: Caminho para carregar modelo treinado
        """
        self.model = None
        self.feature_names = []
        self.is_trained = False

        if model_path and os.path.exists(model_path):
            self.load_model(model_path)

    def create_features(self, match_stats: Dict) -> np.array:
        """
        Cria features para o modelo

        Args:
            match_stats: Estatísticas da partida

        Returns:
            Array de features
        """
        features = []

        # Features do time da casa
        home = match_stats.get("home", {})
        features.extend([
            home.get("goals_scored_avg", 1.5),
            home.get("goals_conceded_avg", 1.5),
            home.get("wins", 0),
            home.get("draws", 0),
            home.get("losses", 0),
            home.get("matches_played", 0),
            home.get("goals_for_total", 0),
            home.get("goals_against_total", 0),
        ])

        # Features do time visitante
        away = match_stats.get("away", {})
        features.extend([
            away.get("goals_scored_avg", 1.5),
            away.get("goals_conceded_avg", 1.5),
            away.get("wins", 0),
            away.get("draws", 0),
            away.get("losses", 0),
            away.get("matches_played", 0),
            away.get("goals_for_total", 0),
            away.get("goals_against_total", 0),
        ])

        # Features derivadas
        features.extend([
            features[0] - features[8],  # Diferença de gols marcados
            features[1] - features[9],  # Diferença de gols sofridos
            features[2] - features[10],  # Diferença de vitórias
            (features[2] + features[3] * 0.5) / max(features[5], 1),  # Pontos por jogo casa
            (features[10] + features[11] * 0.5) / max(features[13], 1),  # Pontos por jogo fora
        ])

        return np.array(features)

    def train(
        self,
        X_train: np.array,
        y_train: np.array,
        X_val: np.array = None,
        y_val: np.array = None,
        params: Dict = None
    ) -> Dict:
        """
        Treina o modelo XGBoost

        Args:
            X_train: Features de treino
            y_train: Labels de treino (0=away_win, 1=draw, 2=home_win)
            X_val: Features de validação (opcional)
            y_val: Labels de validação (opcional)
            params: Parâmetros do XGBoost

        Returns:
            Métricas de treinamento
        """
        if params is None:
            params = {
                "objective": "multi:softprob",
                "num_class": 3,
                "max_depth": 6,
                "learning_rate": 0.1,
                "n_estimators": 100,
                "subsample": 0.8,
                "colsample_bytree": 0.8,
                "random_state": 42,
                "eval_metric": "mlogloss"
            }

        # Cria modelo
        self.model = xgb.XGBClassifier(**params)

        # Treina
        eval_set = [(X_train, y_train)]
        if X_val is not None and y_val is not None:
            eval_set.append((X_val, y_val))

        self.model.fit(
            X_train,
            y_train,
            eval_set=eval_set,
            verbose=False
        )

        self.is_trained = True

        # Calcula métricas
        train_pred = self.model.predict(X_train)
        train_acc = accuracy_score(y_train, train_pred)

        metrics = {
            "train_accuracy": train_acc,
            "n_samples": len(X_train)
        }

        if X_val is not None and y_val is not None:
            val_pred = self.model.predict(X_val)
            val_acc = accuracy_score(y_val, val_pred)
            metrics["val_accuracy"] = val_acc

        return metrics

    def predict(self, match_stats: Dict) -> Dict:
        """
        Faz predição para uma partida

        Args:
            match_stats: Estatísticas da partida

        Returns:
            Probabilidades de resultado
        """
        if not self.is_trained:
            raise Exception("Modelo não treinado. Treine o modelo antes de fazer predições.")

        # Cria features
        features = self.create_features(match_stats)
        features = features.reshape(1, -1)

        # Predição
        probs = self.model.predict_proba(features)[0]

        # probs[0] = away_win, probs[1] = draw, probs[2] = home_win
        return {
            "model": "XGBoost",
            "result": {
                "home_win": float(probs[2]),
                "draw": float(probs[1]),
                "away_win": float(probs[0])
            }
        }

    def predict_goals(self, match_stats: Dict) -> Dict:
        """
        Estima probabilidades de gols baseado no resultado

        Esta é uma aproximação. Para melhor precisão, treine um modelo
        específico para regressão de gols.

        Args:
            match_stats: Estatísticas da partida

        Returns:
            Probabilidades de gols
        """
        result = self.predict(match_stats)

        # Estimativas baseadas em probabilidades de resultado
        home_win_prob = result["result"]["home_win"]
        away_win_prob = result["result"]["away_win"]

        # Jogos com maior probabilidade de vitória tendem a ter mais gols
        over_25_prob = 0.4 + (home_win_prob + away_win_prob) * 0.3

        return {
            "over_2.5": min(over_25_prob, 0.95),
            "under_2.5": max(1 - over_25_prob, 0.05)
        }

    def save_model(self, path: str):
        """Salva modelo treinado"""
        if not self.is_trained:
            raise Exception("Modelo não treinado")

        joblib.dump({
            "model": self.model,
            "feature_names": self.feature_names,
            "is_trained": self.is_trained
        }, path)

        print(f"Modelo salvo em: {path}")

    def load_model(self, path: str):
        """Carrega modelo treinado"""
        data = joblib.load(path)
        self.model = data["model"]
        self.feature_names = data.get("feature_names", [])
        self.is_trained = data.get("is_trained", True)

        print(f"Modelo carregado de: {path}")

    def get_feature_importance(self) -> Dict:
        """Retorna importância das features"""
        if not self.is_trained:
            return {}

        importance = self.model.feature_importances_
        features = self.feature_names if self.feature_names else \
                   [f"feature_{i}" for i in range(len(importance))]

        return dict(zip(features, importance.tolist()))


# Exemplo de uso
if __name__ == "__main__":
    print("=== Modelo XGBoost - Exemplo ===\n")

    # Dados de exemplo (normalmente viriam do banco de dados)
    X_train = np.random.rand(100, 21)  # 100 partidas, 21 features
    y_train = np.random.randint(0, 3, 100)  # 0=away, 1=draw, 2=home

    # Criar e treinar modelo
    model = XGBoostModel()

    print("Treinando modelo...")
    metrics = model.train(X_train, y_train)

    print(f"Acurácia de treino: {metrics['train_accuracy']:.2%}")
    print(f"Amostras: {metrics['n_samples']}")

    # Predição de exemplo
    print("\nPredição de exemplo:")
    match_stats = {
        "home": {
            "goals_scored_avg": 2.0,
            "goals_conceded_avg": 1.0,
            "wins": 7,
            "draws": 2,
            "losses": 1,
            "matches_played": 10,
            "goals_for_total": 20,
            "goals_against_total": 10
        },
        "away": {
            "goals_scored_avg": 1.5,
            "goals_conceded_avg": 1.5,
            "wins": 5,
            "draws": 3,
            "losses": 2,
            "matches_played": 10,
            "goals_for_total": 15,
            "goals_against_total": 15
        }
    }

    prediction = model.predict(match_stats)

    print(f"Casa: {prediction['result']['home_win']:.1%}")
    print(f"Empate: {prediction['result']['draw']:.1%}")
    print(f"Fora: {prediction['result']['away_win']:.1%}")
