"""
Módulo para gerenciamento do banco de dados
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import config

Base = declarative_base()


class League(Base):
    """Tabela de ligas"""
    __tablename__ = "leagues"
    
    id = Column(Integer, primary_key=True)
    api_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    country = Column(String)
    season = Column(Integer)
    
    teams = relationship("Team", back_populates="league")
    matches = relationship("Match", back_populates="league")


class Team(Base):
    """Tabela de times"""
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True)
    api_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    league_id = Column(Integer, ForeignKey("leagues.id"))
    
    league = relationship("League", back_populates="teams")
    home_matches = relationship("Match", foreign_keys="Match.home_team_id", back_populates="home_team")
    away_matches = relationship("Match", foreign_keys="Match.away_team_id", back_populates="away_team")


class Match(Base):
    """Tabela de partidas"""
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True)
    api_id = Column(Integer, unique=True, nullable=False)
    league_id = Column(Integer, ForeignKey("leagues.id"))
    home_team_id = Column(Integer, ForeignKey("teams.id"))
    away_team_id = Column(Integer, ForeignKey("teams.id"))
    date = Column(DateTime)
    status = Column(String)
    
    # Resultado
    home_goals = Column(Integer)
    away_goals = Column(Integer)
    
    # Estatísticas
    home_shots = Column(Integer)
    away_shots = Column(Integer)
    home_shots_on_target = Column(Integer)
    away_shots_on_target = Column(Integer)
    home_corners = Column(Integer)
    away_corners = Column(Integer)
    home_fouls = Column(Integer)
    away_fouls = Column(Integer)
    home_yellow_cards = Column(Integer)
    away_yellow_cards = Column(Integer)
    home_red_cards = Column(Integer)
    away_red_cards = Column(Integer)
    
    # Relacionamentos
    league = relationship("League", back_populates="matches")
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    predictions = relationship("Prediction", back_populates="match")


class Prediction(Base):
    """Tabela de predições"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Probabilidades de resultado
    home_win_prob = Column(Float)
    draw_prob = Column(Float)
    away_win_prob = Column(Float)
    
    # Probabilidades de gols
    over_2_5_prob = Column(Float)
    under_2_5_prob = Column(Float)
    btts_yes_prob = Column(Float)
    btts_no_prob = Column(Float)
    
    # Probabilidades de cartões
    over_3_5_cards_prob = Column(Float)
    under_3_5_cards_prob = Column(Float)
    
    # Probabilidades de escanteios
    over_9_5_corners_prob = Column(Float)
    under_9_5_corners_prob = Column(Float)
    
    # Probabilidades de faltas
    over_25_fouls_prob = Column(Float)
    under_25_fouls_prob = Column(Float)
    
    # Metadados
    model_version = Column(String)
    confidence_level = Column(String)
    
    # Relacionamento
    match = relationship("Match", back_populates="predictions")


class DatabaseManager:
    """Gerenciador do banco de dados"""
    
    def __init__(self, database_url: str = None):
        """
        Inicializa o gerenciador
        
        Args:
            database_url: URL do banco de dados
        """
        self.database_url = database_url or config.DATABASE_URL
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Cria todas as tabelas"""
        Base.metadata.create_all(self.engine)
        print("Tabelas criadas com sucesso")
    
    def drop_tables(self):
        """Remove todas as tabelas"""
        Base.metadata.drop_all(self.engine)
        print("Tabelas removidas")
    
    def get_session(self):
        """Retorna uma nova sessão"""
        return self.Session()
    
    def add_league(self, api_id: int, name: str, country: str, season: int):
        """Adiciona uma liga"""
        session = self.get_session()
        try:
            # Verifica se já existe
            existing = session.query(League).filter_by(api_id=api_id).first()
            if existing:
                return existing
            
            league = League(
                api_id=api_id,
                name=name,
                country=country,
                season=season
            )
            session.add(league)
            session.commit()
            return league
        finally:
            session.close()
    
    def add_team(self, api_id: int, name: str, league_id: int):
        """Adiciona um time"""
        session = self.get_session()
        try:
            # Verifica se já existe
            existing = session.query(Team).filter_by(api_id=api_id).first()
            if existing:
                return existing
            
            team = Team(
                api_id=api_id,
                name=name,
                league_id=league_id
            )
            session.add(team)
            session.commit()
            return team
        finally:
            session.close()
    
    def add_match(self, match_data: dict):
        """Adiciona uma partida"""
        session = self.get_session()
        try:
            # Verifica se já existe
            existing = session.query(Match).filter_by(api_id=match_data["api_id"]).first()
            if existing:
                # Atualiza dados
                for key, value in match_data.items():
                    setattr(existing, key, value)
                session.commit()
                return existing
            
            match = Match(**match_data)
            session.add(match)
            session.commit()
            return match
        finally:
            session.close()
    
    def add_prediction(self, prediction_data: dict):
        """Adiciona uma predição"""
        session = self.get_session()
        try:
            prediction = Prediction(**prediction_data)
            session.add(prediction)
            session.commit()
            return prediction
        finally:
            session.close()
    
    def get_team_by_name(self, name: str):
        """Busca time por nome"""
        session = self.get_session()
        try:
            return session.query(Team).filter(Team.name.ilike(f"%{name}%")).all()
        finally:
            session.close()
    
    def get_team_matches(self, team_id: int, limit: int = 10):
        """Busca partidas de um time"""
        session = self.get_session()
        try:
            matches = session.query(Match).filter(
                (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
            ).order_by(Match.date.desc()).limit(limit).all()
            return matches
        finally:
            session.close()
    
    def get_h2h_matches(self, team1_id: int, team2_id: int, limit: int = 5):
        """Busca confrontos diretos"""
        session = self.get_session()
        try:
            matches = session.query(Match).filter(
                ((Match.home_team_id == team1_id) & (Match.away_team_id == team2_id)) |
                ((Match.home_team_id == team2_id) & (Match.away_team_id == team1_id))
            ).order_by(Match.date.desc()).limit(limit).all()
            return matches
        finally:
            session.close()
    
    def get_match_predictions(self, match_id: int):
        """Busca predições de uma partida"""
        session = self.get_session()
        try:
            return session.query(Prediction).filter_by(match_id=match_id).order_by(
                Prediction.created_at.desc()
            ).all()
        finally:
            session.close()


# Exemplo de uso
if __name__ == "__main__":
    db = DatabaseManager()
    
    # Cria tabelas
    db.create_tables()
    
    # Adiciona uma liga de exemplo
    league = db.add_league(
        api_id=71,
        name="Brasileirão Série A",
        country="Brazil",
        season=2025
    )
    print(f"Liga adicionada: {league.name}")
    
    # Adiciona um time de exemplo
    team = db.add_team(
        api_id=123,
        name="Flamengo",
        league_id=league.id
    )
    print(f"Time adicionado: {team.name}")

