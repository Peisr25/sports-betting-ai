"""
Banco de dados SQLite EXPANDIDO para sistema DUAL-API
Suporta dados de football-data.org + API-Football v3

Dados extras incluem:
- Estatísticas detalhadas (corners, fouls, shots, possession, etc)
- Eventos de jogo (gols, cartões, substituições)
- Escalações (lineups)
- Odds/Probabilidades
"""
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, JSON, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()


class Match(Base):
    """
    Tabela de partidas - Dados combinados de ambas APIs

    Suporta IDs de ambas as APIs:
    - match_id_fd: ID da football-data.org
    - match_id_apif: ID da API-Football v3
    """
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)

    # IDs das APIs (pelo menos um deve estar presente)
    match_id_fd = Column(Integer, nullable=True, index=True)  # football-data.org
    match_id_apif = Column(Integer, nullable=True, index=True)  # API-Football v3

    # Dados básicos
    competition = Column(String, index=True)
    season = Column(Integer, index=True)
    home_team = Column(String)
    away_team = Column(String)
    home_team_id_fd = Column(Integer, nullable=True)
    away_team_id_fd = Column(Integer, nullable=True)
    home_team_id_apif = Column(Integer, nullable=True)
    away_team_id_apif = Column(Integer, nullable=True)

    # Resultado
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    home_score_ht = Column(Integer, nullable=True)  # Half-time
    away_score_ht = Column(Integer, nullable=True)

    # Metadados
    match_date = Column(DateTime, index=True)
    status = Column(String)  # SCHEDULED, LIVE, FINISHED, etc
    referee = Column(String, nullable=True)
    venue = Column(String, nullable=True)

    # Fonte dos dados
    data_source = Column(String)  # 'football-data', 'api-football', 'both'

    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relacionamentos
    statistics = relationship("MatchStatistics", back_populates="match", uselist=False)
    events = relationship("MatchEvent", back_populates="match")


class MatchStatistics(Base):
    """
    Estatísticas DETALHADAS da partida
    Dados da API-Football v3 (muito mais rico que football-data.org)
    """
    __tablename__ = "match_statistics"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'), unique=True)

    # Posse de bola
    home_possession = Column(Integer, nullable=True)  # Percentagem
    away_possession = Column(Integer, nullable=True)

    # Chutes (Shots)
    home_shots_total = Column(Integer, nullable=True)
    away_shots_total = Column(Integer, nullable=True)
    home_shots_on_goal = Column(Integer, nullable=True)
    away_shots_on_goal = Column(Integer, nullable=True)
    home_shots_off_goal = Column(Integer, nullable=True)
    away_shots_off_goal = Column(Integer, nullable=True)
    home_shots_blocked = Column(Integer, nullable=True)
    away_shots_blocked = Column(Integer, nullable=True)
    home_shots_inside_box = Column(Integer, nullable=True)
    away_shots_inside_box = Column(Integer, nullable=True)
    home_shots_outside_box = Column(Integer, nullable=True)
    away_shots_outside_box = Column(Integer, nullable=True)

    # Escanteios (Corners)
    home_corners = Column(Integer, nullable=True)
    away_corners = Column(Integer, nullable=True)

    # Impedimentos (Offsides)
    home_offsides = Column(Integer, nullable=True)
    away_offsides = Column(Integer, nullable=True)

    # Faltas (Fouls)
    home_fouls = Column(Integer, nullable=True)
    away_fouls = Column(Integer, nullable=True)

    # Cartões
    home_yellow_cards = Column(Integer, nullable=True)
    away_yellow_cards = Column(Integer, nullable=True)
    home_red_cards = Column(Integer, nullable=True)
    away_red_cards = Column(Integer, nullable=True)

    # Defesas do goleiro
    home_goalkeeper_saves = Column(Integer, nullable=True)
    away_goalkeeper_saves = Column(Integer, nullable=True)

    # Passes
    home_passes_total = Column(Integer, nullable=True)
    away_passes_total = Column(Integer, nullable=True)
    home_passes_accurate = Column(Integer, nullable=True)
    away_passes_accurate = Column(Integer, nullable=True)
    home_passes_percentage = Column(Integer, nullable=True)
    away_passes_percentage = Column(Integer, nullable=True)

    # Ataques esperados (Expected goals - xG)
    home_expected_goals = Column(Float, nullable=True)
    away_expected_goals = Column(Float, nullable=True)

    # Dados JSON brutos (para estatísticas adicionais)
    raw_stats_json = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.now)

    # Relacionamento
    match = relationship("Match", back_populates="statistics")


