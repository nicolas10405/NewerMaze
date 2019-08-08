import Setup_Maze
from numpy.random import choice
import numpy
import random
import Services
import time
import os
import sys

# Config (Global)

maxX = 25
maxY = maxX
maxZ = maxX

save_open_s_matrix_to_file = True

debugging_view = False #Lowest level / most details
debugging_view_L2 = False
only_show_round_statistics = True
super_speed = [False, 10]

always_shorten_route = False
show_visualization = True
auto_rotate = False

version_for_file_format = "v01"

# Config (Round)

starting_position = [5, 5, 5]
goal_position = [10, 10, 10]
distance = abs(starting_position[0] - goal_position[0]) + abs(starting_position[1] - goal_position[1]) + abs(starting_position[2] - goal_position[2])

learning_factor = 250
abs_reward = distance * learning_factor  # round(0.25 * maxX * maxY * maxZ) # AI
reactivate_after = 0  # tacts #AI
# max_tact_allowed = 10000
max_tact_allowed = round(0.1 * maxX * maxY * maxZ)  # AI
rounds_to_run = 500

store_for_statistics = []
last20percent = []
overall_mean = 0
median = 0
p20_mean = 0

# Round initialization
def round_init(passed_status):
    global route, short_route, tact, status, tact_last_update, time_last_update

    route = [starting_position]
    short_route = []
    tact = 1
    status = passed_status

    tact_last_update = 0
    time_last_update = time.time()


#round_init("First initialization")

# Services

def set_borders():
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


def update_strength(total_strength, route):
    extra_strength = round(total_strength / len(route))

    i = 0

    for i in range(len(route) - 1):
        direction = Services.step_direction(route[i], route[i + 1])
        strength[route[i][0]][route[i][1]][route[i][2]][direction[0]][direction[1]] += extra_strength

    if not only_show_round_statistics: print("----Strength updated: +" + str(extra_strength) + " to path----")


def test_print(tact_adjuster=0):
    print("\n----- Tact", tact + tact_adjuster, "(", tact_adjuster, ")------")
    print("Status: " + status)
    if debugging_view:
        print("Current position:")
        print(current_position)
        print("CanGO Matrix:")
        print(current_cg_matrix)
    print("New Position:")
    print("-->", new_Position, "(after move in direction " + str(int(random_choice)) + ")")
    print("Strength Matrix:")
    print(current_s_matrix)
    if short_route:
        print("Short Route: " + str(len(short_route)) + " steps")
        if debugging_view_L2: print(short_route, "\n")


