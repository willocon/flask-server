# state.py

import os

LOG_DIR = os.getenv("LOG_DIR", "logs")

current_image_name = None
current_csv_name = None

isFound = False
currentWinner = None
score = None
usernameSet = set()

def getGameNumber():
    try:
        with open(os.path.join(LOG_DIR, "gameNum.txt"), "r") as f:
            number = int(f.read().strip())+1
            f.close()
    except FileNotFoundError:
        number = 0
    return number

queued_users = set()
client_event_queues = {}

def incrementGameNumber(gameNum):
    with open(os.path.join(LOG_DIR, "gameNum.txt"), "w") as f:
        f.write(str(gameNum))
        f.close()
