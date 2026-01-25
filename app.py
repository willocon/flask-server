from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from scheduler import start_scheduler, generate_on_startup

import atexit
import datetime

import os
import queue
import json
import state
import evaluation

app = Flask(__name__)
CORS(app)

IMAGE_DIR = os.getenv("IMAGE_DIR", "images")
LOG_DIR = os.getenv("LOG_DIR", "/logs")

def exit_handler():
    print("Shutting down scheduler...")
    evaluation.evaluatePlayers()

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
generate_on_startup()
start_scheduler()
atexit.register(exit_handler)

@app.route("/")
def hello():
	return "Hello World!"

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

    if state.isFound == False:
        state.isFound = True
        print(f"Game: {state.getGameNumber()}")
        username = data.get("username")
        state.currentWinner = username
        print(f"Winner: {username}")
        currenttime = datetime.datetime.now()
        score = 1000-round(((currenttime.minute%10)*60+currenttime.second)/0.6)
        state.score = score
        print(f"Score: {score}")
        with open(os.path.join(LOG_DIR, "currentgame.log"), "a") as f:
            f.write(f"{username},{score},{True}\n")
            f.close()
        return jsonify({"message": "winner"}), 200
    else:
        currenttime = datetime.datetime.now()
        score = 1000-round(((currenttime.minute%10)*60+currenttime.second)/0.6)
        with open(os.path.join(LOG_DIR, "currentgame.log"), "a") as f:
            f.write(f"{data.get('username')},{score},{False}\n")
            f.close()
    return jsonify({"message": "not winner"}), 200

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
            payload = {
                "image_url": f"/images/{state.current_image_name}",
                "csv_url": f"/images/{state.current_csv_name}"
            }
            yield f"event: ready\ndata: {json.dumps(payload)}\n\n"

        # normal streaming events with frequent keepalives
        while True:
            try:
                msg = q.get(timeout=2)  # Wait max 2 seconds
                yield f"event: ready\ndata: {msg}\n\n"
            except queue.Empty:
                # Send keepalive comment every 2 seconds
                yield ": keepalive\n\n"

    return Response(stream(), mimetype="text/event-stream")


@app.route("/images/<filename>")
def serve_image(filename):
    return send_from_directory(IMAGE_DIR, filename)

@app.route("/csv/<filename>")
def serve_csv(filename):
    return send_from_directory(IMAGE_DIR, filename)

if __name__ == "__main__":
    app.run(debug=True, threaded=True, use_reloader=False)
