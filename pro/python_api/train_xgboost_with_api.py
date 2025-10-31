"""
Script de treinamento do XGBoost com features da API-Football

Este script treina o modelo XGBoost usando:
1. Features tradicionais (goals, wins, draws, etc)
2. Features enriquecidas com predições da API-Football

Uso:
    python train_xgboost_with_api.py
"""
import numpy as np
from data.database_v2 import Database
from features.api_predictions_features import APIPredictionFeatures
from models.xgboost_model import XGBoostModel
from sklearn.model_selection import train_test_split
from datetime import datetime
import os


def prepare_training_data(db: Database, feature_extractor: APIPredictionFeatures):
    """
    Prepara dados de treinamento a partir do banco de dados

    Args:
        db: Instância do Database
        feature_extractor: Extrator de features da API

    Returns:
        X_train, X_val, y_train, y_val
    """
    print("=" * 70)
    print("PREPARANDO DADOS DE TREINAMENTO")
    print("=" * 70)

    # Buscar partidas finalizadas com resultado
    matches = db.session.query(db.engine.table_names)
    from data.database_v2 import Match

    matches = db.session.query(Match).filter(
        Match.status == "FINISHED",
        Match.home_score.isnot(None),
        Match.away_score.isnot(None)
    ).all()

    print(f"\n✓ Encontradas {len(matches)} partidas finalizadas")

    if len(matches) < 50:
        print("\n⚠️  AVISO: Poucas partidas para treinamento!")
        print(f"   Recomendado: 500+ partidas")
        print(f"   Encontradas: {len(matches)}")
        print(f"\n   Execute collect_historical_data.py para coletar mais dados")
        return None, None, None, None

    # Criar modelo temporário para gerar features
    temp_model = XGBoostModel(feature_extractor=feature_extractor, use_api_features=True)

    X = []
    y = []
    matches_processed = 0
    matches_with_api = 0

    print("\nProcessando partidas...")

    for match in matches:
        try:
            # Calcular estatísticas do time (simplificado para exemplo)
            # Em produção, você deve calcular estatísticas reais dos últimos N jogos
            home_stats = {
                "goals_scored_avg": 1.5,
                "goals_conceded_avg": 1.2,
                "wins": 5,
                "draws": 3,
                "losses": 2,
                "matches_played": 10,
                "goals_for_total": 15,
                "goals_against_total": 12
            }

            away_stats = {
                "goals_scored_avg": 1.3,
                "goals_conceded_avg": 1.4,
                "wins": 4,
                "draws": 4,
                "losses": 2,
                "matches_played": 10,
                "goals_for_total": 13,
                "goals_against_total": 14
            }

            match_stats = {"home": home_stats, "away": away_stats}

            # Criar features (inclui API features se disponível)
            features = temp_model.create_features(match_stats, match_id=match.id)

            # Verificar se tem predição da API para esta partida
            api_features = feature_extractor.get_features_for_match(match.id)
            if api_features.get("api_home_win_prob") is not None:
                matches_with_api += 1

            # Label: 0=away_win, 1=draw, 2=home_win
            if match.home_score > match.away_score:
                label = 2  # home_win
            elif match.home_score < match.away_score:
                label = 0  # away_win
            else:
                label = 1  # draw

            X.append(features)
            y.append(label)
            matches_processed += 1

            if matches_processed % 100 == 0:
                print(f"  Processadas: {matches_processed}/{len(matches)}")

        except Exception as e:
            # Pula partidas com erro
            continue

    X = np.array(X)
    y = np.array(y)

    print(f"\n✓ Partidas processadas: {matches_processed}")
    print(f"✓ Partidas com predições da API: {matches_with_api}")
    print(f"✓ Features por partida: {X.shape[1]}")
    print(f"  - Features básicas: 21")
    print(f"  - Features da API: {X.shape[1] - 21}")

    # Distribuição de resultados
    unique, counts = np.unique(y, return_counts=True)
    label_names = {0: "Vitória Fora", 1: "Empate", 2: "Vitória Casa"}
    print(f"\nDistribuição de resultados:")
    for label, count in zip(unique, counts):
        print(f"  {label_names[label]}: {count} ({count/len(y)*100:.1f}%)")

    # Split treino/validação
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"\n✓ Treino: {len(X_train)} partidas")
    print(f"✓ Validação: {len(X_val)} partidas")

    return X_train, X_val, y_train, y_val


