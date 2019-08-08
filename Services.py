import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d
import time
import ast
import os


def generate_id(version, string="_", *args):

    unique_id = ""

    for num in args:
        unique_id += str(num)

    file_id = "S_Matrix_" + str(unique_id) + string + version

    return file_id


def convert_route(route):
    route_x = []
    route_y = []
    route_z = []

    for i in range(len(route)):
        route_x += [route[i][0]]
        route_y += [route[i][1]]
        route_z += [route[i][2]]

    return route_x, route_y, route_z


def step_direction(step1, step2):

    if step2[0] - step1[0] == 1: direction = [0,0]
    if step2[0] - step1[0] == -1: direction = [0,1]

    if step2[1] - step1[1] == 1: direction = [1,0]
    if step2[1] - step1[1] == -1: direction = [1,1]

    if step2[2] - step1[2] == 1: direction = [2,0]
    if step2[2] - step1[2] == -1: direction = [2,1]

    return direction


def draw_path(route, short_route, goal, tact, status, auto_rotate=False):
    route_x, route_y, route_z = convert_route(route)

    fig = plt.figure()
    ax = plt.axes(projection="3d")

    ax.scatter3D(route_x[0], route_y[0], route_z[0], marker="^")  # Start
    ax.scatter3D(route_x[-1], route_y[-1], route_z[-1], marker=">")  # Last position
    ax.scatter3D(goal[0], goal[1], goal[2], marker="x")  # Goal position

    ax.set(title="PATH: " + str(tact - 1) + " tacts | " + status)  # Titel
    ax.plot3D(route_x, route_y, route_z, "grey")  # Long route

    if short_route:
        s_route_x, s_route_y, s_route_z = convert_route(short_route)
        ax.plot3D(s_route_x, s_route_y, s_route_z, "blue")  # Short route

    if auto_rotate:

        for angle in range(-30, 330):
            ax.view_init(azim=angle)
            plt.draw()
            plt.pause(.001)

        plt.show()

    else:
        plt.show()


def status_update(number, dubs):

    progress_number = round(number * (200 / dubs))
    progress_number_100er = 2 * (progress_number // 100)
    progress_number_remain = progress_number % 100

    progress_string = "#" + str(progress_number_100er * 100) + "#" * progress_number_remain

    print("Step 2 of 2 (Shortening path...): [" + progress_string + "] ",
          str(number) + " deviations eliminated")

    return time.time()


def clean_up_route(long_route):

    start_time2 = time.time()
    last_execution_time = start_time2 - 0.5
    status_counter = 1
    continue_to_check = True

    number_of_duplicates_assumed = 500  # len([x for n, x in enumerate(long_route) if x in long_route[:n]])
    print("\n----Starting path optimization:----")

    initial_length = len(long_route)

    while continue_to_check:

        long_route_rev = long_route.copy()
        long_route_rev.reverse()

        check_list = []
        check_list.clear()

        for i in range(len(long_route_rev)):
            if long_route_rev[i] not in check_list:
                check_list.append(long_route_rev[i])
                continue_to_check = False

            else:
                duplicate = long_route_rev[i]

                first_index = long_route.index(duplicate)
                last_index = len(long_route_rev) - (long_route_rev.index(duplicate))

                items_to_pop = last_index - (first_index + 1)

                for i_ in range(items_to_pop):
                    long_route.pop(first_index)

                continue_to_check = True

                status_counter = status_counter + 1

                if time.time() - last_execution_time > 0.5:
                    last_execution_time = status_update(status_counter, number_of_duplicates_assumed)

                break

    end_time2 = time.time()

    print("\n----Path shortening completed-----")
    print(str(round((end_time2 - start_time2) * 1000)), "ms for shortening path")
    print("From " + str(initial_length) + " steps to " + str(len(long_route)) + " steps (" + str(
        round((len(long_route) / initial_length) * 100)) + "%) of original\n")

    return long_route  # now shortend


### FOR ANALYSIS
'''
def clean_up_route(long_route):

    start_time2 = time.time()

    continue_to_check = True

    while continue_to_check:

        long_route_rev = long_route.copy()
        long_route_rev.reverse()

        check_list = []
        check_list.clear()

        for i in range(len(long_route_rev)):
            if long_route_rev[i] not in check_list:
                check_list.append(long_route_rev[i])
                continue_to_check = False

            else:
                duplicate = long_route_rev[i]

                print("\nDUPE")
                print(duplicate)

                first_index = long_route.index(duplicate)
                last_index = len(long_route_rev)-(long_route_rev.index(duplicate))

                print("***Long Route***")
                print(long_route)

                print("***Long Rev Route***")
                print(long_route_rev)

                items_to_pop = last_index - (first_index + 1)

                print("Index:", first_index,last_index, "Items:", items_to_pop)

                for i_ in range(items_to_pop):
                    print(long_route.pop(first_index))

                print ("deletion done")
                print(long_route)

                continue_to_check = True

                break



    end_time2 = time.time()

    print("Zeit shortening(ms):", str(round((end_time2 - start_time2) * 1000)))

    return long_route #now shortend



'''

def save_s_matrix(filename, matrix):
    f = open(str(filename) + ".smx", "wt")
    f.write(str(matrix))
    f.close()
    print("***Matrix saved to file: " + filename)


def open_s_matrix(filename, matrix):
    if os.path.exists(str(filename) + ".smx"):
        f = open(str(filename) + ".smx", "rt")
        matrix = f.read()
        matrix = ast.literal_eval(matrix)
        f.close()
        print("\n***Matrix opened from file: " + filename)
    else:
        print("\n***No record found for this configuration")
    return matrix


