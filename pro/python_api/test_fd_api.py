"""
Testa o que realmente está disponível na API football-data.org
"""
import os
import sys
from dotenv import load_dotenv
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data.collector import FootballDataCollector

load_dotenv("../.env")
api_key = os.getenv("FOOTBALL_DATA_API_KEY")

if not api_key:
    print("❌ FOOTBALL_DATA_API_KEY não encontrada no .env")
    sys.exit(1)

print("=" * 70)
print("  TESTE: O QUE ESTÁ DISPONÍVEL NA football-data.org?")
print("=" * 70)

collector = FootballDataCollector(api_key)

# 1. Testar partidas da Premier League
print("\n1️⃣ Buscando partidas FINISHED da Premier League...")
try:
    matches = collector.get_matches(
        competition_code="PL",
        status="FINISHED"
    )
    
    print(f"   ✅ {len(matches)} partidas encontradas")
    
    if matches:
        # Pegar a primeira partida
        match = matches[0]
        match_id = match.get("id")
        
        print(f"\n   Testando partida ID: {match_id}")
        print(f"   {match.get('homeTeam', {}).get('name')} vs {match.get('awayTeam', {}).get('name')}")
        print(f"   Data: {match.get('utcDate')}")
        
        # Verificar o que tem disponível
        print("\n   📊 Dados disponíveis:")
        print(f"      Score: {'✅' if match.get('score') else '❌'}")
        print(f"      Goals detalhados: {'✅' if match.get('goals') else '❌'}")
        print(f"      Bookings: {'✅' if match.get('bookings') else '❌'}")
        print(f"      Substitutions: {'✅' if match.get('substitutions') else '❌'}")
        print(f"      Lineup: {'✅' if match.get('homeTeam', {}).get('lineup') else '❌'}")
        print(f"      Formation: {'✅' if match.get('homeTeam', {}).get('formation') else '❌'}")
        
        # O MAIS IMPORTANTE: Statistics
        home_stats = match.get('homeTeam', {}).get('statistics')
        away_stats = match.get('awayTeam', {}).get('statistics')
        
        print(f"      Home Team Statistics: {'✅' if home_stats else '❌'}")
        print(f"      Away Team Statistics: {'✅' if away_stats else '❌'}")
        
        if home_stats:
            print("\n   ⭐ STATISTICS DISPONÍVEIS:")
            for key, value in home_stats.items():
                print(f"      - {key}: {value}")
        else:
            print("\n   ⚠️  STATISTICS NÃO DISPONÍVEL nesta partida!")
            print("      Isso pode significar:")
            print("      1. Free tier não tem acesso")
            print("      2. Partida não tem statistics registradas")
            print("      3. Precisamos fazer requisição diferente")
        
        # Salvar amostra
        with open("sample_match_fd.json", "w") as f:
            json.dump(match, f, indent=2)
        print("\n   💾 Amostra salva: sample_match_fd.json")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 2. Testar partidas SCHEDULED
print("\n\n2️⃣ Buscando partidas SCHEDULED...")
try:
    scheduled = collector.get_matches(
        competition_code="PL",
        status="SCHEDULED"
    )
    
    print(f"   ✅ {len(scheduled)} partidas agendadas encontradas")
    
    if scheduled:
        match = scheduled[0]
        print(f"\n   Amostra:")
        print(f"   {match.get('homeTeam', {}).get('name')} vs {match.get('awayTeam', {}).get('name')}")
        print(f"   Data: {match.get('utcDate')}")
        print(f"   Status: {match.get('status')}")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 3. Testar histórico de um time específico
print("\n\n3️⃣ Testando histórico de um time...")
try:
    # Manchester City ID = 65
    team_matches = collector.get_team_matches_history(
        team_id=65,
        last_n=5,
        status="FINISHED"
    )
    
    print(f"   ✅ {len(team_matches)} partidas do Manchester City")
    
    if team_matches:
        # Verificar se TEM statistics
        has_stats = any(
            m.get('homeTeam', {}).get('statistics') or 
            m.get('awayTeam', {}).get('statistics') 
            for m in team_matches
        )
        print(f"\n   Statistics disponíveis: {'✅ SIM' if has_stats else '❌ NÃO'}")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")

print("\n" + "=" * 70)
print("  CONCLUSÃO")
print("=" * 70)
print("\n⚠️  IMPORTANTE: Verifique o arquivo sample_match_fd.json")
print("   para ver EXATAMENTE o que está disponível!")
print("\n" + "=" * 70)
