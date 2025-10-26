"""
Engine de predição que integra coleta de dados, processamento e modelos
"""
from typing import Dict, Optional
from data.collector import FootballDataCollector
from data.processor import DataProcessor
from data.database import DatabaseManager
from models.ensemble import EnsembleModel
from config import config


class PredictionEngine:
    """
    Engine principal de predição que orquestra todo o processo
    """
    
    def __init__(self, api_key: str = None):
        """
        Inicializa o engine de predição
        
        Args:
            api_key: Chave da API Football
        """
        self.collector = FootballDataCollector(api_key)
        self.processor = DataProcessor()
        self.db = DatabaseManager()
        self.model = EnsembleModel()
        
        # Tenta carregar modelos ML treinados
        try:
            self.model.load_ml_models("./models/trained")
            print("Modelos ML carregados com sucesso")
        except Exception as e:
            print(f"Aviso: Modelos ML não carregados - {e}")
            print("Usando apenas modelo Poisson")
    
    def predict_match(
        self,
        home_team_name: str,
        away_team_name: str,
        league_name: str = "Brasileirão Série A",
        season: int = 2025
    ) -> Dict:
        """
        Faz predição para uma partida
        
        Args:
            home_team_name: Nome do time da casa
            away_team_name: Nome do time visitante
            league_name: Nome da liga
            season: Temporada
            
        Returns:
            Dicionário com predições e recomendações
        """
        try:
            # 1. Busca times
            print(f"Buscando times: {home_team_name} vs {away_team_name}")
            home_team = self._find_team(home_team_name, league_name)
            away_team = self._find_team(away_team_name, league_name)
            
            if not home_team or not away_team:
                return {
                    "error": "Times não encontrados",
                    "home_team_found": home_team is not None,
                    "away_team_found": away_team is not None
                }
            
            # 2. Coleta dados dos times
            print("Coletando dados dos times...")
            league_id = self._get_league_id(league_name)
            
            home_matches = self.collector.get_fixtures(
                league_id=league_id,
                season=season,
                team_id=home_team["id"],
                last_n=10
            )
            
            away_matches = self.collector.get_fixtures(
                league_id=league_id,
                season=season,
                team_id=away_team["id"],
                last_n=10
            )
            
            # 3. Coleta confrontos diretos
            print("Coletando confrontos diretos...")
            h2h_matches = self.collector.get_head_to_head(
                home_team["id"],
                away_team["id"],
                last_n=5
            )
            
            # 4. Processa dados
            print("Processando dados...")
            home_stats = self.processor.calculate_team_averages(
                home_matches, home_team["id"], is_home=True
            )
            away_stats = self.processor.calculate_team_averages(
                away_matches, away_team["id"], is_home=False
            )
            
            home_form = self.processor.calculate_form(home_matches, home_team["id"])
            away_form = self.processor.calculate_form(away_matches, away_team["id"])
            
            h2h_stats = self.processor.calculate_h2h_stats(
                h2h_matches, home_team["id"], away_team["id"]
            )
            
            # 5. Prepara features para ML
            match_data = {
                "home_goals_avg": home_stats["goals_scored_avg"],
                "away_goals_avg": away_stats["goals_scored_avg"],
                "home_goals_conceded_avg": home_stats["goals_conceded_avg"],
                "away_goals_conceded_avg": away_stats["goals_conceded_avg"],
                "home_shots_avg": home_stats["shots_avg"],
                "away_shots_avg": away_stats["shots_avg"],
                "home_shots_on_target_avg": home_stats["shots_on_target_avg"],
                "away_shots_on_target_avg": away_stats["shots_on_target_avg"],
                "home_corners_avg": home_stats["corners_avg"],
                "away_corners_avg": away_stats["corners_avg"],
                "home_fouls_avg": home_stats["fouls_avg"],
                "away_fouls_avg": away_stats["fouls_avg"],
                "home_yellow_cards_avg": home_stats["yellow_cards_avg"],
                "away_yellow_cards_avg": away_stats["yellow_cards_avg"],
                "home_red_cards_avg": home_stats["red_cards_avg"],
                "away_red_cards_avg": away_stats["red_cards_avg"],
                "home_form": home_form,
                "away_form": away_form,
                **h2h_stats
            }
            
            # 6. Faz predição
            print("Gerando predições...")
            predictions = self.model.predict(
                home_stats={
                    "goals_scored_avg": home_stats["goals_scored_avg"],
                    "goals_conceded_avg": home_stats["goals_conceded_avg"]
                },
                away_stats={
                    "goals_scored_avg": away_stats["goals_scored_avg"],
                    "goals_conceded_avg": away_stats["goals_conceded_avg"]
                },
                match_data=match_data
            )
            
            # 7. Gera recomendações
            print("Gerando recomendações...")
            recommendations = self.model.generate_recommendations(predictions)
            
            # 8. Monta resposta
            response = {
                "match": {
                    "home_team": home_team["name"],
                    "away_team": away_team["name"],
                    "league": league_name,
                    "season": season
                },
                "team_stats": {
                    "home": home_stats,
                    "away": away_stats,
                    "home_form": home_form,
                    "away_form": away_form
                },
                "head_to_head": h2h_stats,
                "predictions": predictions,
                "recommendations": recommendations,
                "api_requests_used": self.collector.get_request_count()
            }
            
            return response
        
        except Exception as e:
            return {
                "error": str(e),
                "api_requests_used": self.collector.get_request_count()
            }
    
    def _find_team(self, team_name: str, league_name: str) -> Optional[Dict]:
        """
        Busca time por nome
        
        Args:
            team_name: Nome do time
            league_name: Nome da liga
            
        Returns:
            Dados do time ou None
        """
        league_id = self._get_league_id(league_name)
        teams = self.collector.search_team(team_name, league_id)
        
        if teams:
            # Retorna o primeiro resultado
            team_data = teams[0]["team"]
            return {
                "id": team_data["id"],
                "name": team_data["name"],
                "logo": team_data.get("logo", "")
            }
        
        return None
    
    def _get_league_id(self, league_name: str) -> int:
        """
        Retorna ID da liga
        
        Args:
            league_name: Nome da liga
            
        Returns:
            ID da liga
        """
        # Mapeia nomes comuns para IDs
        league_mapping = {
            "brasileirão série a": 71,
            "brasileirao": 71,
            "serie a brasil": 71,
            "premier league": 39,
            "la liga": 140,
            "bundesliga": 78,
            "serie a": 135,
            "ligue 1": 61
        }
        
        return league_mapping.get(league_name.lower(), 71)
    
    def update_database(
        self,
        league_name: str = "Brasileirão Série A",
        season: int = 2025
    ):
        """
        Atualiza banco de dados com dados recentes
        
        Args:
            league_name: Nome da liga
            season: Temporada
        """
        try:
            league_id = self._get_league_id(league_name)
            
            # Busca times da liga
            print(f"Buscando times da {league_name}...")
            teams = self.collector.get_teams(league_id, season)
            
            # Adiciona liga ao banco
            db_league = self.db.add_league(
                api_id=league_id,
                name=league_name,
                country="Brazil",
                season=season
            )
            
            # Adiciona times ao banco
            for team_data in teams:
                team = team_data["team"]
                self.db.add_team(
                    api_id=team["id"],
                    name=team["name"],
                    league_id=db_league.id
                )
            
            print(f"{len(teams)} times adicionados ao banco de dados")
            
            # Busca partidas recentes
            print("Buscando partidas recentes...")
            fixtures = self.collector.get_fixtures(
                league_id=league_id,
                season=season,
                last_n=50
            )
            
            print(f"{len(fixtures)} partidas encontradas")
            print(f"Requisições API usadas: {self.collector.get_request_count()}")
            
        except Exception as e:
            print(f"Erro ao atualizar banco de dados: {e}")


# Exemplo de uso
if __name__ == "__main__":
    engine = PredictionEngine()
    
    # Exemplo de predição
    print("=" * 60)
    print("EXEMPLO DE PREDIÇÃO")
    print("=" * 60)
    
    result = engine.predict_match(
        home_team_name="Flamengo",
        away_team_name="Palmeiras",
        league_name="Brasileirão Série A"
    )
    
    if "error" in result:
        print(f"Erro: {result['error']}")
    else:
        print(f"\nPartida: {result['match']['home_team']} vs {result['match']['away_team']}")
        print(f"\nProbabilidades:")
        if "result" in result["predictions"]:
            print(f"  Vitória Casa: {result['predictions']['result']['home_win']:.1%}")
            print(f"  Empate: {result['predictions']['result']['draw']:.1%}")
            print(f"  Vitória Fora: {result['predictions']['result']['away_win']:.1%}")
        
        print(f"\nRecomendações:")
        for i, rec in enumerate(result["recommendations"][:3], 1):
            print(f"  {i}. {rec['market']} - {rec['bet']}")
            print(f"     Probabilidade: {rec['probability']:.1%} | Confiança: {rec['confidence']}")

