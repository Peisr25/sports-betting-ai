"""
Script para consultar classificação de uma competição
"""
import requests
import sys
from datetime import datetime


def get_standings(competition_code="PL"):
    """
    Busca classificação de uma competição

    Args:
        competition_code: Código da competição (PL, BSA, CL, etc)
    """
    url = f"http://localhost:5000/standings/{competition_code}"

    print(f"\n{'=' * 70}")
    print(f"CLASSIFICAÇÃO - {competition_code}")
    print(f"{'=' * 70}\n")

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Extrai classificação
        standings = data.get("standings", [])

        if not standings:
            print("Nenhuma classificação encontrada.")
            return

        # Primeira tabela (geralmente a geral)
        table = standings[0].get("table", [])

        print(f"{'Pos':<5} {'Time':<30} {'J':<5} {'V':<5} {'E':<5} {'D':<5} {'GP':<5} {'GC':<5} {'SG':<5} {'Pts':<5}")
        print("-" * 70)

        for entry in table:
            team = entry.get("team", {})
            print(
                f"{entry.get('position', '-'):<5} "
                f"{team.get('name', 'N/A'):<30} "
                f"{entry.get('playedGames', 0):<5} "
                f"{entry.get('won', 0):<5} "
                f"{entry.get('draw', 0):<5} "
                f"{entry.get('lost', 0):<5} "
                f"{entry.get('goalsFor', 0):<5} "
                f"{entry.get('goalsAgainst', 0):<5} "
                f"{entry.get('goalDifference', 0):<5} "
                f"{entry.get('points', 0):<5}"
            )

        print("-" * 70)
        print(f"\nAtualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar à API.")
        print("Verifique se o servidor está rodando: python app.py")
    except requests.exceptions.HTTPError as e:
        print(f"❌ Erro HTTP: {e}")
    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    # Código da competição via argumento ou padrão PL
    comp_code = sys.argv[1] if len(sys.argv) > 1 else "PL"

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

    print(f"\nBuscando classificação de: {competitions.get(comp_code, comp_code)}")
    get_standings(comp_code)

    print("\n💡 Dica: Use python classificacao.py BSA para ver o Brasileirão")
    print("   Competições: PL, PD, BL1, SA, FL1, CL, BSA\n")
