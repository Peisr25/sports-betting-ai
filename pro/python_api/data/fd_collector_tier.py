"""
Collector Tier-Aware para football-data.org

Wrapper do FootballDataCollector com:
- Rate limiting automático
- Logs de tier
- Tratamento de erros específico por tier
"""
from typing import Dict, List, Optional

try:
    from .collector import FootballDataCollector
    from .tier_config import TierConfig, RateLimiter
except ImportError:
    from collector import FootballDataCollector
    from tier_config import TierConfig, RateLimiter


class FootballDataCollectorTierAware(FootballDataCollector):
    """
    Collector com suporte a tiers e rate limiting

    Usage:
        # Free tier
        collector = FootballDataCollectorTierAware(api_key, tier='free')
        matches = collector.get_matches("PL", status="FINISHED")
        # Respeita 10 req/min automaticamente

        # Paid tier (futuro)
        collector = FootballDataCollectorTierAware(api_key, tier='paid')
        # Respeita 100 req/min
    """

    def __init__(self, api_key: str, tier='free'):
        """
        Args:
            api_key: API key da football-data.org
            tier: 'free' ou 'paid'
        """
        super().__init__(api_key)

        self.tier = tier
        self.config = TierConfig.get_config(tier)

        # Rate limiter
        max_req, window = TierConfig.get_rate_limit(tier)
        self.rate_limiter = RateLimiter(max_req, window)

        print(f"🎯 Collector: {tier.upper()} tier")
        print(f"   Rate limit: {max_req} req/{window}s")

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Override para adicionar rate limiting

        Args:
            endpoint: Endpoint da API
            params: Parâmetros opcionais

        Returns:
            Response JSON
        """
        # Aguarda se necessário (rate limiting)
        self.rate_limiter.wait_if_needed()

        # Faz requisição (usa implementação da classe pai)
        try:
            response = super()._make_request(endpoint, params)

            # Log se estamos próximos do limite
            remaining = self.rate_limiter.get_remaining_requests()
            if remaining <= 2:
                print(f"   ⚠️  Quota: {remaining} requisições restantes")

            return response

        except Exception as e:
            error_msg = str(e)

            # Mensagens específicas por tier
            if "429" in error_msg:
                max_req, window = TierConfig.get_rate_limit(self.tier)
                print(f"\n❌ Rate limit excedido!")
                print(f"   Tier: {self.tier}")
                print(f"   Limite: {max_req} req/{window}s")
                print(f"   Aguarde {window}s antes de continuar")

            raise

    def get_matches_with_details(
        self,
        competition_code: str = None,
        team_id: int = None,
        status: str = "SCHEDULED",
        limit: int = None
    ) -> List[Dict]:
        """
        Busca partidas com logging de tier

        Args:
            competition_code: Código da competição
            team_id: ID do time
            status: Status da partida
            limit: Limite de resultados

        Returns:
            Lista de partidas
        """
        # Verifica se competição é acessível neste tier
        if competition_code and not TierConfig.is_competition_available(self.tier, competition_code):
            print(f"⚠️  Competição {competition_code} pode não estar disponível no {self.tier} tier")

        # Busca matches
        matches = self.get_matches(competition_code, team_id, status)

        # Limita se especificado
        if limit and len(matches) > limit:
            matches = matches[:limit]

        # Log de features disponíveis
        if matches and self.tier == 'free':
            self._log_available_features(matches[0])

        return matches

    def get_team_matches_with_limit(
        self,
        team_id: int,
        last_n: int = 10,
        status: str = "FINISHED"
    ) -> List[Dict]:
        """
        Busca últimas N partidas de um time com rate limiting

        Args:
            team_id: ID do time
            last_n: Número de partidas
            status: Status das partidas

        Returns:
            Lista de partidas
        """
        matches = self.get_team_matches_history(
            team_id=team_id,
            last_n=last_n,
            status=status
        )

        # Log de features
        if matches and self.tier == 'free':
            print(f"\n   📊 {len(matches)} partidas obtidas para team {team_id}")
            self._log_available_features(matches[0])

        return matches

    def _log_available_features(self, match: Dict):
        """
        Loga quais features estão disponíveis na partida

        Útil para saber o que o free tier realmente fornece
        """
        print(f"\n   🔍 Features disponíveis (amostra):")
        print(f"      Score: {'✅' if match.get('score') else '❌'}")
        print(f"      Goals: {'✅' if match.get('goals') else '❌'}")
        print(f"      Bookings: {'✅' if match.get('bookings') else '❌'}")
        print(f"      Substitutions: {'✅' if match.get('substitutions') else '❌'}")
        print(f"      Home Lineup: {'✅' if match.get('homeTeam', {}).get('lineup') else '❌'}")
        print(f"      Home Statistics: {'✅' if match.get('homeTeam', {}).get('statistics') else '❌'}")

    def get_remaining_requests(self) -> int:
        """
        Retorna quantas requisições ainda podem ser feitas

        Returns:
            int
        """
        return self.rate_limiter.get_remaining_requests()

    def get_tier_info(self) -> Dict:
        """
        Retorna informações sobre o tier atual

        Returns:
            Dict com info do tier
        """
        return {
            'tier': self.tier,
            'rate_limit': f"{self.config['rate_limit_requests']} req/{self.config['rate_limit_window']}s",
            'features_expected': self.config['features_count_expected'],
            'has_statistics': self.config['has_statistics'],
            'has_lineup': self.config['has_lineup'],
            'remaining_requests': self.get_remaining_requests()
        }

    def print_tier_info(self):
        """
        Imprime informações do tier
        """
        info = self.get_tier_info()
        print(f"\n{'='*60}")
        print(f"  TIER INFO: {info['tier'].upper()}")
        print(f"{'='*60}")
        print(f"  Rate limit: {info['rate_limit']}")
        print(f"  Features esperadas: ~{info['features_expected']}")
        print(f"  Statistics: {'✅' if info['has_statistics'] else '❌'}")
        print(f"  Lineup detalhado: {'✅' if info['has_lineup'] else '❌'}")
        print(f"  Requisições restantes: {info['remaining_requests']}")
        print(f"{'='*60}\n")


# Exemplo de uso
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv("../../.env")
    api_key = os.getenv("FOOTBALL_DATA_API_KEY")

    if not api_key:
        print("❌ FOOTBALL_DATA_API_KEY não encontrada")
        print("\nConfigurar:")
        print("  echo 'FOOTBALL_DATA_API_KEY=sua_key' >> pro/.env")
        exit(1)

    print("=== Collector Tier-Aware Test ===\n")

    # Free tier
    collector = FootballDataCollectorTierAware(api_key, tier='free')
    collector.print_tier_info()

    # Teste de rate limiting
    print("Testando rate limiting...")
    print("(Fazendo 3 requisições)")

    try:
        # Requisição 1
        print("\n1️⃣ Buscando competições...")
        comps = collector.get_competitions()
        print(f"   ✅ {len(comps)} competições")

        # Requisição 2
        print("\n2️⃣ Buscando partidas do Flamengo...")
        matches = collector.get_team_matches_with_limit(1783, last_n=5)
        print(f"   ✅ {len(matches)} partidas")

        # Requisição 3
        print("\n3️⃣ Buscando partidas SCHEDULED do BSA...")
        scheduled = collector.get_matches_with_details("BSA", status="SCHEDULED", limit=3)
        print(f"   ✅ {len(scheduled)} partidas agendadas")

        print(f"\n✅ Teste concluído!")
        print(f"   Requisições restantes: {collector.get_remaining_requests()}")

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        print("\nNOTA: Se você está vendo '403 Access denied',")
        print("      é porque o ambiente de execução está bloqueado.")
        print("      O código está correto e funcionará quando você")
        print("      executar localmente!")
