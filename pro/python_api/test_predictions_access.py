"""
Script de Teste: Verificar Acesso às Predições da API-Football

Este script testa:
1. Se seu plano tem acesso ao endpoint /predictions
2. Se consegue acessar predições de partidas agendadas (futuras)
3. Quais dados de predição estão disponíveis

Uso:
python test_predictions_access.py --apif-key SUA_KEY
"""
import sys
import os
import argparse
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.api_football_collector import APIFootballCollector


def test_predictions_access(api_key: str):
    """
    Testa acesso às predições da API-Football
    """
    print("="*70)
    print("TESTE DE ACESSO ÀS PREDIÇÕES DA API-FOOTBALL")
    print("="*70)
    print()

    collector = APIFootballCollector(api_key)

    # Teste 1: Buscar fixtures agendados (próximos dias)
    print("📋 Teste 1: Buscando fixtures agendados...")
    print("-"*70)

    try:
        # Buscar próximos 5 jogos do Brasileirão
        today = datetime.now()
        next_7_days = today + timedelta(days=7)

        fixtures = collector.get_fixtures(
            league_id=71,  # Brasileirão
            season=2024,
            status="NS",  # Not Started (agendados)
        )

        if not fixtures:
            print("⚠️  Nenhum fixture agendado encontrado no Brasileirão")
            print("   Tentando outras ligas...")

            # Tentar Premier League
            fixtures = collector.get_fixtures(
                league_id=39,  # Premier League
                season=2024,
                status="NS"
            )

        if fixtures:
            print(f"✅ Encontrados {len(fixtures)} fixtures agendados\n")

            # Pegar os primeiros 3 fixtures
            test_fixtures = fixtures[:3]

            for i, fixture in enumerate(test_fixtures, 1):
                fixture_id = fixture["fixture"]["id"]
                home_team = fixture["teams"]["home"]["name"]
                away_team = fixture["teams"]["away"]["name"]
                match_date = fixture["fixture"]["date"]

                print(f"[{i}] {home_team} vs {away_team}")
                print(f"    ID: {fixture_id}")
                print(f"    Data: {match_date}")
                print()

            # Teste 2: Tentar acessar predições
            print("\n" + "="*70)
            print("📊 Teste 2: Tentando acessar PREDIÇÕES...")
            print("="*70)
            print()

            test_fixture = test_fixtures[0]
            fixture_id = test_fixture["fixture"]["id"]
            home_team = test_fixture["teams"]["home"]["name"]
            away_team = test_fixture["teams"]["away"]["name"]

            print(f"Testando predições para: {home_team} vs {away_team}")
            print(f"Fixture ID: {fixture_id}\n")

            # Chamar endpoint de predições
            params = {"fixture": fixture_id}
            data = collector._make_request("predictions", params)

            # Verificar resposta
            errors = data.get("errors")
            response = data.get("response", [])

            if errors:
                print("❌ ERRO AO ACESSAR PREDIÇÕES:")
                print(f"   {errors}")
                print()

                # Verificar tipo de erro
                if isinstance(errors, dict):
                    if errors.get("requests"):
                        print("💡 Tipo de erro: Limite de requisições")
                    elif errors.get("token"):
                        print("💡 Tipo de erro: API key inválida")
                    elif "plan" in str(errors).lower() or "subscription" in str(errors).lower():
                        print("💡 Tipo de erro: Restrição de plano")
                        print("   Seu plano não tem acesso ao endpoint /predictions")
                        print()
                        print("   SOLUÇÕES:")
                        print("   1. Upgrade para plano pago (a partir de $19/mês)")
                        print("   2. Usar apenas nossas próprias predições (Poisson + XGBoost)")
                return False

            elif response:
                print("✅ ACESSO ÀS PREDIÇÕES CONFIRMADO!")
                print()

                # Analisar dados da predição
                prediction_data = response[0]

                # Predição principal
                predictions = prediction_data.get("predictions", {})

                print("📈 DADOS DA PREDIÇÃO:")
                print("-"*70)

                # Winner
                winner = predictions.get("winner", {})
                if winner:
                    print(f"Vencedor previsto: {winner.get('name')} ({winner.get('comment')})")

                # Percentuais
                percent = predictions.get("percent", {})
                if percent:
                    print(f"\nPercentuais:")
                    print(f"  Casa: {percent.get('home')}")
                    print(f"  Empate: {percent.get('draw')}")
                    print(f"  Fora: {percent.get('away')}")

                # Over/Under
                under_over = predictions.get("under_over")
                if under_over:
                    print(f"\nOver/Under: {under_over}")

                # Goals
                goals = predictions.get("goals", {})
                if goals:
                    print(f"\nGols previstos:")
                    print(f"  Casa: {goals.get('home')}")
                    print(f"  Fora: {goals.get('away')}")

                # Advice
                advice = predictions.get("advice")
                if advice:
                    print(f"\nRecomendação: {advice}")

                # Comparações
                comparison = prediction_data.get("comparison", {})
                if comparison:
                    print(f"\n📊 COMPARAÇÕES:")
                    print("-"*70)
                    print(f"Forma: Casa {comparison.get('form', {}).get('home')} x Fora {comparison.get('form', {}).get('away')}")
                    print(f"Ataque: Casa {comparison.get('att', {}).get('home')} x Fora {comparison.get('att', {}).get('away')}")
                    print(f"Defesa: Casa {comparison.get('def', {}).get('home')} x Fora {comparison.get('def', {}).get('away')}")
                    print(f"Poisson: Casa {comparison.get('poisson_distribution', {}).get('home')} x Fora {comparison.get('poisson_distribution', {}).get('away')}")
                    print(f"H2H: Casa {comparison.get('h2h', {}).get('home')} x Fora {comparison.get('h2h', {}).get('away')}")
                    print(f"TOTAL: Casa {comparison.get('total', {}).get('home')} x Fora {comparison.get('total', {}).get('away')}")

                # Teams data
                teams = prediction_data.get("teams", {})
                if teams:
                    print(f"\n📊 ESTATÍSTICAS DOS TIMES:")
                    print("-"*70)

                    home = teams.get("home", {})
                    away = teams.get("away", {})

                    if home:
                        print(f"\n{home.get('name')} (Casa):")
                        last_5 = home.get("last_5", {})
                        if last_5:
                            print(f"  Últimos 5 jogos - Forma: {last_5.get('form')}, Ataque: {last_5.get('att')}, Defesa: {last_5.get('def')}")

                    if away:
                        print(f"\n{away.get('name')} (Fora):")
                        last_5 = away.get("last_5", {})
                        if last_5:
                            print(f"  Últimos 5 jogos - Forma: {last_5.get('form')}, Ataque: {last_5.get('att')}, Defesa: {last_5.get('def')}")

                print()
                print("="*70)
                print("✅ SEU PLANO TEM ACESSO COMPLETO ÀS PREDIÇÕES!")
                print("="*70)
                print()

                return True

            else:
                print("⚠️  Resposta vazia do endpoint /predictions")
                print("   Pode ser que não haja predições disponíveis para este fixture")
                return None

        else:
            print("⚠️  Nenhum fixture agendado encontrado para testar")
            return None

    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False


