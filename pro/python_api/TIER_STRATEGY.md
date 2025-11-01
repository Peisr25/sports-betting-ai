# 🎯 Estratégia: Arquitetura Tier-Aware (Free vs Paid)

## 📋 Conceito

Criar código **COMPLETO** que:
- ✅ Calcula TODAS as features possíveis (como se fosse paid tier)
- ✅ Degrada gracefully quando dados não disponíveis (free tier)
- ✅ Flag `tier='free'` ou `tier='paid'` controla comportamento
- ✅ Fácil upgrade: apenas mudar flag quando assinar plano

---

## 🏗️ Design Pattern: Graceful Degradation

```python
class FeatureExtractor:
    def __init__(self, tier='free'):
        self.tier = tier
        self.features_available = self._detect_features()
    
    def extract_features(self, match_data):
        features = {}
        
        # SEMPRE tenta extrair todas as features
        features.update(self._extract_basic_features(match_data))
        features.update(self._extract_advanced_features(match_data))
        features.update(self._extract_premium_features(match_data))
        
        # Remove None values (features não disponíveis)
        return {k: v for k, v in features.items() if v is not None}
```

---

## 📊 Níveis de Features

### Tier 1: BASIC (sempre disponível)
```python
def _extract_basic_features(self, match_data):
    """
    Features que SEMPRE existem (score básico)
    """
    return {
        'goals_scored': match_data.get('score', {}).get('fullTime', {}).get('home'),
        'goals_conceded': match_data.get('score', {}).get('fullTime', {}).get('away'),
        'is_home': 1 if match_data.get('homeTeam') else 0
    }
```

### Tier 2: STANDARD (provável no free tier)
```python
def _extract_standard_features(self, match_data):
    """
    Features que PODEM estar disponíveis no free tier
    """
    goals = match_data.get('goals', [])
    bookings = match_data.get('bookings', [])
    
    return {
        'total_goals': len(goals) if goals else None,
        'yellow_cards': len([b for b in bookings if b.get('card') == 'YELLOW']) if bookings else None,
        'red_cards': len([b for b in bookings if b.get('card') == 'RED']) if bookings else None,
    }
```

### Tier 3: PREMIUM (apenas paid tier)
```python
def _extract_premium_features(self, match_data):
    """
    Features detalhadas (statistics completas)
    Retorna None se não disponível
    """
    stats = match_data.get('homeTeam', {}).get('statistics')
    
    if not stats:
        return {
            'shots': None,
            'shots_on_goal': None,
            'possession': None,
            'corners': None,
            'fouls': None,
            'saves': None
        }
    
    return {
        'shots': stats.get('shots'),
        'shots_on_goal': stats.get('shots_on_goal'),
        'possession': stats.get('ball_possession'),
        'corners': stats.get('corner_kicks'),
        'fouls': stats.get('fouls'),
        'saves': stats.get('saves')
    }
```

---

## 🎛️ Configuração Tier

```python
# config.py
class TierConfig:
    FREE = {
        'name': 'free',
        'rate_limit': 10,  # req/min
        'features_expected': ['basic', 'standard'],
        'competitions': ['PL', 'PD', 'BL1', 'SA', 'FL1'],
        'features_count': 8  # ~8 features básicas
    }
    
    PAID = {
        'name': 'paid',
        'rate_limit': 100,  # req/min
        'features_expected': ['basic', 'standard', 'premium'],
        'competitions': 'all',
        'features_count': 25  # ~25 features completas
    }
    
    @classmethod
    def get_config(cls, tier='free'):
        return cls.FREE if tier == 'free' else cls.PAID
```

---

## 🔧 Feature Extractor Completo

