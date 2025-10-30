"""
Script para buscar próximos jogos e fazer predições automáticas
"""
import requests
import sys
from datetime import datetime
import time


def get_matches_and_predict(competition_code="PL", max_predictions=5):
    """
    Busca próximas partidas e faz predições automaticamente

    Args:
        competition_code: Código da competição
        max_predictions: Número máximo de predições a fazer
    """
    print(f"\n{'=' * 80}")
    print(f"PRÓXIMOS JOGOS E PREDIÇÕES - {competition_code}")
    print(f"{'=' * 80}\n")

    # Busca próximas partidas
    try:
        print("Buscando próximas partidas...\n")
        response = requests.get(
            f"http://localhost:5000/matches/{competition_code}",
            params={"status": "SCHEDULED"}
        )
        response.raise_for_status()
        data = response.json()

        matches = data.get("matches", [])

        if not matches:
            print("Nenhuma partida agendada encontrada.")
            return

        print(f"✓ Encontradas {len(matches)} partidas agendadas\n")

        # Processa cada partida
        predictions_made = 0

        for match in matches[:max_predictions]:
            home_team = match.get("homeTeam", {}).get("name", "")
            away_team = match.get("awayTeam", {}).get("name", "")
            match_date = match.get("utcDate", "")

            # Formata data
            try:
                dt = datetime.fromisoformat(match_date.replace('Z', '+00:00'))
                formatted_date = dt.strftime("%d/%m/%Y %H:%M")
            except:
                formatted_date = match_date

            print(f"\n{'─' * 80}")
            print(f"📅 {formatted_date}")
            print(f"🏟️  {home_team} vs {away_team}")
            print(f"{'─' * 80}")

            # Faz predição
            try:
                print("   Gerando predição...")

                pred_response = requests.post(
                    "http://localhost:5000/predict",
                    json={
                        "home_team": home_team,
                        "away_team": away_team,
                        "competition": competition_code
                    },
                    timeout=30
                )

                if pred_response.status_code == 200:
                    pred_data = pred_response.json()

                    # Resultado
                    result = pred_data.get("predictions", {}).get("result", {})
                    print(f"   Resultado: Casa {result.get('home_win', 0):.1%} | "
                          f"Empate {result.get('draw', 0):.1%} | "
                          f"Fora {result.get('away_win', 0):.1%}")

                    # Gols
                    goals = pred_data.get("predictions", {}).get("goals", {})
                    print(f"   Gols: Over 2.5 {goals.get('over_2.5', 0):.1%} | "
                          f"Under 2.5 {goals.get('under_2.5', 0):.1%}")

                    # BTTS
                    btts = pred_data.get("predictions", {}).get("both_teams_score", {})
                    print(f"   Ambos Marcam: Sim {btts.get('yes', 0):.1%} | "
                          f"Não {btts.get('no', 0):.1%}")

                    # Recomendações
                    recommendations = pred_data.get("recommendations", [])
                    if recommendations:
                        print("   💡 Recomendações:")
                        for rec in recommendations[:3]:
                            print(f"      • {rec.get('market')}: {rec.get('bet')} "
                                  f"({rec.get('confidence')}, {rec.get('probability', 0):.1%})")
                    else:
                        print("   💡 Sem recomendações fortes")

                    predictions_made += 1

                else:
                    print(f"   ⚠️ Erro ao gerar predição: {pred_response.status_code}")

                # Pequena pausa para não sobrecarregar a API
                time.sleep(1)

            except requests.exceptions.Timeout:
                print("   ⚠️ Timeout ao gerar predição")
            except Exception as e:
                print(f"   ⚠️ Erro: {e}")

        print(f"\n{'=' * 80}")
        print(f"✓ Total de predições geradas: {predictions_made}")
        print(f"{'=' * 80}\n")

    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar à API.")
        print("Verifique se o servidor está rodando: python app.py")
    except requests.exceptions.HTTPError as e:
        print(f"❌ Erro HTTP: {e}")
    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    # Argumentos
    comp_code = sys.argv[1] if len(sys.argv) > 1 else "PL"
    max_pred = int(sys.argv[2]) if len(sys.argv) > 2 else 5

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
    print(f"Máximo de predições: {max_pred}")

    get_matches_and_predict(comp_code, max_pred)

    print("💡 Exemplos de uso:")
    print("   python jogos_e_predicoes.py BSA 3   # 3 predições do Brasileirão")
    print("   python jogos_e_predicoes.py CL 10   # 10 predições da Champions")
    print("   python jogos_e_predicoes.py PL      # 5 predições da Premier League (padrão)\n")
