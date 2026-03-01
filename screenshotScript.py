import os
import random
import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from PIL import Image

import graphs as g

# ---------------- SETTINGS ----------------
NUM_SCREENSHOTS = 1
DELAY = 60      # Seconds to wait before screenshot
CHROME_DRIVER_PATH = "/usr/bin/chromedriver"   # Docker path for Chromium driver

# World bounds (fully random)
MIN_X, MAX_X = 1200, 3900
MIN_Y, MAX_Y = 7, 10
MIN_Z, MAX_Z = 2800, 3900
MIN_YAW, MAX_YAW = 0, 2047

# Reachability constraints
MAGIC_LEVEL = 30
GP_BUDGET = 500
FAIRY_RINGS = True

# Scheduler tools
global is_ready
is_ready = False

# -------------------------------------------

def random_tile():
    #rng coordinates
    x = random.randint(MIN_X, MAX_X)
    y = random.randint(MIN_Y, MAX_Y)
    z = random.randint(MIN_Z, MAX_Z)
    yeet = random.randint(0,3) # 0=north,1=east,2=south,3=west
    yaw = 0
    for i in range(yeet):
        yaw += 512
    return x, y, z, yaw, yeet

def toggle_ui_with_js(driver):
    #simulate pressing f1 to get rid of ui
    js = """
        document.dispatchEvent(new KeyboardEvent('keydown', {key: 'F1'}));
    """
    driver.execute_script(js)

def crop_center_square(path):
    #crop the image to be a square
    img = Image.open(path)
    w, h = img.size

    side = min(w, h)

    left = (w - side) // 2
    top = (h - side) // 2
    right = left + side
    bottom = top + side

    img_cropped = img.crop((left, top, right, bottom))
    img_cropped.save(path)