```python
class FootballDataFeatureExtractor:
    """
    Extrator de features tier-aware
    
    Usage:
        # Free tier
        extractor = FootballDataFeatureExtractor(tier='free')
        features = extractor.extract(match_data)
        # Retorna: 6-10 features básicas
        
        # Paid tier
        extractor = FootballDataFeatureExtractor(tier='paid')
        features = extractor.extract(match_data)
        # Retorna: 20-30 features completas
    """
    
    def __init__(self, tier='free'):
        self.tier = tier
        self.config = TierConfig.get_config(tier)
        
    def extract_team_features(self, team_id, matches):
        """
        Extrai features de um time baseado em últimas N partidas
        
        Args:
            team_id: ID do time
            matches: Lista de partidas (FINISHED)
            
        Returns:
            Dict com features disponíveis
        """
        features = {}
        
        # TIER 1: BASIC - Sempre funciona
        features['goals_scored_avg'] = self._calc_goals_avg(team_id, matches, 'scored')
        features['goals_conceded_avg'] = self._calc_goals_avg(team_id, matches, 'conceded')
        features['win_rate'] = self._calc_win_rate(team_id, matches)
        features['matches_analyzed'] = len(matches)
        
        # TIER 2: STANDARD - Tenta extrair
        if self._has_goals_details(matches):
            features['goals_from_penalty'] = self._calc_penalty_goals(team_id, matches)
            features['goals_first_half'] = self._calc_first_half_goals(team_id, matches)
        
        if self._has_bookings(matches):
            features['yellow_cards_avg'] = self._calc_yellow_cards_avg(team_id, matches)
            features['red_cards_avg'] = self._calc_red_cards_avg(team_id, matches)
        
        # TIER 3: PREMIUM - Só se disponível
        if self._has_statistics(matches):
            features['shots_avg'] = self._calc_stat_avg(team_id, matches, 'shots')
            features['shots_on_goal_avg'] = self._calc_stat_avg(team_id, matches, 'shots_on_goal')
            features['possession_avg'] = self._calc_stat_avg(team_id, matches, 'ball_possession')
            features['corners_avg'] = self._calc_stat_avg(team_id, matches, 'corner_kicks')
            features['fouls_avg'] = self._calc_stat_avg(team_id, matches, 'fouls')
            features['saves_avg'] = self._calc_stat_avg(team_id, matches, 'saves')
            features['shot_accuracy'] = self._calc_shot_accuracy(team_id, matches)
            features['conversion_rate'] = self._calc_conversion_rate(team_id, matches)
        
        if self._has_lineup(matches):
            features['formation_stability'] = self._calc_formation_stability(team_id, matches)
            features['avg_starters_age'] = self._calc_avg_age(team_id, matches)
        
        # Remove None values
        return {k: v for k, v in features.items() if v is not None}
    
    def _has_statistics(self, matches):
        """Verifica se partidas têm statistics"""
        if not matches:
            return False
        return any(
            m.get('homeTeam', {}).get('statistics') or 
            m.get('awayTeam', {}).get('statistics')
            for m in matches
        )
    
    def _has_goals_details(self, matches):
        """Verifica se tem detalhes de gols"""
        if not matches:
            return False
        return any(m.get('goals') for m in matches)
    
    def _has_bookings(self, matches):
        """Verifica se tem cartões"""
        if not matches:
            return False
        return any(m.get('bookings') for m in matches)
    
    def _has_lineup(self, matches):
        """Verifica se tem escalação"""
        if not matches:
            return False
        return any(
            m.get('homeTeam', {}).get('lineup') or 
            m.get('awayTeam', {}).get('lineup')
            for m in matches
        )
    
    # ... métodos de cálculo ...
```

---

## 🤖 Modelos Adaptativos

```python
class AdaptiveXGBoostModel:
    """
    XGBoost que se adapta ao número de features disponíveis
    """
    
    def __init__(self, tier='free'):
        self.tier = tier
        self.model = None
        self.feature_names = None
        self.is_trained = False
        
    def train(self, X, y):
        """
        Treina com quantas features estiverem disponíveis
        
        Args:
            X: Array de features (shape: [n_samples, n_features])
            y: Labels
        """
        self.feature_names = [f"feature_{i}" for i in range(X.shape[1])]
        
        print(f"🎯 Treinando com {X.shape[1]} features")
        
        # XGBoost funciona com qualquer número de features
        self.model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            objective='multi:softprob',
            num_class=3
        )
        
        self.model.fit(X, y)
        self.is_trained = True
        
        print(f"✅ Modelo treinado com {X.shape[1]} features")
        
    def predict(self, X):
        """
        Faz predição com features disponíveis
        
        Se X tem MENOS features que o treinamento:
        - Preenche com valores médios
        
        Se X tem MAIS features:
        - Ignora features extras
        """
        if not self.is_trained:
            raise Exception("Modelo não treinado")
        
        expected_features = len(self.feature_names)
        actual_features = X.shape[1]
        
        if actual_features < expected_features:
            # Preenche com zeros (ou médias)
            padding = np.zeros((X.shape[0], expected_features - actual_features))
            X = np.hstack([X, padding])
            print(f"⚠️  Features preenchidas: {actual_features} → {expected_features}")
        
        elif actual_features > expected_features:
            # Trunca features extras
            X = X[:, :expected_features]
            print(f"⚠️  Features truncadas: {actual_features} → {expected_features}")
        
        return self.model.predict_proba(X)
```

---

## 📦 Collector Tier-Aware

