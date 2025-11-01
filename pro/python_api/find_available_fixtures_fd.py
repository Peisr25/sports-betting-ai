"""
Busca partidas agendadas disponíveis na football-data.org

Similar ao find_available_fixtures.py mas usa a API football-data.org
que tem acesso gratuito a várias ligas europeias.

Uso:
    python find_available_fixtures_fd.py
"""
from data.collector import FootballDataCollector
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json


def print_section(title):
    """Helper para printar seções"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def get_available_competitions():
    """
    Retorna lista de competições disponíveis na football-data.org

    Free tier inclui:
    - Top 5 ligas europeias
    - Champions League
    - Copa do Mundo (quando disponível)
    - Copas nacionais selecionadas
    """
    return [
        {"code": "PL", "name": "Premier League", "country": "England"},
        {"code": "PD", "name": "La Liga", "country": "Spain"},
        {"code": "BL1", "name": "Bundesliga", "country": "Germany"},
        {"code": "SA", "name": "Serie A", "country": "Italy"},
        {"code": "FL1", "name": "Ligue 1", "country": "France"},
        {"code": "DED", "name": "Eredivisie", "country": "Netherlands"},
        {"code": "PPL", "name": "Primeira Liga", "country": "Portugal"},
        {"code": "CL", "name": "UEFA Champions League", "country": "Europe"},
        {"code": "ELC", "name": "Championship", "country": "England"},
        {"code": "EC", "name": "European Championship", "country": "Europe"},
        {"code": "WC", "name": "World Cup", "country": "World"},
    ]


def find_available_fixtures_fd(api_key: str, days_ahead: int = 14):
    """
    Busca fixtures agendados na football-data.org

    Args:
        api_key: Chave da football-data.org
        days_ahead: Quantos dias à frente buscar
    """
    print_section("BUSCANDO PARTIDAS NA FOOTBALL-DATA.ORG")

    collector = FootballDataCollector(api_key)

    # Datas de busca
    today = datetime.now()
    end_date = today + timedelta(days=days_ahead)

    print(f"\n📅 Período de busca:")
    print(f"   De: {today.strftime('%Y-%m-%d')}")
    print(f"   Até: {end_date.strftime('%Y-%m-%d')}")
    print(f"   Dias: {days_ahead}")

    # Competições para testar
    competitions = get_available_competitions()

    print(f"\n🔍 Testando {len(competitions)} competições...")

    # Resultados
    available_competitions = []
    restricted_competitions = []
    empty_competitions = []

    total_fixtures = 0

    for i, comp in enumerate(competitions, 1):
        comp_code = comp["code"]
        comp_name = comp["name"]
        country = comp["country"]

        print(f"\n[{i}/{len(competitions)}] 🏆 {comp_name} ({country}) - Code: {comp_code}")

        try:
            # Buscar fixtures agendados
            matches = collector.get_matches(
                competition_code=comp_code,
                status="SCHEDULED"
            )

            if not matches:
                print(f"   ℹ️  Sem jogos agendados")
                empty_competitions.append(comp)
                continue

            # Filtrar por data
            filtered_matches = []
            for match in matches:
                match_date_str = match.get("utcDate")
                if not match_date_str:
                    continue

                match_date = datetime.fromisoformat(match_date_str.replace('Z', '+00:00'))

                if today <= match_date <= end_date:
                    filtered_matches.append(match)

            if filtered_matches:
                print(f"   ✅ {len(filtered_matches)} jogos agendados encontrados!")

                # Mostra alguns exemplos
                for j, match in enumerate(filtered_matches[:3], 1):
                    home = match.get("homeTeam", {}).get("name", "?")
                    away = match.get("awayTeam", {}).get("name", "?")
                    date = match.get("utcDate", "")

                    # Parse date
                    try:
                        dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
                        date_str = dt.strftime("%d/%m %H:%M")
                    except:
                        date_str = date[:16]

                    print(f"      {j}. {home} vs {away} - {date_str}")

                if len(filtered_matches) > 3:
                    print(f"      ... e mais {len(filtered_matches) - 3} jogos")

                available_competitions.append({
                    "competition": comp,
                    "fixtures": filtered_matches,
                    "count": len(filtered_matches)
                })

                total_fixtures += len(filtered_matches)
            else:
                print(f"   ℹ️  {len(matches)} jogos, mas nenhum no período")
                empty_competitions.append(comp)

        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Erro: {error_msg}")

            if "403" in error_msg or "restricted" in error_msg.lower():
                restricted_competitions.append({
                    "competition": comp,
                    "error": error_msg
                })
            else:
                empty_competitions.append(comp)

    # Resumo
    print_section("RESUMO")

    print(f"\n📊 Estatísticas:")
    print(f"   Competições testadas: {len(competitions)}")
    print(f"   ✅ Com jogos disponíveis: {len(available_competitions)}")
    print(f"   ❌ Com restrições: {len(restricted_competitions)}")
    print(f"   ℹ️  Sem jogos agendados: {len(empty_competitions)}")
    print(f"   📅 Total de fixtures encontrados: {total_fixtures}")

    # Competições disponíveis
    if available_competitions:
        print(f"\n\n✅ COMPETIÇÕES COM JOGOS DISPONÍVEIS ({len(available_competitions)}):")
        print("=" * 70)

        # Ordena por quantidade de jogos
        available_competitions.sort(key=lambda x: x["count"], reverse=True)

        for i, item in enumerate(available_competitions, 1):
            comp = item["competition"]
            count = item["count"]
            print(f"\n{i}. 🏆 {comp['name']} ({comp['country']})")
            print(f"   Código: {comp['code']}")
            print(f"   Jogos agendados: {count}")
            print(f"   Comando para coletar dados:")
            print(f"   python collect_historical_data.py {comp['code']} --season 2024")

    # Competições com restrição
    if restricted_competitions:
        print(f"\n\n❌ COMPETIÇÕES COM RESTRIÇÕES ({len(restricted_competitions)}):")
        print("=" * 70)

        for i, item in enumerate(restricted_competitions, 1):
            comp = item["competition"]
            error = item["error"]
            print(f"\n{i}. {comp['name']} ({comp['country']}) - Code: {comp['code']}")
            print(f"   Erro: {error}")

    # Salvar relatório
    report = {
        "timestamp": datetime.now().isoformat(),
        "api": "football-data.org",
        "period": {
            "from": today.strftime("%Y-%m-%d"),
            "to": end_date.strftime("%Y-%m-%d"),
            "days": days_ahead
        },
        "summary": {
            "competitions_tested": len(competitions),
            "available": len(available_competitions),
            "restricted": len(restricted_competitions),
            "empty": len(empty_competitions),
            "total_fixtures": total_fixtures
        },
        "available_competitions": [
            {
                "code": item["competition"]["code"],
                "name": item["competition"]["name"],
                "country": item["competition"]["country"],
                "fixtures_count": item["count"]
            }
            for item in available_competitions
        ]
    }

    report_file = "available_fixtures_fd_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n\n💾 Relatório salvo: {report_file}")

    # Sugestões
    if available_competitions:
        print_section("PRÓXIMOS PASSOS")

        print("\n🎯 Você pode coletar dados dessas competições:")
        print("\n1. Coletar dados históricos:")
        top_comp = available_competitions[0]["competition"]
        print(f"   python collect_historical_data.py {top_comp['code']} --season 2024")

        print("\n2. Coletar de TODAS as competições disponíveis:")
        print("   Crie um script bash para iterar")

        print("\n3. Fazer predições:")
        print("   python app.py")
        print("   POST /predict com times das competições disponíveis")

    else:
        print_section("⚠️  NENHUMA COMPETIÇÃO DISPONÍVEL")
        print("\nVerifique:")
        print("  1. Se a API key está correta")
        print("  2. Se não estourou o limite de requisições")
        print("  3. Documentação: https://www.football-data.org/")


def main():
    """Função principal"""
    print("\n" + "=" * 70)
    print(" " * 10 + "BUSCA DE FIXTURES NA FOOTBALL-DATA.ORG")
    print("=" * 70)
    print("\nEste script testa competições da football-data.org")
    print("para encontrar jogos agendados acessíveis no plano free.")

    # Carrega API key
    load_dotenv()
    api_key = os.getenv("FOOTBALL_DATA_API_KEY")

    if not api_key:
        print("\n❌ FOOTBALL_DATA_API_KEY não encontrada!")
        print("\nConfigure no arquivo .env:")
        print("  FOOTBALL_DATA_API_KEY=your_key_here")
        return

    print(f"\n✓ API Key encontrada: {api_key[:10]}...")

    # Parâmetros
    print("\n⚙️  Configurações:")

    # Dias à frente
    days_str = input("\nQuantos dias à frente buscar? [14]: ").strip()
    days_ahead = int(days_str) if days_str else 14

    print(f"\n📋 Resumo:")
    print(f"   Dias à frente: {days_ahead}")
    print(f"   Competições: ~11 (free tier)")

    # Confirmação
    confirm = input("\nContinuar? [S/n]: ").strip().lower()
    if confirm == 'n':
        print("\n⚠️  Cancelado pelo usuário")
        return

    # Busca
    try:
        find_available_fixtures_fd(api_key, days_ahead)

        print("\n" + "=" * 70)
        print(" " * 20 + "✅ BUSCA CONCLUÍDA!")
        print("=" * 70 + "\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Busca interrompida pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro durante busca: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
