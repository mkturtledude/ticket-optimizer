import pyscipopt as scip
import base, calculator
import copy

def solveProblem(courses, combinationsOnCourses, originalInventoryIdToItem, tickets):
    ## Create model
    print("Creating and solving model...")
    model = scip.Model()

    combinationsToVariables = []
    allCombinationScores = []
    allCombinationVariables = []
    combinationVariablesByCourse = []
    # print("Creating y variables")
    for i in range(len(courses)):
        course = courses[i]
        combinationVariablesByCourse.append([])
        combinationsToVariables.append(dict())
        for c in combinationsOnCourses[course]:
            if c in combinationsToVariables[-1]:
                v = combinationsToVariables[-1][c]
            else:
                did = c[1].gameItem.id
                dl = c[1].level
                du = c[1].uncaps
                kid = c[2].gameItem.id
                kl = c[2].level
                ku = c[2].uncaps
                gid = c[3].gameItem.id
                gl = c[3].level
                gu = c[3].uncaps
                v = model.addVar(vtype="B",
                                 name="y_%s_%s_%s_%s_%s_%s_%s_%s_%s_%s" % (i, did, dl, du, kid, kl, ku, gid, gl, gu))
                # variablesToCombinations[v] = c
                combinationsToVariables[-1][c] = v
            allCombinationScores.append(c[0])
            allCombinationVariables.append(v)
            combinationVariablesByCourse[-1].append(v)
            # print("\t[{}/{}/{}] + [{}/{}/{}] + [{}/{}/{}] -> {}".format(c[1].englishName, c[1].level, c[1].basePoints, c[2].englishName, c[2].level, c[2].basePoints, c[3].englishName, c[3].level, c[3].basePoints, c[0]))

    # print("Adding constraints OneCombPerCourse")
    for courseCombinations in combinationVariablesByCourse:
        model.addCons(scip.quicksum(v for v in courseCombinations) == 1, "OneCombPerCourse")

    itemsToVariables = dict()
    # print("Adding x variables and constraints CombOnlyIf")
    for courseCombinations in combinationsToVariables:
        for c in courseCombinations:
            combinationVariable = courseCombinations[c]
            did = c[1].gameItem.id
            dl = c[1].level
            du = c[1].uncaps
            kid = c[2].gameItem.id
            kl = c[2].level
            ku = c[2].uncaps
            gid = c[3].gameItem.id
            gl = c[3].level
            gu = c[3].uncaps
            d = tuple([did, dl, du])
            k = tuple([kid, kl, ku])
            g = tuple([gid, gl, gu])
            if d in itemsToVariables:
                dv = itemsToVariables[d]
            else:
                dv = model.addVar(vtype="B", name="x_%s_%s_%s" % (did, dl, du))
                itemsToVariables[d] = dv
            if k in itemsToVariables:
                kv = itemsToVariables[k]
            else:
                kv = model.addVar(vtype="B", name="x_%s_%s_%s" % (kid, kl, ku))
                itemsToVariables[k] = kv
            if g in itemsToVariables:
                gv = itemsToVariables[g]
            else:
                gv = model.addVar(vtype="B", name="x_%s_%s_%s" % (gid, gl, gu))
                itemsToVariables[g] = gv
            model.addCons(combinationVariable <= dv, "CombOnlyIfDriver")
            model.addCons(combinationVariable <= kv, "CombOnlyIfKart")
            model.addCons(combinationVariable <= gv, "CombOnlyIfGlider")

    itemIdToVariables = dict()
    for item in itemsToVariables:
        id = item[0]
        if not id in itemIdToVariables:
            itemIdToVariables[id] = []
        itemIdToVariables[id].append(itemsToVariables[item])

    # print("Adding constraints OneStatePerItem")
    for id in itemIdToVariables:
        model.addCons(scip.quicksum(v for v in itemIdToVariables[id]) <= 1, "OneStatePerItem")

    normalDriverVariables = []
    normalKartVariables = []
    normalGliderVariables = []
    superDriverVariables = []
    superKartVariables = []
    superGliderVariables = []
    highEndDriverVariables = []
    highEndKartVariables = []
    highEndGliderVariables = []
    normalDriverRemainingLevelTickets = []
    normalKartRemainingLevelTickets = []
    normalGliderRemainingLevelTickets = []
    superDriverRemainingLevelTickets = []
    superKartRemainingLevelTickets = []
    superGliderRemainingLevelTickets = []
    highEndDriverRemainingLevelTickets = []
    highEndKartRemainingLevelTickets = []
    highEndGliderRemainingLevelTickets = []
    normalDriverRemainingUncapTickets = []
    normalKartRemainingUncapTickets = []
    normalGliderRemainingUncapTickets = []
    superDriverRemainingUncapTickets = []
    superKartRemainingUncapTickets = []
    superGliderRemainingUncapTickets = []
    highEndDriverRemainingUncapTickets = []
    highEndKartRemainingUncapTickets = []
    highEndGliderRemainingUncapTickets = []
    for item in itemsToVariables:
        originalItem = originalInventoryIdToItem[item[0]]
        rarity = originalItem.gameItem.rarity
        type = originalItem.gameItem.type
        v = itemsToVariables[item]
        levelTicketsNeeded = base.calculateLevelTicketsNeeded(originalItem, item[1])
        uncapTicketsNeeded = base.calculateCapTicketsNeeded(originalItem, item[2])
        if type == "D":
            if rarity == "HE":
                highEndDriverVariables.append(v)
                highEndDriverRemainingLevelTickets.append(levelTicketsNeeded)
                highEndDriverRemainingUncapTickets.append(uncapTicketsNeeded)
            elif rarity == "S":
                superDriverVariables.append(v)
                superDriverRemainingLevelTickets.append(levelTicketsNeeded)
                superDriverRemainingUncapTickets.append(uncapTicketsNeeded)
            else:
                assert (rarity == "N")
                normalDriverVariables.append(v)
                normalDriverRemainingLevelTickets.append(levelTicketsNeeded)
                normalDriverRemainingUncapTickets.append(uncapTicketsNeeded)
        elif type == "K":
            if rarity == "HE":
                highEndKartVariables.append(v)
                highEndKartRemainingLevelTickets.append(levelTicketsNeeded)
                highEndKartRemainingUncapTickets.append(uncapTicketsNeeded)
            elif rarity == "S":
                superKartVariables.append(v)
                superKartRemainingLevelTickets.append(levelTicketsNeeded)
                superKartRemainingUncapTickets.append(uncapTicketsNeeded)
            else:
                assert (rarity == "N")
                normalKartVariables.append(v)
                normalKartRemainingLevelTickets.append(levelTicketsNeeded)
                normalKartRemainingUncapTickets.append(uncapTicketsNeeded)
        else:
            assert (type == "G")
            if rarity == "HE":
                highEndGliderVariables.append(v)
                highEndGliderRemainingLevelTickets.append(levelTicketsNeeded)
                highEndGliderRemainingUncapTickets.append(uncapTicketsNeeded)
            elif rarity == "S":
                superGliderVariables.append(v)
                superGliderRemainingLevelTickets.append(levelTicketsNeeded)
                superGliderRemainingUncapTickets.append(uncapTicketsNeeded)
            else:
                assert (rarity == "N")
                normalGliderVariables.append(v)
                normalGliderRemainingLevelTickets.append(levelTicketsNeeded)
                normalGliderRemainingUncapTickets.append(uncapTicketsNeeded)

    # print("Adding ticket constraints")
    model.addCons(scip.quicksum(normalDriverRemainingLevelTickets[i] * normalDriverVariables[i] for i in
                                range(len(normalDriverVariables))) <= tickets.lnd, "NDlevels")
    model.addCons(scip.quicksum(normalDriverRemainingUncapTickets[i] * normalDriverVariables[i] for i in
                                range(len(normalDriverVariables))) <= tickets.und, "NDuncaps")
    model.addCons(scip.quicksum(normalKartRemainingLevelTickets[i] * normalKartVariables[i] for i in
                                range(len(normalKartVariables))) <= tickets.lnk, "NKlevels")
    model.addCons(scip.quicksum(normalKartRemainingUncapTickets[i] * normalKartVariables[i] for i in
                                range(len(normalKartVariables))) <= tickets.unk, "NKuncaps")
    model.addCons(scip.quicksum(normalGliderRemainingLevelTickets[i] * normalGliderVariables[i] for i in
                                range(len(normalGliderVariables))) <= tickets.lng, "NGlevels")
    model.addCons(scip.quicksum(normalGliderRemainingUncapTickets[i] * normalGliderVariables[i] for i in
                                range(len(normalGliderVariables))) <= tickets.ung, "NGuncaps")

    model.addCons(scip.quicksum(superDriverRemainingLevelTickets[i] * superDriverVariables[i] for i in
                                range(len(superDriverVariables))) <= tickets.lsd, "SDlevels")
    model.addCons(scip.quicksum(superDriverRemainingUncapTickets[i] * superDriverVariables[i] for i in
                                range(len(superDriverVariables))) <= tickets.usd, "SDuncaps")
    model.addCons(scip.quicksum(superKartRemainingLevelTickets[i] * superKartVariables[i] for i in
                                range(len(superKartVariables))) <= tickets.lsk, "SKlevels")
    model.addCons(scip.quicksum(superKartRemainingUncapTickets[i] * superKartVariables[i] for i in
                                range(len(superKartVariables))) <= tickets.usk, "SKuncaps")
    model.addCons(scip.quicksum(superGliderRemainingLevelTickets[i] * superGliderVariables[i] for i in
                                range(len(superGliderVariables))) <= tickets.lsg, "SGlevels")
    model.addCons(scip.quicksum(superGliderRemainingUncapTickets[i] * superGliderVariables[i] for i in
                                range(len(superGliderVariables))) <= tickets.usg, "SGuncaps")

    model.addCons(scip.quicksum(highEndDriverRemainingLevelTickets[i] * highEndDriverVariables[i] for i in
                                range(len(highEndDriverVariables))) <= tickets.lhd, "HDlevels")
    model.addCons(scip.quicksum(highEndDriverRemainingUncapTickets[i] * highEndDriverVariables[i] for i in
                                range(len(highEndDriverVariables))) <= tickets.uhd, "HDuncaps")
    model.addCons(scip.quicksum(highEndKartRemainingLevelTickets[i] * highEndKartVariables[i] for i in
                                range(len(highEndKartVariables))) <= tickets.lhk, "HKlevels")
    model.addCons(scip.quicksum(highEndKartRemainingUncapTickets[i] * highEndKartVariables[i] for i in
                                range(len(highEndKartVariables))) <= tickets.uhk, "HKuncaps")
    model.addCons(scip.quicksum(highEndGliderRemainingLevelTickets[i] * highEndGliderVariables[i] for i in
                                range(len(highEndGliderVariables))) <= tickets.lhg, "HGlevels")
    model.addCons(scip.quicksum(highEndGliderRemainingUncapTickets[i] * highEndGliderVariables[i] for i in
                                range(len(highEndGliderVariables))) <= tickets.uhg, "HGuncaps")

    model.setObjective(scip.quicksum(
        allCombinationScores[i] * allCombinationVariables[i] for i in range(len(allCombinationVariables))), "maximize")
    # model.writeProblem("tickets.lp")
    # exit(0)
    model.hideOutput()
    model.optimize()

    # model.writeBestSol("tickets-ffb.sol")
    model.printBestSol()

    sol = model.getBestSol()

    optimalCombinations = []
    for courseMap in combinationsToVariables:
        for c in courseMap:
            variable = courseMap[c]
            if abs(model.getSolVal(sol, variable) - 1) < 0.0001:
                optimalCombinations.append([c[1].gameItem.id, c[1].level, c[1].uncaps, c[2].gameItem.id, c[2].level, c[2].uncaps, c[3].gameItem.id, c[3].level, c[3].uncaps])

    print("Done solving model!")
    return optimalCombinations


