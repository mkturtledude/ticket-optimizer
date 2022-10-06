import copy

import base, calculator, solver

def isFeasible(originalItem, targetLevel, targetUncaps, tickets):
    t = originalItem.gameItem.type
    r = originalItem.gameItem.rarity
    ltn = base.calculateLevelTicketsNeeded(originalItem, targetLevel)
    utn = base.calculateCapTicketsNeeded(originalItem, targetUncaps)
    if t == "D":
        if r == "N":
            if ltn > tickets.lnd or utn > tickets.und:
                return False
        elif r == "S":
            if ltn > tickets.lsd or utn > tickets.usd:
                return False
        else:
            assert(r == "HE")
            if ltn > tickets.lhd or utn > tickets.uhd:
                return False
    elif t == "K":
        if r == "N":
            if ltn > tickets.lnk or utn > tickets.unk:
                return False
        elif r == "S":
            if ltn > tickets.lsk or utn > tickets.unk:
                return False
        else:
            assert(r == "HE")
            if ltn > tickets.lhk or utn > tickets.uhk:
                return False
    else:
        assert(t == "G")
        if r == "N":
            if ltn > tickets.lng or utn > tickets.ung:
                return False
        elif r == "S":
            if ltn > tickets.lsg or utn > tickets.usg:
                return False
        else:
            assert(r == "HE")
            if ltn > tickets.lhg or utn > tickets.uhg:
                return False
    return True

def expandInventoryByType(items, itemType, numberOfMiis, tickets):
    result = set()
    for item in items:
        minLevel = item.level
        minUncaps = item.uncaps
        for level in range(minLevel,8+1):
            partialLevels = item.partialLevels if level == minLevel else 0
            for uncaps in range(minUncaps, 4+1):
                if isFeasible(item, level, uncaps, tickets):
                    basePoints = base.calculateBasePoints(itemType, item.rarity, uncaps, item.isMii, numberOfMiis)
                    result.add(base.InventoryItem(item.gameItem, level, basePoints, uncaps, partialLevels))
    # print("Input inventory has size {}".format(len(items)))
    # print("Output inventory has size {}".format(len(result)))
    return result

def expandInventory(inventory, tickets):
    result = base.Inventory()
    result.drivers = expandInventoryByType(inventory.drivers, "D", inventory.numberOfMiis, tickets)
    result.karts = expandInventoryByType(inventory.karts, "K", inventory.numberOfMiis, tickets)
    result.gliders = expandInventoryByType(inventory.gliders, "G", inventory.numberOfMiis, tickets)
    return result


def getMaxShelves(course, inventory):
    #print("Calling getMaxShelves with an inventory with size {}/{}/{}".format(len(inventory.drivers), len(inventory.karts), len(inventory.gliders)))
    maxDriverShelf = 0
    for driver in inventory.drivers:
        assert(driver)
        maxDriverShelf = max(maxDriverShelf, calculator.getShelf(course, driver))
    maxKartShelf = 0
    for kart in inventory.karts:
        assert(kart)
        maxKartShelf = max(maxKartShelf, calculator.getShelf(course, kart))
    maxGliderShelf = 0
    for glider in inventory.gliders:
        assert(glider)
        maxGliderShelf = max(maxGliderShelf, calculator.getShelf(course, glider))
    #print("getMaxShelves on course {} will return {}/{}/{}".format(course.englishName, maxDriverShelf, maxKartShelf, maxGliderShelf))
    return maxDriverShelf, maxKartShelf, maxGliderShelf

def createCombinationsOnCourses(courses, optWithCurrent, expandedInventory, playerLevel):
    combinationsOnCourses = dict()
    for course in courses:
        combinationsOnCourses[course] = set()
        reducedInventory = base.Inventory()
        referenceScore = optWithCurrent[course][0]
        referenceDriver = optWithCurrent[course][1]
        referenceKart = optWithCurrent[course][2]
        referenceGlider = optWithCurrent[course][3]
        if not referenceDriver:
            print("Course {} has no reference driver".format(course.englishName))
        if not referenceKart:
            print("Course {} has no reference kart".format(course.englishName))
        if not referenceGlider:
            print("Course {} has no reference glider".format(course.englishName))
        assert(referenceDriver)
        assert(referenceKart)
        assert(referenceGlider)

        # For each item in the expanded inventory, calculate the score obtained by combining it with the other 2 reference items
        # If it beats the reference score, add the item to the course-dependent reduced inventory
        maxDriverShelf, maxKartShelf, maxGliderShelf = getMaxShelves(course, expandedInventory)

        for driver in expandedInventory.drivers:
            if calculator.getShelf(course, driver) >= maxDriverShelf:
                if referenceScore <= calculator.calculateScore(driver, referenceKart, referenceGlider,
                                                               playerLevel, course):
                    reducedInventory.drivers.add(driver)
        for kart in expandedInventory.karts:
            if calculator.getShelf(course, kart) >= maxKartShelf:
                if referenceScore <= calculator.calculateScore(referenceDriver, kart, referenceGlider,
                                                               playerLevel, course):
                    reducedInventory.karts.add(kart)
        for glider in expandedInventory.gliders:
            if calculator.getShelf(course, glider) >= maxGliderShelf:
                if referenceScore <= calculator.calculateScore(referenceDriver, referenceKart, glider,
                                                               playerLevel, course):
                    reducedInventory.gliders.add(glider)

        # For each DKG combination in the reduced inventory, calculate the score and save score+combination in combinationsOnCourses
        for driver in reducedInventory.drivers:
            for kart in reducedInventory.karts:
                for glider in reducedInventory.gliders:
                    score = calculator.calculateScore(driver, kart, glider, playerLevel, course)
                    combinationsOnCourses[course].add(tuple([score, driver, kart, glider]))
        # print("{} has {} combinations".format(course.englishName, len(combinationsOnCourses[course])))
    return combinationsOnCourses

