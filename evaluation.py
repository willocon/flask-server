#evaluation.py

import os
import state

LOG_DIR = os.getenv("LOG_DIR", "/logs")

def evaluatePlayers():
    with open(os.path.join(LOG_DIR, "currentgame.log"), "r") as f:
        lines = f.readlines()
        f.close()

    for line in lines[1:]:  # Skip header
        username, score, winner = line.strip().split(",")
        with open(os.path.join(LOG_DIR, "leaderboard.log"),"r") as lb:
            lb_lines = lb.readlines()
            lb.close()
        user_found = False
        for i in range(len(lb_lines)):
            lb_username, lb_score, lb_wins = lb_lines[i].strip().split(",")
            if lb_username == username:
                user_found = True
                lb_score = int(lb_score) + int(score)
                lb_wins = int(lb_wins) + (1 if winner == "True" else 0)
                lb_lines[i] = f"{lb_username},{lb_score},{lb_wins}\n"
                with open(os.path.join(LOG_DIR, "leaderboard.log"),"w") as lb:
                    lb.writelines(lb_lines)
                    lb.close()
                break
        if not user_found:
            lb_lines.append(f"{username},{score},{1 if winner == 'True' else 0}\n")
            with open(os.path.join(LOG_DIR, "leaderboard.log"),"w") as lb:
                lb.writelines(lb_lines)
                lb.close()

    # sort leaderboard entries by score (descending)
    with open(os.path.join(LOG_DIR, "leaderboard.log"),"r") as lb:
        lb_lines = lb.readlines()
        lb.close()

    if len(lb_lines) > 1:
        entries = []
        for entry in lb_lines[1:]: # Skip header
            line = entry.strip()
            name, sc, wins = line.split(",")
            sc = int(sc)
            wins = int(wins)
            entries.append((name, sc, wins))
        # sort by score descending
        entries.sort(key=lambda x: x[1], reverse=True)
        sorted_lines = [f"{n},{s},{w}\n" for n, s, w in entries]
        with open(os.path.join(LOG_DIR, "leaderboard.log"),"w") as lb:
            lb.write("username,score,winner\n")
            lb.writelines(sorted_lines)


    total_games = state.getGameNumber()

    for line in lines[1:]:
        username, score, winner = line.strip().split(",")
        with open(os.path.join(LOG_DIR, "games.log"), "a") as g:
            g.write(f"{total_games},{username},{score},{winner}\n")
            g.close()

    # clear currentgame.log for next game
    with open(os.path.join(LOG_DIR, "currentgame.log"), "w") as f:
        f.write("username,score,winner\n")
        f.close()
