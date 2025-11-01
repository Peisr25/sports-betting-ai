"""
Monitor em tempo real de oportunidades de apostas
Executa o pipeline periodicamente e alerta sobre novas oportunidades
"""
import os
import sys
import json
import time
import subprocess
from datetime import datetime
from typing import List, Dict, Set


class BettingMonitor:
    """Monitor de oportunidades de apostas"""
    
    def __init__(self, interval_minutes: int = 30):
        self.interval_minutes = interval_minutes
        self.interval_seconds = interval_minutes * 60
        self.seen_fixtures: Set[int] = set()
        self.seen_recommendations: Set[str] = set()
        self.run_count = 0
    
    def run_pipeline(self) -> bool:
        """Executa pipeline completo"""
        try:
            print(f"\n{'='*70}")
            print(f"  🔄 EXECUTANDO PIPELINE (Rodada #{self.run_count + 1})")
            print(f"{'='*70}\n")
            
            result = subprocess.run(
                [sys.executable, "run_betting_pipeline.py"],
                check=True,
                text=True,
                capture_output=True
            )
            
            # Mostrar saída
            print(result.stdout)
            
            if result.stderr:
                print("⚠️  Avisos:", result.stderr)
            
            self.run_count += 1
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Erro ao executar pipeline:")
            print(e.stdout)
            print(e.stderr)
            return False
    
    def check_new_fixtures(self) -> List[Dict]:
        """Verifica se há novas fixtures"""
        if not os.path.exists("live_and_upcoming_fixtures.json"):
            return []
        
        with open("live_and_upcoming_fixtures.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        all_fixtures = data.get("all_fixtures", [])
        
        new_fixtures = []
        for fixture in all_fixtures:
            fixture_id = fixture["fixture_id"]
            if fixture_id not in self.seen_fixtures:
                new_fixtures.append(fixture)
                self.seen_fixtures.add(fixture_id)
        
        return new_fixtures
    
    def check_new_recommendations(self) -> List[Dict]:
        """Verifica se há novas recomendações"""
        if not os.path.exists("betting_recommendations.json"):
            return []
        
        with open("betting_recommendations.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        recommendations = data.get("recommendations", [])
        
        new_recs = []
        for rec in recommendations:
            # Criar ID único para a recomendação
            fixture_id = rec["fixture"]["fixture_id"]
            market = rec["analysis"]["best_bet"]["market"]
            rec_id = f"{fixture_id}_{market}"
            
            if rec_id not in self.seen_recommendations:
                new_recs.append(rec)
                self.seen_recommendations.add(rec_id)
        
        return new_recs
    
    def alert_new_opportunities(self, recommendations: List[Dict]):
        """Alerta sobre novas oportunidades"""
        if not recommendations:
            return
        
        print("\n" + "🚨"*35)
        print("  NOVAS OPORTUNIDADES DE APOSTAS!")
        print("🚨"*35)
        
        for i, rec in enumerate(recommendations, 1):
            fixture = rec["fixture"]
            analysis = rec["analysis"]
            best = analysis["best_bet"]
            
            print(f"\n🎯 OPORTUNIDADE #{i}")
            print("-" * 70)
            print(f"Partida: {rec['match']}")
            print(f"Liga: {fixture['league']}")
            print(f"Horário: {fixture['date']}")
            print(f"Status: {fixture['status']}")
            
            print(f"\n💰 APOSTA: {best['market']} @ {best['odds']:.2f}")
            print(f"   Valor Esperado: {best['expected_value']*100:+.1f}%")
            print(f"   Probabilidade: {best['probability']*100:.1f}%")
            print(f"   Kelly Stake: {best['kelly_stake']*100:.1f}% do bankroll")
        
        print("\n" + "="*70 + "\n")
    
    def show_status(self):
        """Mostra status do monitor"""
        print("\n" + "📊"*35)
        print("  STATUS DO MONITOR")
        print("📊"*35)
        
        print(f"\n⏱️  Próxima execução: {self.interval_minutes} minutos")
        print(f"🔄 Total de execuções: {self.run_count}")
        print(f"🎯 Fixtures monitoradas: {len(self.seen_fixtures)}")
        print(f"💰 Recomendações geradas: {len(self.seen_recommendations)}")
        
        # Estatísticas dos arquivos
        if os.path.exists("betting_recommendations.json"):
            with open("betting_recommendations.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            total = data.get("total_analyzed", 0)
            recommended = data.get("recommended_bets", 0)
            
            print(f"\n📈 Última análise:")
            print(f"   Partidas analisadas: {total}")
            print(f"   Apostas recomendadas: {recommended}")
            
            if recommended > 0:
                # Top recomendação
                recs = data.get("recommendations", [])
                if recs:
                    best = recs[0]
                    best_bet = best["analysis"]["best_bet"]
                    
                    print(f"\n🏆 Melhor oportunidade atual:")
                    print(f"   {best['match']}")
                    print(f"   {best_bet['market']} @ {best_bet['odds']:.2f}")
                    print(f"   EV: {best_bet['expected_value']*100:+.1f}%")
        
        print("\n" + "="*70 + "\n")
    
    def countdown(self):
        """Contagem regressiva até próxima execução"""
        print(f"\n⏳ Aguardando {self.interval_minutes} minutos até próxima execução...")
        print("   (Pressione Ctrl+C para parar)\n")
        
        remaining = self.interval_seconds
        
        try:
            while remaining > 0:
                mins = remaining // 60
                secs = remaining % 60
                
                # Atualizar linha
                print(f"\r   ⏱️  {mins:02d}:{secs:02d} restantes", end="", flush=True)
                
                time.sleep(1)
                remaining -= 1
            
            print("\r   ✅ Tempo esgotado! Iniciando nova execução...\n")
            
        except KeyboardInterrupt:
            raise
    
    def run(self):
        """Loop principal do monitor"""
        print("\n" + "🎯"*35)
        print("  MONITOR DE APOSTAS ESPORTIVAS")
        print("🎯"*35)
        
        print(f"\n⚙️  Configuração:")
        print(f"   Intervalo: {self.interval_minutes} minutos")
        print(f"   Início: {datetime.now().strftime('%H:%M:%S')}")
        
        print("\n💡 Dica: Mantenha este monitor rodando em segundo plano")
        print("   Ele alertará sobre novas oportunidades automaticamente")
        
        input("\n   Pressione Enter para iniciar o monitor...")
        
        try:
            while True:
                # Executar pipeline
                if self.run_pipeline():
                    # Verificar novas fixtures
                    new_fixtures = self.check_new_fixtures()
                    if new_fixtures:
                        print(f"\n🆕 {len(new_fixtures)} novas fixtures encontradas!")
                    
                    # Verificar novas recomendações
                    new_recs = self.check_new_recommendations()
                    if new_recs:
                        self.alert_new_opportunities(new_recs)
                    else:
                        print("\n✅ Nenhuma nova oportunidade no momento")
                
                # Mostrar status
                self.show_status()
                
                # Aguardar próxima execução
                self.countdown()
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Monitor interrompido pelo usuário")
            print(f"\n📊 Estatísticas finais:")
            print(f"   Execuções: {self.run_count}")
            print(f"   Fixtures monitoradas: {len(self.seen_fixtures)}")
            print(f"   Recomendações geradas: {len(self.seen_recommendations)}")
            print("\n👋 Até logo!\n")


def main():
    """Interface principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Monitor em tempo real de oportunidades de apostas"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Intervalo entre execuções em minutos (padrão: 30)"
    )
    
    args = parser.parse_args()
    
    # Verificar se scripts existem
    required_scripts = [
        "run_betting_pipeline.py",
        "find_live_and_upcoming.py",
        "collect_team_history.py",
        "calculate_predictions.py",
        "generate_betting_recommendations.py"
    ]
    
    missing = [s for s in required_scripts if not os.path.exists(s)]
    
    if missing:
        print("\n❌ Scripts necessários não encontrados:")
        for script in missing:
            print(f"   - {script}")
        print("\n   Execute este script da pasta pro/python_api/")
        return 1
    
    # Iniciar monitor
    monitor = BettingMonitor(interval_minutes=args.interval)
    monitor.run()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
