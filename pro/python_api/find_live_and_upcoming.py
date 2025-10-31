"""
Sistema de Descoberta de Partidas para Apostas
Busca partidas AO VIVO e AGENDADAS na API-Football
Essas são as partidas disponíveis para apostar!
"""
import os
import sys
import json
from datetime import datetime, timedelta
from typing import List, Dict
import requests
from dotenv import load_dotenv

# Carregar .env da pasta pai (pro/.env)
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class LiveFixturesFinder:
    """Encontra partidas ao vivo e próximas disponíveis para apostas"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("API_FOOTBALL_KEY")
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            "x-rapidapi-host": "v3.football.api-sports.io",
            "x-rapidapi-key": self.api_key
        }
    
    def get_live_fixtures(self) -> List[Dict]:
        """
        Busca TODAS as partidas ao vivo que você tem acesso
        
        Returns:
            Lista de partidas ao vivo
        """
        url = f"{self.base_url}/fixtures"
        params = {"live": "all"}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("errors") and len(data["errors"]) > 0:
                raise Exception(f"API Error: {data['errors']}")
            
            return data.get("response", [])
            
        except Exception as e:
            print(f"❌ Erro ao buscar partidas ao vivo: {e}")
            return []
    
    def get_upcoming_fixtures(self, days: int = 1) -> List[Dict]:
        """
        Busca partidas agendadas para os próximos N dias
        
        Args:
            days: Número de dias à frente
            
        Returns:
            Lista de partidas agendadas
        """
        fixtures = []
        
        for day_offset in range(days):
            date = datetime.now() + timedelta(days=day_offset)
            date_str = date.strftime("%Y-%m-%d")
            
            url = f"{self.base_url}/fixtures"
            params = {"date": date_str}
            
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                if data.get("errors") and len(data["errors"]) > 0:
                    continue
                
                day_fixtures = data.get("response", [])
                
                # Filtrar apenas partidas não iniciadas
                upcoming = [
                    f for f in day_fixtures 
                    if f["fixture"]["status"]["short"] in ["NS", "TBD", "PST"]
                ]
                
                fixtures.extend(upcoming)
                
            except Exception as e:
                print(f"⚠️ Erro na data {date_str}: {e}")
                continue
        
        return fixtures
    
    def format_fixture_display(self, fixture: Dict) -> Dict:
        """Formata dados da partida para exibição"""
        fix = fixture.get("fixture", {})
        league = fixture.get("league", {})
        teams = fixture.get("teams", {})
        goals = fixture.get("goals", {})
        score = fixture.get("score", {})
        
        # Data e hora
        date_str = fix.get("date", "")
        if date_str:
            try:
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                date_formatted = dt.strftime("%d/%m/%Y %H:%M")
            except:
                date_formatted = date_str
        else:
            date_formatted = "Data desconhecida"
        
        # Status
        status = fix.get("status", {})
        status_long = status.get("long", "Unknown")
        status_short = status.get("short", "?")
        elapsed = status.get("elapsed")
        
        if elapsed:
            status_display = f"{status_long} ({elapsed}')"
        else:
            status_display = status_long
        
        # Placar
        home_goals = goals.get("home")
        away_goals = goals.get("away")
        
        if home_goals is not None and away_goals is not None:
            score_display = f"{home_goals} x {away_goals}"
        else:
            score_display = "- x -"
        
        return {
            "fixture_id": fix.get("id"),
            "date": date_formatted,
            "timestamp": fix.get("timestamp"),
            "league_name": league.get("name", "Unknown"),
            "league_id": league.get("id"),
            "country": league.get("country", "Unknown"),
            "home_team": teams.get("home", {}).get("name", "Unknown"),
            "home_team_id": teams.get("home", {}).get("id"),
            "away_team": teams.get("away", {}).get("name", "Unknown"),
            "away_team_id": teams.get("away", {}).get("id"),
            "status": status_display,
            "status_short": status_short,
            "score": score_display,
            "venue": fix.get("venue", {}).get("name", "Unknown"),
            "raw_data": fixture  # Dados completos para análise
        }


def main():
    """Interface principal"""
    print("\n" + "="*70)
    print("🎯 DESCOBERTA DE PARTIDAS PARA APOSTAS")
    print("="*70)
    
    # Verificar API key
    api_key = os.getenv("API_FOOTBALL_KEY")
    if not api_key:
        print("\n❌ API_FOOTBALL_KEY não configurada!")
        print("Configure no arquivo .env:")
        print("API_FOOTBALL_KEY=sua_key_aqui")
        return
    
    finder = LiveFixturesFinder(api_key)
    
    # Menu
    print("\n📋 Opções:")
    print("  1. Buscar partidas AO VIVO")
    print("  2. Buscar partidas AGENDADAS (próximos dias)")
    print("  3. Buscar AMBAS (ao vivo + agendadas)")
    
    choice = input("\nEscolha [1/2/3]: ").strip() or "3"
    
    all_fixtures = []
    live_count = 0
    upcoming_count = 0
    
    # 1. Buscar ao vivo
    if choice in ["1", "3"]:
        print("\n🔴 Buscando partidas AO VIVO...")
        live_fixtures = finder.get_live_fixtures()
        live_count = len(live_fixtures)
        all_fixtures.extend(live_fixtures)
        print(f"   ✅ {live_count} partidas ao vivo encontradas")
    
    # 2. Buscar agendadas
    if choice in ["2", "3"]:
        days = input("\n📅 Quantos dias à frente buscar? [1]: ").strip() or "1"
        try:
            days = int(days)
        except:
            days = 1
        
        print(f"\n📅 Buscando partidas agendadas ({days} dias)...")
        upcoming_fixtures = finder.get_upcoming_fixtures(days)
        upcoming_count = len(upcoming_fixtures)
        all_fixtures.extend(upcoming_fixtures)
        print(f"   ✅ {upcoming_count} partidas agendadas encontradas")
    
    if not all_fixtures:
        print("\n❌ Nenhuma partida encontrada!")
        return
    
    # Formatar e exibir
    print("\n" + "="*70)
    print("⚽ PARTIDAS DISPONÍVEIS PARA APOSTAR")
    print("="*70)
    
    formatted_fixtures = []
    leagues_stats = {}
    
    for fixture in all_fixtures:
        formatted = finder.format_fixture_display(fixture)
        formatted_fixtures.append(formatted)
        
        # Estatísticas por liga
        league_name = formatted["league_name"]
        if league_name not in leagues_stats:
            leagues_stats[league_name] = {
                "league_id": formatted["league_id"],
                "country": formatted["country"],
                "count": 0,
                "fixtures": []
            }
        leagues_stats[league_name]["count"] += 1
        leagues_stats[league_name]["fixtures"].append(formatted)
    
    # Exibir por liga
    for league_name, stats in sorted(leagues_stats.items(), key=lambda x: x[1]["count"], reverse=True):
        print(f"\n🏆 {league_name} ({stats['country']})")
        print(f"   Liga ID: {stats['league_id']}")
        print(f"   Partidas: {stats['count']}")
        print("   " + "-"*66)
        
        for i, fix in enumerate(stats["fixtures"][:10], 1):  # Mostrar até 10
            status_icon = "🔴" if fix["status_short"] not in ["NS", "TBD", "PST"] else "🟢"
            print(f"   {i}. {status_icon} {fix['home_team']} {fix['score']} {fix['away_team']}")
            print(f"      {fix['date']} - {fix['status']}")
            print(f"      Fixture ID: {fix['fixture_id']}")
        
        if len(stats["fixtures"]) > 10:
            print(f"   ... e mais {len(stats['fixtures']) - 10} partidas")
    
    # Resumo
    print("\n" + "="*70)
    print("📊 RESUMO")
    print("="*70)
    print(f"🔴 Partidas ao vivo: {live_count}")
    print(f"🟢 Partidas agendadas: {upcoming_count}")
    print(f"📅 Total de partidas: {len(all_fixtures)}")
    print(f"🏆 Ligas diferentes: {len(leagues_stats)}")
    
    # Top ligas
    print("\n🏆 TOP 5 LIGAS:")
    for i, (league_name, stats) in enumerate(sorted(leagues_stats.items(), key=lambda x: x[1]["count"], reverse=True)[:5], 1):
        print(f"   {i}. {league_name} - {stats['count']} partidas (ID: {stats['league_id']})")
    
    # Salvar relatório
    report = {
        "timestamp": datetime.now().isoformat(),
        "live_fixtures": live_count,
        "upcoming_fixtures": upcoming_count,
        "total_fixtures": len(all_fixtures),
        "total_leagues": len(leagues_stats),
        "leagues": leagues_stats,
        "all_fixtures": formatted_fixtures
    }
    
    report_file = "live_and_upcoming_fixtures.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Relatório salvo: {report_file}")
    
    # Próximos passos
    print("\n" + "="*70)
    print("🚀 PRÓXIMOS PASSOS")
    print("="*70)
    print("\n1️⃣ Coletar dados históricos desses times:")
    print("   python collect_team_history.py --from-live-fixtures")
    print("\n2️⃣ Calcular previsões para essas partidas:")
    print("   python calculate_predictions.py --from-live-fixtures")
    print("\n3️⃣ Gerar recomendações de apostas:")
    print("   python generate_betting_recommendations.py")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
