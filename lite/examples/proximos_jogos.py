"""
Script para consultar próximas partidas de uma competição
"""
import requests
import sys
from datetime import datetime


def get_upcoming_matches(competition_code="PL", status="SCHEDULED"):
    """
    Busca próximas partidas de uma competição

    Args:
        competition_code: Código da competição (PL, BSA, CL, etc)
        status: Status das partidas (SCHEDULED, LIVE, FINISHED)
    """
    url = f"http://localhost:5000/matches/{competition_code}"
    params = {"status": status}

    print(f"\n{'=' * 80}")
    print(f"PRÓXIMAS PARTIDAS - {competition_code} ({status})")
    print(f"{'=' * 80}\n")

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        matches = data.get("matches", [])

        if not matches:
            print(f"Nenhuma partida com status '{status}' encontrada.")
            return

        print(f"Total de partidas: {len(matches)}\n")

        for i, match in enumerate(matches[:20], 1):  # Limita a 20 partidas
            home_team = match.get("homeTeam", {}).get("name", "N/A")
            away_team = match.get("awayTeam", {}).get("name", "N/A")
            match_date = match.get("utcDate", "")

            # Formata data
            if match_date:
                try:
                    dt = datetime.fromisoformat(match_date.replace('Z', '+00:00'))
                    formatted_date = dt.strftime("%d/%m/%Y %H:%M")
                except:
                    formatted_date = match_date
            else:
                formatted_date = "Data não disponível"

            # Status
            status_match = match.get("status", "N/A")

            # Placar (se disponível)
            score = match.get("score", {}).get("fullTime", {})
            if score.get("home") is not None:
                score_str = f"{score['home']} x {score['away']}"
            else:
                score_str = "- x -"

            print(f"{i}. [{formatted_date}]")
            print(f"   {home_team} {score_str} {away_team}")
            print(f"   Status: {status_match}")
            print()

        if len(matches) > 20:
            print(f"... e mais {len(matches) - 20} partidas")

    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar à API.")
        print("Verifique se o servidor está rodando: python app.py")
    except requests.exceptions.HTTPError as e:
        print(f"❌ Erro HTTP: {e}")
    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    # Argumentos: código da competição e status
    comp_code = sys.argv[1] if len(sys.argv) > 1 else "PL"
    status = sys.argv[2] if len(sys.argv) > 2 else "SCHEDULED"

    # Competições disponíveis
    competitions = {
        "PL": "Premier League",
        "PD": "La Liga",
        "BL1": "Bundesliga",
        "SA": "Serie A",
        "FL1": "Ligue 1",
        "CL": "Champions League",
        "BSA": "Brasileirão Série A"
    }

    print(f"\nBuscando partidas de: {competitions.get(comp_code, comp_code)}")
    print(f"Status: {status}")

    get_upcoming_matches(comp_code, status)

    print("\n💡 Exemplos de uso:")
    print("   python proximos_jogos.py BSA SCHEDULED  # Próximas partidas do Brasileirão")
    print("   python proximos_jogos.py PL FINISHED    # Partidas finalizadas da Premier League")
    print("   python proximos_jogos.py CL LIVE        # Partidas ao vivo da Champions\n")
