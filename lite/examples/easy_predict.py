"""
Script de predição simples e rápida
"""
import requests
import sys
import json


def predict_match(home_team, away_team, competition="PL"):
    """
    Faz predição de uma partida

    Args:
        home_team: Nome do time da casa
        away_team: Nome do time visitante
        competition: Código da competição
    """
    url = "http://localhost:5000/predict"

    payload = {
        "home_team": home_team,
        "away_team": away_team,
        "competition": competition
    }

    print(f"\n{'=' * 70}")
    print(f"PREDIÇÃO: {home_team} vs {away_team}")
    print(f"Competição: {competition}")
    print(f"{'=' * 70}\n")

    try:
        print("Buscando dados e gerando predição...\n")

        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

        # Match info
        match = data.get("match", {})
        print(f"🏟️  {match.get('home_team')} vs {match.get('away_team')}")
        print()

        # Statistics
        stats = data.get("statistics", {})
        home_stats = stats.get("home", {})
        away_stats = stats.get("away", {})

        print("📊 ESTATÍSTICAS:")
        print(f"   Casa: {home_stats.get('goals_avg')} gols/jogo | Sofre: {home_stats.get('conceded_avg')}")
        print(f"         Forma: {home_stats.get('form')} ({home_stats.get('matches')} jogos)")
        print(f"   Fora: {away_stats.get('goals_avg')} gols/jogo | Sofre: {away_stats.get('conceded_avg')}")
        print(f"         Forma: {away_stats.get('form')} ({away_stats.get('matches')} jogos)")
        print()

        # Predictions
        preds = data.get("predictions", {})

        print("🎯 PREDIÇÕES:")
        print()

        # Resultado
        result = preds.get("result", {})
        print("   Resultado (1X2):")
        print(f"      Casa: {result.get('home_win', 0):.1%}")
        print(f"      Empate: {result.get('draw', 0):.1%}")
        print(f"      Fora: {result.get('away_win', 0):.1%}")
        print()

        # Gols
        goals = preds.get("goals", {})
        print("   Total de Gols:")
        print(f"      Over 2.5: {goals.get('over_2.5', 0):.1%}")
        print(f"      Under 2.5: {goals.get('under_2.5', 0):.1%}")
        print()

        # BTTS
        btts = preds.get("both_teams_score", {})
        print("   Ambos Marcam:")
        print(f"      Sim: {btts.get('yes', 0):.1%}")
        print(f"      Não: {btts.get('no', 0):.1%}")
        print()

        # Placar mais provável
        most_likely = preds.get("most_likely_score", {})
        print(f"   Placar Mais Provável: {most_likely.get('score')} ({most_likely.get('probability', 0):.1%})")
        print()

        # Recomendações
        recommendations = data.get("recommendations", [])

        if recommendations:
            print("💡 RECOMENDAÇÕES:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec.get('market')}: {rec.get('bet')}")
                print(f"      Confiança: {rec.get('confidence')} ({rec.get('probability', 0):.1%})")
                print()
        else:
            print("💡 Nenhuma recomendação forte para esta partida.")
            print()

        # Confiança geral
        confidence = data.get("confidence", "Média")
        print(f"Confiança Geral: {confidence}")

        print("=" * 70)

    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar à API.")
        print("Verifique se o servidor está rodando: python app.py")
    except requests.exceptions.HTTPError as e:
        print(f"❌ Erro HTTP: {e.response.status_code}")
        try:
            error_detail = e.response.json().get("detail", "Erro desconhecido")
            print(f"Detalhes: {error_detail}")
        except:
            print(f"Detalhes: {e.response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("\n❌ Uso incorreto!")
        print("   python easy_predict.py <time_casa> <time_fora> [competicao]")
        print("\n📖 Exemplos:")
        print("   python easy_predict.py Arsenal Chelsea PL")
        print("   python easy_predict.py Flamengo Palmeiras BSA")
        print("   python easy_predict.py Barcelona Madrid PD")
        print("\n🏆 Competições disponíveis:")
        print("   PL  - Premier League")
        print("   BSA - Brasileirão Série A")
        print("   PD  - La Liga (Espanha)")
        print("   BL1 - Bundesliga (Alemanha)")
        print("   SA  - Serie A (Itália)")
        print("   FL1 - Ligue 1 (França)")
        print("   CL  - Champions League")
        sys.exit(1)

    home = sys.argv[1]
    away = sys.argv[2]
    comp = sys.argv[3] if len(sys.argv) > 3 else "PL"

    predict_match(home, away, comp)