class MatchEvent(Base):
    """
    Eventos da partida (gols, cartões, substituições)
    Dados da API-Football v3
    """
    __tablename__ = "match_events"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'), index=True)

    # Tempo do evento
    time_elapsed = Column(Integer)  # Minuto
    time_extra = Column(Integer, nullable=True)  # Tempo adicional

    # Tipo de evento
    event_type = Column(String)  # 'Goal', 'Card', 'subst', 'Var', etc
    event_detail = Column(String, nullable=True)  # 'Normal Goal', 'Yellow Card', etc

    # Time e jogador
    team = Column(String)  # 'home' ou 'away'
    player_name = Column(String, nullable=True)
    player_id = Column(Integer, nullable=True)
    assist_player_name = Column(String, nullable=True)
    assist_player_id = Column(Integer, nullable=True)

    # Comentários/Detalhes
    comments = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.now)

    # Relacionamento
    match = relationship("Match", back_populates="events")


class MatchOdds(Base):
    """
    Odds/Probabilidades das casas de apostas
    Dados da API-Football v3
    """
    __tablename__ = "match_odds"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'), index=True)

    # Casa de apostas
    bookmaker_name = Column(String)
    bookmaker_id = Column(Integer)

    # Mercado de apostas
    bet_name = Column(String)  # 'Match Winner', 'Over/Under', 'BTTS', etc

    # Odds (JSON com todas as opções do mercado)
    # Ex: {"home": 1.80, "draw": 3.50, "away": 4.50}
    odds_values = Column(JSON)

    # Timestamp da odd
    update_timestamp = Column(DateTime)

    created_at = Column(DateTime, default=datetime.now)


class Team(Base):
    """
    Tabela de times (consolidado de ambas APIs)
    """
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)

    # IDs das APIs
    team_id_fd = Column(Integer, nullable=True, unique=True, index=True)
    team_id_apif = Column(Integer, nullable=True, unique=True, index=True)

    # Dados básicos
    name = Column(String, index=True)
    short_name = Column(String, nullable=True)
    code = Column(String, nullable=True)  # Ex: 'BEN', 'FCP'
    country = Column(String, nullable=True)
    founded = Column(Integer, nullable=True)

    # Visual
    logo_url = Column(String, nullable=True)

    # Estádio
    venue_name = Column(String, nullable=True)
    venue_city = Column(String, nullable=True)
    venue_capacity = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Prediction(Base):
    """Tabela de predições do modelo"""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'))
    model_name = Column(String)  # 'poisson', 'xgboost', 'ensemble'

    # Probabilidades
    home_win_prob = Column(Float)
    draw_prob = Column(Float)
    away_win_prob = Column(Float)
    over_25_prob = Column(Float, nullable=True)
    btts_yes_prob = Column(Float, nullable=True)

    # Mercados adicionais (com dados da API-Football)
    corners_over_95_prob = Column(Float, nullable=True)
    cards_over_35_prob = Column(Float, nullable=True)

    # Predição
    predicted_score = Column(String, nullable=True)
    predicted_corners_home = Column(Float, nullable=True)
    predicted_corners_away = Column(Float, nullable=True)

    # Confiança
    confidence = Column(String)
    confidence_score = Column(Float, nullable=True)

    # Dados JSON (para predições extras)
    extra_predictions = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.now)


class BettingResult(Base):
    """Tabela de resultados de apostas (para backtesting)"""
    __tablename__ = "betting_results"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'))
    market = Column(String)  # 'result', 'over_under', 'btts', 'corners', etc
    bet = Column(String)
    probability = Column(Float)
    odds = Column(Float)
    stake = Column(Float)
    result = Column(String)  # win, loss, push
    profit = Column(Float)
    created_at = Column(DateTime, default=datetime.now)