def status_update(percent):
    global time_last_update
    global tact_last_update

    tps = round((tact - tact_last_update) / (time.time() - time_last_update))
    rt_min = round(((max_tact_allowed - tact) / tps) // 60)
    rt_sec = round(((max_tact_allowed - tact) / tps) % 60)
    print("Step 1 of 2 (Making moves...): [" + "#" * int(percent / 2) + "-" * (50 - int(percent / 2)) + "] ",
          str(percent) + "% of max, now tact: " + str(tact) + ") - Speed: " + str(tps) + " TPS - max runtime: " + str(
              rt_min) + " min " + str(rt_sec) + "s")
    time_last_update = time.time()
    tact_last_update = tact


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

        random_choice = choice(a=(0, 1, 2, 3, 4, 5),
                               size=1,
                               p=(x_p_n, x_m_n, y_p_n, y_m_n, z_p_n, z_m_n))

        new_Position = [[x + 1, y, z], [x - 1, y, z], [x, y + 1, z], [x, y - 1, z], [x, y, z + 1], [x, y, z - 1]][
            int(random_choice)]

        canGo[x][y][z] = False

        if reactivate_after != 0 and reactivate_after < tact:
            canGo[route[-1 * reactivate_after][0]][route[-1 * reactivate_after][1]][
                route[-1 * reactivate_after][2]] = True

        route.append(new_Position)

        if debugging_view:
            test_print()
    else:
        new_Position = []

    return new_Position


# Initalisierung

maze_id = Services.generate_id(version_for_file_format, "_", maxX, maxY, maxZ, starting_position, goal_position)
print("Started " + str(rounds_to_run) + " rounds - Distance: " + str(distance) + " steps - ID: " + maze_id + "\n")

strength = Setup_Maze.setupDefaultMazeS(maxX, maxY, maxZ, defaultValue=100)
if save_open_s_matrix_to_file: strength = Services.open_s_matrix(maze_id, strength)

for i in range(rounds_to_run):

    if not only_show_round_statistics: Services.round_header(i)

    round_init("Round initialization")

    canGo = Setup_Maze.setupDefaultMazeCG(maxX + 1, maxY + 1, maxZ + 1,
                                          defaultValue=True)  # max +1 to give room for 3 boundary planes set to false
    set_borders()

    current_position = starting_position

    status = "Initialized round"

    if not only_show_round_statistics: print("----Searching goal---- \n(Max: " + str(max_tact_allowed) + " tacts)")
    status = "Running"

    start_time = time.time()
    div_for_status = round(max_tact_allowed / 50)

    while tact <= max_tact_allowed:

        current_position = make_a_move(current_position)

        if not current_position:
            if not only_show_round_statistics: print("\nRound terminated: No more options to move \n")
            status = "Terminated (Reason: No more options to move)"
            break

        if current_position == goal_position:
            status = "Goal found"
            if not only_show_round_statistics: print(status)
            long_route = route.copy()
            if reactivate_after == 0:
                short_route = route
            else:
                short_route = Services.clean_up_route(long_route, only_show_round_statistics)
            update_strength(abs_reward, short_route)
            if save_open_s_matrix_to_file: Services.save_s_matrix(maze_id, strength, only_show_round_statistics)
            break

        status = "Maximum tact count Reached"

        tact += 1

        if not only_show_round_statistics:
            if tact % div_for_status == 0 or tact % 25000 == 0:
                status_update((round((tact / max_tact_allowed) * 100)))

    if status != "Goal found" and always_shorten_route:
        long_route = route.copy()
        short_route = Services.clean_up_route(long_route, only_show_round_statistics)

    # Statistics calculation
    end_time = time.time()
    ms = (end_time - start_time) * 1000
    if ms != 0:
        tps = round(tact / (ms / 1000))
    else:
        tps = 0

    if not only_show_round_statistics: test_print(-1)

    # Final (always shown) statistics

    if short_route:

        length_for_stat = len(short_route) - 1
        store_for_statistics.append(length_for_stat)

        overall_mean = int(round(numpy.mean(store_for_statistics)))
        median = int(round(numpy.median(store_for_statistics)))
        index_last20percent = int(round(max(len(store_for_statistics) / 5, 0)))
        index_last20percent = len(store_for_statistics) - index_last20percent

        if index_last20percent >= 5:
            last20percent.clear()
            last20percent = store_for_statistics[index_last20percent:]
            p20_mean = int(round(numpy.mean(last20percent)))

    else:
        length_for_stat = "n/a"

    len_filler = len(str(max_tact_allowed)) - len(str(tact))

    if super_speed[0]:
        if i % super_speed[1] == 0:
            print(\
                "Round: " + str(i + 1) + \
                " | Tacts: " + len_filler * " " + str(tact) + \
                " | Shortest route [Avg: " + str(overall_mean) + " Median: " + str(median) + " Avg(L20): " + str(p20_mean) + "] now: " + str(length_for_stat) + \
                " steps || Runtime: ", round(ms), "ms  | ", tps, "TPS || Status: " + status)
    else:
        print( \
            "Round: " + str(i + 1) + \
            " | Tacts: " + len_filler * " " + str(tact) + \
            " | Shortest route [Avg: " + str(overall_mean) + " Median: " + str(median) + " Avg(L20): " + str(
                p20_mean) + "] now: " + str(length_for_stat) + \
            " steps || Runtime: ", round(ms), "ms  | ", tps, "TPS || Status: " + status)
# scratch

# Draw route
if show_visualization: Services.draw_path(route, short_route, goal_position, tact, status, auto_rotate)

print(store_for_statistics)
#print(strength)