def check_in_bounds(x, z):
    #check if the coordinates are in bounds using generated if statements
    if (x >= 1274 and x <= 1327 and z >= 2880 and z <= 2941):
        return True
    if (x >= 1319 and x <= 1484 and z >= 2839 and z <= 2994):
        return True
    if (x >= 1547 and x <= 1788 and z >= 2956 and z <= 3193):
        return True
    if (x >= 1597 and x <= 1697 and z >= 2899 and z <= 2955):
        return True
    if (x >= 1499 and x <= 1541 and z >= 2972 and z <= 3008):
        return True
    if (x >= 1432 and x <= 1544 and z >= 3010 and z <= 3193):
        return True
    if (x >= 1427 and x <= 1712 and z >= 3196 and z <= 3330):
        return True
    if (x >= 1186 and x <= 1363 and z >= 3090 and z <= 3197):
        return True
    if (x >= 1217 and x <= 1400 and z >= 3016 and z <= 3088):
        return True
    if (x >= 1238 and x <= 1282 and z >= 2990 and z <= 3014):
        return True
    if (x >= 1353 and x <= 1421 and z >= 3200 and z <= 3327):
        return True
    if (x >= 1342 and x <= 1459 and z >= 3334 and z <= 3404):
        return True
    if (x >= 1093 and x <= 1201 and z >= 3334 and z <= 3447):
        return True
    if (x >= 1206 and x <= 1339 and z >= 3323 and z <= 3455):
        return True
    if (x >= 1157 and x <= 1424 and z >= 3467 and z <= 3583):
        return True
    if (x >= 1180 and x <= 1333 and z >= 3589 and z <= 3662):
        return True
    if (x >= 1355 and x <= 1379 and z >= 3622 and z <= 3644):
        return True
    if (x >= 1201 and x <= 1336 and z >= 3664 and z <= 3781):
        return True
    if (x >= 1273 and x <= 1338 and z >= 3784 and z <= 3833):
        return True
    if (x >= 1340 and x <= 1854 and z >= 3686 and z <= 3834):
        return True
    if (x >= 1405 and x <= 1855 and z >= 3838 and z <= 3965):
        return True
    if (x >= 1408 and x <= 1796 and z >= 3504 and z <= 3679):
        return True
    if (x >= 1494 and x <= 1603 and z >= 3400 and z <= 3500):
        return True
    if (x >= 1605 and x <= 1644 and z >= 3433 and z <= 3500):
        return True
    if (x >= 1797 and x <= 1853 and z >= 3457 and z <= 3654):
        return True
    if (x >= 1688 and x <= 1793 and z >= 3460 and z <= 3500):
        return True
    if (x >= 1701 and x <= 1752 and z >= 2918 and z <= 2950):
        return True
    if (x >= 2095 and x <= 2311 and z >= 2943 and z <= 2976):
        return True
    if (x >= 2150 and x <= 2283 and z >= 2779 and z <= 2825):
        return True
    if (x >= 2625 and x <= 2689 and z >= 2631 and z <= 2686):
        return True
    if (x >= 2689 and x <= 2819 and z >= 2687 and z <= 2812):
        return True
    if (x >= 2440 and x <= 2472 and z >= 2822 and z <= 2873):
        return True
    if (x >= 2471 and x <= 2651 and z >= 2847 and z <= 3008):
        return True
    if (x >= 2169 and x <= 2309 and z >= 3138 and z <= 3264):
        return True
    if (x >= 2313 and x <= 2360 and z >= 3144 and z <= 3194):
        return True
    if (x >= 2126 and x <= 2293 and z >= 3386 and z <= 3447):
        return True
    if (x >= 2306 and x <= 2359 and z >= 3661 and z <= 3697):
        return True
    if (x >= 2282 and x <= 2400 and z >= 3532 and z <= 3636):
        return True
    if (x >= 2379 and x <= 2547 and z >= 3337 and z <= 3529):
        return True
    if (x >= 2499 and x <= 2557 and z >= 3531 and z <= 3595):
        return True
    if (x >= 2497 and x <= 2556 and z >= 3712 and z <= 3765):
        return True
    if (x >= 2298 and x <= 2433 and z >= 3766 and z <= 3903):
        return True
    if (x >= 2175 and x <= 2238 and z >= 3778 and z <= 3840):
        return True
    if (x >= 2053 and x <= 2171 and z >= 3847 and z <= 3961):
        return True
    if (x >= 2491 and x <= 2630 and z >= 3837 and z <= 3905):
        return True
    if (x >= 2491 and x <= 2530 and z >= 3615 and z <= 3652):
        return True
    if (x >= 2449 and x <= 2740 and z >= 3264 and z <= 3335):
        return True
    if (x >= 2448 and x <= 2635 and z >= 3110 and z <= 3260):
        return True
    if (x >= 2635 and x <= 2677 and z >= 3200 and z <= 3249):
        return True
    if (x >= 2637 and x <= 2686 and z >= 3140 and z <= 3176):
        return True
    if (x >= 2331 and x <= 2496 and z >= 3031 and z <= 3074):
        return True
    if (x >= 2434 and x <= 2629 and z >= 3070 and z <= 3110):
        return True
    if (x >= 2762 and x <= 2946 and z >= 2882 and z <= 3123):
        return True
    if (x >= 2708 and x <= 2770 and z >= 3145 and z <= 3240):
        return True
    if (x >= 2771 and x <= 2870 and z >= 3143 and z <= 3216):
        return True
    if (x >= 2870 and x <= 2957 and z >= 3138 and z <= 3181):
        return True
    if (x >= 2546 and x <= 2745 and z >= 3338 and z <= 3403):
        return True
    if (x >= 2549 and x <= 2592 and z >= 3408 and z <= 3503):
        return True
    if (x >= 2627 and x <= 2940 and z >= 3407 and z <= 3511):
        return True
    if (x >= 2600 and x <= 2747 and z >= 3606 and z <= 3730):
        return True
    if (x >= 2699 and x <= 2746 and z >= 3751 and z <= 3832):
        return True
    if (x >= 2643 and x <= 2751 and z >= 3516 and z <= 3600):
        return True
    if (x >= 2753 and x <= 2781 and z >= 3586 and z <= 3650):
        return True
    if (x >= 2800 and x <= 2942 and z >= 3516 and z <= 3576):
        return True
    if (x >= 2802 and x <= 2873 and z >= 3333 and z <= 3387):
        return True
    if (x >= 2922 and x <= 3393 and z >= 3204 and z <= 3519):
        return True
    if (x >= 2876 and x <= 2922 and z >= 3327 and z <= 3403):
        return True
    if (x >= 2979 and x <= 3023 and z >= 3104 and z <= 3201):
        return True
    if (x >= 3093 and x <= 3124 and z >= 3151 and z <= 3175):
        return True
    if (x >= 3134 and x <= 3249 and z >= 3136 and z <= 3201):
        return True
    if (x >= 3396 and x <= 3519 and z >= 3455 and z <= 3591):
        return True
    if (x >= 3523 and x <= 3707 and z >= 3402 and z <= 3572):
        return True
    if (x >= 3405 and x <= 3535 and z >= 3180 and z <= 3459):
        return True
    if (x >= 3539 and x <= 3584 and z >= 3263 and z <= 3326):
        return True
    if (x >= 3677 and x <= 3755 and z >= 3278 and z <= 3387):
        return True
    if (x >= 3654 and x <= 3843 and z >= 2933 and z <= 3063):
        return True
    if (x >= 3777 and x <= 3836 and z >= 2815 and z <= 2878):
        return True
    if (x >= 3641 and x <= 3690 and z >= 3700 and z <= 3807):
        return True
    if (x >= 3661 and x <= 3718 and z >= 3811 and z <= 3884):
        return True
    if (x >= 3720 and x <= 3764 and z >= 3796 and z <= 3842):
        return True
    if (x >= 3726 and x <= 3795 and z >= 3736 and z <= 3792):
        return True
    if (x >= 3766 and x <= 3822 and z >= 3793 and z <= 3828):
        return True
    if (x >= 3800 and x <= 3821 and z >= 3755 and z <= 3788):
        return True
    if (x >= 3263 and x <= 3403 and z >= 3134 and z <= 3200):
        return True
    if (x >= 3214 and x <= 3341 and z >= 3074 and z <= 3121):
        return True
    if (x >= 3157 and x <= 3354 and z >= 2933 and z <= 3055):
        return True
    if (x >= 3146 and x <= 3258 and z >= 2813 and z <= 2924):
        return True
    if (x >= 3280 and x <= 3433 and z >= 2753 and z <= 2923):
        return True
    if (x >= 3288 and x <= 3395 and z >= 2675 and z <= 2745):
        return True
    if (x >= 3378 and x <= 3464 and z >= 2927 and z <= 3126):
        return True
    if (x >= 3465 and x <= 3531 and z >= 2947 and z <= 3122):
        return True
    if (x >= 2269 and x <= 2278 and z >= 4034 and z <= 4050):
        return True
    if (x >= 3357 and x <= 3375 and z >= 2949 and z <= 3009):
        return True
    return False

