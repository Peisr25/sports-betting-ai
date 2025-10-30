"""
Sistema de Coleta Incremental de Dados Históricos
Respeita rate limit de 10 req/min da API football-data.org
"""
import time
import sys
from datetime import datetime
from typing import List, Dict
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.collector import FootballDataCollector
from data.database import Database


class HistoricalDataCollector:
    """
    Coleta dados históricos de competições respeitando rate limit

    Features:
    - Respeita 10 req/min do tier gratuito
    - Salva no banco SQLite
    - Retoma coleta de onde parou
    - Mostra progresso em tempo real
    """

    def __init__(self, api_key: str, db_path: str = "database/betting.db"):
        """
        Args:
            api_key: Token da API football-data.org
            db_path: Caminho para o banco SQLite
        """
        self.collector = FootballDataCollector(api_key)
        self.db = Database(db_path)

        # Rate limit: 10 req/min = 1 req a cada 6 segundos
        self.request_delay = 6.5  # segundos (margem de segurança)

    def collect_competition_season(
        self,
        competition_code: str,
        season: int = 2024,
        save_to_db: bool = True
    ) -> Dict:
        """
        Coleta todos os dados de uma temporada

        Args:
            competition_code: Código da competição (BSA, PL, etc)
            season: Ano da temporada
            save_to_db: Se deve salvar no banco

        Returns:
            Estatísticas da coleta
        """
        print(f"\n{'='*70}")
        print(f"COLETA DE DADOS HISTÓRICOS")
        print(f"{'='*70}")
        print(f"Competição: {competition_code}")
        print(f"Temporada: {season}")
        print(f"Rate Limit: {self.request_delay}s entre requisições")
        print(f"{'='*70}\n")

        stats = {
            "teams_collected": 0,
            "matches_collected": 0,
            "requests_made": 0,
            "time_elapsed": 0,
            "errors": []
        }

        start_time = time.time()

        try:
            # 1. Buscar times da competição
            print("📋 Buscando times...")
            teams = self.collector.get_teams(competition_code)
            print(f"✓ Encontrados {len(teams)} times\n")

            stats["requests_made"] += 1
            time.sleep(self.request_delay)

            # 2. Para cada time, buscar partidas
            for i, team in enumerate(teams, 1):
                team_name = team.get("name", "Unknown")
                team_id = team.get("id")

                print(f"[{i}/{len(teams)}] Coletando dados de: {team_name}")

                try:
                    # Buscar partidas do time
                    matches = self.collector.get_team_matches_history(
                        team_id,
                        last_n=50  # Máximo permitido pela API
                    )

                    stats["requests_made"] += 1

                    # Salvar no banco
                    if save_to_db:
                        saved_count = self._save_matches_to_db(
                            matches,
                            competition_code,
                            season
                        )
                        stats["matches_collected"] += saved_count
                        print(f"  ✓ Salvas {saved_count} partidas no banco")
                    else:
                        stats["matches_collected"] += len(matches)
                        print(f"  ✓ Coletadas {len(matches)} partidas")

                    stats["teams_collected"] += 1

                    # Respeitar rate limit
                    if i < len(teams):  # Não esperar no último
                        print(f"  ⏳ Aguardando {self.request_delay}s (rate limit)...")
                        time.sleep(self.request_delay)

                except Exception as e:
                    error_msg = f"Erro ao coletar {team_name}: {e}"
                    print(f"  ✗ {error_msg}")
                    stats["errors"].append(error_msg)

                print()  # Linha em branco

        except Exception as e:
            error_msg = f"Erro geral: {e}"
            print(f"\n✗ {error_msg}")
            stats["errors"].append(error_msg)

        # Estatísticas finais
        stats["time_elapsed"] = time.time() - start_time

        print(f"{'='*70}")
        print("COLETA FINALIZADA")
        print(f"{'='*70}")
        print(f"Times coletados: {stats['teams_collected']}/{len(teams) if 'teams' in locals() else 0}")
        print(f"Partidas salvas: {stats['matches_collected']}")
        print(f"Requisições feitas: {stats['requests_made']}")
        print(f"Tempo total: {stats['time_elapsed']/60:.1f} minutos")
        print(f"Erros: {len(stats['errors'])}")

        if stats["errors"]:
            print("\n⚠️  Erros encontrados:")
            for error in stats["errors"][:5]:  # Mostra apenas os 5 primeiros
                print(f"  - {error}")

        print(f"{'='*70}\n")

        return stats

    def _save_matches_to_db(
        self,
        matches: List[Dict],
        competition: str,
        season: int
    ) -> int:
        """Salva partidas no banco evitando duplicatas"""
        saved_count = 0

        for match in matches:
            try:
                match_id = match.get("id")

                # Verifica se já existe
                existing = self.db.session.query(self.db.Match).filter_by(
                    match_id=match_id
                ).first()

                if existing:
                    continue  # Pula duplicatas

                # Extrai dados da partida
                match_data = {
                    "match_id": match_id,
                    "competition": competition,
                    "home_team": match.get("homeTeam", {}).get("name", "Unknown"),
                    "away_team": match.get("awayTeam", {}).get("name", "Unknown"),
                    "home_score": match.get("score", {}).get("fullTime", {}).get("home"),
                    "away_score": match.get("score", {}).get("fullTime", {}).get("away"),
                    "match_date": datetime.fromisoformat(
                        match.get("utcDate", "").replace('Z', '+00:00')
                    ),
                    "status": match.get("status", "UNKNOWN")
                }

                # Salva no banco
                self.db.save_match(match_data)
                saved_count += 1

            except Exception as e:
                print(f"    ⚠️ Erro ao salvar partida {match.get('id')}: {e}")

        return saved_count

    def get_db_stats(self, competition: str = None) -> Dict:
        """Retorna estatísticas do banco de dados"""
        from sqlalchemy import func

        query = self.db.session.query(
            func.count(self.db.Match.id).label('total_matches'),
            func.count(func.distinct(self.db.Match.competition)).label('competitions')
        )

        if competition:
            query = query.filter(self.db.Match.competition == competition)

        result = query.first()

        return {
            "total_matches": result.total_matches if result else 0,
            "competitions": result.competitions if result else 0
        }


