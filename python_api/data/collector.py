"""
Módulo para coleta de dados da API-Football
"""
import requests
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from config import config


class FootballDataCollector:
    """
    Coleta dados da API-Football
    """
    
    def __init__(self, api_key: str = None):
        """
        Inicializa o coletor de dados
        
        Args:
            api_key: Chave da API Football (usa config se não fornecida)
        """
        self.api_key = api_key or config.API_FOOTBALL_KEY
        self.base_url = config.API_FOOTBALL_BASE_URL
        self.headers = {
            "x-apisports-key": self.api_key
        }
        self.request_count = 0
        self.max_requests = config.API_RATE_LIMIT_PER_DAY
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Faz requisição à API
        
        Args:
            endpoint: Endpoint da API
            params: Parâmetros da requisição
            
        Returns:
            Resposta JSON
        """
        if self.request_count >= self.max_requests:
            raise Exception(f"Limite de {self.max_requests} requisições atingido")
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            self.request_count += 1
            
            data = response.json()
            
            # Verifica erros da API
            if data.get("errors"):
                raise Exception(f"Erro da API: {data['errors']}")
            
            return data
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro na requisição: {str(e)}")
    
    def get_leagues(self, country: str = "Brazil") -> List[Dict]:
        """
        Busca ligas disponíveis
        
        Args:
            country: País
            
        Returns:
            Lista de ligas
        """
        params = {"country": country}
        data = self._make_request("leagues", params)
        return data.get("response", [])
    
    def get_teams(self, league_id: int, season: int) -> List[Dict]:
        """
        Busca times de uma liga
        
        Args:
            league_id: ID da liga
            season: Ano da temporada
            
        Returns:
            Lista de times
        """
        params = {
            "league": league_id,
            "season": season
        }
        data = self._make_request("teams", params)
        return data.get("response", [])
    
    def get_fixtures(
        self,
        league_id: int,
        season: int,
        team_id: Optional[int] = None,
        last_n: int = 10
    ) -> List[Dict]:
        """
        Busca partidas
        
        Args:
            league_id: ID da liga
            season: Ano da temporada
            team_id: ID do time (opcional)
            last_n: Número de partidas recentes
            
        Returns:
            Lista de partidas
        """
        params = {
            "league": league_id,
            "season": season,
            "last": last_n
        }
        
        if team_id:
            params["team"] = team_id
        
        data = self._make_request("fixtures", params)
        return data.get("response", [])
    
    def get_fixture_statistics(self, fixture_id: int) -> Dict:
        """
        Busca estatísticas de uma partida
        
        Args:
            fixture_id: ID da partida
            
        Returns:
            Estatísticas da partida
        """
        params = {"fixture": fixture_id}
        data = self._make_request("fixtures/statistics", params)
        return data.get("response", [])
    
    def get_team_statistics(
        self,
        team_id: int,
        league_id: int,
        season: int
    ) -> Dict:
        """
        Busca estatísticas de um time
        
        Args:
            team_id: ID do time
            league_id: ID da liga
            season: Ano da temporada
            
        Returns:
            Estatísticas do time
        """
        params = {
            "team": team_id,
            "league": league_id,
            "season": season
        }
        data = self._make_request("teams/statistics", params)
        return data.get("response", {})
    
    def get_head_to_head(
        self,
        team1_id: int,
        team2_id: int,
        last_n: int = 5
    ) -> List[Dict]:
        """
        Busca confrontos diretos entre dois times
        
        Args:
            team1_id: ID do primeiro time
            team2_id: ID do segundo time
            last_n: Número de confrontos recentes
            
        Returns:
            Lista de confrontos
        """
        params = {
            "h2h": f"{team1_id}-{team2_id}",
            "last": last_n
        }
        data = self._make_request("fixtures/headtohead", params)
        return data.get("response", [])
    
    def search_team(self, team_name: str, league_id: int = None) -> List[Dict]:
        """
        Busca time por nome
        
        Args:
            team_name: Nome do time
            league_id: ID da liga (opcional)
            
        Returns:
            Lista de times encontrados
        """
        params = {"search": team_name}
        if league_id:
            params["league"] = league_id
        
        data = self._make_request("teams", params)
        return data.get("response", [])
    
    def get_upcoming_fixtures(
        self,
        league_id: int,
        days_ahead: int = 7
    ) -> List[Dict]:
        """
        Busca próximas partidas
        
        Args:
            league_id: ID da liga
            days_ahead: Dias à frente para buscar
            
        Returns:
            Lista de próximas partidas
        """
        today = datetime.now()
        end_date = today + timedelta(days=days_ahead)
        
        params = {
            "league": league_id,
            "from": today.strftime("%Y-%m-%d"),
            "to": end_date.strftime("%Y-%m-%d")
        }
        
        data = self._make_request("fixtures", params)
        return data.get("response", [])
    
    def extract_match_statistics(self, statistics: List[Dict]) -> Dict:
        """
        Extrai estatísticas relevantes de uma partida
        
        Args:
            statistics: Estatísticas brutas da API
            
        Returns:
            Estatísticas processadas
        """
        processed = {
            "home": {},
            "away": {}
        }
        
        if not statistics or len(statistics) < 2:
            return processed
        
        home_stats = statistics[0].get("statistics", [])
        away_stats = statistics[1].get("statistics", [])
        
        # Mapeia estatísticas
        stat_mapping = {
            "Shots on Goal": "shots_on_goal",
            "Total Shots": "total_shots",
            "Blocked Shots": "blocked_shots",
            "Shots insidebox": "shots_inside_box",
            "Shots outsidebox": "shots_outside_box",
            "Fouls": "fouls",
            "Corner Kicks": "corners",
            "Yellow Cards": "yellow_cards",
            "Red Cards": "red_cards",
            "Goalkeeper Saves": "goalkeeper_saves",
            "Total passes": "total_passes",
            "Passes accurate": "passes_accurate",
            "Passes %": "pass_accuracy"
        }
        
        for stat in home_stats:
            stat_type = stat.get("type")
            if stat_type in stat_mapping:
                key = stat_mapping[stat_type]
                value = stat.get("value")
                # Converte para número se possível
                try:
                    if value is not None and value != "":
                        if "%" in str(value):
                            value = float(str(value).replace("%", ""))
                        else:
                            value = float(value)
                except:
                    pass
                processed["home"][key] = value
        
        for stat in away_stats:
            stat_type = stat.get("type")
            if stat_type in stat_mapping:
                key = stat_mapping[stat_type]
                value = stat.get("value")
                # Converte para número se possível
                try:
                    if value is not None and value != "":
                        if "%" in str(value):
                            value = float(str(value).replace("%", ""))
                        else:
                            value = float(value)
                except:
                    pass
                processed["away"][key] = value
        
        return processed
    
    def get_request_count(self) -> int:
        """Retorna número de requisições feitas"""
        return self.request_count
    
    def reset_request_count(self):
        """Reseta contador de requisições"""
        self.request_count = 0


# Exemplo de uso
if __name__ == "__main__":
    # Nota: Você precisa configurar API_FOOTBALL_KEY no arquivo .env
    collector = FootballDataCollector()
    
    print("Buscando ligas do Brasil...")
    try:
        leagues = collector.get_leagues("Brazil")
        for league in leagues[:3]:
            print(f"- {league['league']['name']} (ID: {league['league']['id']})")
    except Exception as e:
        print(f"Erro: {e}")
    
    print(f"\nRequisições feitas: {collector.get_request_count()}")