# return a yOffset, used to adjust the y coordinate based on x and z, avoids clipping into the ground
def check_y_offset(x, z):
    if (x >= 2496 and x <= 2542 and z >= 3463 and z <= 3525):
        return 10
    if (x >= 3587 and x <= 3668 and z >= 3331 and z <= 3398):
        return 8
    if (x >= 3531 and x <= 3572 and z >= 3529 and z <= 3567):
        return 8
    if (x >= 2987 and x <= 3037 and z >= 3452 and z <= 3522):
        return 9
    if (x >= 2810 and x <= 2878 and z >= 3495 and z <= 3561):
        return 8
    if (x >= 2830 and x <= 2877 and z >= 3441 and z <= 3491):
        return 8
    if (x >= 2494 and x <= 2521 and z >= 3621 and z <= 3649):
        return 7
    if (x >= 2429 and x <= 2452 and z >= 3150 and z <= 3172):
        return 8
    if (x >= 1625 and x <= 1732 and z >= 3128 and z <= 3170):
        return 7
    if (x >= 1347 and x <= 1475 and z >= 2902 and z <= 2957):
        return 10
    if (x >= 1536 and x <= 1577 and z >= 3027 and z <= 3065):
        return 10
    if (x >= 1419 and x <= 1468 and z >= 3134 and z <= 3208):
        return 20
    if (x >= 1618 and x <= 1713 and z >= 3213 and z <= 3265):
        return 10
    if (x >= 1147 and x <= 1203 and z >= 3377 and z <= 3448):
        return 8
    if (x >= 1207 and x <= 1299 and z >= 3530 and z <= 3602):
        return 10
    if (x >= 1462 and x <= 1574 and z >= 3535 and z <= 3673):
        return 11
    if (x >= 1277 and x <= 1344 and z >= 3781 and z <= 3843):
        return 10
    if (x >= 1404 and x <= 1569 and z >= 3732 and z <= 3883):
        return 10
    if (x >= 1608 and x <= 1739 and z >= 3703 and z <= 3778):
        return 10
    if (x >= 1576 and x <= 1856 and z >= 3780 and z <= 3896):
        return 15
    if (x >= 2052 and x <= 2170 and z >= 3846 and z <= 3955):
        return 6
    if (x >= 2494 and x <= 2530 and z >= 3839 and z <= 3878):
        return 7
    if (x >= 2521 and x <= 2556 and z >= 3715 and z <= 3768):
        return 10
    if (x >= 2142 and x <= 2181 and z >= 3396 and z <= 3438):
        return 12
    if (x >= 3352 and x <= 3374 and z >= 3282 and z <= 3325):
        return 7
    if (x >= 3352 and x <= 3424 and z >= 3137 and z <= 3191):
        return 9
    if (x >= 3426 and x <= 3454 and z >= 3211 and z <= 3260):
        return 5
    if (x >= 3191 and x <= 3353 and z >= 2965 and z <= 3003):
        return 5
    if (x >= 2953 and x <= 3000 and z >= 3324 and z <= 3356):
        return 10
    if (x >= 2144 and x <= 2252 and z >= 2775 and z <= 2818):
        return 5
    if (x >= 2695 and x <= 2811 and z >= 2714 and z <= 2766):
        return 6
    #1319,3400,1348,3369
    if (x >= 1319 and x <= 1348 and z >= 3369 and z <= 3400):
        return 12
    #1282,3459,1309,3431
    if (x >= 1282 and x <= 1309 and z >= 3431 and z <= 3459):
        return 12
    #1264,3486,1437,3590
    if (x >= 1264 and x <= 1437 and z >= 3486 and z <= 3590):
        return 7
    return 0

