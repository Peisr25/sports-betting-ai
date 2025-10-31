"""
Exemplo de Uso Completo: Sistema Integrado com API-Football

Este script demonstra como usar o sistema completo:
1. Conectar ao banco de dados
2. Usar feature extractor
3. Fazer predições com cada modelo
4. Comparar resultados
5. Analisar valor de apostas
"""
from data.database_v2 import Database, Match
from features.api_predictions_features import APIPredictionFeatures
from models.poisson import PoissonModel
from models.xgboost_model import XGBoostModel
from models.ensemble import EnsembleModel
import glob
import os


def print_section(title):
    """Helper para printar seções"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def example_1_feature_extraction():
    """Exemplo 1: Extrair features de predições da API"""
    print_section("EXEMPLO 1: Feature Extraction")

    # Conecta ao banco
    db = Database("database/betting_v2.db")
    feature_extractor = APIPredictionFeatures(db)

    print(f"\n✓ Feature Extractor criado")
    print(f"  Total de features: {feature_extractor.get_feature_count()}")

    # Busca uma partida com predição da API
    predictions = db.session.query(db.session.query(Match).filter(
        Match.id.in_(
            db.session.query(db.Prediction.match_id).filter(
                db.Prediction.model_name == "api-football"
            )
        )
    ).limit(1).all())

    from data.database_v2 import Prediction
    api_preds = db.session.query(Prediction).filter(
        Prediction.model_name == "api-football"
    ).limit(1).all()

    if api_preds:
        pred = api_preds[0]
        match = db.session.query(Match).filter(Match.id == pred.match_id).first()

        if match:
            print(f"\n📊 Partida: {match.home_team} vs {match.away_team}")
            print(f"   Match ID: {match.id}")

            # Extrai features
            features = feature_extractor.get_features_for_match(match.id)

            print(f"\n📈 Features extraídas:")
            print(f"   Home Win Prob: {features['api_home_win_prob']:.2%}")
            print(f"   Draw Prob: {features['api_draw_prob']:.2%}")
            print(f"   Away Win Prob: {features['api_away_win_prob']:.2%}")
            print(f"   Home Advantage: {features['api_home_advantage']:.3f}")
            print(f"   Confidence: {features['api_prediction_confidence']:.2%}")

            if features['api_form_home'] is not None:
                print(f"\n   Form Home: {features['api_form_home']:.2%}")
                print(f"   Form Away: {features['api_form_away']:.2%}")
                print(f"   Form Diff: {features['api_form_diff']:.3f}")
    else:
        print("\n⚠️  Nenhuma predição da API encontrada no banco")
        print("   Execute: python collect_predictions.py")

    db.close()


def example_2_individual_models():
    """Exemplo 2: Predições com cada modelo individual"""
    print_section("EXEMPLO 2: Predições Individuais")

    db = Database("database/betting_v2.db")
    feature_extractor = APIPredictionFeatures(db)

    # Dados de exemplo
    match_stats = {
        "home": {
            "goals_scored_avg": 2.0,
            "goals_conceded_avg": 1.0,
            "wins": 7,
            "draws": 2,
            "losses": 1,
            "matches_played": 10,
            "goals_for_total": 20,
            "goals_against_total": 10
        },
        "away": {
            "goals_scored_avg": 1.5,
            "goals_conceded_avg": 1.5,
            "wins": 5,
            "draws": 3,
            "losses": 2,
            "matches_played": 10,
            "goals_for_total": 15,
            "goals_against_total": 15
        }
    }

    print("\n📊 Estatísticas:")
    print(f"   Casa: {match_stats['home']['goals_scored_avg']:.1f} gols/jogo")
    print(f"   Fora: {match_stats['away']['goals_scored_avg']:.1f} gols/jogo")

    # 1. Poisson
    print("\n🔢 1. MODELO POISSON")
    poisson = PoissonModel()
    pred_poisson = poisson.predict_match(
        home_attack=match_stats["home"]["goals_scored_avg"],
        away_attack=match_stats["away"]["goals_scored_avg"],
        home_defense=match_stats["home"]["goals_conceded_avg"],
        away_defense=match_stats["away"]["goals_conceded_avg"]
    )
    print(f"   Casa: {pred_poisson['result']['home_win']:.1%}")
    print(f"   Empate: {pred_poisson['result']['draw']:.1%}")
    print(f"   Fora: {pred_poisson['result']['away_win']:.1%}")

    # 2. XGBoost (se treinado)
    print("\n🤖 2. MODELO XGBOOST")
    model_files = glob.glob("models/saved/xgboost_with_api_*.pkl")
    if model_files:
        latest_model = max(model_files, key=os.path.getctime)
        xgboost = XGBoostModel(
            model_path=latest_model,
            feature_extractor=feature_extractor,
            use_api_features=True
        )

        # Para exemplo, usa match_id=None (features neutras)
        pred_xgboost = xgboost.predict(match_stats, match_id=None)
        print(f"   Casa: {pred_xgboost['result']['home_win']:.1%}")
        print(f"   Empate: {pred_xgboost['result']['draw']:.1%}")
        print(f"   Fora: {pred_xgboost['result']['away_win']:.1%}")
        print(f"   API Features: {pred_xgboost['api_features_used']}")
    else:
        print("   ⚠️  Modelo não treinado")
        print("   Execute: python train_xgboost_with_api.py")

    # 3. API-Football (se disponível)
    print("\n🌐 3. API-FOOTBALL PREDICTIONS")
    from models.ensemble import APIFootballModel
    api_model = APIFootballModel(db)

    # Busca uma partida com predição
    from data.database_v2 import Prediction
    api_preds = db.session.query(Prediction).filter(
        Prediction.model_name == "api-football"
    ).limit(1).all()

    if api_preds:
        pred = api_preds[0]
        pred_api = api_model.predict(pred.match_id)
        if pred_api:
            print(f"   Casa: {pred_api['result']['home_win']:.1%}")
            print(f"   Empate: {pred_api['result']['draw']:.1%}")
            print(f"   Fora: {pred_api['result']['away_win']:.1%}")
    else:
        print("   ⚠️  Predições da API não encontradas")
        print("   Execute: python collect_predictions.py")

    db.close()


def example_3_ensemble():
    """Exemplo 3: Ensemble combinando todos os modelos"""
    print_section("EXEMPLO 3: Ensemble (Combina Todos)")

    db = Database("database/betting_v2.db")
    feature_extractor = APIPredictionFeatures(db)

    # Cria ensemble
    ensemble = EnsembleModel(
        database=db,
        include_api_predictions=True,
        strategy="weighted_average"
    )

    # Tenta carregar XGBoost
    model_files = glob.glob("models/saved/xgboost_with_api_*.pkl")
    if model_files:
        latest_model = max(model_files, key=os.path.getctime)
        xgboost = XGBoostModel(
            model_path=latest_model,
            feature_extractor=feature_extractor,
            use_api_features=True
        )
        ensemble.add_model("xgboost", xgboost, weight=0.3)

    print(f"\n📊 Modelos no ensemble: {list(ensemble.models.keys())}")
    print(f"📊 Pesos: {ensemble.weights}")

    # Dados de exemplo
    match_stats = {
        "home": {
            "goals_scored_avg": 2.0,
            "goals_conceded_avg": 1.0,
            "wins": 7,
            "draws": 2,
            "losses": 1,
            "matches_played": 10,
            "goals_for_total": 20,
            "goals_against_total": 10
        },
        "away": {
            "goals_scored_avg": 1.5,
            "goals_conceded_avg": 1.5,
            "wins": 5,
            "draws": 3,
            "losses": 2,
            "matches_played": 10,
            "goals_for_total": 15,
            "goals_against_total": 15
        }
    }

    # Predição ensemble
    pred_ensemble = ensemble.predict(match_stats, match_id=None)

    print(f"\n🎯 PREDIÇÃO ENSEMBLE:")
    print(f"   Modelo: {pred_ensemble['model']}")
    print(f"   Estratégia: {pred_ensemble['strategy']}")
    print(f"   Modelos usados: {pred_ensemble['models_used']}")
    print(f"\n   Resultado:")
    print(f"     Casa: {pred_ensemble['result']['home_win']:.1%}")
    print(f"     Empate: {pred_ensemble['result']['draw']:.1%}")
    print(f"     Fora: {pred_ensemble['result']['away_win']:.1%}")

    if "weights" in pred_ensemble:
        print(f"\n   Pesos aplicados:")
        for model, weight in pred_ensemble["weights"].items():
            print(f"     {model}: {weight:.2f}")

    db.close()


def example_4_value_analysis():
    """Exemplo 4: Análise de valor com odds"""
    print_section("EXEMPLO 4: Análise de Valor")

    from analysis.value_analysis import ValueAnalyzer

    # Predições do nosso modelo
    predictions = {
        "result": {
            "home_win": 0.55,
            "draw": 0.25,
            "away_win": 0.20
        },
        "goals": {
            "over_2.5": 0.60,
            "under_2.5": 0.40
        },
        "both_teams_score": {
            "yes": 0.65,
            "no": 0.35
        }
    }

    # Odds das casas de apostas
    odds = {
        "result": {
            "home_win": 2.0,   # Nossa prob: 55% (implied: 50%)
            "draw": 3.5,        # Nossa prob: 25% (implied: 28%)
            "away_win": 5.0     # Nossa prob: 20% (implied: 20%)
        },
        "goals": {
            "over_2.5": 1.8,    # Nossa prob: 60% (implied: 55%)
            "under_2.5": 2.1    # Nossa prob: 40% (implied: 47%)
        }
    }

    print("\n📊 Nossas Predições:")
    print(f"   Casa: {predictions['result']['home_win']:.1%}")
    print(f"   Empate: {predictions['result']['draw']:.1%}")
    print(f"   Fora: {predictions['result']['away_win']:.1%}")

    print("\n💰 Odds das Casas:")
    print(f"   Casa: {odds['result']['home_win']:.2f}")
    print(f"   Empate: {odds['result']['draw']:.2f}")
    print(f"   Fora: {odds['result']['away_win']:.2f}")

    # Análise de valor
    analyzer = ValueAnalyzer()
    analyses = analyzer.analyze_match(
        predictions=predictions,
        odds=odds,
        stake=100
    )

    print(f"\n🔍 ANÁLISE DE VALOR:")
    print(f"   Total de mercados analisados: {len(analyses)}")

    # Filtra bets com valor
    value_bets = [a for a in analyses if a["has_value"]]
    print(f"   Bets com valor encontradas: {len(value_bets)}")

    if value_bets:
        print(f"\n💎 MELHORES APOSTAS (Value Bets):")
        for i, bet in enumerate(value_bets[:5], 1):
            print(f"\n   {i}. {bet['market']} - {bet['bet']}")
            print(f"      Nossa probabilidade: {bet['probability']:.1%}")
            print(f"      Odd: {bet['odds']:.2f}")
            print(f"      Valor Esperado: R$ {bet['expected_value']:.2f}")
            print(f"      ROI: {bet['roi']:.1%}")
            print(f"      Kelly: {bet['kelly_stake']:.1f}% da banca")

            if bet['expected_value'] > 0:
                print(f"      ✅ RECOMENDADO!")
            else:
                print(f"      ❌ Sem valor")
    else:
        print("\n   ℹ️  Nenhum value bet encontrado neste jogo")


def main():
    """Função principal"""
    print("\n" + "=" * 70)
    print(" " * 15 + "SISTEMA INTEGRADO - EXEMPLOS DE USO")
    print("=" * 70)

    try:
        # Exemplo 1
        example_1_feature_extraction()
        input("\n[Pressione ENTER para continuar...]")

        # Exemplo 2
        example_2_individual_models()
        input("\n[Pressione ENTER para continuar...]")

        # Exemplo 3
        example_3_ensemble()
        input("\n[Pressione ENTER para continuar...]")

        # Exemplo 4
        example_4_value_analysis()

        print("\n" + "=" * 70)
        print(" " * 20 + "✅ EXEMPLOS CONCLUÍDOS!")
        print("=" * 70)

        print("\n📚 Próximos Passos:")
        print("   1. Colete mais dados: python collect_predictions.py")
        print("   2. Treine o XGBoost: python train_xgboost_with_api.py")
        print("   3. Inicie a API: python app.py")
        print("   4. Faça backtesting para validar melhorias")
        print("\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Exemplos interrompidos pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