def calculateOptWithCurrent(courses, inventory, playerLevel):
    totalScore = 0
    optWithCurrent = dict()
    ## This whole loop only looks for the optimal combinations with the current loadouts, i.e., without any upgrades
    ## It also fills the dict optWithCurrent
    for course in courses:
        maxScore = 0
        d = None
        k = None
        g = None
        combinations = 0

        ## Create reduced inventory from original inventory ##
        reducedInventory = base.Inventory()

        maxDriverShelf, maxKartShelf, maxGliderShelf = getMaxShelves(course, inventory)

        for driver in inventory.drivers:
            if calculator.getShelf(course, driver) >= maxDriverShelf:
                reducedInventory.drivers.add(driver)
        for kart in inventory.karts:
            if calculator.getShelf(course, kart) >= maxKartShelf:
                reducedInventory.karts.add(kart)
        for glider in inventory.gliders:
            if calculator.getShelf(course, glider) >= maxGliderShelf:
                reducedInventory.gliders.add(glider)
        # print("{}: The reduced inventory has {} drivers, {} karts and {} gliders".format(course.englishName, len(reducedInventory.drivers), len(reducedInventory.karts), len(reducedInventory.gliders)))
        inv = reducedInventory
        for driver in inv.drivers:
            for kart in inv.karts:
                for glider in inv.gliders:
                    combinations += 1
                    score = calculator.calculateScore(driver, kart, glider, playerLevel, course)
                    if maxScore < score:
                        maxScore = score
                        d = driver
                        k = kart
                        g = glider
        # # print("Calculating score again")
        # if course.englishName == "SNES Donut Plains 2T":
        #     print("Found course")
        #     calculator.calculateScore(d,k,g,PLAYER_LEVEL,course)
        #     exit(0)
        optWithCurrent[course] = [maxScore, d, k, g]
        # print(maxScore)
        totalScore += maxScore
    #     # Uncomment for pre-fill of DKR sheet
        print(maxScore)
    #     print("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(d.englishName, calculator.getShelf(course, d), d.level, d.basePoints, k.englishName, calculator.getShelf(course, k), k.level, k.basePoints, g.englishName, calculator.getShelf(course, g), g.level, g.basePoints))
    return totalScore, optWithCurrent

def createOriginalInventoryIdToItem(inventory):
    originalInventoryIdToItem = dict()
    for d in inventory.drivers:
        originalInventoryIdToItem[d.gameItem.id] = d
    for k in inventory.karts:
        originalInventoryIdToItem[k.gameItem.id] = k
    for g in inventory.gliders:
        originalInventoryIdToItem[g.gameItem.id] = g
    return originalInventoryIdToItem

def updateInventory(currentInventory, solutionCombinations):
    result = copy.deepcopy(currentInventory)
    driverIdToCombinations = dict()
    kartIdToCombinations = dict()
    gliderIdToCombinations = dict()
    for c in solutionCombinations:
        driverIdToCombinations[c[0]] = [c[0],c[1],c[2]]
        kartIdToCombinations[c[3]] = [c[3],c[4],c[5]]
        gliderIdToCombinations[c[6]] = [c[6],c[7],c[8]]

    for d in result.drivers:
        if d.gameItem.id in driverIdToCombinations:
            comb = driverIdToCombinations[d.gameItem.id]
            if (comb[1] > d.level):
                d.partialLevels = 0
            d.level = comb[1]
            d.uncaps = comb[2]
            d.basePoints = base.calculateBasePoints(d.gameItem.type, d.gameItem.rarity, d.uncaps, d.gameItem.isMii, currentInventory.numberOfMiis)
    for k in result.karts:
        if k.gameItem.id in kartIdToCombinations:
            comb = kartIdToCombinations[k.gameItem.id]
            if (comb[1] > k.level):
                k.partialLevels = 0
            k.level = comb[1]
            k.uncaps = comb[2]
            k.basePoints = base.calculateBasePoints(k.gameItem.type, k.gameItem.rarity, k.uncaps, k.gameItem.isMii, currentInventory.numberOfMiis)
    for g in result.gliders:
        if g.gameItem.id in gliderIdToCombinations:
            comb = gliderIdToCombinations[g.gameItem.id]
            if (comb[1] > g.level):
                g.partialLevels = 0
            g.level = comb[1]
            g.uncaps = comb[2]
            g.basePoints = base.calculateBasePoints(g.gameItem.type, g.gameItem.rarity, g.uncaps, g.gameItem.isMii, currentInventory.numberOfMiis)
    return result


