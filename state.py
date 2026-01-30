# state.py

from models import db, Game

current_image_name = None
current_csv_name = None

isFound = False
currentWinner = None
score = None
usernameSet = set()

def getGameNumber():
    """Get the next game number from the database"""
    latest_game = Game.query.order_by(Game.game_number.desc()).first()
    return (latest_game.game_number + 1) if latest_game else 1

queued_users = set()
client_event_queues = {}

def incrementGameNumber(gameNum):
    """Create a new game entry in the database"""
    new_game = Game(game_number=gameNum)
    db.session.add(new_game)
    db.session.commit()
