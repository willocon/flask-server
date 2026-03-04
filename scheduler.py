from apscheduler.schedulers.background import BackgroundScheduler
import json
import shutil
import state
import evaluation
import os
import time
import screenshotScript

IMAGE_DIR = os.getenv("IMAGE_DIR", "images")

# Will be set by app.py
app = None


def generate_on_startup():
    global current_image_name
    global current_csv_name

    print("selecting startup image + CSV...")

    state.incrementGameNumber(state.getGameNumber())

    # randomly pick an image
    screenshotScript.generate_screenshot(first_run=True)

def first_image_and_csv_ready():

    # move location into the exposed endpoint
    shutil.copy(f"{IMAGE_DIR}/next/screenshot.png", f"{IMAGE_DIR}/screenshot.png")
    shutil.copy(f"{IMAGE_DIR}/next/coords.csv", f"{IMAGE_DIR}/coords.csv")

    # generate the next location that will be used next game
    screenshotScript.generate_screenshot(first_run=False)

    image_name = "screenshot.png"
    state.current_image_name = image_name
    # image_url = f"/images/{image_name}"

    csv_name = "coords.csv"
    state.current_csv_name = csv_name
    # csv_url = f"/images/{csv_name}"

    print("Startup files generated.")
    

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

    image_name = "screenshot.png"
    state.current_image_name = image_name
    image_url = f"/images/{image_name}"

    csv_name = "coords.csv"
    state.current_csv_name = csv_name
    csv_url = f"/images/{csv_name}"
    # move the previously generated image into the exposed endpoint
    shutil.copy(f"{IMAGE_DIR}/next/screenshot.png", f"{IMAGE_DIR}/screenshot.png")
    shutil.copy(f"{IMAGE_DIR}/next/coords.csv", f"{IMAGE_DIR}/coords.csv")

    payload = json.dumps({
                "image_url": image_url,
                "csv_url": csv_url
            })
    for user in list(state.queued_users):    
        state.client_event_queues[user].put(payload)

    # generate the next location that will be used next game
    ready = False
    screenshotScript.generate_screenshot(first_run=False)
        
    if (len(state.queued_users) == 0):
        print("No users queued.")
        return

    print("Assigned image link & pushed SSE events. Next image generated.")


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        batch_generate,
        "cron",
        minute="0,10,20,30,40,50",
    )
    scheduler.start()