# This file is a simplified and better documented version of solver.py (which is used by the app, this one isn't)
# I think it has everything you need, but feel free to check how solver.py is used in the app

# First I had implemented this using SCIP, but the hosting site forced me to use pip, so I had to switch to pulp.
# I don't think there's a big difference, sometimes I use SCIP locally for debugging
SCIP = False

if SCIP:
    import pyscipopt as scip
else:
    import pulp as plp


class GameItem:
    def __init__(self, name, id, type, rarity):
        self.name = name
        self.id = id
        self.type = type # "D", "K", "G"
        self.rarity = rarity # "HE", "S", "N"
        
class InventoryItem:
    def __init__(self, gameItem, level, uncaps, partialLevels):
        self.gameItem = gameItem
        self.level = level
        self.uncaps = uncaps
        self.partialLevels = partialLevels


"""
Class encoding the amount of tickets available
In each of the members: The first letter is the ticket type (Level or Uncaps), the second is the rarity (n/s/h) and
the third is the item type (d/k/g)
"""
class TicketStash:
    lnd = 0
    lnk = 0
    lng = 0
    lsd = 0
    lsk = 0
    lsg = 0
    lhd = 0
    lhk = 0
    lhg = 0
    und = 0
    unk = 0
    ung = 0
    usd = 0
    usk = 0
    usg = 0
    uhd = 0
    uhk = 0
    uhg = 0

# Uses the originalItem's rarity, level and sublevels to calculate how many level-up tickets are needed to reach the targetLevel
def calculateLevelTicketsNeeded(originalItem, targetLevel):
    #TODO: Implement
    return 0

# Uses the originalItem's uncaps to calculate how many uncap tickets are needed to reach the targetLevel
def calculateCapTicketsNeeded(originalItem, targetUncaps):
    #TODO: Implement
    return 0