def analyze_predictions_usefulness():
    """
    Analisa a utilidade das predições da API-Football
    """
    print("\n" + "="*70)
    print("💡 ANÁLISE: UTILIDADE DAS PREDIÇÕES DA API-FOOTBALL")
    print("="*70)
    print()

    print("🤔 AS PREDIÇÕES DA API-FOOTBALL SÃO ÚTEIS?")
    print("-"*70)
    print()

    print("✅ SIM! Aqui está como usá-las estrategicamente:")
    print()

    print("1️⃣  ENSEMBLE COM NOSSOS MODELOS")
    print("   Combinar predições da API com nossas próprias (Poisson + XGBoost)")
    print("   Exemplo: Média ponderada")
    print("     - Nossa predição: 65% vitória casa")
    print("     - API-Football: 60% vitória casa")
    print("     - Ensemble: 62.5% (média) ou peso maior no nosso modelo")
    print()

    print("2️⃣  FEATURE ENGINEERING")
    print("   Usar dados da API como features ADICIONAIS no XGBoost:")
    print("     - api_home_win_prob")
    print("     - api_draw_prob")
    print("     - api_away_win_prob")
    print("     - api_form_comparison")
    print("     - api_att_comparison")
    print("     - api_def_comparison")
    print("     - api_poisson_home")
    print("   Isso enriquece MUITO o modelo!")
    print()

    print("3️⃣  IDENTIFICAR VALUE BETS")
    print("   Quando NOSSA predição DIFERE significativamente da API:")
    print("   Exemplo:")
    print("     - Nossa predição: 70% vitória casa")
    print("     - API prediz: 50% vitória casa")
    print("     - AÇÃO: Investigar! Pode ser value bet se acharmos que")
    print("             nossa análise está correta")
    print()

    print("4️⃣  VALIDAÇÃO CRUZADA")
    print("   Comparar nossas predições com a API:")
    print("     - Se ambas concordam (ex: 65% vs 60%): ✅ Confiança alta")
    print("     - Se discordam muito (ex: 70% vs 40%): ⚠️ Investigar")
    print()

    print("5️⃣  BACKTESTING COMPARATIVO")
    print("   Comparar performance:")
    print("     - Nosso modelo vs API-Football vs Ensemble")
    print("     - Ver qual tem melhor ROI")
    print()

    print("⚠️  O QUE NÃO FAZER:")
    print("-"*70)
    print("❌ Usar APENAS as predições da API (ignorar nossos modelos)")
    print("   Por quê? Perdemos nosso edge competitivo!")
    print()
    print("❌ Confiar cegamente nas predições da API")
    print("   Por quê? A API não conhece nuances locais/recentes")
    print()

    print("\n" + "="*70)
    print("💰 ESTRATÉGIA RECOMENDADA:")
    print("="*70)
    print()
    print("1. Coletar predições da API para partidas agendadas")
    print("2. Gerar NOSSAS predições (Poisson + XGBoost)")
    print("3. Comparar ambas:")
    print("   • Se concordam (±10%): ✅ Apostar com confiança")
    print("   • Se discordam muito: ⚠️ Analisar manualmente ou passar")
    print("4. Usar ensemble quando ambas concordam")
    print("5. Treinar modelo com features da API (melhor opção!)")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Testa acesso às predições da API-Football"
    )

    parser.add_argument(
        "--apif-key",
        help="API key da API-Football v3"
    )

    args = parser.parse_args()

    # Obter API key
    api_key = args.apif_key or os.getenv("API_FOOTBALL_KEY")

    if not api_key:
        print("❌ API key da API-Football não configurada!")
        print("\nOpções:")
        print("1. Passe --apif-key SUA_KEY")
        print("2. Configure API_FOOTBALL_KEY no .env")
        sys.exit(1)

    # Executar teste
    has_access = test_predictions_access(api_key)

    # Mostrar análise de utilidade
    analyze_predictions_usefulness()

    # Resumo final
    print("\n" + "="*70)
    print("📋 RESUMO DO TESTE")
    print("="*70)

    if has_access:
        print("✅ Status: ACESSO CONFIRMADO")
        print("✅ Você pode usar predições da API-Football!")
        print()
        print("🚀 PRÓXIMOS PASSOS:")
        print("   1. Criar script de coleta de predições")
        print("   2. Integrar com nossos modelos (ensemble)")
        print("   3. Adicionar features da API ao XGBoost")
        print("   4. Fazer backtesting comparativo")

    elif has_access is False:
        print("❌ Status: SEM ACESSO")
        print("⚠️  Seu plano não inclui o endpoint /predictions")
        print()
        print("💡 OPÇÕES:")
        print("   1. Upgrade para plano pago (recomendado se precisa deste recurso)")
        print("   2. Usar apenas nossos próprios modelos")
        print("   3. Focar em melhorar nossos modelos com dados que temos")
        print()
        print("ℹ️  Nossos modelos (Poisson + XGBoost) já são muito bons!")
        print("   As predições da API são um BÔNUS, não essenciais.")

    else:
        print("⚠️  Status: INDETERMINADO")
        print("   Não foi possível confirmar acesso (sem fixtures para testar)")

    print("="*70)


if __name__ == "__main__":
    main()
