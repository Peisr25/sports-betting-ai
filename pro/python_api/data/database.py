"""
Banco de dados SQLite para armazenar histórico de partidas e predições
"""
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class Match(Base):
    """Tabela de partidas"""
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, unique=True)
    competition = Column(String)
    home_team = Column(String)
    away_team = Column(String)
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    match_date = Column(DateTime)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.now)


class Prediction(Base):
    """Tabela de predições"""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer)
    model_name = Column(String)
    home_win_prob = Column(Float)
    draw_prob = Column(Float)
    away_win_prob = Column(Float)
    over_25_prob = Column(Float, nullable=True)
    btts_yes_prob = Column(Float, nullable=True)
    predicted_score = Column(String, nullable=True)
    confidence = Column(String)
    created_at = Column(DateTime, default=datetime.now)


class BettingResult(Base):
    """Tabela de resultados de apostas (para backtesting)"""
    __tablename__ = "betting_results"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer)
    market = Column(String)
    bet = Column(String)
    probability = Column(Float)
    odds = Column(Float)
    stake = Column(Float)
    result = Column(String)  # win, loss, push
    profit = Column(Float)
    created_at = Column(DateTime, default=datetime.now)


class Database:
    """Gerenciador de banco de dados"""

    def __init__(self, db_path: str = "database/betting.db"):
        """
        Args:
            db_path: Caminho para o arquivo do banco
        """
        # Cria diretório se não existir
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Conecta ao banco
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def save_match(self, match_data: dict) -> Match:
        """Salva partida no banco"""
        match = Match(**match_data)
        self.session.add(match)
        self.session.commit()
        return match

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

    def get_matches(self, competition: str = None, limit: int = 100):
        """Busca partidas"""
        query = self.session.query(Match)
        if competition:
            query = query.filter(Match.competition == competition)
        return query.order_by(Match.match_date.desc()).limit(limit).all()

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
    print("✓ Banco de dados criado com sucesso!")