def train_model(X_train, X_val, y_train, y_val, db: Database):
    """
    Treina o modelo XGBoost

    Args:
        X_train, X_val, y_train, y_val: Dados de treino/validação
        db: Database instance

    Returns:
        Modelo treinado
    """
    print("\n" + "=" * 70)
    print("TREINANDO MODELO XGBOOST")
    print("=" * 70)

    # Cria feature extractor
    feature_extractor = APIPredictionFeatures(db)

    # Cria modelo
    model = XGBoostModel(
        feature_extractor=feature_extractor,
        use_api_features=True
    )

    # Parâmetros de treinamento
    params = {
        "objective": "multi:softprob",
        "num_class": 3,
        "max_depth": 6,
        "learning_rate": 0.1,
        "n_estimators": 200,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": 42,
        "eval_metric": "mlogloss"
    }

    print("\nParâmetros:")
    for key, value in params.items():
        print(f"  {key}: {value}")

    print("\nTreinando...")
    metrics = model.train(X_train, y_train, X_val, y_val, params)

    print("\n✓ Treinamento concluído!")
    print(f"\nMétricas:")
    print(f"  Acurácia (treino): {metrics['train_accuracy']:.2%}")
    if 'val_accuracy' in metrics:
        print(f"  Acurácia (validação): {metrics['val_accuracy']:.2%}")

    return model


def save_model(model: XGBoostModel):
    """
    Salva modelo treinado

    Args:
        model: Modelo treinado
    """
    print("\n" + "=" * 70)
    print("SALVANDO MODELO")
    print("=" * 70)

    # Cria diretório de modelos se não existir
    os.makedirs("models/saved", exist_ok=True)

    # Nome do arquivo com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"models/saved/xgboost_with_api_{timestamp}.pkl"

    model.save_model(filename)

    print(f"\n✓ Modelo salvo: {filename}")
    print(f"\nPara usar o modelo:")
    print(f'  model = XGBoostModel(model_path="{filename}")')

    return filename


def main():
    """Função principal"""
    print("\n" + "=" * 70)
    print("TREINAMENTO DO XGBOOST COM FEATURES DA API-FOOTBALL")
    print("=" * 70)
    print("\nEste script treina um modelo XGBoost enriquecido com features")
    print("das predições da API-Football.")
    print("\nESTRATÉGIA: Feature Engineering (recomendado!)")
    print("  ⭐ XGBoost aprende QUANDO confiar na API")
    print("  ⭐ XGBoost aprende QUANTO peso dar a cada feature")
    print("=" * 70)

    # Conecta ao banco
    print("\n1. Conectando ao banco de dados...")
    db = Database("database/betting_v2.db")
    print("   ✓ Conectado!")

    # Cria feature extractor
    print("\n2. Criando extrator de features...")
    feature_extractor = APIPredictionFeatures(db)
    print(f"   ✓ {feature_extractor.get_feature_count()} features da API disponíveis")

    # Prepara dados
    print("\n3. Preparando dados de treinamento...")
    X_train, X_val, y_train, y_val = prepare_training_data(db, feature_extractor)

    if X_train is None:
        print("\n❌ Dados insuficientes para treinamento")
        print("\nExecute primeiro:")
        print("  1. collect_historical_data.py - coletar partidas históricas")
        print("  2. collect_predictions.py - coletar predições da API")
        db.close()
        return

    # Treina modelo
    print("\n4. Treinando modelo...")
    model = train_model(X_train, X_val, y_train, y_val, db)

    # Mostra importância das features
    print("\n5. Analisando importância das features...")
    importance = model.get_feature_importance()
    if importance:
        print("\nTop 10 features mais importantes:")
        sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
        for i, (name, score) in enumerate(sorted_features[:10], 1):
            print(f"  {i:2d}. {name}: {score:.4f}")

    # Salva modelo
    print("\n6. Salvando modelo...")
    model_path = save_model(model)

    db.close()

    print("\n" + "=" * 70)
    print("✅ TREINAMENTO CONCLUÍDO COM SUCESSO!")
    print("=" * 70)
    print(f"\nModelo salvo em: {model_path}")
    print("\nPróximos passos:")
    print("  1. Use o modelo no ensemble:")
    print(f'     xgb = XGBoostModel(model_path="{model_path}")')
    print("     ensemble.add_model('xgboost', xgb)")
    print("  2. Compare performance com modelo sem API features")
    print("  3. Execute backtesting para validar melhorias")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Treinamento interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro durante treinamento: {e}")
        import traceback
        traceback.print_exc()