```python
class FootballDataCollectorTierAware(FootballDataCollector):
    """
    Collector que respeita limites do tier
    """
    
    def __init__(self, api_key, tier='free'):
        super().__init__(api_key)
        self.tier = tier
        self.config = TierConfig.get_config(tier)
        self.rate_limiter = RateLimiter(
            max_requests=self.config['rate_limit'],
            time_window=60
        )
    
    def _make_request(self, endpoint, params=None):
        """
        Override para adicionar rate limiting
        """
        self.rate_limiter.wait_if_needed()
        return super()._make_request(endpoint, params)
    
    def get_detailed_match(self, match_id):
        """
        Busca detalhes completos de uma partida
        
        Free tier: Pode não ter statistics
        Paid tier: Tem tudo
        """
        match = self._make_request(f"matches/{match_id}")
        
        if self.tier == 'free':
            # Log o que está disponível
            has_stats = bool(match.get('homeTeam', {}).get('statistics'))
            has_lineup = bool(match.get('homeTeam', {}).get('lineup'))
            
            print(f"📊 Match {match_id}:")
            print(f"   Statistics: {'✅' if has_stats else '❌'}")
            print(f"   Lineup: {'✅' if has_lineup else '❌'}")
        
        return match
```

---

## 🎯 Pipeline Tier-Aware

```python
class BettingPipelineFD:
    """
    Pipeline completo com suporte a free/paid tier
    """
    
    def __init__(self, api_key, tier='free', db_path="database/betting_v2.db"):
        self.tier = tier
        self.config = TierConfig.get_config(tier)
        
        # Componentes tier-aware
        self.collector = FootballDataCollectorTierAware(api_key, tier)
        self.extractor = FootballDataFeatureExtractor(tier)
        self.db = Database(db_path)
        
        # Modelos
        self.poisson = PoissonModel()
        self.xgboost = AdaptiveXGBoostModel(tier)
        self.ensemble = EnsembleModel()
        
        print(f"🎯 Pipeline inicializado: {tier.upper()} tier")
        print(f"   Features esperadas: {self.config['features_count']}")
        print(f"   Rate limit: {self.config['rate_limit']} req/min")
    
    def analyze_scheduled_matches(self, days_ahead=7):
        """
        Analisa partidas agendadas
        
        Funciona com free OU paid tier
        """
        # Busca partidas SCHEDULED
        scheduled = self.collector.get_matches(
            competition_code="PL",
            status="SCHEDULED"
        )
        
        results = []
        for match in scheduled[:10]:  # Limita para não estourar quota
            result = self._analyze_match(match)
            results.append(result)
        
        return results
    
    def _analyze_match(self, match):
        """
        Analisa uma partida
        
        Adapta-se às features disponíveis
        """
        home_id = match['homeTeam']['id']
        away_id = match['awayTeam']['id']
        
        # Busca histórico
        home_matches = self.collector.get_team_matches_history(home_id, last_n=10)
        away_matches = self.collector.get_team_matches_history(away_id, last_n=10)
        
        # Extrai features (quantas estiverem disponíveis)
        home_features = self.extractor.extract_team_features(home_id, home_matches)
        away_features = self.extractor.extract_team_features(away_id, away_matches)
        
        print(f"\n📊 Features extraídas:")
        print(f"   Home: {len(home_features)} features")
        print(f"   Away: {len(away_features)} features")
        
        # Predição (modelo se adapta)
        X = self._combine_features(home_features, away_features)
        prediction = self.xgboost.predict(X) if self.xgboost.is_trained else None
        
        return {
            'match': f"{match['homeTeam']['name']} vs {match['awayTeam']['name']}",
            'features_used': len(home_features) + len(away_features),
            'tier': self.tier,
            'prediction': prediction
        }
```

---

## 💾 Exemplo de Uso

```python
# FREE TIER (agora)
pipeline_free = BettingPipelineFD(
    api_key="sua_key",
    tier='free'
)
results = pipeline_free.analyze_scheduled_matches()
# Features: ~8-12
# Funciona com dados limitados

# PAID TIER (futuro - apenas mudar flag)
pipeline_paid = BettingPipelineFD(
    api_key="sua_key",
    tier='paid'  # ← ÚNICA mudança!
)
results = pipeline_paid.analyze_scheduled_matches()
# Features: ~25-30
# Usa todos os dados disponíveis
```

---

## 🎉 Vantagens

1. ✅ **Código único** - Free e Paid usam mesma base
2. ✅ **Upgrade fácil** - Só mudar `tier='paid'`
3. ✅ **Graceful degradation** - Funciona com o que tiver
4. ✅ **Preparado para futuro** - Todos os cálculos já implementados
5. ✅ **Testável** - Pode testar com dados simulados
6. ✅ **Manutenível** - Um lugar para cada feature

---

## 🚀 Próxima Implementação

1. `data/fd_feature_extractor.py` - Extrator tier-aware
2. `data/tier_config.py` - Configurações
3. `models/adaptive_models.py` - Modelos adaptativos
4. `analysis/betting_pipeline_fd.py` - Pipeline completo
5. `train_model_fd.py` - Treino com features variáveis

**Tudo preparado para FREE agora, PAID depois!** 🎯