def createSolutionCombinations(inventory, courses, tickets, playerLevel):
    currentInventory = copy.deepcopy(inventory)
    currentTickets = copy.deepcopy(tickets)
    currentTickets.setKartsToZero()
    currentTickets.setGlidersToZero()
    originalInventoryIdToItem = createOriginalInventoryIdToItem(currentInventory)
    totalScore, optWithCurrent = calculateOptWithCurrent(courses, currentInventory, playerLevel)
    totalBeforeUpgrades = copy.deepcopy(totalScore)
    optLoadoutsBeforeUpgrades = copy.deepcopy(optWithCurrent)
    print("The total score without any upgrades is {}".format(totalScore))
    expandedInventory = expandInventory(currentInventory, currentTickets)
    combinationsOnCourses = createCombinationsOnCourses(courses, optWithCurrent, expandedInventory, playerLevel)
    solutionCombinations = solver.solveProblem(courses, combinationsOnCourses, originalInventoryIdToItem, currentTickets)

    currentInventory = updateInventory(currentInventory, solutionCombinations)
    currentTickets = copy.deepcopy(tickets)
    currentTickets.setDriversToZero()
    currentTickets.setGlidersToZero()
    originalInventoryIdToItem = createOriginalInventoryIdToItem(currentInventory)
    totalScore, optWithCurrent = calculateOptWithCurrent(courses, currentInventory, playerLevel)
    print("The total score after driver upgrades is {}".format(totalScore))
    expandedInventory = expandInventory(currentInventory, currentTickets)
    combinationsOnCourses = createCombinationsOnCourses(courses, optWithCurrent, expandedInventory, playerLevel)
    solutionCombinations = solver.solveProblem(courses, combinationsOnCourses, originalInventoryIdToItem, currentTickets)

    currentInventory = updateInventory(currentInventory, solutionCombinations)
    currentTickets = copy.deepcopy(tickets)
    currentTickets.setDriversToZero()
    currentTickets.setKartsToZero()
    originalInventoryIdToItem = createOriginalInventoryIdToItem(currentInventory)
    totalScore, optWithCurrent = calculateOptWithCurrent(courses, currentInventory, playerLevel)
    print("The total score after driver and kart upgrades is {}".format(totalScore))
    expandedInventory = expandInventory(currentInventory, currentTickets)
    combinationsOnCourses = createCombinationsOnCourses(courses, optWithCurrent, expandedInventory, playerLevel)

    solutionCombinations = solver.solveProblem(courses, combinationsOnCourses, originalInventoryIdToItem, currentTickets)

    currentInventory = updateInventory(currentInventory, solutionCombinations)
    totalScore, optWithCurrent = calculateOptWithCurrent(courses, currentInventory, playerLevel)
    print("The total score after all upgrades is {}".format(totalScore))

    courseLoadouts = dict()
    for c in optWithCurrent:
        courseLoadouts[c] = []
        for c2 in optLoadoutsBeforeUpgrades:
            if c.englishName == c2.englishName and c.sortId == c2.sortId:
                s0 = round(optLoadoutsBeforeUpgrades[c2][0])
                d0 = optLoadoutsBeforeUpgrades[c2][1]
                k0 = optLoadoutsBeforeUpgrades[c2][2]
                g0 = optLoadoutsBeforeUpgrades[c2][3]
                l = [d0.englishName,str(d0.level),str(d0.basePoints),k0.englishName,str(k0.level),str(k0.basePoints),str(g0.englishName),str(g0.level),str(g0.basePoints),str(s0)]
                courseLoadouts[c].append(l)

        s = round(optWithCurrent[c][0])
        d = optWithCurrent[c][1]
        k = optWithCurrent[c][2]
        g = optWithCurrent[c][3]
        l = [d.englishName,str(d.level),str(d.basePoints),k.englishName,str(k.level),str(k.basePoints),str(g.englishName),str(g.level),str(g.basePoints),str(s), str(s-s0)]
        courseLoadouts[c].append(l)

    return solutionCombinations, courseLoadouts, [str(round(totalBeforeUpgrades)), str(round(totalScore)), str(round(totalScore - totalBeforeUpgrades))]



def optimize(inventory, courses, tickets, playerLevel):
    solutionCombinations, courseLoadouts, totalScores = createSolutionCombinations(inventory, courses, tickets, playerLevel)
    upgrades, rows = solver.constructUpgradeTableStrings(solutionCombinations, inventory, courses)
    return upgrades, rows, courseLoadouts, totalScores
