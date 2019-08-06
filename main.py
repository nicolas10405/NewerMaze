import Setup_Maze
from numpy.random import choice

import Services
import time

# Config (Global)

maxX = 10
maxY = maxX
maxZ = maxX

speed_optimized = True
always_shorten_route = True
auto_rotate = True

# Config (Round)

starting_position = [25, 75, 25]
goal_position = [75, 25, 75]

abs_reward = round(maxX * maxY * maxZ) / 1000  # AI
reactivate_after = 100  # tacts #AI

route = [starting_position]
short_route = []
tact = 1

tact_last_update = 0
time_last_update = time.time()

# max_tact_allowed = 200
max_tact_allowed = round(1 * maxX * maxY * maxZ)  # AI


# Services

def set_borders():  # TBD, ob + 1 oder +2

    for y_ in range(maxY):
        for z_ in range(maxZ):
            canGo[maxX][y_][z_] = False

    for x_ in range(maxX):
        for z_ in range(maxZ):
            canGo[x_][maxY][z_] = False

    for x_ in range(maxX):
        for y_ in range(maxY):
            canGo[x_][y_][maxZ] = False


def get_cg_matrix(x, y, z):
    cg_matrix = [
        [canGo[x + 1][y][z], canGo[x - 1][y][z]],
        [canGo[x][y + 1][z], canGo[x][y - 1][z]],
        [canGo[x][y][z + 1], canGo[x][y][z - 1]]
    ]

    return cg_matrix


def test_print(tact_adjuster=0):
    print("\n----- Tact", tact + tact_adjuster, "------")
    if tact_adjuster != 0:
        print("*tact adjustment:", tact_adjuster)
    print("Status:")
    print(status)
    print("Current position:")
    print(current_position)
    print("Strength Matrix:")
    print(current_s_matrix)
    print("CanGO Matrix:")
    print(current_cg_matrix)
    print("New Position:")
    print(new_Position, "(after move in direction " + str(int(random_choice)) + ")")
    if not short_route:
        print("Long Route:")
        print(route, "\n")
    else:
        print("Short Route:")
        print(short_route, "\n")


def status_update(percent):
    global time_last_update
    global tact_last_update

    tps = round((tact - tact_last_update)/(time.time()-time_last_update))
    rt_min = round(((max_tact_allowed - tact) / tps) // 60)
    rt_sec = round(((max_tact_allowed - tact) / tps) % 60)
    print("Step 1 of 2 (Making moves...): [" + "#" * int(percent / 2) + "-" * (50 - int(percent / 2)) + "] ",
          str(percent) + "% of max, now tact: " + str(tact) + ") - Speed: " + str(tps) + " TPS - max runtime: " + str(rt_min) + " min " + str(rt_sec) + "s")
    time_last_update = time.time()
    tact_last_update = tact


# Initalisierung

canGo = Setup_Maze.setupDefaultMaze(maxX + 1, maxY + 1, maxZ + 1,
                                    defaultValue=True)  # max +1 to give room for 3 boundary planes set to false
defaultValue = 100  # Starting value of individual strengths
strength = Setup_Maze.setupDefaultMaze(maxX, maxY, maxZ,
                                       defaultValue=[[defaultValue, defaultValue], [defaultValue, defaultValue],
                                                     [defaultValue, defaultValue]])

current_position = starting_position

set_borders()

status = "Initialized round"
print(status)


# Tact

def make_a_move(current_position):
    global current_s_matrix, current_cg_matrix
    global new_Position, random_choice
    global x, y, z

    x = current_position[0]
    y = current_position[1]
    z = current_position[2]

    current_s_matrix = strength[x][y][z]
    current_cg_matrix = get_cg_matrix(x, y, z)

    x_p = current_cg_matrix[0][0] * current_s_matrix[0][0]
    x_m = current_cg_matrix[0][1] * current_s_matrix[0][1]
    y_p = current_cg_matrix[1][0] * current_s_matrix[1][0]
    y_m = current_cg_matrix[1][1] * current_s_matrix[1][1]
    z_p = current_cg_matrix[2][0] * current_s_matrix[2][0]
    z_m = current_cg_matrix[2][1] * current_s_matrix[2][1]

    total_e_matrix = x_p + x_m + \
                     y_p + y_m + \
                     z_p + z_m

    if total_e_matrix != 0:

        x_p_n = x_p / total_e_matrix
        x_m_n = x_m / total_e_matrix
        y_p_n = y_p / total_e_matrix
        y_m_n = y_m / total_e_matrix
        z_p_n = z_p / total_e_matrix
        z_m_n = z_m / total_e_matrix

        random_choice = choice(a=(0, 1, 2, 3, 4, 5), \
                               size=1, \
                               p=(x_p_n, x_m_n, y_p_n, y_m_n, z_p_n, z_m_n))

        new_Position = [[x + 1, y, z], [x - 1, y, z], [x, y + 1, z], [x, y - 1, z], [x, y, z + 1], [x, y, z - 1]][
            int(random_choice)]

        canGo[x][y][z] = False

        if reactivate_after != 0 and reactivate_after < tact:
            canGo[route[-1 * reactivate_after][0]][route[-1 * reactivate_after][1]][
                route[-1 * reactivate_after][2]] = True

        route.append(new_Position)

        if not speed_optimized:
            test_print()
    else:
        new_Position = []

    return new_Position


print("Searching goal... \n (Max: " + str(max_tact_allowed) + " tacts)")
status = "Running"

start_time = time.time()

div_for_status = round(max_tact_allowed / 50)

while tact <= max_tact_allowed:

    current_position = make_a_move(current_position)

    if not current_position:
        print("\n*** Round terminated: No more options to move *** \n")
        status = "Terminated (Reason: No more options to move)"
        break

    if current_position == goal_position:
        status = "Goal found"
        print(status)
        # Cleanup route
        break

    status = "Maximum tact count Reached"

    tact += 1

    if tact % div_for_status == 0 or tact % 25000 == 0:
        status_update((round((tact / max_tact_allowed) * 100)))

if status == "Goal found" or always_shorten_route:
    long_route = route.copy()
    short_route = Services.clean_up_route(long_route)

# Statistics calculation
end_time = time.time()
ms = (end_time - start_time) * 1000
if ms != 0:
    tps = round(tact / (ms / 1000))
else:
    tps = 0

test_print(-1)

# scratch


# Final (always shown) statistics
print("Runtime: ", round(ms), "ms  // ", tps, "tacts per second")

# Draw route
Services.draw_path(route, short_route, goal_position, tact, status, auto_rotate)
