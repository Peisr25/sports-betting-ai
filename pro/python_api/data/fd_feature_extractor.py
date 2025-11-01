"""
Feature Extractor Tier-Aware para football-data.org

Extrai features adaptando-se ao tier (free vs paid)
- FREE: ~10 features básicas (score, goals, bookings)
- PAID: ~25 features completas (+ statistics, lineup)

Graceful degradation: sempre tenta todas, remove None
"""
from typing import Dict, List, Optional
import numpy as np

try:
    from .tier_config import TierConfig
except ImportError:
    # Para execução direta
    from tier_config import TierConfig


class FootballDataFeatureExtractor:
    """
    Extrator de features com suporte a múltiplos tiers

    Usage:
        # Free tier
        extractor = FootballDataFeatureExtractor(tier='free')
        features = extractor.extract_team_features(team_id, matches)
        # Retorna: ~8-12 features

        # Paid tier (futuro)
        extractor = FootballDataFeatureExtractor(tier='paid')
        features = extractor.extract_team_features(team_id, matches)
        # Retorna: ~20-30 features
    """

    def __init__(self, tier='free'):
        """
        Args:
            tier: 'free' ou 'paid'
        """
        self.tier = tier
        self.config = TierConfig.get_config(tier)

        print(f"🎯 Feature Extractor: {tier.upper()} tier")
        print(f"   Features esperadas: ~{self.config['features_count_expected']}")

    def extract_team_features(self, team_id: int, matches: List[Dict]) -> Dict:
        """
        Extrai features de um time baseado em últimas N partidas

        SEMPRE tenta extrair TODAS as features
        Remove as que retornam None (não disponíveis)

        Args:
            team_id: ID do time
            matches: Lista de partidas FINISHED

        Returns:
            Dict com features disponíveis
        """
        if not matches:
            return {}

        features = {}

        # TIER 1: BASIC - Sempre funciona (baseado apenas em score)
        features.update(self._extract_basic_features(team_id, matches))

        # TIER 2: STANDARD - Tenta extrair (goals, bookings, substitutions)
        features.update(self._extract_standard_features(team_id, matches))

        # TIER 3: PREMIUM - Só se disponível (statistics, lineup detalhado)
        if self.config['has_statistics']:
            features.update(self._extract_premium_features(team_id, matches))

        # Remove None values (features não disponíveis)
        features = {k: v for k, v in features.items() if v is not None}

        return features

    # ==================== TIER 1: BASIC ====================

    def _extract_basic_features(self, team_id: int, matches: List[Dict]) -> Dict:
        """
        Features BÁSICAS que SEMPRE existem

        Baseadas apenas em score (fullTime)
        """
        features = {
            'goals_scored_avg': self._calc_goals_avg(team_id, matches, 'scored'),
            'goals_conceded_avg': self._calc_goals_avg(team_id, matches, 'conceded'),
            'win_rate': self._calc_win_rate(team_id, matches),
            'draw_rate': self._calc_draw_rate(team_id, matches),
            'loss_rate': self._calc_loss_rate(team_id, matches),
            'clean_sheet_rate': self._calc_clean_sheet_rate(team_id, matches),
            'matches_analyzed': len(matches)
        }

        return features

    def _calc_goals_avg(self, team_id: int, matches: List[Dict], goal_type: str) -> Optional[float]:
        """
        Calcula média de gols marcados ou sofridos

        Args:
            goal_type: 'scored' ou 'conceded'
        """
        goals_list = []

        for match in matches:
            score = match.get('score', {}).get('fullTime', {})
            home_id = match.get('homeTeam', {}).get('id')

            home_goals = score.get('home')
            away_goals = score.get('away')

            if home_goals is None or away_goals is None:
                continue

            is_home = (home_id == team_id)

            if goal_type == 'scored':
                goals = home_goals if is_home else away_goals
            else:  # conceded
                goals = away_goals if is_home else home_goals

            goals_list.append(goals)

        return round(np.mean(goals_list), 2) if goals_list else None

    def _calc_win_rate(self, team_id: int, matches: List[Dict]) -> Optional[float]:
        """
        Calcula taxa de vitórias
        """
        wins = 0
        total = 0

        for match in matches:
            result = self._get_match_result(team_id, match)
            if result is not None:
                total += 1
                if result == 'W':
                    wins += 1

        return round(wins / total, 3) if total > 0 else None

    def _calc_draw_rate(self, team_id: int, matches: List[Dict]) -> Optional[float]:
        """
        Calcula taxa de empates
        """
        draws = 0
        total = 0

        for match in matches:
            result = self._get_match_result(team_id, match)
            if result is not None:
                total += 1
                if result == 'D':
                    draws += 1

        return round(draws / total, 3) if total > 0 else None

    def _calc_loss_rate(self, team_id: int, matches: List[Dict]) -> Optional[float]:
        """
        Calcula taxa de derrotas
        """
        losses = 0
        total = 0

        for match in matches:
            result = self._get_match_result(team_id, match)
            if result is not None:
                total += 1
                if result == 'L':
                    losses += 1

        return round(losses / total, 3) if total > 0 else None

    def _calc_clean_sheet_rate(self, team_id: int, matches: List[Dict]) -> Optional[float]:
        """
        Calcula % de jogos sem sofrer gol
        """
        clean_sheets = 0
        total = 0

        for match in matches:
            score = match.get('score', {}).get('fullTime', {})
            home_id = match.get('homeTeam', {}).get('id')

            home_goals = score.get('home')
            away_goals = score.get('away')

            if home_goals is None or away_goals is None:
                continue

            total += 1
            is_home = (home_id == team_id)
            conceded = away_goals if is_home else home_goals

            if conceded == 0:
                clean_sheets += 1

        return round(clean_sheets / total, 3) if total > 0 else None

    def _get_match_result(self, team_id: int, match: Dict) -> Optional[str]:
        """
        Retorna resultado da partida: 'W', 'D' ou 'L'
        """
        score = match.get('score', {}).get('fullTime', {})
        home_id = match.get('homeTeam', {}).get('id')

        home_goals = score.get('home')
        away_goals = score.get('away')

        if home_goals is None or away_goals is None:
            return None

        is_home = (home_id == team_id)

        if home_goals == away_goals:
            return 'D'
        elif (home_goals > away_goals and is_home) or (away_goals > home_goals and not is_home):
            return 'W'
        else:
            return 'L'

    # ==================== TIER 2: STANDARD ====================

    def _extract_standard_features(self, team_id: int, matches: List[Dict]) -> Dict:
        """
        Features STANDARD (podem estar disponíveis no free tier)

        Baseadas em: goals, bookings, substitutions
        """
        features = {}

        # Goals detalhados
        if self._has_goals_details(matches):
            features['goals_from_penalty'] = self._calc_penalty_goals(team_id, matches)
            features['goals_first_half'] = self._calc_first_half_goals(team_id, matches)
            features['assists_avg'] = self._calc_assists_avg(team_id, matches)

        # Disciplina
        if self._has_bookings(matches):
            features['yellow_cards_avg'] = self._calc_yellow_cards_avg(team_id, matches)
            features['red_cards_avg'] = self._calc_red_cards_avg(team_id, matches)

        # Substituições
        if self._has_substitutions(matches):
            features['substitutions_avg'] = self._calc_substitutions_avg(team_id, matches)

        return features

    def _has_goals_details(self, matches: List[Dict]) -> bool:
        """
        Verifica se partidas têm detalhes de gols
        """
        return any(m.get('goals') for m in matches)

    def _has_bookings(self, matches: List[Dict]) -> bool:
        """
        Verifica se partidas têm cartões
        """
        return any(m.get('bookings') for m in matches)

    def _has_substitutions(self, matches: List[Dict]) -> bool:
        """
        Verifica se partidas têm substituições
        """
        return any(m.get('substitutions') for m in matches)

    def _calc_penalty_goals(self, team_id: int, matches: List[Dict]) -> Optional[float]:
        """
        Calcula média de gols de pênalti
        """
        penalty_goals = 0
        total_matches = 0

        for match in matches:
            goals = match.get('goals', [])
            if not goals:
                continue

            total_matches += 1

            for goal in goals:
                if goal.get('type') == 'PENALTY':
                    scorer_team = goal.get('team', {}).get('id')
                    if scorer_team == team_id:
                        penalty_goals += 1

        return round(penalty_goals / total_matches, 2) if total_matches > 0 else None

    def _calc_first_half_goals(self, team_id: int, matches: List[Dict]) -> Optional[float]:
        """
        Calcula média de gols no primeiro tempo
        """
        first_half_goals = 0
        total_matches = 0

        for match in matches:
            goals = match.get('goals', [])
            if not goals:
                continue

            total_matches += 1

            for goal in goals:
                minute = goal.get('minute', 0)
                if minute <= 45:  # Primeiro tempo
                    scorer_team = goal.get('team', {}).get('id')
                    if scorer_team == team_id:
                        first_half_goals += 1

        return round(first_half_goals / total_matches, 2) if total_matches > 0 else None

    def _calc_assists_avg(self, team_id: int, matches: List[Dict]) -> Optional[float]:
        """
        Calcula média de assistências
        """
        assists = 0
        total_matches = 0

        for match in matches:
            goals = match.get('goals', [])
            if not goals:
                continue

            total_matches += 1

            for goal in goals:
                if goal.get('assist'):
                    scorer_team = goal.get('team', {}).get('id')
                    if scorer_team == team_id:
                        assists += 1

        return round(assists / total_matches, 2) if total_matches > 0 else None

    def _calc_yellow_cards_avg(self, team_id: int, matches: List[Dict]) -> Optional[float]:
        """
        Calcula média de cartões amarelos
        """
        yellow_cards = 0
        total_matches = 0

        for match in matches:
            bookings = match.get('bookings', [])
            if not bookings:
                continue

            total_matches += 1

            for booking in bookings:
                if booking.get('card') == 'YELLOW':
                    team = booking.get('team', {}).get('id')
                    if team == team_id:
                        yellow_cards += 1

        return round(yellow_cards / total_matches, 2) if total_matches > 0 else None

    def _calc_red_cards_avg(self, team_id: int, matches: List[Dict]) -> Optional[float]:
        """
        Calcula média de cartões vermelhos
        """
        red_cards = 0
        total_matches = 0

        for match in matches:
            bookings = match.get('bookings', [])
            if not bookings:
                continue

            total_matches += 1

            for booking in bookings:
                card = booking.get('card')
                if card in ['RED', 'YELLOW_RED']:
                    team = booking.get('team', {}).get('id')
                    if team == team_id:
                        red_cards += 1

        return round(red_cards / total_matches, 2) if total_matches > 0 else None

    def _calc_substitutions_avg(self, team_id: int, matches: List[Dict]) -> Optional[float]:
        """
        Calcula média de substituições
        """
        substitutions = 0
        total_matches = 0

        for match in matches:
            subs = match.get('substitutions', [])
            if not subs:
                continue

            total_matches += 1

            for sub in subs:
                team = sub.get('team', {}).get('id')
                if team == team_id:
                    substitutions += 1

        return round(substitutions / total_matches, 2) if total_matches > 0 else None

    # ==================== TIER 3: PREMIUM ====================

    def _extract_premium_features(self, team_id: int, matches: List[Dict]) -> Dict:
        """
        Features PREMIUM (apenas paid tier)

        Baseadas em: statistics (shots, possession, etc)
        """
        features = {}

        if self._has_statistics(matches):
            features['shots_avg'] = self._calc_stat_avg(team_id, matches, 'shots')
            features['shots_on_goal_avg'] = self._calc_stat_avg(team_id, matches, 'shots_on_goal')
            features['possession_avg'] = self._calc_stat_avg(team_id, matches, 'ball_possession')
            features['corners_avg'] = self._calc_stat_avg(team_id, matches, 'corner_kicks')
            features['fouls_avg'] = self._calc_stat_avg(team_id, matches, 'fouls')
            features['saves_avg'] = self._calc_stat_avg(team_id, matches, 'saves')

            # Features derivadas
            features['shot_accuracy'] = self._calc_shot_accuracy(team_id, matches)
            features['conversion_rate'] = self._calc_conversion_rate(team_id, matches)

        return features

    def _has_statistics(self, matches: List[Dict]) -> bool:
        """
        Verifica se partidas têm statistics detalhadas
        """
        return any(
            m.get('homeTeam', {}).get('statistics') or
            m.get('awayTeam', {}).get('statistics')
            for m in matches
        )

    def _calc_stat_avg(self, team_id: int, matches: List[Dict], stat_name: str) -> Optional[float]:
        """
        Calcula média de uma estatística específica
        """
        stat_values = []

        for match in matches:
            home_id = match.get('homeTeam', {}).get('id')
            is_home = (home_id == team_id)

            if is_home:
                stats = match.get('homeTeam', {}).get('statistics', {})
            else:
                stats = match.get('awayTeam', {}).get('statistics', {})

            if stats and stat_name in stats:
                stat_values.append(stats[stat_name])

        return round(np.mean(stat_values), 2) if stat_values else None

    def _calc_shot_accuracy(self, team_id: int, matches: List[Dict]) -> Optional[float]:
        """
        Calcula precisão de chutes (shots_on_goal / shots)
        """
        total_shots = 0
        total_on_goal = 0

        for match in matches:
            home_id = match.get('homeTeam', {}).get('id')
            is_home = (home_id == team_id)

            if is_home:
                stats = match.get('homeTeam', {}).get('statistics', {})
            else:
                stats = match.get('awayTeam', {}).get('statistics', {})

            if stats:
                shots = stats.get('shots', 0)
                on_goal = stats.get('shots_on_goal', 0)

                total_shots += shots
                total_on_goal += on_goal

        if total_shots > 0:
            return round(total_on_goal / total_shots, 3)
        return None

    def _calc_conversion_rate(self, team_id: int, matches: List[Dict]) -> Optional[float]:
        """
        Calcula taxa de conversão (goals / shots_on_goal)
        """
        total_goals = 0
        total_on_goal = 0

        for match in matches:
            home_id = match.get('homeTeam', {}).get('id')
            is_home = (home_id == team_id)

            # Goals
            score = match.get('score', {}).get('fullTime', {})
            home_goals = score.get('home', 0)
            away_goals = score.get('away', 0)
            goals = home_goals if is_home else away_goals
            total_goals += goals

            # Shots on goal
            if is_home:
                stats = match.get('homeTeam', {}).get('statistics', {})
            else:
                stats = match.get('awayTeam', {}).get('statistics', {})

            if stats:
                on_goal = stats.get('shots_on_goal', 0)
                total_on_goal += on_goal

        if total_on_goal > 0:
            return round(total_goals / total_on_goal, 3)
        return None

    # ==================== HELPERS ====================

    def get_feature_names(self) -> List[str]:
        """
        Retorna lista de nomes de features que podem ser extraídas
        """
        basic = [
            'goals_scored_avg', 'goals_conceded_avg',
            'win_rate', 'draw_rate', 'loss_rate',
            'clean_sheet_rate', 'matches_analyzed'
        ]

        standard = [
            'goals_from_penalty', 'goals_first_half', 'assists_avg',
            'yellow_cards_avg', 'red_cards_avg', 'substitutions_avg'
        ]

        premium = [
            'shots_avg', 'shots_on_goal_avg', 'possession_avg',
            'corners_avg', 'fouls_avg', 'saves_avg',
            'shot_accuracy', 'conversion_rate'
        ]

        if self.config['has_statistics']:
            return basic + standard + premium
        else:
            return basic + standard


