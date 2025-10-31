"""
Coletor de dados da API football-data.org
Documentação: https://www.football-data.org/documentation/quickstart
"""
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class FootballDataCollector:
    """
    Coleta dados da API football-data.org

    Tier Gratuito: 10 requisições por minuto
    Endpoints disponíveis: /competitions, /teams, /matches, /standings
    """

    def __init__(self, api_key: str = None):
        """
        Inicializa o coletor

        Args:
            api_key: Token da API football-data.org
        """
        self.api_key = api_key or "YOUR_API_KEY_HERE"
        self.base_url = "https://api.football-data.org/v4"
        self.headers = {
            "X-Auth-Token": self.api_key
        }
        self.request_count = 0

        # Mapeamento de códigos de competição
        self.competitions = {
            "PL": 2021,    # Premier League
            "PD": 2014,    # La Liga (Primera División)
            "BL1": 2002,   # Bundesliga
            "SA": 2019,    # Serie A
            "FL1": 2015,   # Ligue 1
            "CL": 2001,    # Champions League
            "BSA": 2013,   # Brasileirão Série A
            "PPL": 2017,   # Primeira Liga (Portugal)
            "DED": 2003,   # Eredivisie (Holanda)
            "EC": 2018,    # European Championship
            "WC": 2000     # World Cup
        }

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Faz requisição à API

        Args:
            endpoint: Endpoint da API
            params: Parâmetros opcionais

        Returns:
            Resposta JSON
        """
        url = f"{self.base_url}/{endpoint}"

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            self.request_count += 1
            return response.json()

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                raise Exception("Limite de requisições atingido (10/min no tier gratuito)")
            elif e.response.status_code == 403:
                raise Exception("API key inválida ou sem acesso a esta competição")
            else:
                raise Exception(f"Erro HTTP {e.response.status_code}: {e.response.text}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro na requisição: {str(e)}")

    def get_competition_id(self, code: str) -> int:
        """
        Obtém ID da competição pelo código

        Args:
            code: Código da competição (ex: PL, BSA, CL)

        Returns:
            ID da competição
        """
        return self.competitions.get(code.upper(), None)

    def get_competitions(self) -> List[Dict]:
        """
        Lista todas as competições disponíveis

        Returns:
            Lista de competições
        """
        data = self._make_request("competitions")
        return data.get("competitions", [])

    def get_teams(self, competition_code: str) -> List[Dict]:
        """
        Busca times de uma competição

        Args:
            competition_code: Código da competição (ex: PL, BSA)

        Returns:
            Lista de times
        """
        comp_id = self.get_competition_id(competition_code)
        if not comp_id:
            raise Exception(f"Competição '{competition_code}' não encontrada")

        data = self._make_request(f"competitions/{comp_id}/teams")
        return data.get("teams", [])

    def get_matches(
        self,
        competition_code: str = None,
        team_id: int = None,
        status: str = "SCHEDULED",
        date_from: str = None,
        date_to: str = None
    ) -> List[Dict]:
        """
        Busca partidas

        Args:
            competition_code: Código da competição (ex: PL, BSA)
            team_id: ID do time (opcional)
            status: Status da partida (SCHEDULED, LIVE, FINISHED)
            date_from: Data inicial (YYYY-MM-DD)
            date_to: Data final (YYYY-MM-DD)

        Returns:
            Lista de partidas
        """
        if competition_code:
            comp_id = self.get_competition_id(competition_code)
            if not comp_id:
                raise Exception(f"Competição '{competition_code}' não encontrada")
            endpoint = f"competitions/{comp_id}/matches"
        elif team_id:
            endpoint = f"teams/{team_id}/matches"
        else:
            endpoint = "matches"

        params = {}
        if status:
            params["status"] = status
        if date_from:
            params["dateFrom"] = date_from
        if date_to:
            params["dateTo"] = date_to

        data = self._make_request(endpoint, params)
        return data.get("matches", [])

    def get_standings(self, competition_code: str) -> Dict:
        """
        Busca classificação de uma competição

        Args:
            competition_code: Código da competição (ex: PL, BSA)

        Returns:
            Tabela de classificação
        """
        comp_id = self.get_competition_id(competition_code)
        if not comp_id:
            raise Exception(f"Competição '{competition_code}' não encontrada")

        data = self._make_request(f"competitions/{comp_id}/standings")
        return data

    def get_team_matches_history(
        self,
        team_id: int,
        last_n: int = 10,
        status: str = "FINISHED",
        date_from: str = None,
        date_to: str = None
    ) -> List[Dict]:
        """
        Busca histórico de partidas de um time

        Args:
            team_id: ID do time
            last_n: Número de partidas (limitado pela API)
            status: Status das partidas
            date_from: Data inicial (YYYY-MM-DD) - opcional
            date_to: Data final (YYYY-MM-DD) - opcional

        Returns:
            Lista de partidas
        """
        params = {
            "status": status,
            "limit": last_n
        }

        if date_from:
            params["dateFrom"] = date_from
        if date_to:
            params["dateTo"] = date_to

        data = self._make_request(f"teams/{team_id}/matches", params)
        matches = data.get("matches", [])

        # Filtra apenas partidas finalizadas e ordena por data
        finished = [m for m in matches if m.get("status") == "FINISHED"]
        finished.sort(key=lambda x: x.get("utcDate", ""), reverse=True)

        return finished[:last_n]

    def get_head_to_head(self, team1_id: int, team2_id: int) -> List[Dict]:
        """
        Busca confrontos diretos (head-to-head)

        Args:
            team1_id: ID do primeiro time
            team2_id: ID do segundo time

        Returns:
            Lista de confrontos
        """
        # A API football-data.org não tem endpoint direto de H2H
        # Vamos buscar as partidas de ambos os times e filtrar
        matches1 = self.get_team_matches_history(team1_id, last_n=50)

        h2h = []
        for match in matches1:
            home_id = match.get("homeTeam", {}).get("id")
            away_id = match.get("awayTeam", {}).get("id")

            if (home_id == team1_id and away_id == team2_id) or \
               (home_id == team2_id and away_id == team1_id):
                h2h.append(match)

        return h2h[:10]  # Últimos 10 confrontos

    def search_team_by_name(self, team_name: str, competition_code: str) -> Optional[Dict]:
        """
        Busca time por nome em uma competição

        Args:
            team_name: Nome do time
            competition_code: Código da competição

        Returns:
            Dados do time ou None
        """
        teams = self.get_teams(competition_code)

        # Busca exata
        for team in teams:
            if team_name.lower() in team.get("name", "").lower() or \
               team_name.lower() in team.get("shortName", "").lower():
                return team

        return None

    def get_request_count(self) -> int:
        """Retorna número de requisições feitas"""
        return self.request_count

    def reset_request_count(self):
        """Reseta contador de requisições"""
        self.request_count = 0


# Exemplo de uso
if __name__ == "__main__":
    import os

    # Obter API key do ambiente
    api_key = os.getenv("FOOTBALL_DATA_API_KEY", "YOUR_API_KEY_HERE")

    collector = FootballDataCollector(api_key)

    print("=== Football-Data.org API Collector ===\n")

    # Listar competições
    print("Competições disponíveis:")
    for code, comp_id in list(collector.competitions.items())[:5]:
        print(f"  {code}: ID {comp_id}")

    # Buscar times da Premier League
    print("\n\nBuscando times da Premier League...")
    try:
        teams = collector.get_teams("PL")
        print(f"Encontrados {len(teams)} times")
        for team in teams[:3]:
            print(f"  - {team['name']} (ID: {team['id']})")
    except Exception as e:
        print(f"Erro: {e}")

    print(f"\nRequisições feitas: {collector.get_request_count()}")
