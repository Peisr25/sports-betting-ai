"""
Coleta dados históricos dos times das partidas ao vivo/agendadas
Usa football-data.org para buscar histórico e estatísticas
"""
import os
import sys
import json
from datetime import datetime
import time
from dotenv import load_dotenv

# Carregar .env da pasta pai (pro/.env)
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.collector import FootballDataCollector
from data.database import Database, Match


class TeamHistoryCollector:
    """Coleta histórico de times para análise de apostas"""
    
    def __init__(self, football_data_key: str):
        self.collector = FootballDataCollector(football_data_key)
        self.db = Database("database/betting.db")
        self.request_delay = 6.5  # Rate limit
    
    def find_team_in_football_data(self, team_name: str, competition_code: str = "BSA") -> dict:
        """
        Tenta encontrar o time na football-data.org
        
        Args:
            team_name: Nome do time (da API-Football)
            competition_code: Código da competição
            
        Returns:
            Dados do time ou None
        """
        try:
            teams = self.collector.get_teams(competition_code)
            
            # Busca por nome similar
            team_name_lower = team_name.lower()
            
            for team in teams:
                team_name_fd = team.get("name", "").lower()
                team_short = team.get("shortName", "").lower()
                
                # Verificar match parcial
                if (team_name_lower in team_name_fd or 
                    team_name_fd in team_name_lower or
                    team_name_lower in team_short or
                    team_short in team_name_lower):
                    return team
            
            return None
            
        except Exception as e:
            print(f"   ⚠️ Erro ao buscar time: {e}")
            return None
    
    def collect_team_history(self, team_id: int, team_name: str, last_n: int = 15) -> list:
        """
        Coleta histórico de partidas do time
        
        Args:
            team_id: ID do time na football-data.org
            team_name: Nome do time
            last_n: Número de partidas
            
        Returns:
            Lista de partidas
        """
        try:
            matches = self.collector.get_team_matches_history(
                team_id,
                last_n=last_n,
                status="FINISHED"
            )
            
            print(f"      ✅ {len(matches)} partidas encontradas")
            
            # Salvar no banco
            saved = 0
            for match in matches:
                try:
                    match_id = match.get("id")
                    
                    # Verificar se já existe
                    existing = self.db.session.query(Match).filter_by(
                        match_id=match_id
                    ).first()
                    
                    if existing:
                        continue
                    
                    # Extrair dados
                    match_date_str = match.get("utcDate", "")
                    match_date = datetime.fromisoformat(
                        match_date_str.replace('Z', '+00:00')
                    )
                    
                    match_data = {
                        "match_id": match_id,
                        "competition": match.get("competition", {}).get("code", "UNKNOWN"),
                        "home_team": match.get("homeTeam", {}).get("name", "Unknown"),
                        "away_team": match.get("awayTeam", {}).get("name", "Unknown"),
                        "home_score": match.get("score", {}).get("fullTime", {}).get("home"),
                        "away_score": match.get("score", {}).get("fullTime", {}).get("away"),
                        "match_date": match_date,
                        "status": match.get("status", "UNKNOWN")
                    }
                    
                    self.db.save_match(match_data)
                    saved += 1
                    
                except Exception as e:
                    continue
            
            if saved > 0:
                print(f"      💾 {saved} partidas novas salvas no banco")
            
            return matches
            
        except Exception as e:
            print(f"      ❌ Erro: {e}")
            return []
    
    def process_live_fixtures_file(self, filename: str = "live_and_upcoming_fixtures.json"):
        """
        Processa o arquivo de fixtures ao vivo/agendadas
        Coleta histórico de todos os times
        """
        if not os.path.exists(filename):
            print(f"❌ Arquivo {filename} não encontrado!")
            print("Execute primeiro: python find_live_and_upcoming.py")
            return
        
        # Carregar fixtures
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        fixtures = data.get("all_fixtures", [])
        
        if not fixtures:
            print("❌ Nenhuma fixture encontrada no arquivo!")
            return
        
        print("\n" + "="*70)
        print("📊 COLETANDO HISTÓRICO DOS TIMES")
        print("="*70)
        print(f"\nTotal de partidas: {len(fixtures)}")
        print(f"Times únicos: calculando...")
        
        # Extrair times únicos
        teams = set()
        for fix in fixtures:
            teams.add((fix["home_team"], fix["home_team_id"]))
            teams.add((fix["away_team"], fix["away_team_id"]))
        
        teams_list = sorted(list(teams))
        print(f"Times únicos: {len(teams_list)}")
        
        # Coletar histórico de cada time
        print("\n🔍 Buscando histórico na football-data.org...")
        print("(Apenas times do Brasileirão terão dados)\n")
        
        success_count = 0
        not_found_count = 0
        error_count = 0
        
        for i, (team_name, apif_team_id) in enumerate(teams_list, 1):
            print(f"[{i}/{len(teams_list)}] {team_name}")
            
            # Tentar encontrar na football-data.org
            team_fd = self.find_team_in_football_data(team_name, "BSA")
            
            if team_fd:
                print(f"   ✅ Encontrado: {team_fd.get('name')}")
                
                # Coletar histórico
                matches = self.collect_team_history(
                    team_fd.get("id"),
                    team_fd.get("name"),
                    last_n=15
                )
                
                if matches:
                    success_count += 1
                else:
                    error_count += 1
                
                # Rate limit
                if i < len(teams_list):
                    time.sleep(self.request_delay)
            else:
                print(f"   ℹ️  Time não encontrado no Brasileirão")
                not_found_count += 1
        
        # Resumo
        print("\n" + "="*70)
        print("📊 RESUMO DA COLETA")
        print("="*70)
        print(f"✅ Times com histórico coletado: {success_count}")
        print(f"ℹ️  Times não encontrados: {not_found_count}")
        print(f"❌ Erros: {error_count}")
        
        # Estatísticas do banco
        total_matches = self.db.session.query(Match).count()
        print(f"\n💾 Total de partidas no banco: {total_matches}")
        
        print("\n💡 Próximo passo:")
        print("   python calculate_predictions.py --from-live-fixtures")
        print("="*70 + "\n")


def main():
    """Interface principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Coleta histórico de times para análise de apostas"
    )
    parser.add_argument(
        "--from-live-fixtures",
        action="store_true",
        help="Usar times do arquivo live_and_upcoming_fixtures.json"
    )
    parser.add_argument(
        "--football-data-key",
        help="API key da football-data.org"
    )
    
    args = parser.parse_args()
    
    # API key
    fd_key = args.football_data_key or os.getenv("FOOTBALL_DATA_API_KEY")
    
    if not fd_key:
        print("❌ FOOTBALL_DATA_API_KEY não configurada!")
        print("Configure no .env ou passe --football-data-key")
        return
    
    collector = TeamHistoryCollector(fd_key)
    
    if args.from_live_fixtures:
        collector.process_live_fixtures_file()
    else:
        print("❌ Use --from-live-fixtures para processar as partidas encontradas")
        print("\nExemplo:")
        print("  python collect_team_history.py --from-live-fixtures")


if __name__ == "__main__":
    main()
