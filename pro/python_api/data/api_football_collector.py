"""
Coletor de dados da API-Football v3
Documentação: https://www.api-football.com/documentation-v3

Recursos:
- Estatísticas detalhadas (corners, fouls, shots, possession)
- Eventos de jogo (gols, cartões, substituições)
- Escalações (lineups)
- Odds/Probabilidades
- Dados em tempo real (atualização a cada 15s)
"""
import requests
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class APIFootballCollector:
    """
    Coletor para API-Football v3

    Rate Limits (Plano Free):
    - 100 requisições por dia
    - 10 requisições por minuto
    """

    def __init__(self, api_key: str = None):
        """
        Args:
            api_key: Token da API-Football v3
        """
        self.api_key = api_key or "YOUR_API_KEY_HERE"
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            "x-apisports-key": self.api_key
        }
        self.request_count = 0
        self.last_request_time = None

        # Mapeamento de ligas (ID da API-Football)
        self.leagues = {
            "PL": 39,      # Premier League
            "PD": 140,     # La Liga
            "BL1": 78,     # Bundesliga
            "SA": 135,     # Serie A
            "FL1": 61,     # Ligue 1
            "CL": 2,       # Champions League
            "BSA": 71,     # Brasileirão Série A
            "PPL": 94,     # Primeira Liga (Portugal)
            "DED": 88,     # Eredivisie (Holanda)
        }

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Faz requisição à API com tratamento de rate limit

        Args:
            endpoint: Endpoint da API (ex: "fixtures")
            params: Parâmetros da consulta

        Returns:
            Dados da resposta
        """
        # Rate limiting básico (espera 6s entre requests para Free tier)
        if self.last_request_time:
            elapsed = time.time() - self.last_request_time
            if elapsed < 6.0:  # 10 req/min = 1 a cada 6s
                time.sleep(6.0 - elapsed)

        url = f"{self.base_url}/{endpoint}"

        try:
            response = requests.get(url, headers=self.headers, params=params or {})
            response.raise_for_status()

            self.request_count += 1
            self.last_request_time = time.time()

            data = response.json()

            # Verifica erros na resposta
            if data.get("errors"):
                print(f"⚠️ API Warning: {data['errors']}")

            # Log dos rate limits
            remaining = response.headers.get('x-ratelimit-requests-remaining')
            if remaining:
                print(f"  Rate Limit: {remaining} requests restantes hoje")

            return data

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("❌ Rate limit excedido! Aguarde 1 minuto...")
                time.sleep(60)
                return self._make_request(endpoint, params)
            elif e.response.status_code == 403:
                print("❌ Acesso negado. Verifique sua API key ou plano de subscrição.")
            else:
                print(f"❌ Erro HTTP {e.response.status_code}: {e}")
            raise

        except Exception as e:
            print(f"❌ Erro ao fazer requisição: {e}")
            raise

    def get_league_id(self, competition_code: str) -> Optional[int]:
        """Converte código de competição para ID da API-Football"""
        return self.leagues.get(competition_code)

    def get_leagues(self, country: str = None, season: int = None) -> List[Dict]:
        """
        Busca ligas disponíveis

        Args:
            country: Nome do país (ex: "Brazil")
            season: Ano da temporada (ex: 2024)

        Returns:
            Lista de ligas
        """
        params = {}
        if country:
            params["country"] = country
        if season:
            params["season"] = season

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
        league_id: int = None,
        season: int = None,
        team_id: int = None,
        date: str = None,
        status: str = None,
        last: int = None,
        next: int = None
    ) -> List[Dict]:
        """
        Busca fixtures (partidas)

        Args:
            league_id: ID da liga
            season: Ano da temporada
            team_id: ID do time
            date: Data no formato YYYY-MM-DD
            status: Status (ex: "FT" para finalizados, "NS" para agendados)
            last: Últimas N partidas
            next: Próximas N partidas

        Returns:
            Lista de fixtures
        """
        params = {}
        if league_id:
            params["league"] = league_id
        if season:
            params["season"] = season
        if team_id:
            params["team"] = team_id
        if date:
            params["date"] = date
        if status:
            params["status"] = status
        if last:
            params["last"] = last
        if next:
            params["next"] = next

        data = self._make_request("fixtures", params)
        return data.get("response", [])

    def get_fixture_statistics(self, fixture_id: int) -> List[Dict]:
        """
        Busca estatísticas DETALHADAS de uma partida

        Inclui:
        - Posse de bola
        - Chutes (total, no gol, fora, bloqueados)
        - Escanteios
        - Faltas
        - Cartões
        - Impedimentos
        - Passes
        - Expected Goals (xG)

        Args:
            fixture_id: ID da partida

        Returns:
            Estatísticas por time (array com 2 objetos: home e away)
        """
        params = {"fixture": fixture_id}
        data = self._make_request("fixtures/statistics", params)
        return data.get("response", [])

    def get_fixture_events(self, fixture_id: int) -> List[Dict]:
        """
        Busca eventos da partida (gols, cartões, substituições)

        Args:
            fixture_id: ID da partida

        Returns:
            Lista de eventos cronológicos
        """
        params = {"fixture": fixture_id}
        data = self._make_request("fixtures/events", params)
        return data.get("response", [])

    def get_fixture_lineups(self, fixture_id: int) -> List[Dict]:
        """
        Busca escalações da partida

        Args:
            fixture_id: ID da partida

        Returns:
            Escalações por time
        """
        params = {"fixture": fixture_id}
        data = self._make_request("fixtures/lineups", params)
        return data.get("response", [])

    def get_odds(
        self,
        fixture_id: int = None,
        league_id: int = None,
        season: int = None,
        bookmaker_id: int = None
    ) -> List[Dict]:
        """
        Busca odds/probabilidades

        Args:
            fixture_id: ID da partida
            league_id: ID da liga
            season: Ano da temporada
            bookmaker_id: ID da casa de apostas

        Returns:
            Odds disponíveis
        """
        params = {}
        if fixture_id:
            params["fixture"] = fixture_id
        if league_id:
            params["league"] = league_id
        if season:
            params["season"] = season
        if bookmaker_id:
            params["bookmaker"] = bookmaker_id

        data = self._make_request("odds", params)
        return data.get("response", [])

    def get_standings(self, league_id: int, season: int) -> List[Dict]:
        """
        Busca classificação da liga

        Args:
            league_id: ID da liga
            season: Ano da temporada

        Returns:
            Classificação
        """
        params = {
            "league": league_id,
            "season": season
        }

        data = self._make_request("standings", params)
        return data.get("response", [])

    def get_team_statistics(self, league_id: int, season: int, team_id: int) -> Dict:
        """
        Busca estatísticas completas de um time na temporada

        Args:
            league_id: ID da liga
            season: Ano da temporada
            team_id: ID do time

        Returns:
            Estatísticas do time
        """
        params = {
            "league": league_id,
            "season": season,
            "team": team_id
        }

        data = self._make_request("teams/statistics", params)
        response = data.get("response")
        return response if response else {}

    def parse_statistics_to_dict(self, stats_array: List[Dict]) -> Dict:
        """
        Converte array de estatísticas da API para dicionário estruturado

        Args:
            stats_array: Array retornado por get_fixture_statistics()

        Returns:
            Dict com estatísticas de home e away
        """
        result = {
            "home": {},
            "away": {}
        }

        if not stats_array or len(stats_array) < 2:
            return result

        # Processa cada time (home e away)
        for team_stats in stats_array:
            team_name = team_stats.get("team", {}).get("name", "")
            is_home = stats_array.index(team_stats) == 0  # Primeiro é home
            key = "home" if is_home else "away"

            # Extrai estatísticas
            statistics = team_stats.get("statistics", [])

            # Cria mapa de estatísticas
            stats_map = {}
            for stat in statistics:
                stat_type = stat.get("type")
                stat_value = stat.get("value")

                # Converte valores
                if stat_value is None:
                    stat_value = 0
                elif isinstance(stat_value, str):
                    # Remove % e converte para int
                    stat_value = stat_value.replace("%", "")
                    try:
                        stat_value = int(stat_value) if "." not in stat_value else float(stat_value)
                    except:
                        stat_value = 0

                stats_map[stat_type] = stat_value

            result[key] = stats_map

        return result


# Exemplo de uso
if __name__ == "__main__":
    # Cria instância do coletor
    collector = APIFootballCollector(api_key="YOUR_API_KEY")

    # Exemplo 1: Buscar ligas do Brasil
    print("📋 Ligas do Brasil:")
    leagues = collector.get_leagues(country="Brazil", season=2024)
    for league in leagues[:3]:
        print(f"  - {league['league']['name']} (ID: {league['league']['id']})")

    # Exemplo 2: Buscar times do Brasileirão 2024
    print("\n⚽ Times do Brasileirão 2024:")
    teams = collector.get_teams(league_id=71, season=2024)
    for team in teams[:5]:
        print(f"  - {team['team']['name']} (ID: {team['team']['id']})")

    # Exemplo 3: Buscar últimas partidas finalizadas
    print("\n🏆 Últimas partidas do Brasileirão:")
    fixtures = collector.get_fixtures(league_id=71, season=2024, status="FT", last=3)
    for fixture in fixtures:
        home = fixture['teams']['home']['name']
        away = fixture['teams']['away']['name']
        score_home = fixture['goals']['home']
        score_away = fixture['goals']['away']
        print(f"  - {home} {score_home} x {score_away} {away}")

    print(f"\n✅ Total de requisições: {collector.request_count}")