class Database:
    """Gerenciador de banco de dados com suporte DUAL-API"""

    def __init__(self, db_path: str = "database/betting_v2.db"):
        """
        Args:
            db_path: Caminho para o arquivo do banco
        """
        # Cria diretório se não existir
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        # Conecta ao banco
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def save_match(self, match_data: dict) -> Match:
        """
        Salva ou atualiza partida no banco
        Suporta merge de dados de ambas APIs
        """
        # Verifica se já existe (por qualquer um dos IDs)
        match = None
        if match_data.get('match_id_fd'):
            match = self.session.query(Match).filter_by(
                match_id_fd=match_data['match_id_fd']
            ).first()

        if not match and match_data.get('match_id_apif'):
            match = self.session.query(Match).filter_by(
                match_id_apif=match_data['match_id_apif']
            ).first()

        if match:
            # Atualiza campos existentes
            for key, value in match_data.items():
                if value is not None:
                    setattr(match, key, value)
            match.updated_at = datetime.now()
        else:
            # Cria novo
            match = Match(**match_data)
            self.session.add(match)

        self.session.commit()
        return match

    def save_match_statistics(self, stats_data: dict) -> MatchStatistics:
        """Salva estatísticas detalhadas da partida"""
        # Verifica se já existe
        existing = self.session.query(MatchStatistics).filter_by(
            match_id=stats_data['match_id']
        ).first()

        if existing:
            for key, value in stats_data.items():
                if value is not None:
                    setattr(existing, key, value)
            self.session.commit()
            return existing
        else:
            stats = MatchStatistics(**stats_data)
            self.session.add(stats)
            self.session.commit()
            return stats

    def save_match_event(self, event_data: dict) -> MatchEvent:
        """Salva evento da partida"""
        event = MatchEvent(**event_data)
        self.session.add(event)
        self.session.commit()
        return event

    def save_match_odds(self, odds_data: dict) -> MatchOdds:
        """Salva odds da partida"""
        odds = MatchOdds(**odds_data)
        self.session.add(odds)
        self.session.commit()
        return odds

    def save_team(self, team_data: dict) -> Team:
        """Salva ou atualiza time no banco"""
        # Verifica se já existe
        team = None
        if team_data.get('team_id_fd'):
            team = self.session.query(Team).filter_by(
                team_id_fd=team_data['team_id_fd']
            ).first()

        if not team and team_data.get('team_id_apif'):
            team = self.session.query(Team).filter_by(
                team_id_apif=team_data['team_id_apif']
            ).first()

        if team:
            for key, value in team_data.items():
                if value is not None:
                    setattr(team, key, value)
            team.updated_at = datetime.now()
        else:
            team = Team(**team_data)
            self.session.add(team)

        self.session.commit()
        return team

    def save_prediction(self, pred_data: dict) -> Prediction:
        """Salva predição no banco"""
        prediction = Prediction(**pred_data)
        self.session.add(prediction)
        self.session.commit()
        return prediction

    def save_betting_result(self, result_data: dict) -> BettingResult:
        """Salva resultado de aposta"""
        result = BettingResult(**result_data)
        self.session.add(result)
        self.session.commit()
        return result

    def get_matches(self, competition: str = None, season: int = None, limit: int = 100):
        """Busca partidas"""
        query = self.session.query(Match)

        if competition:
            query = query.filter(Match.competition == competition)
        if season:
            query = query.filter(Match.season == season)

        return query.order_by(Match.match_date.desc()).limit(limit).all()

    def get_match_with_stats(self, match_id: int):
        """Busca partida com todas as estatísticas"""
        match = self.session.query(Match).filter_by(id=match_id).first()
        return match

    def get_predictions(self, match_id: int = None):
        """Busca predições"""
        query = self.session.query(Prediction)
        if match_id:
            query = query.filter(Prediction.match_id == match_id)
        return query.all()

    def close(self):
        """Fecha conexão"""
        self.session.close()


if __name__ == "__main__":
    db = Database()
    print("✓ Banco de dados V2 (Dual-API) criado com sucesso!")
    print(f"✓ Tabelas: {list(Base.metadata.tables.keys())}")