'''
Input:

combinations: list<set<tuple<score, item, item, item>>>
    The list contains as many sets as there are courses in the tour (usually 45), in that order.
    Each tuple represents a "combination". It contains, in that order, a score, a driver, a kart and a glider. 
    The score is the one that corresponds to those loadouts on the given course. The score is a number. 
    The items correspond, in that order, to D, K and G. They are objects of the class InventoryItem. 
    They need to contain game ID, level and number of uncaps. 
    See how the variable "combination" is used, and adapt to your convenience.
idToOriginalInventoryItem: A dict that maps the item's game ID to an InventoryItem (see above). 
    These items should be exactly as they are in the inventory, as opposed to those in the "combinations" parameter,
    which represent hypothetical upgrades. 
    The data that we need from this inventory item is: Rarity, Type (D/K/G), possibility to 
    calculate the number of tickets needed to any given level (taking into account partial upgrades) or to any given 
    number of uncaps. All this data could in theory be included in the items of the previous parameter, but I did it 
    this way to avoid duplication.
tickets: An object of the TicketStash class

This function will consider all possible upgrades given in "combinations", and it will use the data in "idToOriginalInventoryItem"
to calculate the ticket consumption of each of these combinations. It will then find the maximum set of combinations
(using the scores in "combinations") subject to not exceeding the given amounts of tickets.

It will return all combinations found, in the following format:
[[driverId, driverLevel, driverUncaps, kartId, kartLevel, kartUncaps, gliderId, gliderLevel, gliderUncaps]]

There are 2 factors that blow up the runtime of this function:
1. Lots of tickets
2. Having many options on a track, especially if they are all at low levels. The most common example is the first track
   of the second cup, where all Miis are top-shelf. 
   
If the two combine, the function might take hours to complete. For that reason, I implemented an iterative version.
First, I find the best combination for each track with the current loadouts. I also calculate all possible combinations
and their respective scores. Then, I call this function passing it only the glider tickets (and 0 for D/K tickets).
Once it finds the optimal glider upgrades, I assume those upgrades and call this function again, this time with the kart tickets.
The "idToOriginalInventoryItem" now contains the upgraded gliders. Finally, I optimize the glider tickets, assuming the kart
and glider upgrades. This is all done in createSolutionCombinations(), in util.py.

This isn't guaranteed to be optimal overall, and some people have found concrete examples where it's not, but it's still quite good.
In the future I want to try different approaches, maybe a different order or additional iterations.

'''
def solve(combinations, idToOriginalInventoryItem, tickets):
    ## Create model
    print("Creating and solving model...")
    if SCIP:
        model = scip.Model()
    else:
        prob = plp.LpProblem("ScoreMaximization", plp.LpMaximize)

    combinationsToVariables = []
    allCombinationScores = []
    allCombinationVariables = []
    combinationVariablesByCourse = []
    for i in range(len(combinations)): # i will be used to name the variables
        courseCombinations = combinations[i]
        combinationVariablesByCourse.append([])
        combinationsToVariables.append(dict())
        for combination in courseCombinations:
            if combination in combinationsToVariables[-1]:
                v = combinationsToVariables[-1][combination]
            else:
                did = combination[1].gameItem.id
                dl = combination[1].level
                du = combination[1].uncaps
                kid = combination[2].gameItem.id
                kl = combination[2].level
                ku = combination[2].uncaps
                gid = combination[3].gameItem.id
                gl = combination[3].level
                gu = combination[3].uncaps
                if SCIP:
                    v = model.addVar(vtype="B",
                                     name="y_%s_%s_%s_%s_%s_%s_%s_%s_%s_%s" % (i, did, dl, du, kid, kl, ku, gid, gl, gu))
                else:
                    v = plp.LpVariable("y_%s_%s_%s_%s_%s_%s_%s_%s_%s_%s" % (i, did, dl, du, kid, kl, ku, gid, gl, gu), 0, 1, plp.LpInteger)
                combinationsToVariables[-1][combination] = v
            allCombinationScores.append(combination[0])
            allCombinationVariables.append(v)
            combinationVariablesByCourse[-1].append(v)
            
    if SCIP:
        model.setObjective(scip.quicksum(
            allCombinationScores[i] * allCombinationVariables[i] for i in range(len(allCombinationVariables))), "maximize")
    else:
        prob += plp.lpSum(allCombinationScores[i] * allCombinationVariables[i] for i in range(len(allCombinationVariables)))

    for courseCombinations in combinationVariablesByCourse:
        if SCIP:
            model.addCons(scip.quicksum(v for v in courseCombinations) == 1, "OneCombPerCourse")
        else:
            prob += plp.lpSum(v for v in courseCombinations) == 1

    itemsToVariables = dict()
    for courseCombinations in combinationsToVariables:
        for combination in courseCombinations:
            combinationVariable = courseCombinations[combination]
            did = combination[1].gameItem.id
            dl = combination[1].level
            du = combination[1].uncaps
            kid = combination[2].gameItem.id
            kl = combination[2].level
            ku = combination[2].uncaps
            gid = combination[3].gameItem.id
            gl = combination[3].level
            gu = combination[3].uncaps
            d = tuple([did, dl, du])
            k = tuple([kid, kl, ku])
            g = tuple([gid, gl, gu])
            if d in itemsToVariables:
                dv = itemsToVariables[d]
            else:
                if SCIP:
                    dv = model.addVar(vtype="B", name="x_%s_%s_%s" % (did, dl, du))
                else:
                    dv = plp.LpVariable("x_%s_%s_%s" % (did, dl, du), 0, 1, plp.LpInteger)
                itemsToVariables[d] = dv
            if k in itemsToVariables:
                kv = itemsToVariables[k]
            else:
                if SCIP:
                    kv = model.addVar(vtype="B", name="x_%s_%s_%s" % (kid, kl, ku))
                else:
                    kv = plp.LpVariable("x_%s_%s_%s" % (kid, kl, ku), 0, 1, plp.LpInteger)
                itemsToVariables[k] = kv
            if g in itemsToVariables:
                gv = itemsToVariables[g]
            else:
                if SCIP:
                    gv = model.addVar(vtype="B", name="x_%s_%s_%s" % (gid, gl, gu))
                else:
                    gv = plp.LpVariable("x_%s_%s_%s" % (gid, gl, gu), 0, 1, plp.LpInteger)
                itemsToVariables[g] = gv
            if SCIP:
                model.addCons(combinationVariable <= dv, "CombOnlyIfDriver")
                model.addCons(combinationVariable <= kv, "CombOnlyIfKart")
                model.addCons(combinationVariable <= gv, "CombOnlyIfGlider")
            else:
                prob += combinationVariable <= dv
                prob += combinationVariable <= kv
                prob += combinationVariable <= gv

    itemIdToVariables = dict()
    for item in itemsToVariables:
        id = item[0]
        if not id in itemIdToVariables:
            itemIdToVariables[id] = []
        itemIdToVariables[id].append(itemsToVariables[item])

    # print("Adding constraints OneStatePerItem")
    for id in itemIdToVariables:
        if SCIP:
            model.addCons(scip.quicksum(v for v in itemIdToVariables[id]) <= 1, "OneStatePerItem")
        else:
            prob += plp.lpSum(v for v in itemIdToVariables[id]) <= 1

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
        originalItem = idToOriginalInventoryItem[item[0]]
        rarity = originalItem.gameItem.rarity
        type = originalItem.gameItem.type
        v = itemsToVariables[item]
        levelTicketsNeeded = calculateLevelTicketsNeeded(originalItem, item[1])
        uncapTicketsNeeded = calculateCapTicketsNeeded(originalItem, item[2])
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

    if not SCIP:
        prob += plp.lpSum(normalDriverRemainingLevelTickets[i] * normalDriverVariables[i] for i in
                                    range(len(normalDriverVariables))) <= tickets.lnd, "NDlevels"
        prob += plp.lpSum(normalDriverRemainingUncapTickets[i] * normalDriverVariables[i] for i in
                                    range(len(normalDriverVariables))) <= tickets.und, "NDuncaps"
        prob += plp.lpSum(normalKartRemainingLevelTickets[i] * normalKartVariables[i] for i in
                                    range(len(normalKartVariables))) <= tickets.lnk, "NKlevels"
        prob += plp.lpSum(normalKartRemainingUncapTickets[i] * normalKartVariables[i] for i in
                                    range(len(normalKartVariables))) <= tickets.unk, "NKuncaps"
        prob += plp.lpSum(normalGliderRemainingLevelTickets[i] * normalGliderVariables[i] for i in
                                    range(len(normalGliderVariables))) <= tickets.lng, "NGlevels"
        prob += plp.lpSum(normalGliderRemainingUncapTickets[i] * normalGliderVariables[i] for i in
                                    range(len(normalGliderVariables))) <= tickets.ung, "NGuncaps"

        prob += plp.lpSum(superDriverRemainingLevelTickets[i] * superDriverVariables[i] for i in
                                    range(len(superDriverVariables))) <= tickets.lsd, "SDlevels"
        prob += plp.lpSum(superDriverRemainingUncapTickets[i] * superDriverVariables[i] for i in
                                    range(len(superDriverVariables))) <= tickets.usd, "SDuncaps"
        prob += plp.lpSum(superKartRemainingLevelTickets[i] * superKartVariables[i] for i in
                                    range(len(superKartVariables))) <= tickets.lsk, "SKlevels"
        prob += plp.lpSum(superKartRemainingUncapTickets[i] * superKartVariables[i] for i in
                                    range(len(superKartVariables))) <= tickets.usk, "SKuncaps"
        prob += plp.lpSum(superGliderRemainingLevelTickets[i] * superGliderVariables[i] for i in
                                    range(len(superGliderVariables))) <= tickets.lsg, "SGlevels"
        prob += plp.lpSum(superGliderRemainingUncapTickets[i] * superGliderVariables[i] for i in
                                    range(len(superGliderVariables))) <= tickets.usg, "SGuncaps"

        prob += plp.lpSum(highEndDriverRemainingLevelTickets[i] * highEndDriverVariables[i] for i in
                                    range(len(highEndDriverVariables))) <= tickets.lhd, "HDlevels"
        prob += plp.lpSum(highEndDriverRemainingUncapTickets[i] * highEndDriverVariables[i] for i in
                                    range(len(highEndDriverVariables))) <= tickets.uhd, "HDuncaps"
        prob += plp.lpSum(highEndKartRemainingLevelTickets[i] * highEndKartVariables[i] for i in
                                    range(len(highEndKartVariables))) <= tickets.lhk, "HKlevels"
        prob += plp.lpSum(highEndKartRemainingUncapTickets[i] * highEndKartVariables[i] for i in
                                    range(len(highEndKartVariables))) <= tickets.uhk, "HKuncaps"
        prob += plp.lpSum(highEndGliderRemainingLevelTickets[i] * highEndGliderVariables[i] for i in
                                    range(len(highEndGliderVariables))) <= tickets.lhg, "HGlevels"
        prob += plp.lpSum(highEndGliderRemainingUncapTickets[i] * highEndGliderVariables[i] for i in
                                    range(len(highEndGliderVariables))) <= tickets.uhg, "HGuncaps"
    else:
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

    if SCIP:
        # model.writeProblem("scip.lp")
        model.optimize()
        sol = model.getBestSol()
        # model.writeBestSol("tickets-ffb.sol")
    else:
        # prob.writeLP("pulp.lp")
        prob.solve()

    optimalCombinations = []
    for courseMap in combinationsToVariables:
        for c in courseMap:
            variable = courseMap[c]
            if SCIP:
                isSelected = (abs(model.getSolVal(sol, variable) - 1) < 0.0001)
            else:
                isSelected = (variable.varValue and (abs(variable.varValue - 1.0) < 0.0001))
            if isSelected:
                optimalCombinations.append([c[1].gameItem.id, c[1].level, c[1].uncaps, c[2].gameItem.id, c[2].level, c[2].uncaps, c[3].gameItem.id, c[3].level, c[3].uncaps])

    print("Done solving model!")
    return optimalCombinations
