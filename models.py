from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime

db = SQLAlchemy()

class Player(db.Model):
    __tablename__ = 'players'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    total_score = db.Column(db.Integer, default=0, nullable=False)
    total_wins = db.Column(db.Integer, default=0, nullable=False)
    total_games = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to game results
    game_results = db.relationship('GameResult', backref='player', lazy=True)
    
    def __repr__(self):
        return f'<Player {self.username}>'
    
    def to_dict(self):
        return {
            'username': self.username,
            'score': self.total_score,
            'wins': self.total_wins,
            'totalGames': self.total_games
        }


class Game(db.Model):
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    game_number = db.Column(db.Integer, unique=True, nullable=False, index=True)
    image_number = db.Column(db.Integer)
    winner_username = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationship to game results
    game_results = db.relationship('GameResult', backref='game', lazy=True)
    
    def __repr__(self):
        return f'<Game {self.game_number}>'


class GameResult(db.Model):
    __tablename__ = 'game_results'
    
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    is_winner = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<GameResult game={self.game_id} player={self.player_id}>'


class CurrentGame(db.Model):
    __tablename__ = 'current_game'
    
    id = db.Column(db.Integer, primary_key=True)
    game_number = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    is_winner = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CurrentGame {self.username}>'


def init_db(app):
    """Initialize the database"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")


def get_latest_game_number():
    """Get the latest game number from the database"""
    latest_game = Game.query.order_by(Game.game_number.desc()).first()
    return latest_game.game_number if latest_game else 0
