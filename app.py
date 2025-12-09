from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from scheduler import start_scheduler, generate_on_startup

import os
import queue
import json
import state

app = Flask(__name__)
CORS(app)

IMAGE_DIR = "images"


# queued_users = set()
# client_event_queues = {}  # user_id -> Queue()

# # For storing URL assigned this batch
# ready_links = {}  # user_id -> image_url


@app.route("/join", methods=["POST"])
def join():
    data = request.json
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    state.queued_users.add(user_id)
    state.client_event_queues[user_id] = queue.Queue()
    return jsonify({"message": "added"}), 200


@app.route("/events")
def events():
    user_id = request.args.get("user_id")
    if not user_id or user_id not in state.client_event_queues:
        return Response("User not registered", status=400)

    q = state.client_event_queues[user_id]

    def stream():
        # send current image + CSV immediately if available
        if state.current_image_name or state.current_csv_name:
            payload = {}

            if state.current_image_name:
                payload["image_url"] = f"/images/{state.current_image_name}"

            if state.current_csv_name:
                payload["csv_url"] = f"/images/{state.current_csv_name}"

            yield f"event: ready\ndata: {json.dumps(payload)}\n\n"

        # normal streaming events
        while True:
            msg = q.get()
            yield f"event: ready\ndata: {msg}\n\n"

    return Response(stream(), mimetype="text/event-stream")


@app.route("/images/<filename>")
def serve_image(filename):
    return send_from_directory(IMAGE_DIR, filename)

@app.route("/csv/<filename>")
def serve_csv(filename):
    return send_from_directory(IMAGE_DIR, filename)



if __name__ == "__main__":
    os.makedirs(IMAGE_DIR, exist_ok=True)
    generate_on_startup()
    start_scheduler()
    app.run(debug=True, threaded=True)