def get_prev_coords():
    with open('images/coords.csv','r') as file:
        reader = csv.reader(file)
        for row in reader:
            return int(row[0]), int(row[1])
    # default to lumbridge if no coords found (on startup)
    return 3221, 3218

def check_reachable(x, z):
    (prevX,prevZ) = get_prev_coords()
    graph = g.from_file('graph.csv')
    g.connect_fairy_ring_nodes(graph)
    g.connect_walkable_nodes(graph, max_distance=200)
    g.add_start_and_destination(graph, 'start', (prevX, prevZ), 'destination', (x, z))
    constraints = g.Constraints(MAGIC_LEVEL, GP_BUDGET, FAIRY_RINGS)
    result = g.dijkstra(graph, 'start', 'destination', constraints)
    if result == float('inf'):
        return False
    return True

    
def get_ready_state():
    global is_ready
    return is_ready

def generate_screenshot():
    #screenshot generator
    global is_ready
    is_ready = False

    output_dir = "images/next"
    os.makedirs(output_dir, exist_ok=True)

    service = Service(CHROME_DRIVER_PATH)
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless=new")  # headless mode
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--disable-gpu")  # Required for Docker
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=service, options=options)
    for i in range(NUM_SCREENSHOTS):
        inBound = False
        y = 0
        while not inBound or not reachable:
            x, y, z, yaw, yeet = random_tile()

            match yeet:
                case 0:
                    tilex, tilez = x, z + 10
                case 1:
                    tilex, tilez = x + 10, z
                case 2:
                    tilex, tilez = x, z - 10
                case _:
                    tilex, tilez = x - 10, z

            # check bounds using generated if statements
            inBound = check_in_bounds(tilex, tilez)
            # if in bounds, check if reachable from previous location using dijkstra's with constraints, if not reachable, reroll
            if inBound:
                reachable = check_reachable(tilex, tilez)
        
        y += check_y_offset(x, z)

        url = f"https://osrs.world/?cx={x}&cy={y}&cz={z}&p=-230&y={yaw}&v=1"

        print(f"[Screenshot {i+1}/{NUM_SCREENSHOTS}] Loading {url}")
        driver.get(url)
        if i == 0:
            time.sleep(2)

        time.sleep(2)  # small load delay
        time.sleep(DELAY)
        toggle_ui_with_js(driver)



        filename = os.path.join(output_dir, "screenshot.png")
        driver.save_screenshot(filename)
        # crop the center to 1:1
        # current_img_dir = os.path.join(os.getcwd(), "images")
        # crop_center_square(os.path.join(current_img_dir, "screenshot.png"))

        csv_file = os.path.join(output_dir, "coords.csv")
        
        match yeet:
            case 0:
                z += 10
            case 1:
                x += 10
            case 2:
                z -= 10
            case _:
                x -= 10

        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            # write one row with this screenshot’s data
            writer.writerow([x, z, 0])

        

        print(f"Saved {filename}")

    driver.quit()
    is_ready = True
    print("All screenshots complete!")

if __name__ == "__main__":
    generate_screenshot()