# Exemplo de uso
if __name__ == "__main__":
    print("=== Feature Extractor Test ===\n")

    # Dados de exemplo (simulados)
    sample_matches = [
        {
            'homeTeam': {'id': 65, 'name': 'Manchester City'},
            'awayTeam': {'id': 57, 'name': 'Arsenal'},
            'score': {'fullTime': {'home': 2, 'away': 1}},
            'goals': [
                {'minute': 15, 'type': 'REGULAR', 'team': {'id': 65}},
                {'minute': 30, 'type': 'PENALTY', 'team': {'id': 65}},
                {'minute': 75, 'type': 'REGULAR', 'team': {'id': 57}}
            ],
            'bookings': [
                {'card': 'YELLOW', 'team': {'id': 65}},
                {'card': 'YELLOW', 'team': {'id': 57}}
            ]
        }
    ]

    # Free tier
    print("FREE TIER:")
    extractor_free = FootballDataFeatureExtractor(tier='free')
    features_free = extractor_free.extract_team_features(65, sample_matches)
    print(f"\n  Features extraídas: {len(features_free)}")
    for key, value in features_free.items():
        print(f"    {key}: {value}")

    # Paid tier (simulado)
    print("\n\nPAID TIER (simulado):")
    extractor_paid = FootballDataFeatureExtractor(tier='paid')
    features_paid = extractor_paid.extract_team_features(65, sample_matches)
    print(f"\n  Features extraídas: {len(features_paid)}")
    print(f"  (Mesmas que free tier pois dados simulados não têm statistics)")
