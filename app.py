from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import scheduler
from models import db, init_db, Player, CurrentGame

import atexit
import datetime

import os
import queue
import json
import state
import evaluation

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///game.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

IMAGE_DIR = os.getenv("IMAGE_DIR", "images")
LOG_DIR = os.getenv("LOG_DIR", "logs")

def exit_handler():
    print("Shutting down scheduler...")
    with app.app_context():
        evaluation.evaluatePlayers()

# Initialize database
init_db(app)

# Set app reference for scheduler
scheduler.app = app

# Initialize within app context
with app.app_context():
    os.makedirs(IMAGE_DIR, exist_ok=True)
    scheduler.generate_on_startup()
    scheduler.start_scheduler()

atexit.register(exit_handler)

@app.route("/")
def about_page():
    return send_from_directory(".", "about.html")

@app.route("/leaderboard")
def leaderboard_page():
    return send_from_directory(".", "leaderboardWP.html")

@app.route("/privacypolicy")
def privacy_policy_page():
    return send_from_directory(".", "privacypolicy.html")

@app.route("/static/<path:filename>")
def font(filename):
    return send_from_directory("static", filename)

@app.route("/join", methods=["POST"])
def join():
    data = request.json
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    state.queued_users.add(user_id)
    state.client_event_queues[user_id] = queue.Queue()
    return jsonify({"message": "added"}), 200

@app.route("/completed", methods=["POST"])
def completed():
    data = request.json
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    if user_id not in state.queued_users:
        return jsonify({"error": "user_id not in game"}), 400

    if state.usernameSet.__contains__(data.get("username")):
        return jsonify({"error": "user already completed"}), 400
    
    state.usernameSet.add(data.get("username"))

    username = data.get("username")
    currenttime = datetime.datetime.now()
    score = 1000-round(((currenttime.minute%10)*60+currenttime.second)/0.6)
    
    if state.isFound == False:
        state.isFound = True
        print(f"Game: {state.getGameNumber()}")
        state.currentWinner = username
        print(f"Winner: {username}")
        state.score = score
        print(f"Score: {score}")
        
        # Save to database
        current_game = CurrentGame(
            game_number=state.getGameNumber(),
            userid = user_id,
            username=username,
            score=score,
            is_winner=True
        )
        db.session.add(current_game)
        db.session.commit()
        
        return jsonify({"message": "winner", "score": score}), 200
    else:
        # Save to database
        current_game = CurrentGame(
            game_number=state.getGameNumber(),
            userid = user_id,
            username=username,
            score=score,
            is_winner=False
        )
        db.session.add(current_game)
        db.session.commit()
        
    return jsonify({"message": "not winner", "score": score}), 200

@app.route("/leave", methods=["POST"])
def leave():
    data = request.json
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    state.queued_users.discard(user_id)
    state.client_event_queues.pop(user_id, None)
    return jsonify({"message": "removed"}), 200


@app.route("/events")
def events():
    user_id = request.args.get("user_id")
    if not user_id or user_id not in state.client_event_queues:
        return Response("User not registered", status=400)

    q = state.client_event_queues[user_id]

    def stream():
        # send current image + CSV immediately if available
        if state.current_image_name and state.current_csv_name:
            current_time = datetime.datetime.now()
            minutesAndSeconds = current_time.minute % 10 * 60 + current_time.second
            payload = {
                "image_url": f"/images/{state.current_image_name}",
                "csv_url": f"/images/{state.current_csv_name}",
                "time": minutesAndSeconds,
                "difficulty": state.current_difficulty
            }
            yield f"event: ready\ndata: {json.dumps(payload)}\n\n"

        # send first available message
        try:
            msg = q.get(timeout=10)  # Wait max 10 seconds
            yield f"event: ready\ndata: {msg}\n\n"
        except queue.Empty:
            pass

    return Response(stream(), mimetype="text/event-stream")


@app.route("/images/<filename>")
def serve_image(filename):
    return send_from_directory(IMAGE_DIR, filename)

@app.route("/csv/<filename>")
def serve_csv(filename):
    return send_from_directory(IMAGE_DIR, filename)

@app.route("/leaderboard-json")
def get_leaderboard():
    try:
        # Get all players ordered by total score (descending)
        players = Player.query.order_by(Player.total_score.desc()).all()
        
        leaderboard = [player.to_dict() for player in players]
        
        return jsonify(leaderboard), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/difficulty")
def get_difficulty():
    return state.difficultyString

if __name__ == "__main__":
    app.run(debug=True, threaded=True, use_reloader=False)
