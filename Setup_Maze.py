def setupDefaultMaze(maxX, maxY, maxZ, defaultValue):

    setup_result = []

    for zi in range(maxZ):
        setup_result2 = []

        for yi in range(maxY):
            setup_result1 = []

            for xi in range(maxX):
                setup_result1.append(defaultValue)

            setup_result2.append(setup_result1)

        setup_result.append(setup_result2)

    return setup_result

