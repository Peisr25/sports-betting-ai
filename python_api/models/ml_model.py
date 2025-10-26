"""
Modelo de Machine Learning para previsão de apostas esportivas
Usa XGBoost para prever múltiplos mercados
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pickle
import os


class MLBettingModel:
    """
    Modelo de ML para previsão de múltiplos mercados de apostas
    """
    
    def __init__(self):
        """Inicializa os modelos para diferentes mercados"""
        self.models = {}
        self.scalers = {}
        self.feature_names = []
        
        # Modelos para diferentes mercados
        self.market_models = {
            "result": None,  # 1x2
            "over_2_5": None,  # Over 2.5 gols
            "btts": None,  # Ambos marcam
            "over_3_5_cards": None,  # Over 3.5 cartões
            "over_9_5_corners": None,  # Over 9.5 escanteios
            "over_25_fouls": None  # Over 25 faltas
        }
    
    def prepare_features(self, match_data: Dict) -> np.ndarray:
        """
        Prepara features para o modelo
        
        Args:
            match_data: Dicionário com estatísticas da partida
            
        Returns:
            Array numpy com features
        """
        features = []
        
        # Features básicas de gols
        features.extend([
            match_data.get("home_goals_avg", 0),
            match_data.get("away_goals_avg", 0),
            match_data.get("home_goals_conceded_avg", 0),
            match_data.get("away_goals_conceded_avg", 0),
        ])
        
        # Features de chutes
        features.extend([
            match_data.get("home_shots_avg", 0),
            match_data.get("away_shots_avg", 0),
            match_data.get("home_shots_on_target_avg", 0),
            match_data.get("away_shots_on_target_avg", 0),
        ])
        
        # Features de escanteios
        features.extend([
            match_data.get("home_corners_avg", 0),
            match_data.get("away_corners_avg", 0),
        ])
        
        # Features de faltas
        features.extend([
            match_data.get("home_fouls_avg", 0),
            match_data.get("away_fouls_avg", 0),
        ])
        
        # Features de cartões
        features.extend([
            match_data.get("home_yellow_cards_avg", 0),
            match_data.get("away_yellow_cards_avg", 0),
            match_data.get("home_red_cards_avg", 0),
            match_data.get("away_red_cards_avg", 0),
        ])
        
        # Features de forma recente
        features.extend([
            match_data.get("home_form", 0),
            match_data.get("away_form", 0),
        ])
        
        # Features de confronto direto
        features.extend([
            match_data.get("h2h_home_wins", 0),
            match_data.get("h2h_draws", 0),
            match_data.get("h2h_away_wins", 0),
        ])
        
        return np.array(features).reshape(1, -1)
    
    def train_result_model(
        self,
        X: np.ndarray,
        y: np.ndarray,
        test_size: float = 0.2
    ) -> Dict[str, float]:
        """
        Treina modelo para prever resultado (1x2)
        
        Args:
            X: Features
            y: Labels (0=casa, 1=empate, 2=fora)
            test_size: Proporção de dados para teste
            
        Returns:
            Métricas de avaliação
        """
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Normalização
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Modelo XGBoost para classificação multiclasse
        model = xgb.XGBClassifier(
            objective='multi:softprob',
            num_class=3,
            max_depth=6,
            learning_rate=0.1,
            n_estimators=100,
            random_state=42
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Avaliação
        train_accuracy = model.score(X_train_scaled, y_train)
        test_accuracy = model.score(X_test_scaled, y_test)
        
        self.models["result"] = model
        self.scalers["result"] = scaler
        
        return {
            "train_accuracy": train_accuracy,
            "test_accuracy": test_accuracy
        }
    
    def train_binary_model(
        self,
        market_name: str,
        X: np.ndarray,
        y: np.ndarray,
        test_size: float = 0.2
    ) -> Dict[str, float]:
        """
        Treina modelo para mercados binários (sim/não)
        
        Args:
            market_name: Nome do mercado
            X: Features
            y: Labels (0=não, 1=sim)
            test_size: Proporção de dados para teste
            
        Returns:
            Métricas de avaliação
        """
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Normalização
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Modelo XGBoost para classificação binária
        model = xgb.XGBClassifier(
            objective='binary:logistic',
            max_depth=5,
            learning_rate=0.1,
            n_estimators=100,
            random_state=42
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Avaliação
        train_accuracy = model.score(X_train_scaled, y_train)
        test_accuracy = model.score(X_test_scaled, y_test)
        
        self.models[market_name] = model
        self.scalers[market_name] = scaler
        
        return {
            "train_accuracy": train_accuracy,
            "test_accuracy": test_accuracy
        }
    
    def predict_result(self, match_data: Dict) -> Dict[str, float]:
        """
        Prediz resultado da partida (1x2)
        
        Args:
            match_data: Dados da partida
            
        Returns:
            Probabilidades para cada resultado
        """
        if "result" not in self.models or self.models["result"] is None:
            raise ValueError("Modelo de resultado não treinado")
        
        X = self.prepare_features(match_data)
        X_scaled = self.scalers["result"].transform(X)
        
        probabilities = self.models["result"].predict_proba(X_scaled)[0]
        
        return {
            "home_win": float(probabilities[0]),
            "draw": float(probabilities[1]),
            "away_win": float(probabilities[2])
        }
    
    def predict_binary_market(
        self,
        market_name: str,
        match_data: Dict
    ) -> Dict[str, float]:
        """
        Prediz mercado binário
        
        Args:
            market_name: Nome do mercado
            match_data: Dados da partida
            
        Returns:
            Probabilidades
        """
        if market_name not in self.models or self.models[market_name] is None:
            raise ValueError(f"Modelo {market_name} não treinado")
        
        X = self.prepare_features(match_data)
        X_scaled = self.scalers[market_name].transform(X)
        
        probabilities = self.models[market_name].predict_proba(X_scaled)[0]
        
        return {
            "no": float(probabilities[0]),
            "yes": float(probabilities[1])
        }
    
    def predict_all_markets(self, match_data: Dict) -> Dict:
        """
        Faz predições para todos os mercados disponíveis
        
        Args:
            match_data: Dados da partida
            
        Returns:
            Dicionário com todas as predições
        """
        predictions = {}
        
        # Resultado
        if "result" in self.models and self.models["result"] is not None:
            predictions["result"] = self.predict_result(match_data)
        
        # Over 2.5 gols
        if "over_2_5" in self.models and self.models["over_2_5"] is not None:
            over_2_5 = self.predict_binary_market("over_2_5", match_data)
            predictions["over_2_5"] = over_2_5["yes"]
            predictions["under_2_5"] = over_2_5["no"]
        
        # Ambos marcam
        if "btts" in self.models and self.models["btts"] is not None:
            btts = self.predict_binary_market("btts", match_data)
            predictions["btts_yes"] = btts["yes"]
            predictions["btts_no"] = btts["no"]
        
        # Over 3.5 cartões
        if "over_3_5_cards" in self.models and self.models["over_3_5_cards"] is not None:
            cards = self.predict_binary_market("over_3_5_cards", match_data)
            predictions["over_3_5_cards"] = cards["yes"]
            predictions["under_3_5_cards"] = cards["no"]
        
        # Over 9.5 escanteios
        if "over_9_5_corners" in self.models and self.models["over_9_5_corners"] is not None:
            corners = self.predict_binary_market("over_9_5_corners", match_data)
            predictions["over_9_5_corners"] = corners["yes"]
            predictions["under_9_5_corners"] = corners["no"]
        
        # Over 25 faltas
        if "over_25_fouls" in self.models and self.models["over_25_fouls"] is not None:
            fouls = self.predict_binary_market("over_25_fouls", match_data)
            predictions["over_25_fouls"] = fouls["yes"]
            predictions["under_25_fouls"] = fouls["no"]
        
        return predictions
    
    def save_models(self, directory: str):
        """
        Salva todos os modelos treinados
        
        Args:
            directory: Diretório onde salvar os modelos
        """
        os.makedirs(directory, exist_ok=True)
        
        for market_name, model in self.models.items():
            if model is not None:
                model_path = os.path.join(directory, f"{market_name}_model.pkl")
                scaler_path = os.path.join(directory, f"{market_name}_scaler.pkl")
                
                with open(model_path, 'wb') as f:
                    pickle.dump(model, f)
                
                with open(scaler_path, 'wb') as f:
                    pickle.dump(self.scalers[market_name], f)
        
        print(f"Modelos salvos em {directory}")
    
    def load_models(self, directory: str):
        """
        Carrega modelos treinados
        
        Args:
            directory: Diretório de onde carregar os modelos
        """
        for market_name in self.market_models.keys():
            model_path = os.path.join(directory, f"{market_name}_model.pkl")
            scaler_path = os.path.join(directory, f"{market_name}_scaler.pkl")
            
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                with open(model_path, 'rb') as f:
                    self.models[market_name] = pickle.load(f)
                
                with open(scaler_path, 'rb') as f:
                    self.scalers[market_name] = pickle.load(f)
                
                print(f"Modelo {market_name} carregado")
            else:
                print(f"Modelo {market_name} não encontrado")


# Exemplo de uso
if __name__ == "__main__":
    model = MLBettingModel()
    
    # Exemplo de dados de partida
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
        "home_form": 12,  # Pontos nos últimos 5 jogos
        "away_form": 10,
        "h2h_home_wins": 3,
        "h2h_draws": 1,
        "h2h_away_wins": 1
    }
    
    print("Exemplo de features preparadas:")
    features = model.prepare_features(match_data)
    print(features)

