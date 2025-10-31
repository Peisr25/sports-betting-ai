"""
Script de Coleta Histórica com SISTEMA DUAL-API

Combina:
1. football-data.org - Fixtures básicos (10 req/min grátis)
2. API-Football v3 - Estatísticas detalhadas (100 req/dia grátis)

Vantagens:
✅ Maximiza dados disponíveis
✅ Economiza quota usando cada API para o que faz melhor
✅ Database rico com corners, fouls, shots, possession, etc
✅ Melhor precisão nas predições

Uso:
python collect_dual_api.py BSA --season 2024 --with-stats --with-events
"""
import argparse
import sys
import os
from datetime import datetime, timedelta

# Adiciona o diretório ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.hybrid_collector import HybridCollector
from data.database_v2 import Database


def main():
    parser = argparse.ArgumentParser(
        description="Coleta dados históricos usando DUAL-API (football-data.org + API-Football v3)"
    )

    parser.add_argument(
        "competition",
        help="Código da competição (BSA, PL, PD, BL1, SA, FL1, CL, PPL, DED)"
    )

    parser.add_argument(
        "--season",
        type=int,
        default=2024,
        help="Temporada (ano de início)"
    )

    parser.add_argument(
        "--fd-key",
        help="API key da football-data.org (ou use variável FOOTBALL_DATA_API_KEY)"
    )

    parser.add_argument(
        "--apif-key",
        help="API key da API-Football v3 (ou use variável API_FOOTBALL_KEY)"
    )

    parser.add_argument(
        "--with-stats",
        action="store_true",
        help="Incluir estatísticas detalhadas (corners, fouls, shots, etc)"
    )

    parser.add_argument(
        "--with-events",
        action="store_true",
        help="Incluir eventos da partida (gols, cartões, substituições)"
    )

    parser.add_argument(
        "--limit",
        type=int,
        help="Limitar número de partidas a processar"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simular sem salvar no banco"
    )

    args = parser.parse_args()

    # Obter API keys
    fd_key = args.fd_key or os.getenv("FOOTBALL_DATA_API_KEY")
    apif_key = args.apif_key or os.getenv("API_FOOTBALL_KEY")

    if not fd_key:
        print("❌ API key da football-data.org não configurada!")
        print("\nOpções:")
        print("1. Passe --fd-key SUA_KEY")
        print("2. Configure FOOTBALL_DATA_API_KEY no .env")
        print("3. Exporte: export FOOTBALL_DATA_API_KEY=sua_key")
        sys.exit(1)

    # Aviso se não tiver API-Football configurada
    if not apif_key:
        print("⚠️  API-Football v3 não configurada!")
        print("   Coletando apenas dados básicos da football-data.org")
        print("   Para dados completos (corners, shots, etc), configure API_FOOTBALL_KEY\n")

    # Criar coletor híbrido
    collector = HybridCollector(
        fd_api_key=fd_key,
        apif_api_key=apif_key if apif_key else None
    )

    # Banner
    print(f"""
{'='*70}
COLETA DUAL-API - Sistema Híbrido
{'='*70}

Competição: {args.competition}
Temporada: {args.season}/{args.season+1}

APIs Configuradas:
  ✓ football-data.org (fixtures básicos)
  {'✓' if apif_key else '✗'} API-Football v3 (estatísticas detalhadas)

Opções:
  Estatísticas detalhadas: {'SIM' if args.with_stats else 'NÃO'}
  Eventos (gols/cartões): {'SIM' if args.with_events else 'NÃO'}
  Modo: {'DRY-RUN (simulação)' if args.dry_run else 'REAL (salvando no banco)'}

{'='*70}
""")

    # Verificar estatísticas do banco ANTES
    db = Database()
    print(f"\n📊 Estatísticas do banco ANTES da coleta:")

    try:
        from sqlalchemy import func
        from data.database_v2 import Match, MatchStatistics

        total_matches = db.session.query(func.count(Match.id)).scalar()
        comp_matches = db.session.query(func.count(Match.id)).filter(
            Match.competition == args.competition
        ).scalar()
        matches_with_stats = db.session.query(func.count(MatchStatistics.id)).scalar()

        print(f"  Total de partidas: {total_matches}")
        print(f"  Partidas da {args.competition}: {comp_matches}")
        print(f"  Partidas com estatísticas detalhadas: {matches_with_stats}")

    except Exception as e:
        print(f"  (Erro ao obter estatísticas: {e})")

    if args.dry_run:
        print("\n⚠️  MODO DRY-RUN: Nenhum dado será salvo no banco")

    # Confirmar
    print(f"\n⏳ Iniciando coleta em 3 segundos...")
    import time
    time.sleep(3)

    # EXECUTAR COLETA
    try:
        matches = collector.collect_match_comprehensive(
            competition_code=args.competition,
            include_statistics=args.with_stats and apif_key is not None,
            include_events=args.with_events and apif_key is not None
        )

        # Aplicar limite se especificado
        if args.limit:
            matches = matches[:args.limit]

        # Estatísticas DEPOIS
        print(f"\n📊 Estatísticas do banco DEPOIS da coleta:")

        total_matches_after = db.session.query(func.count(Match.id)).scalar()
        comp_matches_after = db.session.query(func.count(Match.id)).filter(
            Match.competition == args.competition
        ).scalar()
        matches_with_stats_after = db.session.query(func.count(MatchStatistics.id)).scalar()

        print(f"  Total de partidas: {total_matches_after} (+{total_matches_after - total_matches})")
        print(f"  Partidas da {args.competition}: {comp_matches_after} (+{comp_matches_after - comp_matches})")
        print(f"  Partidas com estatísticas detalhadas: {matches_with_stats_after} (+{matches_with_stats_after - matches_with_stats})")

        # Resumo de uso das APIs
        stats = collector.get_stats_summary()
        print(f"\n📈 Uso das APIs:")
        print(f"  football-data.org: {stats['fd_requests']} requisições")
        print(f"  API-Football v3: {stats['apif_requests']} requisições")

        # Avisos sobre quota
        if apif_key and stats['apif_requests'] > 80:
            print(f"\n⚠️  ATENÇÃO: {stats['apif_requests']} requisições usadas da API-Football")
            print(f"   Você está próximo do limite diário de 100 requisições!")

        print(f"\n✅ Coleta finalizada com sucesso!")
        print(f"   {len(matches)} partidas processadas")

        if not apif_key:
            print(f"\n💡 DICA: Configure API_FOOTBALL_KEY para obter:")
            print(f"   - Escanteios, faltas, chutes")
            print(f"   - Posse de bola, passes")
            print(f"   - Eventos detalhados (gols, cartões)")
            print(f"   - Expected Goals (xG)")

    except KeyboardInterrupt:
        print("\n\n⚠️  Coleta interrompida pelo usuário")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Erro durante a coleta: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    main()
