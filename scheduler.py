from apscheduler.schedulers.background import BackgroundScheduler
import json
import time
import random
import shutil
import state
import evaluation
import os
import graphs as g

IMAGE_DIR = os.getenv("IMAGE_DIR", "images")

# Will be set by app.py
app = None

# Reachability constraints
MAGIC_LEVEL = 15
GP_BUDGET = 250
FAIRY_RINGS = False


def generate_on_startup():
    global current_image_name
    global current_csv_name

    print("selecting startup image + CSV...")

    state.incrementGameNumber(state.getGameNumber())

    prevX,prevZ = 3221,3218 # set lumbridge as init coords
    reachable = False

    while not reachable:
        # randomly pick an image
        imageNum = random.randint(1,500)

        with open(f"{IMAGE_DIR}/{imageNum}/coords.csv", 'r') as f:
            lines = f.readlines()
            last_line = lines[-1]
            x, z, plane = map(int, last_line.strip().split(','))
            print(x,z)
            f.close()

        # set up graph
        graph = g.from_file('graph.csv')
        g.connect_fairy_ring_nodes(graph)
        g.connect_walkable_nodes(graph, max_distance=200)
        g.add_start_and_destination(graph, 'start', (prevX, prevZ), 'destination', (x, z))
        constraints = g.Constraints(MAGIC_LEVEL, GP_BUDGET, FAIRY_RINGS)
        resultNoob, stepsNoob = g.dijkstra(graph, 'start', 'destination', constraints)

        maxConstraints = g.Constraints(99, 10000, True)
        resultMax, stepsMax = g.dijkstra(graph, 'start', 'destination', maxConstraints)

        print(f"Evaluated image {imageNum}: Reachable={resultNoob != float('inf')}, Cost={resultNoob}, Steps={stepsNoob}")
        print(f"Evaluated image {imageNum} with max constraints: Reachable={resultMax != float('inf')}, Cost={resultMax}, Steps={stepsMax}")
        if resultNoob < 240:
            reachable = True
            shutil.copy(f"{IMAGE_DIR}/{imageNum}/screenshot.png", f"{IMAGE_DIR}/screenshot.png")
            shutil.copy(f"{IMAGE_DIR}/{imageNum}/coords.csv", f"{IMAGE_DIR}/coords.csv")
            timeRatio = resultNoob/resultMax if resultMax > 0 else 1
            pathRatio = stepsNoob/stepsMax if stepsMax > 0 else 1
            print(f"Selected image {imageNum} with time ratio {timeRatio:.2f} and path ratio {pathRatio:.2f}")
            difficultyRating = round(((2**(timeRatio * 0.7 + pathRatio * 0.3))-1)/2)
            if difficultyRating < 1:
                difficultyRating = 1
            if difficultyRating > 5:
                difficultyRating = 5
            print(f"Calculated difficulty rating: {difficultyRating}")

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

    image_name = "screenshot.png"
    state.current_image_name = image_name
    image_url = f"/images/{image_name}"

    csv_name = "coords.csv"
    state.current_csv_name = csv_name
    csv_url = f"/images/{csv_name}"
        
    with open(f"{IMAGE_DIR}/coords.csv", 'r') as f:
        lines = f.readlines()
        last_line = lines[-1]
        prevX, prevZ, plane = map(int, last_line.strip().split(','))
        print(f"Previous coords: {prevX}, {prevZ}")
        f.close()
    reachable = False

    while not reachable:
        # randomly pick an image
        imageNum = random.randint(1,500)

        with open(f"{IMAGE_DIR}/{imageNum}/coords.csv", 'r') as f:
            lines = f.readlines()
            last_line = lines[-1]
            x, z, plane = map(int, last_line.strip().split(','))
            print(x,z)
            f.close()

        
        # set up graph
        graph = g.from_file('graph.csv')
        g.connect_fairy_ring_nodes(graph)
        g.connect_walkable_nodes(graph, max_distance=200)
        g.add_start_and_destination(graph, 'start', (prevX, prevZ), 'destination', (x, z))
        constraints = g.Constraints(MAGIC_LEVEL, GP_BUDGET, FAIRY_RINGS)
        resultNoob, stepsNoob = g.dijkstra(graph, 'start', 'destination', constraints)

        maxConstraints = g.Constraints(99, 10000, True)
        resultMax, stepsMax = g.dijkstra(graph, 'start', 'destination', maxConstraints)

        print(f"Evaluated image {imageNum}: Reachable={resultNoob != float('inf')}, Cost={resultNoob}, Steps={stepsNoob}")
        print(f"Evaluated image {imageNum} with max constraints: Reachable={resultMax != float('inf')}, Cost={resultMax}, Steps={stepsMax}")
        if resultNoob < 240:
            reachable = True
            shutil.copy(f"{IMAGE_DIR}/{imageNum}/screenshot.png", f"{IMAGE_DIR}/screenshot.png")
            shutil.copy(f"{IMAGE_DIR}/{imageNum}/coords.csv", f"{IMAGE_DIR}/coords.csv")
            timeRatio = resultNoob/resultMax if resultMax > 0 else 1
            pathRatio = stepsNoob/stepsMax if stepsMax > 0 else 1
            print(f"Selected image {imageNum} with time ratio {timeRatio:.2f} and path ratio {pathRatio:.2f}")
            difficultyRating = round(((2**(timeRatio * 0.7 + pathRatio * 0.3))-1)/2)
            if difficultyRating < 1:
                difficultyRating = 1
            if difficultyRating > 5:
                difficultyRating = 5
            print(f"Calculated difficulty rating: {difficultyRating}")            


    payload = json.dumps({
                "image_url": image_url,
                "csv_url": csv_url
            })
    for user in list(state.queued_users):    
        state.client_event_queues[user].put(payload)

    print("Assigned image link & pushed SSE events.")
    print(imageNum)
    if (len(state.queued_users) == 0):
        print("No users queued.")
        return


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        batch_generate,
        "cron",
        minute="0,10,20,30,40,50",
    )
    scheduler.start()