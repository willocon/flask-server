# state.py

current_image_name = None
current_csv_name = None

isFound = False
currentWinner = None
ticksTook = None

def getGameNumber():
    try:
        with open("gameNum.txt", "r") as f:
            number = int(f.read().strip())+1
            f.close()
    except FileNotFoundError:
        number = 0
    return number

gameNumber = getGameNumber()

queued_users = set()
client_event_queues = {}

def incrementGameNumber(gameNum):
    with open("gameNum.txt", "w") as f:
        f.write(str(gameNum))
        f.close()
