from apscheduler.schedulers.background import BackgroundScheduler
import json
import random
import shutil
import state
import evaluation
import os

IMAGE_DIR = os.getenv("IMAGE_DIR", "images")

# Will be set by app.py
app = None


def generate_on_startup():
    global current_image_name
    global current_csv_name

    print("selecting startup image + CSV...")

    state.incrementGameNumber(state.getGameNumber())

    # randomly pick an image
    imageNum = random.randint(1,500)
    shutil.copy(f"{IMAGE_DIR}/{imageNum}/screenshot.png", f"{IMAGE_DIR}/screenshot.png")
    shutil.copy(f"{IMAGE_DIR}/{imageNum}/coords.csv", f"{IMAGE_DIR}/coords.csv")

    image_name = "screenshot.png"
    state.current_image_name = image_name
    # image_url = f"/images/{image_name}"

    csv_name = "coords.csv"
    state.current_csv_name = csv_name
    # csv_url = f"/images/{csv_name}"

    print("Startup files generated.")
    print(imageNum)


def batch_generate():
    print("Running 10-minute batch...")
    
    if app is None:
        print("Error: app not initialized in scheduler")
        return
    
    with app.app_context():
        evaluation.evaluatePlayers()
        state.usernameSet.clear()
        state.isFound = False
        state.currentWinner = None
        state.incrementGameNumber(state.getGameNumber())

    if (len(state.queued_users) == 0):
        print("No users queued.")
        return

    image_name = "screenshot.png"
    state.current_image_name = image_name
    image_url = f"/images/{image_name}"

    csv_name = "coords.csv"
    state.current_csv_name = csv_name
    csv_url = f"/images/{csv_name}"
    # randomly pick an image
    imageNum = random.randint(1,500)
    shutil.copy(f"{IMAGE_DIR}/{imageNum}/screenshot.png", f"{IMAGE_DIR}/screenshot.png")
    shutil.copy(f"{IMAGE_DIR}/{imageNum}/coords.csv", f"{IMAGE_DIR}/coords.csv")

    payload = json.dumps({
                "image_url": image_url,
                "csv_url": csv_url
            })
    for user in list(state.queued_users):    
        state.client_event_queues[user].put(payload)

    print("Assigned image link & pushed SSE events.")
    print(imageNum)


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        batch_generate,
        "cron",
        minute="0,10,20,30,40,50",
    )
    scheduler.start()