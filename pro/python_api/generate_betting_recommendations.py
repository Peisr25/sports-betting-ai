"""
Gera recomendações de apostas com análise de valor esperado (EV)
Baseado nas previsões calculadas e odds de mercado
"""
import json
import os
from datetime import datetime
from typing import List, Dict


class BettingRecommender:
    """Gera recomendações de apostas inteligentes"""
    
    def __init__(self):
        # Odds de exemplo (em produção, buscar de casas de apostas)
        self.default_odds = {
            "HOME": 2.0,   # Casa vencer
            "DRAW": 3.5,   # Empate
            "AWAY": 3.8    # Fora vencer
        }
        
        # Limites de confiança
        self.min_confidence = 0.45  # 45% mínimo
        self.min_ev = 0.05  # 5% de valor esperado mínimo
        self.min_data_quality = 5  # 5 partidas mínimas por time
    
    def calculate_expected_value(self, probability: float, odds: float) -> float:
        """
        Calcula o valor esperado (EV) de uma aposta
        
        EV = (probabilidade × odds) - 1
        
        EV > 0: Aposta tem valor positivo
        EV < 0: Aposta tem valor negativo
        
        Args:
            probability: Probabilidade estimada (0-1)
            odds: Odd da casa de apostas
            
        Returns:
            Valor esperado (EV)
        """
        return (probability * odds) - 1
    
    def calculate_kelly_criterion(self, probability: float, odds: float) -> float:
        """
        Calcula aposta ótima usando critério de Kelly
        
        Kelly = (probabilidade × odds - 1) / (odds - 1)
        
        Retorna fração do bankroll para apostar
        
        Args:
            probability: Probabilidade estimada (0-1)
            odds: Odd da casa de apostas
            
        Returns:
            Fração do bankroll (0-1)
        """
        if odds <= 1:
            return 0
        
        kelly = (probability * odds - 1) / (odds - 1)
        
        # Kelly fracionado (25% do Kelly completo) para reduzir risco
        return max(0, kelly * 0.25)
    
    def analyze_bet(self, prediction: dict, market_odds: dict = None) -> dict:
        """
        Analisa uma previsão e gera recomendação
        
        Args:
            prediction: Dicionário com previsão
            market_odds: Odds do mercado (opcional)
            
        Returns:
            Análise completa da aposta
        """
        if market_odds is None:
            market_odds = self.default_odds.copy()
        
        # Verificar qualidade dos dados
        home_matches = prediction["home_stats"]["matches_found"]
        away_matches = prediction["away_stats"]["matches_found"]
        
        if home_matches < self.min_data_quality or away_matches < self.min_data_quality:
            return {
                "recommended": False,
                "reason": f"Dados insuficientes (Casa: {home_matches}, Fora: {away_matches})",
                "data_quality": "LOW"
            }
        
        # Analisar cada mercado
        markets = ["HOME", "DRAW", "AWAY"]
        prob_map = {
            "HOME": prediction["probabilities"]["home_win"],
            "DRAW": prediction["probabilities"]["draw"],
            "AWAY": prediction["probabilities"]["away_win"]
        }
        
        best_bet = None
        best_ev = float("-inf")
        
        analyses = []
        
        for market in markets:
            prob = prob_map[market]
            odds = market_odds.get(market, self.default_odds[market])
            
            ev = self.calculate_expected_value(prob, odds)
            kelly = self.calculate_kelly_criterion(prob, odds)
            
            analysis = {
                "market": market,
                "probability": prob,
                "odds": odds,
                "expected_value": ev,
                "kelly_stake": kelly,
                "recommended": ev > self.min_ev and prob > self.min_confidence
            }
            
            analyses.append(analysis)
            
            if ev > best_ev:
                best_ev = ev
                best_bet = analysis
        
        # Recomendação final
        if best_bet and best_bet["expected_value"] > self.min_ev:
            return {
                "recommended": True,
                "data_quality": "HIGH" if min(home_matches, away_matches) >= 10 else "MEDIUM",
                "best_bet": best_bet,
                "all_markets": analyses,
                "confidence": prediction["confidence"],
                "prediction": prediction["prediction"]
            }
        else:
            return {
                "recommended": False,
                "reason": "Nenhum mercado com valor esperado positivo",
                "data_quality": "MEDIUM",
                "all_markets": analyses
            }
    
    def generate_recommendations(self, predictions_file: str = "betting_predictions.json"):
        """Gera recomendações de apostas"""
        if not os.path.exists(predictions_file):
            print(f"❌ Arquivo {predictions_file} não encontrado!")
            return
        
        with open(predictions_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        predictions = data.get("predictions", [])
        
        if not predictions:
            print("❌ Nenhuma previsão encontrada!")
            return
        
        print("\n" + "="*70)
        print("💰 GERANDO RECOMENDAÇÕES DE APOSTAS")
        print("="*70)
        print(f"\nAnalisando {len(predictions)} partidas...\n")
        
        recommendations = []
        
        for prediction in predictions:
            # Ignorar se sem dados suficientes
            if prediction["prediction"] == "INSUFFICIENT_DATA":
                continue
            
            # Analisar aposta
            analysis = self.analyze_bet(prediction)
            
            # Criar recomendação completa
            recommendation = {
                "fixture": prediction["fixture_info"],
                "match": f"{prediction['home_team']} vs {prediction['away_team']}",
                "analysis": analysis,
                "home_stats": prediction["home_stats"],
                "away_stats": prediction["away_stats"],
                "expected_goals": prediction["expected_goals"]
            }
            
            recommendations.append(recommendation)
        
        # Filtrar apenas recomendações positivas
        good_bets = [r for r in recommendations if r["analysis"]["recommended"]]
        
        # Ordenar por valor esperado
        good_bets.sort(key=lambda x: x["analysis"]["best_bet"]["expected_value"], reverse=True)
        
        # Relatório
        print("="*70)
        print("📊 RESUMO DA ANÁLISE")
        print("="*70)
        print(f"\n✅ Partidas analisadas: {len(recommendations)}")
        print(f"🎯 Apostas recomendadas: {len(good_bets)}")
        print(f"❌ Apostas rejeitadas: {len(recommendations) - len(good_bets)}")
        
        if good_bets:
            print("\n" + "="*70)
            print("💎 MELHORES OPORTUNIDADES")
            print("="*70)
            
            for i, bet in enumerate(good_bets[:10], 1):  # Top 10
                print(f"\n🎯 APOSTA #{i}")
                print("-" * 70)
                
                fixture = bet["fixture"]
                analysis = bet["analysis"]
                best = analysis["best_bet"]
                
                print(f"Partida: {bet['match']}")
                print(f"Liga: {fixture['league']}")
                print(f"Data: {fixture['date']}")
                print(f"Status: {fixture['status']}")
                
                if fixture.get("current_score"):
                    print(f"Placar atual: {fixture['current_score']}")
                
                print(f"\n💰 RECOMENDAÇÃO: {best['market']}")
                print(f"   Probabilidade: {best['probability']*100:.1f}%")
                print(f"   Odd: {best['odds']:.2f}")
                print(f"   Valor Esperado: {best['expected_value']*100:+.2f}%")
                print(f"   Kelly Stake: {best['kelly_stake']*100:.1f}% do bankroll")
                
                print(f"\n📊 Qualidade dos Dados: {analysis['data_quality']}")
                print(f"   Casa: {bet['home_stats']['matches_found']} partidas")
                print(f"   Fora: {bet['away_stats']['matches_found']} partidas")
                
                print(f"\n⚽ Gols Esperados: {bet['expected_goals']['home']:.1f} x {bet['expected_goals']['away']:.1f}")
                
                # Mostrar todos os mercados
                print(f"\n📈 Análise de Todos os Mercados:")
                for market in analysis["all_markets"]:
                    status = "✅" if market["recommended"] else "❌"
                    print(f"   {status} {market['market']}: EV={market['expected_value']*100:+.1f}% | "
                          f"Prob={market['probability']*100:.1f}% | Odd={market['odds']:.2f}")
        
        else:
            print("\n⚠️ Nenhuma aposta com valor esperado positivo encontrada.")
            print("   Aguarde por melhores oportunidades.")
        
        # Salvar relatório
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_analyzed": len(recommendations),
            "recommended_bets": len(good_bets),
            "recommendations": good_bets,
            "all_analyses": recommendations,
            "parameters": {
                "min_confidence": self.min_confidence,
                "min_expected_value": self.min_ev,
                "min_data_quality": self.min_data_quality
            }
        }
        
        output_file = "betting_recommendations.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Relatório salvo: {output_file}")
        print("="*70 + "\n")
        
        # Calculadora de apostas
        if good_bets:
            self.show_betting_calculator(good_bets[:5])
    
    def show_betting_calculator(self, top_bets: List[Dict]):
        """Mostra calculadora para as melhores apostas"""
        print("\n" + "="*70)
        print("🧮 CALCULADORA DE APOSTAS")
        print("="*70)
        print("\nDigite seu bankroll para calcular stakes recomendadas:")
        print("(Pressione Enter para pular)")
        
        try:
            bankroll_input = input("\nBankroll (R$): ").strip()
            
            if bankroll_input:
                bankroll = float(bankroll_input)
                
                print(f"\n💵 Bankroll: R$ {bankroll:.2f}")
                print("\n📋 Stakes Recomendadas (Kelly 25%):\n")
                
                total_stake = 0
                
                for i, bet in enumerate(top_bets, 1):
                    best = bet["analysis"]["best_bet"]
                    kelly = best["kelly_stake"]
                    stake = bankroll * kelly
                    total_stake += stake
                    
                    potential_profit = stake * (best["odds"] - 1)
                    
                    print(f"{i}. {bet['match']}")
                    print(f"   Mercado: {best['market']} @ {best['odds']:.2f}")
                    print(f"   Stake: R$ {stake:.2f} ({kelly*100:.1f}% do bankroll)")
                    print(f"   Lucro potencial: R$ {potential_profit:.2f}")
                    print()
                
                print(f"💰 Total investido: R$ {total_stake:.2f} ({total_stake/bankroll*100:.1f}% do bankroll)")
                print(f"💵 Restante: R$ {bankroll - total_stake:.2f}")
                
        except (ValueError, KeyboardInterrupt):
            print("\n✅ Calculadora pulada.")
        
        print("="*70 + "\n")


def main():
    """Interface principal"""
    recommender = BettingRecommender()
    recommender.generate_recommendations()


if __name__ == "__main__":
    main()
