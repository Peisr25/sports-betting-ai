"""
Calcula previsões para partidas ao vivo e agendadas
Usa dados históricos coletados + modelo treinado
"""
import os
import sys
import json
from datetime import datetime
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.database import Database, Match


class PredictionCalculator:
    """Calcula previsões baseado em dados históricos"""
    
    def __init__(self):
        self.db = Database("database/betting.db")
    
    def calculate_team_stats(self, team_name: str, last_n: int = 10) -> dict:
        """
        Calcula estatísticas de um time baseado em histórico
        
        Args:
            team_name: Nome do time
            last_n: Número de partidas para análise
            
        Returns:
            Dicionário com estatísticas
        """
        # Buscar partidas do time
        matches = self.db.session.query(Match).filter(
            ((Match.home_team.like(f"%{team_name}%")) | 
             (Match.away_team.like(f"%{team_name}%"))) &
            (Match.status == "FINISHED") &
            (Match.home_score.isnot(None))
        ).order_by(Match.match_date.desc()).limit(last_n).all()
        
        if not matches:
            return {
                "matches_found": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "goals_scored": 0,
                "goals_conceded": 0,
                "win_rate": 0,
                "avg_goals_scored": 0,
                "avg_goals_conceded": 0
            }
        
        wins = 0
        draws = 0
        losses = 0
        goals_scored = 0
        goals_conceded = 0
        
        for match in matches:
            is_home = team_name.lower() in match.home_team.lower()
            
            if is_home:
                team_goals = match.home_score
                opponent_goals = match.away_score
            else:
                team_goals = match.away_score
                opponent_goals = match.home_score
            
            goals_scored += team_goals
            goals_conceded += opponent_goals
            
            if team_goals > opponent_goals:
                wins += 1
            elif team_goals == opponent_goals:
                draws += 1
            else:
                losses += 1
        
        total = len(matches)
        
        return {
            "matches_found": total,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_scored": goals_scored,
            "goals_conceded": goals_conceded,
            "win_rate": wins / total if total > 0 else 0,
            "draw_rate": draws / total if total > 0 else 0,
            "loss_rate": losses / total if total > 0 else 0,
            "avg_goals_scored": goals_scored / total if total > 0 else 0,
            "avg_goals_conceded": goals_conceded / total if total > 0 else 0,
            "goal_difference": (goals_scored - goals_conceded) / total if total > 0 else 0
        }
    
    def predict_match(self, home_team: str, away_team: str) -> dict:
        """
        Faz previsão para uma partida específica
        
        Args:
            home_team: Time da casa
            away_team: Time visitante
            
        Returns:
            Dicionário com previsão
        """
        # Estatísticas dos times
        home_stats = self.calculate_team_stats(home_team, last_n=10)
        away_stats = self.calculate_team_stats(away_team, last_n=10)
        
        # Verificar se temos dados suficientes
        if home_stats["matches_found"] < 5 or away_stats["matches_found"] < 5:
            return {
                "home_team": home_team,
                "away_team": away_team,
                "prediction": "INSUFFICIENT_DATA",
                "confidence": 0,
                "home_stats": home_stats,
                "away_stats": away_stats,
                "reason": f"Dados insuficientes (Casa: {home_stats['matches_found']}, Fora: {away_stats['matches_found']})"
            }
        
        # Cálculo simples de probabilidades
        # Baseado em: win_rate, goal_difference, home advantage
        
        home_advantage = 0.1  # 10% de vantagem para jogar em casa
        
        home_score = (
            home_stats["win_rate"] * 0.4 +
            (home_stats["goal_difference"] / 3) * 0.3 +
            (1 - away_stats["win_rate"]) * 0.3 +
            home_advantage
        )
        
        away_score = (
            away_stats["win_rate"] * 0.4 +
            (away_stats["goal_difference"] / 3) * 0.3 +
            (1 - home_stats["win_rate"]) * 0.3
        )
        
        draw_score = (
            home_stats["draw_rate"] * 0.5 +
            away_stats["draw_rate"] * 0.5
        )
        
        # Normalizar probabilidades
        total = home_score + away_score + draw_score
        if total > 0:
            home_prob = home_score / total
            draw_prob = draw_score / total
            away_prob = away_score / total
        else:
            home_prob = draw_prob = away_prob = 0.33
        
        # Previsão
        max_prob = max(home_prob, draw_prob, away_prob)
        
        if max_prob == home_prob:
            prediction = "HOME"
        elif max_prob == away_prob:
            prediction = "AWAY"
        else:
            prediction = "DRAW"
        
        # Previsão de gols (método Poisson simplificado)
        expected_home_goals = (home_stats["avg_goals_scored"] + away_stats["avg_goals_conceded"]) / 2
        expected_away_goals = (away_stats["avg_goals_scored"] + home_stats["avg_goals_conceded"]) / 2
        
        return {
            "home_team": home_team,
            "away_team": away_team,
            "prediction": prediction,
            "confidence": max_prob,
            "probabilities": {
                "home_win": home_prob,
                "draw": draw_prob,
                "away_win": away_prob
            },
            "expected_goals": {
                "home": round(expected_home_goals, 2),
                "away": round(expected_away_goals, 2)
            },
            "home_stats": home_stats,
            "away_stats": away_stats
        }
    
    def process_live_fixtures(self, filename: str = "live_and_upcoming_fixtures.json"):
        """Processa fixtures e gera previsões"""
        if not os.path.exists(filename):
            print(f"❌ Arquivo {filename} não encontrado!")
            return
        
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        fixtures = data.get("all_fixtures", [])
        
        if not fixtures:
            print("❌ Nenhuma fixture encontrada!")
            return
        
        print("\n" + "="*70)
        print("🎯 CALCULANDO PREVISÕES")
        print("="*70)
        print(f"\nTotal de partidas: {len(fixtures)}\n")
        
        predictions = []
        
        for i, fixture in enumerate(fixtures, 1):
            home_team = fixture["home_team"]
            away_team = fixture["away_team"]
            
            print(f"[{i}/{len(fixtures)}] {home_team} vs {away_team}")
            
            prediction = self.predict_match(home_team, away_team)
            
            # Adicionar info da fixture
            prediction["fixture_info"] = {
                "fixture_id": fixture["fixture_id"],
                "date": fixture["date"],
                "league": fixture["league_name"],
                "status": fixture["status"],
                "current_score": fixture.get("score", "- x -")
            }
            
            predictions.append(prediction)
            
            # Exibir resultado
            if prediction["prediction"] == "INSUFFICIENT_DATA":
                print(f"   ⚠️ {prediction['reason']}")
            else:
                pred = prediction["prediction"]
                conf = prediction["confidence"] * 100
                home_prob = prediction["probabilities"]["home_win"] * 100
                draw_prob = prediction["probabilities"]["draw"] * 100
                away_prob = prediction["probabilities"]["away_win"] * 100
                
                print(f"   📊 Previsão: {pred} (Confiança: {conf:.1f}%)")
                print(f"   📈 Probabilidades: Casa {home_prob:.1f}% | Empate {draw_prob:.1f}% | Fora {away_prob:.1f}%")
                print(f"   ⚽ Gols esperados: {prediction['expected_goals']['home']:.1f} x {prediction['expected_goals']['away']:.1f}")
            
            print()
        
        # Salvar previsões
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_fixtures": len(fixtures),
            "predictions": predictions
        }
        
        output_file = "betting_predictions.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print("="*70)
        print("📊 RESUMO")
        print("="*70)
        
        # Estatísticas
        with_data = [p for p in predictions if p["prediction"] != "INSUFFICIENT_DATA"]
        without_data = [p for p in predictions if p["prediction"] == "INSUFFICIENT_DATA"]
        
        print(f"\n✅ Previsões geradas: {len(with_data)}")
        print(f"⚠️ Sem dados suficientes: {len(without_data)}")
        
        if with_data:
            # Distribuição de previsões
            home_wins = len([p for p in with_data if p["prediction"] == "HOME"])
            draws = len([p for p in with_data if p["prediction"] == "DRAW"])
            away_wins = len([p for p in with_data if p["prediction"] == "AWAY"])
            
            print(f"\n📈 Distribuição:")
            print(f"   Casa vence: {home_wins} ({home_wins/len(with_data)*100:.1f}%)")
            print(f"   Empate: {draws} ({draws/len(with_data)*100:.1f}%)")
            print(f"   Fora vence: {away_wins} ({away_wins/len(with_data)*100:.1f}%)")
            
            # Melhores apostas (alta confiança)
            best_bets = sorted(with_data, key=lambda x: x["confidence"], reverse=True)[:5]
            
            print(f"\n🎯 TOP 5 APOSTAS (Maior Confiança):")
            for i, bet in enumerate(best_bets, 1):
                info = bet["fixture_info"]
                print(f"\n{i}. {bet['home_team']} vs {bet['away_team']}")
                print(f"   Liga: {info['league']}")
                print(f"   Data: {info['date']}")
                print(f"   Previsão: {bet['prediction']} (Confiança: {bet['confidence']*100:.1f}%)")
                print(f"   Gols: {bet['expected_goals']['home']:.1f} x {bet['expected_goals']['away']:.1f}")
        
        print(f"\n💾 Relatório salvo: {output_file}")
        print("="*70 + "\n")


def main():
    """Interface principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Calcula previsões para partidas ao vivo/agendadas"
    )
    parser.add_argument(
        "--from-live-fixtures",
        action="store_true",
        help="Usar partidas do arquivo live_and_upcoming_fixtures.json"
    )
    
    args = parser.parse_args()
    
    calculator = PredictionCalculator()
    
    if args.from_live_fixtures:
        calculator.process_live_fixtures()
    else:
        print("❌ Use --from-live-fixtures para processar as partidas")
        print("\nExemplo:")
        print("  python calculate_predictions.py --from-live-fixtures")


if __name__ == "__main__":
    main()
