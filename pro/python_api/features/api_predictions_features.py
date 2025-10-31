"""
Feature Engineering para predições da API-Football

Este módulo extrai features úteis das predições da API-Football
para serem usadas como features adicionais no XGBoost.

Estratégia: Feature Engineering (recomendado no PREDICTIONS_GUIDE.md)
- XGBoost aprende QUANDO confiar na API
- XGBoost aprende QUANTO peso dar a cada feature
"""
from typing import Dict, Optional
import json


class APIPredictionFeatures:
    """
    Extrai features de predições da API-Football para usar no XGBoost

    Features extraídas:
    1. Probabilidades básicas (home_win, draw, away_win)
    2. Comparações (form, attack, defense, h2h)
    3. Predições Poisson da API
    4. Under/Over probabilidades
    5. Features derivadas (vantagem, confiança, etc)
    """

    def __init__(self, database):
        """
        Args:
            database: Instância do Database (database_v2.py)
        """
        self.db = database

    def get_features_for_match(self, match_id: int) -> Dict:
        """
        Busca predição da API-Football e extrai features

        Args:
            match_id: ID da partida no banco de dados

        Returns:
            Dicionário com features extraídas
        """
        # Buscar predição da API-Football no banco
        predictions = self.db.get_predictions(match_id=match_id)

        # Filtrar apenas predições da api-football
        api_predictions = [p for p in predictions if p.model_name == "api-football"]

        if not api_predictions:
            # Se não há predição da API, retorna features vazias (None)
            return self._empty_features()

        # Pegar a predição mais recente
        api_pred = api_predictions[-1]

        # Extrair features
        features = self._extract_features(api_pred)

        return features

    def _extract_features(self, prediction) -> Dict:
        """
        Extrai features de uma predição da API-Football

        Args:
            prediction: Objeto Prediction do banco de dados

        Returns:
            Dicionário com features
        """
        features = {}

        # 1. Probabilidades básicas
        features["api_home_win_prob"] = float(prediction.home_win_prob or 0.33)
        features["api_draw_prob"] = float(prediction.draw_prob or 0.33)
        features["api_away_win_prob"] = float(prediction.away_win_prob or 0.33)

        # 2. Features derivadas de probabilidades
        features["api_home_advantage"] = features["api_home_win_prob"] - features["api_away_win_prob"]
        features["api_prediction_confidence"] = max(
            features["api_home_win_prob"],
            features["api_draw_prob"],
            features["api_away_win_prob"]
        )
        features["api_draw_likelihood"] = features["api_draw_prob"]

        # 3. Extrair features do extra_predictions (JSON)
        extra = prediction.extra_predictions or {}

        # Under/Over
        under_over = extra.get("under_over")
        if under_over:
            features["api_over_25_prob"] = self._parse_percentage(under_over, "over")
            features["api_under_25_prob"] = self._parse_percentage(under_over, "under")
        else:
            features["api_over_25_prob"] = None
            features["api_under_25_prob"] = None

        # 4. Comparações (comparison)
        comparison = extra.get("comparison", {})

        # Form (forma dos times)
        form = comparison.get("form", {})
        features["api_form_home"] = self._parse_percentage(form, "home")
        features["api_form_away"] = self._parse_percentage(form, "away")

        # Attack
        att = comparison.get("att", {})
        features["api_att_home"] = self._parse_percentage(att, "home")
        features["api_att_away"] = self._parse_percentage(att, "away")

        # Defense
        def_comp = comparison.get("def", {})
        features["api_def_home"] = self._parse_percentage(def_comp, "home")
        features["api_def_away"] = self._parse_percentage(def_comp, "away")

        # Poisson Distribution
        poisson = comparison.get("poisson_distribution", {})
        features["api_poisson_home"] = self._parse_percentage(poisson, "home")
        features["api_poisson_away"] = self._parse_percentage(poisson, "away")

        # H2H (head to head)
        h2h = comparison.get("h2h", {})
        features["api_h2h_home"] = self._parse_percentage(h2h, "home")
        features["api_h2h_away"] = self._parse_percentage(h2h, "away")

        # Goals (expected goals)
        goals = comparison.get("goals", {})
        features["api_goals_home"] = self._parse_percentage(goals, "home")
        features["api_goals_away"] = self._parse_percentage(goals, "away")

        # Total (comparação geral)
        total = comparison.get("total", {})
        features["api_total_home"] = self._parse_percentage(total, "home")
        features["api_total_away"] = self._parse_percentage(total, "away")

        # 5. Features derivadas de comparações
        if features["api_form_home"] is not None and features["api_form_away"] is not None:
            features["api_form_diff"] = features["api_form_home"] - features["api_form_away"]
        else:
            features["api_form_diff"] = None

        if features["api_att_home"] is not None and features["api_def_away"] is not None:
            features["api_attack_vs_defense"] = features["api_att_home"] - features["api_def_away"]
        else:
            features["api_attack_vs_defense"] = None

        # 6. Teams data (estatísticas dos times)
        teams_data = extra.get("teams_data", {})
        home_team = teams_data.get("home", {})
        away_team = teams_data.get("away", {})

        # Forma recente (últimos 5 jogos)
        home_form = home_team.get("league", {}).get("form")
        away_form = away_team.get("league", {}).get("form")

        features["api_recent_form_home"] = self._form_to_score(home_form)
        features["api_recent_form_away"] = self._form_to_score(away_form)

        return features

    def _empty_features(self) -> Dict:
        """
        Retorna features vazias quando não há predição da API

        Returns:
            Dicionário com todas as features como None
        """
        return {
            # Probabilidades básicas
            "api_home_win_prob": None,
            "api_draw_prob": None,
            "api_away_win_prob": None,

            # Features derivadas
            "api_home_advantage": None,
            "api_prediction_confidence": None,
            "api_draw_likelihood": None,

            # Under/Over
            "api_over_25_prob": None,
            "api_under_25_prob": None,

            # Comparações
            "api_form_home": None,
            "api_form_away": None,
            "api_att_home": None,
            "api_att_away": None,
            "api_def_home": None,
            "api_def_away": None,
            "api_poisson_home": None,
            "api_poisson_away": None,
            "api_h2h_home": None,
            "api_h2h_away": None,
            "api_goals_home": None,
            "api_goals_away": None,
            "api_total_home": None,
            "api_total_away": None,

            # Features derivadas de comparações
            "api_form_diff": None,
            "api_attack_vs_defense": None,

            # Forma recente
            "api_recent_form_home": None,
            "api_recent_form_away": None,
        }

    def _parse_percentage(self, data: Optional[Dict], key: str) -> Optional[float]:
        """
        Parse string de porcentagem para float

        Args:
            data: Dicionário com dados
            key: Chave para buscar

        Returns:
            Valor como float entre 0 e 1, ou None
        """
        if not data or key not in data:
            return None

        value = data[key]
        if value is None:
            return None

        # Se já é número
        if isinstance(value, (int, float)):
            # Se está entre 0 e 1, mantém
            if 0 <= value <= 1:
                return float(value)
            # Se está entre 0 e 100, divide por 100
            elif 0 <= value <= 100:
                return float(value) / 100
            else:
                return None

        # Se é string com %
        if isinstance(value, str):
            try:
                # Remove % e converte
                num = float(value.replace("%", "").strip())
                # Assume que está entre 0 e 100
                return num / 100
            except:
                return None

        return None

    def _form_to_score(self, form_string: Optional[str]) -> Optional[float]:
        """
        Converte string de forma (ex: "WWDLW") para score numérico

        Args:
            form_string: String com forma recente (W=win, D=draw, L=loss)

        Returns:
            Score entre 0 e 1, ou None
        """
        if not form_string:
            return None

        # W = 1 ponto, D = 0.5 pontos, L = 0 pontos
        points = 0
        for char in form_string.upper():
            if char == 'W':
                points += 1
            elif char == 'D':
                points += 0.5
            # L = 0 pontos (não precisa adicionar)

        # Normaliza (máximo 5 pontos se tiver 5 jogos)
        max_points = len(form_string)
        if max_points == 0:
            return None

        return points / max_points

    def get_feature_names(self) -> list:
        """
        Retorna lista com nomes de todas as features

        Returns:
            Lista de nomes de features
        """
        return list(self._empty_features().keys())

    def get_feature_count(self) -> int:
        """
        Retorna número de features

        Returns:
            Número de features
        """
        return len(self._empty_features())


# Exemplo de uso
if __name__ == "__main__":
    from data.database_v2 import Database

    print("=== API Prediction Features - Teste ===\n")

    # Conecta ao banco
    db = Database("database/betting_v2.db")

    # Cria extractor
    feature_extractor = APIPredictionFeatures(db)

    print(f"Total de features: {feature_extractor.get_feature_count()}")
    print(f"\nNomes das features:")
    for i, name in enumerate(feature_extractor.get_feature_names(), 1):
        print(f"  {i:2d}. {name}")

    # Tenta buscar features de uma partida (se existir)
    try:
        matches = db.get_matches(limit=1)
        if matches:
            match = matches[0]
            print(f"\n\nTestando com partida: {match.home_team} vs {match.away_team}")
            print(f"Match ID: {match.id}")

            features = feature_extractor.get_features_for_match(match.id)

            print("\nFeatures extraídas:")
            for name, value in features.items():
                if value is not None:
                    print(f"  {name}: {value:.3f}")
                else:
                    print(f"  {name}: None")
    except Exception as e:
        print(f"\nErro ao testar: {e}")

    db.close()
    print("\n✓ Teste concluído!")