def main():
    """Exemplo de uso"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Coleta dados históricos de competições"
    )
    parser.add_argument(
        "competition",
        help="Código da competição (BSA, PL, PD, etc)"
    )
    parser.add_argument(
        "--season",
        type=int,
        default=2024,
        help="Temporada (padrão: 2024)"
    )
    parser.add_argument(
        "--api-key",
        help="API key (ou use variável de ambiente FOOTBALL_DATA_API_KEY)"
    )
    parser.add_argument(
        "--db",
        default="database/betting.db",
        help="Caminho do banco SQLite"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simular sem salvar no banco"
    )

    args = parser.parse_args()

    # Obter API key
    api_key = args.api_key or os.getenv("FOOTBALL_DATA_API_KEY")

    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("❌ API key não configurada!")
        print("\nOpções:")
        print("1. Passe --api-key SUA_KEY")
        print("2. Configure FOOTBALL_DATA_API_KEY no .env")
        print("3. Exporte: export FOOTBALL_DATA_API_KEY=sua_key")
        return

    # Criar coletor
    collector = HistoricalDataCollector(api_key, args.db)

    # Mostrar estatísticas do banco antes
    print("\n📊 Estatísticas do banco ANTES da coleta:")
    stats_before = collector.get_db_stats(args.competition)
    print(f"  Partidas no banco: {stats_before['total_matches']}")
    print()

    # Confirmar
    if not args.dry_run:
        confirm = input(f"Iniciar coleta de {args.competition} {args.season}? (s/n): ")
        if confirm.lower() != 's':
            print("Operação cancelada.")
            return

    # Coletar
    stats = collector.collect_competition_season(
        args.competition,
        args.season,
        save_to_db=not args.dry_run
    )

    # Mostrar estatísticas do banco depois
    if not args.dry_run:
        print("\n📊 Estatísticas do banco DEPOIS da coleta:")
        stats_after = collector.get_db_stats(args.competition)
        print(f"  Partidas no banco: {stats_after['total_matches']}")
        print(f"  Novas partidas: +{stats_after['total_matches'] - stats_before['total_matches']}")


if __name__ == "__main__":
    main()
