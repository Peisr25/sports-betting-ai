"""
Teste direto da API football-data.org
"""
import requests
import json

API_KEY = "b00e83b0962741e4a703a7dbe7b2f17f"
BASE_URL = "https://api.football-data.org/v4"

print("=" * 70)
print("  TESTE DIRETO DA API FOOTBALL-DATA.ORG")
print("=" * 70)

# Teste 1: Endpoint que funcionou no Postman
print("\n1️⃣ Testando endpoint do Flamengo (SCHEDULED)...")
url = f"{BASE_URL}/teams/1783/matches"
headers = {"X-Auth-Token": API_KEY}
params = {"status": "SCHEDULED"}

print(f"   URL: {url}")
print(f"   Headers: {headers}")
print(f"   Params: {params}")

try:
    response = requests.get(url, headers=headers, params=params)
    print(f"\n   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ SUCESSO!")
        print(f"\n   Filters:")
        print(f"      Competitions: {data.get('filters', {}).get('competitions')}")
        print(f"      Permission: {data.get('filters', {}).get('permission')}")
        print(f"\n   Result Set:")
        print(f"      Count: {data.get('resultSet', {}).get('count')}")
        print(f"      First: {data.get('resultSet', {}).get('first')}")
        print(f"      Last: {data.get('resultSet', {}).get('last')}")
        
        matches = data.get('matches', [])
        print(f"\n   📊 {len(matches)} partidas encontradas:")
        for i, match in enumerate(matches[:3], 1):
            home = match.get('homeTeam', {}).get('name', '?')
            away = match.get('awayTeam', {}).get('name', '?')
            date = match.get('utcDate', '')[:10]
            status = match.get('status', '')
            print(f"      {i}. {home} vs {away} ({date}) - {status}")
        
        # Salvar primeira partida para análise
        if matches:
            with open("sample_match_scheduled.json", "w") as f:
                json.dump(matches[0], f, indent=2)
            print(f"\n   💾 Amostra salva: sample_match_scheduled.json")
    else:
        print(f"   ❌ Erro: {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"   ❌ Exception: {e}")

# Teste 2: Testar partidas FINISHED
print("\n\n2️⃣ Testando partidas FINISHED do Flamengo...")
params = {"status": "FINISHED", "limit": 5}

try:
    response = requests.get(url, headers=headers, params=params)
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        matches = data.get('matches', [])
        print(f"   ✅ {len(matches)} partidas FINISHED encontradas")
        
        if matches:
            # Verificar que dados estão disponíveis
            match = matches[0]
            print(f"\n   📊 Dados disponíveis na partida FINISHED:")
            print(f"      Score: {'✅' if match.get('score') else '❌'}")
            print(f"      Goals: {'✅' if match.get('goals') else '❌'}")
            print(f"      Bookings: {'✅' if match.get('bookings') else '❌'}")
            print(f"      Substitutions: {'✅' if match.get('substitutions') else '❌'}")
            print(f"      Home Lineup: {'✅' if match.get('homeTeam', {}).get('lineup') else '❌'}")
            print(f"      Home Statistics: {'✅' if match.get('homeTeam', {}).get('statistics') else '❌'}")
            
            # Salvar para análise
            with open("sample_match_finished.json", "w") as f:
                json.dump(match, f, indent=2)
            print(f"\n   💾 Amostra salva: sample_match_finished.json")
    else:
        print(f"   ❌ Erro: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Exception: {e}")

# Teste 3: Testar competições
print("\n\n3️⃣ Testando endpoint de competições...")
url = f"{BASE_URL}/competitions"

try:
    response = requests.get(url, headers=headers)
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        competitions = data.get('competitions', [])
        print(f"   ✅ {len(competitions)} competições disponíveis")
        
        print(f"\n   📋 Algumas competições:")
        for comp in competitions[:5]:
            print(f"      - {comp.get('name')} ({comp.get('code')})")
    else:
        print(f"   ❌ Erro: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Exception: {e}")

# Teste 4: Verificar o collector.py
print("\n\n4️⃣ Testando com FootballDataCollector...")
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from data.collector import FootballDataCollector
    
    collector = FootballDataCollector(API_KEY)
    
    # Verificar como está configurado
    print(f"   Base URL: {collector.base_url}")
    print(f"   Headers: {collector.headers}")
    
    # Tentar buscar times do Brasileirão
    print(f"\n   Testando get_teams('BSA')...")
    teams = collector.get_teams("BSA")
    print(f"   ✅ {len(teams)} times encontrados")
    
    for team in teams[:3]:
        print(f"      - {team.get('name')} (ID: {team.get('id')})")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("  CONCLUSÃO")
print("=" * 70)
print("\n✅ Se os testes acima funcionaram, a API está OK!")
print("   Verifique os arquivos JSON gerados para ver os dados disponíveis")
print("\n" + "=" * 70)