def printFinalOutput(solutionCombinations, inventory, courses):
    processedIds = set()
    finalCombinations = []
    driverUpgrades = []
    kartUpgrades = []
    gliderUpgrades = []
    for [did, dl, du, kid, kl, ku, gid, gl, gu] in solutionCombinations:
        newCombination = []
        for d in inventory.drivers:
            if d.gameItem.id == did:
                newCombination.append(copy.deepcopy(d))
                if d.level != dl or d.uncaps != du:
                    newCombination[-1].level = dl
                    newCombination[-1].uncaps = du
                    newCombination[-1].basePoints = base.calculateBasePoints("D", d.gameItem.rarity, du,
                                                                             d.gameItem.isMii, inventory.numberOfMiis)
                    if did not in processedIds:
                        driverUpgrades.append([d.englishName, d.level, d.uncaps, dl, du])
        for k in inventory.karts:
            if k.gameItem.id == kid:
                newCombination.append(copy.deepcopy(k))
                if k.level != kl or k.uncaps != ku:
                    newCombination[-1].level = kl
                    newCombination[-1].uncaps = ku
                    newCombination[-1].basePoints = base.calculateBasePoints("K", k.gameItem.rarity, ku, False,
                                                                             inventory.numberOfMiis)
                    if kid not in processedIds:
                        kartUpgrades.append([k.englishName, k.level, k.uncaps, kl, ku])
        for g in inventory.gliders:
            if g.gameItem.id == gid:
                newCombination.append(copy.deepcopy(g))
                if g.level != gl or g.uncaps != gu:
                    newCombination[-1].level = gl
                    newCombination[-1].uncaps = gu
                    newCombination[-1].basePoints = base.calculateBasePoints("G", g.gameItem.rarity, gu, False,
                                                                             inventory.numberOfMiis)
                    if gid not in processedIds:
                        gliderUpgrades.append([g.englishName, g.level, g.uncaps, gl, gu])
        processedIds.add(did)
        processedIds.add(kid)
        processedIds.add(gid)
        finalCombinations.append(newCombination)

    for l in [driverUpgrades, kartUpgrades, gliderUpgrades]:
        for item in l:
            print("{}: [{}/{}] -> [{}/{}]".format(item[0], item[1], item[2], item[3], item[4]))
        print()

    for i in range(len(finalCombinations)):
        [d, k, g] = finalCombinations[i]
        course = courses[i]
        print("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(d.englishName, calculator.getShelf(course, d),
                                                                      d.level, d.basePoints, k.englishName,
                                                                      calculator.getShelf(course, k), k.level,
                                                                      k.basePoints, g.englishName,
                                                                      calculator.getShelf(course, g), g.level,
                                                                      g.basePoints))
