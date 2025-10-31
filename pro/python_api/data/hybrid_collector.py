"""
Sistema HÍBRIDO que combina duas APIs:
1. football-data.org - Dados básicos (gratuito, boa cobertura Europa)
2. API-Football v3 - Estatísticas detalhadas (corners, fouls, shots, etc)

Estratégia:
- Usar football-data.org para fixtures básicos (economiza quota da API-Football)
- Usar API-Football v3 para estatísticas detalhadas (onde realmente vale a pena)
- Combinar dados no database expandido
- Maximizar dados disponíveis usando ambas as fontes
"""
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from data.collector import FootballDataCollector
from data.api_football_collector import APIFootballCollector
from data.database_v2 import Database, Match, MatchStatistics, MatchEvent, Team


class HybridCollector:
    """
    Coletor híbrido que combina dados de duas APIs

    Filosofia:
    - football-data.org: Source primária para fixtures (10 req/min grátis)
    - API-Football v3: Source secundária para dados ricos (100 req/dia grátis)
    """

    def __init__(
        self,
        fd_api_key: str = None,
        apif_api_key: str = None,
        db_path: str = "database/betting_v2.db"
    ):
        """
        Args:
            fd_api_key: Chave da football-data.org
            apif_api_key: Chave da API-Football v3
            db_path: Caminho do banco de dados
        """
        self.fd_collector = FootballDataCollector(fd_api_key) if fd_api_key else None
        self.apif_collector = APIFootballCollector(apif_api_key) if apif_api_key else None
        self.db = Database(db_path)

        # Mapeamento de IDs de ligas entre as duas APIs
        self.league_mapping = {
            # Código -> (ID football-data, ID API-Football)
            "PL": (2021, 39),      # Premier League
            "PD": (2014, 140),     # La Liga
            "BL1": (2002, 78),     # Bundesliga
            "SA": (2019, 135),     # Serie A
            "FL1": (2015, 61),     # Ligue 1
            "CL": (2001, 2),       # Champions League
            "BSA": (2013, 71),     # Brasileirão
            "PPL": (2017, 94),     # Primeira Liga
            "DED": (2003, 88),     # Eredivisie
        }

        # Estatísticas
        self.stats = {
            "fd_requests": 0,
            "apif_requests": 0,
            "matches_saved": 0,
            "stats_saved": 0,
            "events_saved": 0
        }

    def collect_match_comprehensive(
        self,
        competition_code: str,
        match_date: str = None,
        team_name: str = None,
        include_statistics: bool = True,
        include_events: bool = True
    ) -> List[Match]:
        """
        Coleta dados COMPLETOS de partidas usando ambas APIs

        Fluxo:
        1. Busca fixtures básicos na football-data.org (rápido, gratuito)
        2. Para cada fixture, busca estatísticas detalhadas na API-Football v3
        3. Salva tudo no banco de dados expandido

        Args:
            competition_code: Código da competição (ex: "BSA", "PL")
            match_date: Data no formato YYYY-MM-DD (opcional)
            team_name: Nome do time para filtrar (opcional)
            include_statistics: Se deve buscar estatísticas detalhadas
            include_events: Se deve buscar eventos da partida

        Returns:
            Lista de Match objects salvos no banco
        """
        print(f"\n{'='*70}")
        print(f"COLETA HÍBRIDA - {competition_code}")
        print(f"{'='*70}\n")

        matches_saved = []

        # FASE 1: Buscar fixtures básicos na football-data.org
        print("📊 FASE 1: Buscando fixtures (football-data.org)...")

        if not self.fd_collector:
            print("  ⚠️ API football-data.org não configurada!")
            return matches_saved

        try:
            fd_matches = self.fd_collector.get_matches(
                competition_code=competition_code,
                status="FINISHED"
            )
            self.stats["fd_requests"] += 1
            print(f"  ✓ Encontrados {len(fd_matches)} fixtures")

        except Exception as e:
            print(f"  ❌ Erro ao buscar fixtures: {e}")
            return matches_saved

        # FASE 2: Para cada fixture, buscar dados detalhados
        print(f"\n📊 FASE 2: Enriquecendo com dados detalhados (API-Football v3)...")

        for i, fd_match in enumerate(fd_matches, 1):
            try:
                # Extrair dados básicos do football-data.org
                match_data = self._parse_fd_match(fd_match, competition_code)

                # Salvar match básico
                match_obj = self.db.save_match(match_data)
                self.stats["matches_saved"] += 1

                print(f"\n[{i}/{len(fd_matches)}] {match_data['home_team']} vs {match_data['away_team']}")

                # Se temos API-Football configurada, buscar dados extras
                if self.apif_collector and match_obj.match_id_fd:

                    # Tentar encontrar o fixture correspondente na API-Football
                    apif_fixture_id = self._find_apif_fixture(
                        match_obj,
                        competition_code
                    )

                    if apif_fixture_id:
                        # Atualizar match com ID da API-Football
                        match_obj.match_id_apif = apif_fixture_id
                        match_obj.data_source = "both"
                        self.db.session.commit()

                        # Buscar estatísticas detalhadas
                        if include_statistics:
                            self._fetch_and_save_statistics(match_obj.id, apif_fixture_id)

                        # Buscar eventos
                        if include_events:
                            self._fetch_and_save_events(match_obj.id, apif_fixture_id)

                        print(f"  ✓ Dados completos salvos (ambas APIs)")
                    else:
                        print(f"  ⚠️ Fixture não encontrado na API-Football")

                matches_saved.append(match_obj)

                # Rate limiting: espera entre partidas
                if i < len(fd_matches):
                    time.sleep(1)  # 1s entre processamento de matches

            except Exception as e:
                print(f"  ❌ Erro ao processar match: {e}")
                continue

        # Resumo final
        print(f"\n{'='*70}")
        print("COLETA FINALIZADA")
        print(f"{'='*70}")
        print(f"Partidas salvas: {self.stats['matches_saved']}")
        print(f"Estatísticas salvas: {self.stats['stats_saved']}")
        print(f"Eventos salvos: {self.stats['events_saved']}")
        print(f"Requisições football-data.org: {self.stats['fd_requests']}")
        print(f"Requisições API-Football: {self.stats['apif_requests']}")
        print(f"{'='*70}\n")

        return matches_saved

    def _parse_fd_match(self, fd_match: Dict, competition_code: str) -> Dict:
        """
        Converte fixture da football-data.org para formato do banco

        Args:
            fd_match: Dados do match da football-data.org
            competition_code: Código da competição

        Returns:
            Dict pronto para salvar no banco
        """
        utc_date = fd_match.get("utcDate", "")
        match_date = datetime.fromisoformat(utc_date.replace('Z', '+00:00')) if utc_date else None

        score = fd_match.get("score", {})
        full_time = score.get("fullTime", {})
        half_time = score.get("halfTime", {})

        return {
            "match_id_fd": fd_match.get("id"),
            "competition": competition_code,
            "season": fd_match.get("season", {}).get("startDate", "")[:4],  # Ano
            "home_team": fd_match.get("homeTeam", {}).get("name", "Unknown"),
            "away_team": fd_match.get("awayTeam", {}).get("name", "Unknown"),
            "home_team_id_fd": fd_match.get("homeTeam", {}).get("id"),
            "away_team_id_fd": fd_match.get("awayTeam", {}).get("id"),
            "home_score": full_time.get("home"),
            "away_score": full_time.get("away"),
            "home_score_ht": half_time.get("home"),
            "away_score_ht": half_time.get("away"),
            "match_date": match_date,
            "status": fd_match.get("status"),
            "data_source": "football-data"
        }

    def _find_apif_fixture(self, match: Match, competition_code: str) -> Optional[int]:
        """
        Encontra o fixture correspondente na API-Football

        Estratégia:
        1. Busca por data e liga
        2. Compara nomes dos times
        3. Retorna ID se encontrar match

        Args:
            match: Match object do banco
            competition_code: Código da competição

        Returns:
            ID do fixture na API-Football ou None
        """
        if not self.apif_collector:
            return None

        # Obter ID da liga na API-Football
        league_ids = self.league_mapping.get(competition_code)
        if not league_ids:
            return None

        apif_league_id = league_ids[1]

        # Buscar fixtures da mesma data
        date_str = match.match_date.strftime("%Y-%m-%d")

        try:
            fixtures = self.apif_collector.get_fixtures(
                league_id=apif_league_id,
                date=date_str
            )
            self.stats["apif_requests"] += 1

            # Procurar match pelos nomes dos times
            for fixture in fixtures:
                home_name = fixture["teams"]["home"]["name"].lower()
                away_name = fixture["teams"]["away"]["name"].lower()

                match_home = match.home_team.lower()
                match_away = match.away_team.lower()

                # Comparação flexível (contém)
                if (match_home in home_name or home_name in match_home) and \
                   (match_away in away_name or away_name in match_away):
                    return fixture["fixture"]["id"]

        except Exception as e:
            print(f"    ⚠️ Erro ao buscar fixture na API-Football: {e}")

        return None

    def _fetch_and_save_statistics(self, match_id: int, apif_fixture_id: int):
        """
        Busca e salva estatísticas detalhadas da API-Football

        Args:
            match_id: ID do match no banco
            apif_fixture_id: ID do fixture na API-Football
        """
        try:
            stats_array = self.apif_collector.get_fixture_statistics(apif_fixture_id)
            self.stats["apif_requests"] += 1

            if not stats_array:
                return

            # Parse das estatísticas
            stats_dict = self.apif_collector.parse_statistics_to_dict(stats_array)

            home_stats = stats_dict.get("home", {})
            away_stats = stats_dict.get("away", {})

            # Preparar dados para salvar
            stats_data = {
                "match_id": match_id,
                # Posse
                "home_possession": home_stats.get("Ball Possession", 0),
                "away_possession": away_stats.get("Ball Possession", 0),
                # Chutes
                "home_shots_total": home_stats.get("Total Shots", 0),
                "away_shots_total": away_stats.get("Total Shots", 0),
                "home_shots_on_goal": home_stats.get("Shots on Goal", 0),
                "away_shots_on_goal": away_stats.get("Shots on Goal", 0),
                "home_shots_off_goal": home_stats.get("Shots off Goal", 0),
                "away_shots_off_goal": away_stats.get("Shots off Goal", 0),
                "home_shots_blocked": home_stats.get("Blocked Shots", 0),
                "away_shots_blocked": away_stats.get("Blocked Shots", 0),
                "home_shots_inside_box": home_stats.get("Shots insidebox", 0),
                "away_shots_inside_box": away_stats.get("Shots insidebox", 0),
                "home_shots_outside_box": home_stats.get("Shots outsidebox", 0),
                "away_shots_outside_box": away_stats.get("Shots outsidebox", 0),
                # Escanteios
                "home_corners": home_stats.get("Corner Kicks", 0),
                "away_corners": away_stats.get("Corner Kicks", 0),
                # Impedimentos
                "home_offsides": home_stats.get("Offsides", 0),
                "away_offsides": away_stats.get("Offsides", 0),
                # Faltas
                "home_fouls": home_stats.get("Fouls", 0),
                "away_fouls": away_stats.get("Fouls", 0),
                # Cartões
                "home_yellow_cards": home_stats.get("Yellow Cards", 0),
                "away_yellow_cards": away_stats.get("Yellow Cards", 0),
                "home_red_cards": home_stats.get("Red Cards", 0),
                "away_red_cards": away_stats.get("Red Cards", 0),
                # Defesas
                "home_goalkeeper_saves": home_stats.get("Goalkeeper Saves", 0),
                "away_goalkeeper_saves": away_stats.get("Goalkeeper Saves", 0),
                # Passes
                "home_passes_total": home_stats.get("Total passes", 0),
                "away_passes_total": away_stats.get("Total passes", 0),
                "home_passes_accurate": home_stats.get("Passes accurate", 0),
                "away_passes_accurate": away_stats.get("Passes accurate", 0),
                "home_passes_percentage": home_stats.get("Passes %", 0),
                "away_passes_percentage": away_stats.get("Passes %", 0),
                # Expected Goals
                "home_expected_goals": home_stats.get("expected_goals"),
                "away_expected_goals": away_stats.get("expected_goals"),
                # JSON bruto
                "raw_stats_json": stats_dict
            }

            self.db.save_match_statistics(stats_data)
            self.stats["stats_saved"] += 1
            print(f"    ✓ Estatísticas salvas")

        except Exception as e:
            print(f"    ⚠️ Erro ao buscar estatísticas: {e}")

    def _fetch_and_save_events(self, match_id: int, apif_fixture_id: int):
        """
        Busca e salva eventos da partida (gols, cartões, substituições)

        Args:
            match_id: ID do match no banco
            apif_fixture_id: ID do fixture na API-Football
        """
        try:
            events = self.apif_collector.get_fixture_events(apif_fixture_id)
            self.stats["apif_requests"] += 1

            if not events:
                return

            events_count = 0
            for event in events:
                event_data = {
                    "match_id": match_id,
                    "time_elapsed": event.get("time", {}).get("elapsed", 0),
                    "time_extra": event.get("time", {}).get("extra"),
                    "event_type": event.get("type"),
                    "event_detail": event.get("detail"),
                    "team": "home" if event.get("team", {}).get("id") else "away",
                    "player_name": event.get("player", {}).get("name"),
                    "player_id": event.get("player", {}).get("id"),
                    "assist_player_name": event.get("assist", {}).get("name"),
                    "assist_player_id": event.get("assist", {}).get("id"),
                    "comments": event.get("comments")
                }

                self.db.save_match_event(event_data)
                events_count += 1

            self.stats["events_saved"] += events_count
            print(f"    ✓ {events_count} eventos salvos")

        except Exception as e:
            print(f"    ⚠️ Erro ao buscar eventos: {e}")

    def get_stats_summary(self) -> Dict:
        """Retorna resumo das estatísticas de uso"""
        return self.stats.copy()


# Exemplo de uso
if __name__ == "__main__":
    # Configurar com AMBAS as API keys
    collector = HybridCollector(
        fd_api_key="YOUR_FOOTBALL_DATA_KEY",
        apif_api_key="YOUR_API_FOOTBALL_KEY"
    )

    # Coletar dados COMPLETOS do Brasileirão
    matches = collector.collect_match_comprehensive(
        competition_code="BSA",
        include_statistics=True,
        include_events=True
    )

    print(f"\n✅ {len(matches)} partidas processadas com sucesso!")

    # Ver exemplo de match com stats
    if matches:
        match = collector.db.get_match_with_stats(matches[0].id)
        if match.statistics:
            print(f"\n📊 Exemplo de estatísticas:")
            print(f"  Escanteios: {match.statistics.home_corners} x {match.statistics.away_corners}")
            print(f"  Chutes: {match.statistics.home_shots_total} x {match.statistics.away_shots_total}")
            print(f"  Posse: {match.statistics.home_possession}% x {match.statistics.away_possession}%")
