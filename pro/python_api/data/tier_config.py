"""
Configurações para diferentes tiers de API (free vs paid)

Define limites, features esperadas e comportamentos para cada tier
"""


class TierConfig:
    """
    Configuração de tiers da API football-data.org

    FREE tier:
    - 10 requisições por minuto
    - Competições: Top leagues europeias + BSA
    - Features básicas (score, goals, bookings)

    PAID tier:
    - 100+ requisições por minuto
    - Todas competições
    - Features completas (statistics, lineup detalhado)
    """

    FREE = {
        'name': 'free',
        'rate_limit_requests': 10,
        'rate_limit_window': 60,  # segundos
        'features_expected': ['basic', 'standard'],
        'competitions_available': [
            'PL',   # Premier League
            'PD',   # La Liga
            'BL1',  # Bundesliga
            'SA',   # Serie A
            'FL1',  # Ligue 1
            'DED',  # Eredivisie
            'PPL',  # Primeira Liga
            'BSA',  # Brasileirão
            'CL',   # Champions League
            'ELC',  # Championship
        ],
        'features_count_expected': 10,
        'has_statistics': False,  # Statistics detalhadas não disponíveis
        'has_lineup': False,      # Lineup pode estar limitado
        'has_odds': False,        # Odds requer pacote adicional
        'description': 'Free tier - Dados básicos (score, goals, bookings)'
    }

    PAID = {
        'name': 'paid',
        'rate_limit_requests': 100,
        'rate_limit_window': 60,
        'features_expected': ['basic', 'standard', 'premium'],
        'competitions_available': 'all',
        'features_count_expected': 25,
        'has_statistics': True,   # Statistics completas (shots, possession, etc)
        'has_lineup': True,       # Lineup completo com detalhes
        'has_odds': True,         # Odds disponíveis (se pacote ativado)
        'description': 'Paid tier - Dados completos + statistics detalhadas'
    }

    @classmethod
    def get_config(cls, tier='free'):
        """
        Retorna configuração para o tier especificado

        Args:
            tier: 'free' ou 'paid'

        Returns:
            Dict com configuração
        """
        tier = tier.lower()
        if tier == 'paid':
            return cls.PAID
        return cls.FREE

    @classmethod
    def get_rate_limit(cls, tier='free'):
        """
        Retorna limite de requisições para o tier

        Returns:
            (max_requests, time_window_seconds)
        """
        config = cls.get_config(tier)
        return (
            config['rate_limit_requests'],
            config['rate_limit_window']
        )

    @classmethod
    def has_feature(cls, tier, feature):
        """
        Verifica se feature está disponível no tier

        Args:
            tier: 'free' ou 'paid'
            feature: 'statistics', 'lineup', 'odds'

        Returns:
            bool
        """
        config = cls.get_config(tier)
        feature_key = f'has_{feature}'
        return config.get(feature_key, False)

    @classmethod
    def get_expected_features_count(cls, tier='free'):
        """
        Retorna número esperado de features para o tier

        Returns:
            int
        """
        config = cls.get_config(tier)
        return config['features_count_expected']

    @classmethod
    def is_competition_available(cls, tier, competition_code):
        """
        Verifica se competição está disponível no tier

        Args:
            tier: 'free' ou 'paid'
            competition_code: ex: 'PL', 'BSA', etc

        Returns:
            bool
        """
        config = cls.get_config(tier)
        available = config['competitions_available']

        if available == 'all':
            return True

        return competition_code.upper() in available


class RateLimiter:
    """
    Rate limiter para respeitar limites da API

    Usage:
        limiter = RateLimiter(max_requests=10, time_window=60)
        limiter.wait_if_needed()  # Bloqueia se necessário
    """

    def __init__(self, max_requests=10, time_window=60):
        """
        Args:
            max_requests: Número máximo de requisições
            time_window: Janela de tempo em segundos
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []

    def wait_if_needed(self):
        """
        Aguarda se necessário para respeitar rate limit
        """
        import time

        now = time.time()

        # Remove requisições antigas
        self.requests = [
            r for r in self.requests
            if now - r < self.time_window
        ]

        if len(self.requests) >= self.max_requests:
            # Precisa aguardar
            oldest_request = self.requests[0]
            sleep_time = self.time_window - (now - oldest_request)

            if sleep_time > 0:
                print(f"⏳ Rate limit: aguardando {sleep_time:.1f}s...")
                time.sleep(sleep_time + 0.1)  # +0.1 margem de segurança

                # Remove requisições antigas novamente
                now = time.time()
                self.requests = [
                    r for r in self.requests
                    if now - r < self.time_window
                ]

        # Registra esta requisição
        self.requests.append(time.time())

    def get_remaining_requests(self):
        """
        Retorna quantas requisições ainda podem ser feitas

        Returns:
            int
        """
        import time
        now = time.time()

        # Remove requisições antigas
        self.requests = [
            r for r in self.requests
            if now - r < self.time_window
        ]

        return max(0, self.max_requests - len(self.requests))

    def reset(self):
        """
        Reseta o contador de requisições
        """
        self.requests = []


# Exemplo de uso
if __name__ == "__main__":
    print("=== Tier Configuration ===\n")

    # Free tier
    print("FREE TIER:")
    free_config = TierConfig.get_config('free')
    print(f"  Description: {free_config['description']}")
    print(f"  Rate limit: {free_config['rate_limit_requests']} req/{free_config['rate_limit_window']}s")
    print(f"  Features expected: {free_config['features_count_expected']}")
    print(f"  Has statistics: {free_config['has_statistics']}")
    print(f"  Competitions: {len(free_config['competitions_available'])} available")

    print("\nPAID TIER:")
    paid_config = TierConfig.get_config('paid')
    print(f"  Description: {paid_config['description']}")
    print(f"  Rate limit: {paid_config['rate_limit_requests']} req/{paid_config['rate_limit_window']}s")
    print(f"  Features expected: {paid_config['features_count_expected']}")
    print(f"  Has statistics: {paid_config['has_statistics']}")
    print(f"  Competitions: {paid_config['competitions_available']}")

    # Teste de rate limiter
    print("\n=== Rate Limiter Test ===\n")
    limiter = RateLimiter(max_requests=3, time_window=5)

    import time
    for i in range(5):
        print(f"Requisição {i+1}...")
        limiter.wait_if_needed()
        print(f"  ✅ Executada! (Remaining: {limiter.get_remaining_requests()})")
        time.sleep(0.5)
