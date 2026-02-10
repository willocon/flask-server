#evaluation.py

from models import db, Player, Game, GameResult, CurrentGame
from sqlalchemy import func
import state
import os

IMAGE_DIR = os.getenv("IMAGE_DIR", "images")

def evaluatePlayers():
    """Evaluate players from current game and update leaderboard"""
    # Get all current game entries
    current_games = CurrentGame.query.all()
    
    if not current_games:
        print("No current game entries to evaluate")
        return
    
    # Read coordinates from the CSV file
    coords_data = None
    csv_path = os.path.join(IMAGE_DIR, "coords.csv")
    if os.path.exists(csv_path):
        try:
            with open(csv_path, 'r') as f:
                coords_data = f.read().strip()
        except Exception as e:
            print(f"Error reading coordinates file: {e}")
    
    game_number = state.getGameNumber() - 1  # Current game that's ending
    
    # Get or create the game record
    game = Game.query.filter_by(game_number=game_number).first()
    if not game:
        game = Game(game_number=game_number)
        db.session.add(game)
        db.session.flush()
    
    # Process each player's result
    for current_game_entry in current_games:
        username = current_game_entry.username
        score = current_game_entry.score
        is_winner = current_game_entry.is_winner
        
        # Update winner in game record
        if is_winner and not game.winner_username:
            game.winner_username = username
        
        # Get or create player
        player = Player.query.filter_by(username=username).first()
        if not player:
            player = Player(
                username=username,
                total_score=score,
                total_wins=1 if is_winner else 0,
                total_games=1
            )
            db.session.add(player)
            db.session.flush()
        else:
            # Update player stats
            player.total_score += score
            player.total_wins += 1 if is_winner else 0
            player.total_games += 1
        
        # Create game result record
        game_result = GameResult(
            game_id=game.id,
            player_id=player.id,
            username=username,
            score=score,
            is_winner=is_winner,
            coords=coords_data
        )
        db.session.add(game_result)
    
    # Commit all changes
    db.session.commit()
    
    # Clear current game table
    CurrentGame.query.delete()
    db.session.commit()
    
    print(f"Evaluated {len(current_games)} players for game {game_number}")
