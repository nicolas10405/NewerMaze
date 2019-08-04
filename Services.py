import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d
import time


def convert_route(route):
    route_x = []
    route_y = []
    route_z = []

    for i in range(len(route)):
        route_x += [route[i][0]]
        route_y += [route[i][1]]
        route_z += [route[i][2]]

    return route_x, route_y, route_z


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
    print("Step 2 of 2 (Shortening path...): [" + "#" * int(round(number * (200 / dubs))) + "] ",
          str(number) + " deviations eliminated")

    return time.time()


def clean_up_route(long_route):

    start_time2 = time.time()
    last_execution_time = start_time2 - 0.5
    status_counter = 1
    continue_to_check = True

    number_of_duplicates = 500  # len([x for n, x in enumerate(long_route) if x in long_route[:n]])
    print("\nStarting path optimization: " + str(number_of_duplicates) + " deviations found")

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
                    last_execution_time = status_update(status_counter, number_of_duplicates)

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

'''
                print(str(time.time() - last_execution_time))
                if i % 10 == 0: last_execution_time = status_update(status_counter, number_of_duplicates)
                if i % 10 == 0: 
'''
