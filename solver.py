import base, calculator
import copy
import unidecode
import time


OR_TOOLS = False

if OR_TOOLS:
    from ortools.linear_solver import pywraplp
    from ortools.init import pywrapinit
else:
    import gurobipy as gp
    from gurobipy import GRB


'''
combinations: list<set<tuple<score, item, item, item>>>
    The list contains as many sets as there are courses in the tour (usually 45), in that order.
    Each tuple represents a "combination". It contains, in that order, a score, a driver, a kart and a glider. 
    The score is the one that corresponds to those loadouts on the given course. The score is a number. 
    The items need to contain game ID, level and number of uncaps. See how the variable "combination" is used, and adapt
    to your convenience.
originalInventoryIdToItem: A dict that maps the item's game ID to the item as it is in the inventory. 
    The distinction "as it is in the inventory" is important because the items in combinationsOnCourses represent
    hypothetical upgrades. The data that we need from this inventory item is: Rarity, Type (D/K/G), possibility to 
    calculate the number of tickets needed to any given level (taking into account partial upgrades) or to any given 
    number of uncaps. All this data could in theory be included in the items of the previous parameter, but I did it 
    this way to avoid duplication.
tickets: An object of the following class:
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
    In each of the members: The first letter is the ticket type (Level or Uncaps), the second is the rarity (n/s/h) and
    the third is the item type (d/k/g)
'''
def solve(combinations, originalInventoryIdToItem, tickets):
    ## Create model
    print("Creating and solving model...")
    if OR_TOOLS:
        print("Using OR-Tools")
        solver = pywraplp.Solver.CreateSolver('SCIP')
    else:
        print("Using Gurobi")
        m = gp.Model("ScoreMaximization")



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
                if OR_TOOLS:
                    v = solver.BoolVar("y_%s_%s_%s_%s_%s_%s_%s_%s_%s_%s" % (i, did, dl, du, kid, kl, ku, gid, gl, gu))
                    # v = model.addVar(vtype="B",
                    #                  name="y_%s_%s_%s_%s_%s_%s_%s_%s_%s_%s" % (i, did, dl, du, kid, kl, ku, gid, gl, gu))
                else:
                    v = m.addVar(vtype=GRB.BINARY,
                                     name="y_%s_%s_%s_%s_%s_%s_%s_%s_%s_%s" % (i, did, dl, du, kid, kl, ku, gid, gl, gu))
                    # v = plp.LpVariable("y_%s_%s_%s_%s_%s_%s_%s_%s_%s_%s" % (i, did, dl, du, kid, kl, ku, gid, gl, gu), 0, 1, plp.LpInteger)
                # variablesToCombinations[v] = c
                combinationsToVariables[-1][combination] = v
            allCombinationScores.append(combination[0])
            allCombinationVariables.append(v)
            combinationVariablesByCourse[-1].append(v)
            # print("\t[{}/{}/{}] + [{}/{}/{}] + [{}/{}/{}] -> {}".format(c[1].englishName, c[1].level, c[1].basePoints, c[2].englishName, c[2].level, c[2].basePoints, c[3].englishName, c[3].level, c[3].basePoints, c[0]))

    if OR_TOOLS:
        solver.Maximize(solver.Sum(allCombinationScores[i] * allCombinationVariables[i] for i in range(len(allCombinationVariables))))
        # model.setObjective(scip.quicksum(
        #     allCombinationScores[i] * allCombinationVariables[i] for i in range(len(allCombinationVariables))), "maximize")
    else:
        m.setObjective(gp.quicksum(allCombinationScores[i] * allCombinationVariables[i] for i in range(len(allCombinationVariables))), GRB.MAXIMIZE)
        # prob += plp.lpSum(allCombinationScores[i] * allCombinationVariables[i] for i in range(len(allCombinationVariables)))

    # print("Adding constraints OneCombPerCourse")
    for courseCombinations in combinationVariablesByCourse:
        if OR_TOOLS:
            solver.Add(solver.Sum(v for v in courseCombinations) == 1, name="OneCombPerCourse")
            # model.addCons(scip.quicksum(v for v in courseCombinations) == 1, "OneCombPerCourse")
        else:
            m.addConstr(gp.quicksum(v for v in courseCombinations) == 1, "OneCombPerCourse")
            # prob += plp.lpSum(v for v in courseCombinations) == 1

    itemsToVariables = dict()
    # print("Adding x variables and constraints CombOnlyIf")
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
                if OR_TOOLS:
                    dv = solver.BoolVar("x_%s_%s_%s" % (did, dl, du))
                    # dv = model.addVar(vtype="B", name="x_%s_%s_%s" % (did, dl, du))
                else:
                    dv = m.addVar(vtype=GRB.BINARY, name="x_%s_%s_%s" % (did, dl, du))
                    # dv = plp.LpVariable("x_%s_%s_%s" % (did, dl, du), 0, 1, plp.LpInteger)
                itemsToVariables[d] = dv
            if k in itemsToVariables:
                kv = itemsToVariables[k]
            else:
                if OR_TOOLS:
                    kv = solver.BoolVar("x_%s_%s_%s" % (kid, kl, ku))
                    # kv = model.addVar(vtype="B", name="x_%s_%s_%s" % (kid, kl, ku))
                else:
                    kv = m.addVar(vtype=GRB.BINARY, name="x_%s_%s_%s" % (kid, kl, ku))
                    # kv = plp.LpVariable("x_%s_%s_%s" % (kid, kl, ku), 0, 1, plp.LpInteger)
                itemsToVariables[k] = kv
            if g in itemsToVariables:
                gv = itemsToVariables[g]
            else:
                if OR_TOOLS:
                    gv = solver.BoolVar("x_%s_%s_%s" % (gid, gl, gu))
                    # gv = model.addVar(vtype="B", name="x_%s_%s_%s" % (gid, gl, gu))
                else:
                    gv = m.addVar(vtype=GRB.BINARY, name="x_%s_%s_%s" % (gid, gl, gu))
                    # gv = plp.LpVariable("x_%s_%s_%s" % (gid, gl, gu), 0, 1, plp.LpInteger)
                itemsToVariables[g] = gv
            if OR_TOOLS:
                solver.Add(combinationVariable <= dv, name="CombOnlyIfDriver")
                solver.Add(combinationVariable <= kv, name="CombOnlyIfKart")
                solver.Add(combinationVariable <= gv, name="CombOnlyIfGlider")
                # model.addCons(combinationVariable <= dv, "CombOnlyIfDriver")
                # model.addCons(combinationVariable <= kv, "CombOnlyIfKart")
                # model.addCons(combinationVariable <= gv, "CombOnlyIfGlider")
            else:
                m.addConstr(combinationVariable <= dv, "CombOnlyIfDriver")
                m.addConstr(combinationVariable <= kv, "CombOnlyIfKart")
                m.addConstr(combinationVariable <= gv, "CombOnlyIfGlider")
                # prob += combinationVariable <= dv
                # prob += combinationVariable <= kv
                # prob += combinationVariable <= gv

    itemIdToVariables = dict()
    for item in itemsToVariables:
        id = item[0]
        if not id in itemIdToVariables:
            itemIdToVariables[id] = []
        itemIdToVariables[id].append(itemsToVariables[item])

    # print("Adding constraints OneStatePerItem")
    for id in itemIdToVariables:
        if OR_TOOLS:
            solver.Add(solver.Sum(v for v in itemIdToVariables[id]) <= 1, name="OneStatePerItem")
            # model.addCons(scip.quicksum(v for v in itemIdToVariables[id]) <= 1, "OneStatePerItem")
        else:
            m.addConstr(gp.quicksum(v for v in itemIdToVariables[id]) <= 1, "OneStatePerItem")
            # prob += plp.lpSum(v for v in itemIdToVariables[id]) <= 1

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
    if not OR_TOOLS:
        m.addConstr(gp.quicksum(normalDriverRemainingLevelTickets[i] * normalDriverVariables[i] for i in
                                    range(len(normalDriverVariables))) <= tickets.lnd, "NDlevels")
        m.addConstr(gp.quicksum(normalDriverRemainingUncapTickets[i] * normalDriverVariables[i] for i in
                                    range(len(normalDriverVariables))) <= tickets.und, "NDuncaps")
        m.addConstr(gp.quicksum(normalKartRemainingLevelTickets[i] * normalKartVariables[i] for i in
                                    range(len(normalKartVariables))) <= tickets.lnk, "NKlevels")
        m.addConstr(gp.quicksum(normalKartRemainingUncapTickets[i] * normalKartVariables[i] for i in
                                    range(len(normalKartVariables))) <= tickets.unk, "NKuncaps")
        m.addConstr(gp.quicksum(normalGliderRemainingLevelTickets[i] * normalGliderVariables[i] for i in
                                    range(len(normalGliderVariables))) <= tickets.lng, "NGlevels")
        m.addConstr(gp.quicksum(normalGliderRemainingUncapTickets[i] * normalGliderVariables[i] for i in
                                    range(len(normalGliderVariables))) <= tickets.ung, "NGuncaps")

        m.addConstr(gp.quicksum(superDriverRemainingLevelTickets[i] * superDriverVariables[i] for i in
                                    range(len(superDriverVariables))) <= tickets.lsd, "SDlevels")
        m.addConstr(gp.quicksum(superDriverRemainingUncapTickets[i] * superDriverVariables[i] for i in
                                    range(len(superDriverVariables))) <= tickets.usd, "SDuncaps")
        m.addConstr(gp.quicksum(superKartRemainingLevelTickets[i] * superKartVariables[i] for i in
                                    range(len(superKartVariables))) <= tickets.lsk, "SKlevels")
        m.addConstr(gp.quicksum(superKartRemainingUncapTickets[i] * superKartVariables[i] for i in
                                    range(len(superKartVariables))) <= tickets.usk, "SKuncaps")
        m.addConstr(gp.quicksum(superGliderRemainingLevelTickets[i] * superGliderVariables[i] for i in
                                    range(len(superGliderVariables))) <= tickets.lsg, "SGlevels")
        m.addConstr(gp.quicksum(superGliderRemainingUncapTickets[i] * superGliderVariables[i] for i in
                                    range(len(superGliderVariables))) <= tickets.usg, "SGuncaps")

        m.addConstr(gp.quicksum(highEndDriverRemainingLevelTickets[i] * highEndDriverVariables[i] for i in
                                    range(len(highEndDriverVariables))) <= tickets.lhd, "HDlevels")
        m.addConstr(gp.quicksum(highEndDriverRemainingUncapTickets[i] * highEndDriverVariables[i] for i in
                                    range(len(highEndDriverVariables))) <= tickets.uhd, "HDuncaps")
        m.addConstr(gp.quicksum(highEndKartRemainingLevelTickets[i] * highEndKartVariables[i] for i in
                                    range(len(highEndKartVariables))) <= tickets.lhk, "HKlevels")
        m.addConstr(gp.quicksum(highEndKartRemainingUncapTickets[i] * highEndKartVariables[i] for i in
                                    range(len(highEndKartVariables))) <= tickets.uhk, "HKuncaps")
        m.addConstr(gp.quicksum(highEndGliderRemainingLevelTickets[i] * highEndGliderVariables[i] for i in
                                    range(len(highEndGliderVariables))) <= tickets.lhg, "HGlevels")
        m.addConstr(gp.quicksum(highEndGliderRemainingUncapTickets[i] * highEndGliderVariables[i] for i in
                                    range(len(highEndGliderVariables))) <= tickets.uhg, "HGuncaps")

        # prob += plp.lpSum(normalDriverRemainingLevelTickets[i] * normalDriverVariables[i] for i in
        #                             range(len(normalDriverVariables))) <= tickets.lnd, "NDlevels"
        # prob += plp.lpSum(normalDriverRemainingUncapTickets[i] * normalDriverVariables[i] for i in
        #                             range(len(normalDriverVariables))) <= tickets.und, "NDuncaps"
        # prob += plp.lpSum(normalKartRemainingLevelTickets[i] * normalKartVariables[i] for i in
        #                             range(len(normalKartVariables))) <= tickets.lnk, "NKlevels"
        # prob += plp.lpSum(normalKartRemainingUncapTickets[i] * normalKartVariables[i] for i in
        #                             range(len(normalKartVariables))) <= tickets.unk, "NKuncaps"
        # prob += plp.lpSum(normalGliderRemainingLevelTickets[i] * normalGliderVariables[i] for i in
        #                             range(len(normalGliderVariables))) <= tickets.lng, "NGlevels"
        # prob += plp.lpSum(normalGliderRemainingUncapTickets[i] * normalGliderVariables[i] for i in
        #                             range(len(normalGliderVariables))) <= tickets.ung, "NGuncaps"
        #
        # prob += plp.lpSum(superDriverRemainingLevelTickets[i] * superDriverVariables[i] for i in
        #                             range(len(superDriverVariables))) <= tickets.lsd, "SDlevels"
        # prob += plp.lpSum(superDriverRemainingUncapTickets[i] * superDriverVariables[i] for i in
        #                             range(len(superDriverVariables))) <= tickets.usd, "SDuncaps"
        # prob += plp.lpSum(superKartRemainingLevelTickets[i] * superKartVariables[i] for i in
        #                             range(len(superKartVariables))) <= tickets.lsk, "SKlevels"
        # prob += plp.lpSum(superKartRemainingUncapTickets[i] * superKartVariables[i] for i in
        #                             range(len(superKartVariables))) <= tickets.usk, "SKuncaps"
        # prob += plp.lpSum(superGliderRemainingLevelTickets[i] * superGliderVariables[i] for i in
        #                             range(len(superGliderVariables))) <= tickets.lsg, "SGlevels"
        # prob += plp.lpSum(superGliderRemainingUncapTickets[i] * superGliderVariables[i] for i in
        #                             range(len(superGliderVariables))) <= tickets.usg, "SGuncaps"
        #
        # prob += plp.lpSum(highEndDriverRemainingLevelTickets[i] * highEndDriverVariables[i] for i in
        #                             range(len(highEndDriverVariables))) <= tickets.lhd, "HDlevels"
        # prob += plp.lpSum(highEndDriverRemainingUncapTickets[i] * highEndDriverVariables[i] for i in
        #                             range(len(highEndDriverVariables))) <= tickets.uhd, "HDuncaps"
        # prob += plp.lpSum(highEndKartRemainingLevelTickets[i] * highEndKartVariables[i] for i in
        #                             range(len(highEndKartVariables))) <= tickets.lhk, "HKlevels"
        # prob += plp.lpSum(highEndKartRemainingUncapTickets[i] * highEndKartVariables[i] for i in
        #                             range(len(highEndKartVariables))) <= tickets.uhk, "HKuncaps"
        # prob += plp.lpSum(highEndGliderRemainingLevelTickets[i] * highEndGliderVariables[i] for i in
        #                             range(len(highEndGliderVariables))) <= tickets.lhg, "HGlevels"
        # prob += plp.lpSum(highEndGliderRemainingUncapTickets[i] * highEndGliderVariables[i] for i in
        #                             range(len(highEndGliderVariables))) <= tickets.uhg, "HGuncaps"
    else:
        solver.Add(solver.Sum(normalDriverRemainingLevelTickets[i] * normalDriverVariables[i] for i in
                                    range(len(normalDriverVariables))) <= tickets.lnd, name="NDlevels")
        solver.Add(solver.Sum(normalDriverRemainingUncapTickets[i] * normalDriverVariables[i] for i in
                                    range(len(normalDriverVariables))) <= tickets.und, name="NDuncaps")
        solver.Add(solver.Sum(normalKartRemainingLevelTickets[i] * normalKartVariables[i] for i in
                                    range(len(normalKartVariables))) <= tickets.lnk, name="NKlevels")
        solver.Add(solver.Sum(normalKartRemainingUncapTickets[i] * normalKartVariables[i] for i in
                                    range(len(normalKartVariables))) <= tickets.unk, name="NKuncaps")
        solver.Add(solver.Sum(normalGliderRemainingLevelTickets[i] * normalGliderVariables[i] for i in
                                    range(len(normalGliderVariables))) <= tickets.lng, name="NGlevels")
        solver.Add(solver.Sum(normalGliderRemainingUncapTickets[i] * normalGliderVariables[i] for i in
                                    range(len(normalGliderVariables))) <= tickets.ung, name="NGuncaps")

        solver.Add(solver.Sum(superDriverRemainingLevelTickets[i] * superDriverVariables[i] for i in
                                    range(len(superDriverVariables))) <= tickets.lsd, name="SDlevels")
        solver.Add(solver.Sum(superDriverRemainingUncapTickets[i] * superDriverVariables[i] for i in
                                    range(len(superDriverVariables))) <= tickets.usd, name="SDuncaps")
        solver.Add(solver.Sum(superKartRemainingLevelTickets[i] * superKartVariables[i] for i in
                                    range(len(superKartVariables))) <= tickets.lsk, name="SKlevels")
        solver.Add(solver.Sum(superKartRemainingUncapTickets[i] * superKartVariables[i] for i in
                                    range(len(superKartVariables))) <= tickets.usk, name="SKuncaps")
        solver.Add(solver.Sum(superGliderRemainingLevelTickets[i] * superGliderVariables[i] for i in
                                    range(len(superGliderVariables))) <= tickets.lsg, name="SGlevels")
        solver.Add(solver.Sum(superGliderRemainingUncapTickets[i] * superGliderVariables[i] for i in
                                    range(len(superGliderVariables))) <= tickets.usg, name="SGuncaps")

        solver.Add(solver.Sum(highEndDriverRemainingLevelTickets[i] * highEndDriverVariables[i] for i in
                                    range(len(highEndDriverVariables))) <= tickets.lhd, name="HDlevels")
        solver.Add(solver.Sum(highEndDriverRemainingUncapTickets[i] * highEndDriverVariables[i] for i in
                                    range(len(highEndDriverVariables))) <= tickets.uhd, name="HDuncaps")
        solver.Add(solver.Sum(highEndKartRemainingLevelTickets[i] * highEndKartVariables[i] for i in
                                    range(len(highEndKartVariables))) <= tickets.lhk, name="HKlevels")
        solver.Add(solver.Sum(highEndKartRemainingUncapTickets[i] * highEndKartVariables[i] for i in
                                    range(len(highEndKartVariables))) <= tickets.uhk, name="HKuncaps")
        solver.Add(solver.Sum(highEndGliderRemainingLevelTickets[i] * highEndGliderVariables[i] for i in
                                    range(len(highEndGliderVariables))) <= tickets.lhg, name="HGlevels")
        solver.Add(solver.Sum(highEndGliderRemainingUncapTickets[i] * highEndGliderVariables[i] for i in
                                    range(len(highEndGliderVariables))) <= tickets.uhg, name="HGuncaps")

        #
        # model.addCons(scip.quicksum(normalDriverRemainingLevelTickets[i] * normalDriverVariables[i] for i in
        #                             range(len(normalDriverVariables))) <= tickets.lnd, "NDlevels")
        # model.addCons(scip.quicksum(normalDriverRemainingUncapTickets[i] * normalDriverVariables[i] for i in
        #                             range(len(normalDriverVariables))) <= tickets.und, "NDuncaps")
        # model.addCons(scip.quicksum(normalKartRemainingLevelTickets[i] * normalKartVariables[i] for i in
        #                             range(len(normalKartVariables))) <= tickets.lnk, "NKlevels")
        # model.addCons(scip.quicksum(normalKartRemainingUncapTickets[i] * normalKartVariables[i] for i in
        #                             range(len(normalKartVariables))) <= tickets.unk, "NKuncaps")
        # model.addCons(scip.quicksum(normalGliderRemainingLevelTickets[i] * normalGliderVariables[i] for i in
        #                             range(len(normalGliderVariables))) <= tickets.lng, "NGlevels")
        # model.addCons(scip.quicksum(normalGliderRemainingUncapTickets[i] * normalGliderVariables[i] for i in
        #                             range(len(normalGliderVariables))) <= tickets.ung, "NGuncaps")
        #
        # model.addCons(scip.quicksum(superDriverRemainingLevelTickets[i] * superDriverVariables[i] for i in
        #                             range(len(superDriverVariables))) <= tickets.lsd, "SDlevels")
        # model.addCons(scip.quicksum(superDriverRemainingUncapTickets[i] * superDriverVariables[i] for i in
        #                             range(len(superDriverVariables))) <= tickets.usd, "SDuncaps")
        # model.addCons(scip.quicksum(superKartRemainingLevelTickets[i] * superKartVariables[i] for i in
        #                             range(len(superKartVariables))) <= tickets.lsk, "SKlevels")
        # model.addCons(scip.quicksum(superKartRemainingUncapTickets[i] * superKartVariables[i] for i in
        #                             range(len(superKartVariables))) <= tickets.usk, "SKuncaps")
        # model.addCons(scip.quicksum(superGliderRemainingLevelTickets[i] * superGliderVariables[i] for i in
        #                             range(len(superGliderVariables))) <= tickets.lsg, "SGlevels")
        # model.addCons(scip.quicksum(superGliderRemainingUncapTickets[i] * superGliderVariables[i] for i in
        #                             range(len(superGliderVariables))) <= tickets.usg, "SGuncaps")
        #
        # model.addCons(scip.quicksum(highEndDriverRemainingLevelTickets[i] * highEndDriverVariables[i] for i in
        #                             range(len(highEndDriverVariables))) <= tickets.lhd, "HDlevels")
        # model.addCons(scip.quicksum(highEndDriverRemainingUncapTickets[i] * highEndDriverVariables[i] for i in
        #                             range(len(highEndDriverVariables))) <= tickets.uhd, "HDuncaps")
        # model.addCons(scip.quicksum(highEndKartRemainingLevelTickets[i] * highEndKartVariables[i] for i in
        #                             range(len(highEndKartVariables))) <= tickets.lhk, "HKlevels")
        # model.addCons(scip.quicksum(highEndKartRemainingUncapTickets[i] * highEndKartVariables[i] for i in
        #                             range(len(highEndKartVariables))) <= tickets.uhk, "HKuncaps")
        # model.addCons(scip.quicksum(highEndGliderRemainingLevelTickets[i] * highEndGliderVariables[i] for i in
        #                             range(len(highEndGliderVariables))) <= tickets.lhg, "HGlevels")
        # model.addCons(scip.quicksum(highEndGliderRemainingUncapTickets[i] * highEndGliderVariables[i] for i in
        #                             range(len(highEndGliderVariables))) <= tickets.uhg, "HGuncaps")
    # if OR_TOOLS:
    #     model.writeProblem("scip.lp")
    # else:
    #     prob.writeLP("pulp.lp")
    #     prob.solve()
    #     for v in prob.variables():
    #         if v.varValue and (abs(v.varValue - 1.0) < 0.001):
    #             print(v.name, "=", v.varValue)
    # model.hideOutput()
    if OR_TOOLS:
        lp_str = solver.ExportModelAsLpFormat(False)
        with open('my_model.lp', 'w') as f:
            f.write(lp_str)
        status = solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            print('Solution:')
            print('Objective value =', solver.Objective().Value())
        else:
            print('The problem does not have an optimal solution.')

        # model.optimize()
        # sol = model.getBestSol()
        #model.writeProblem("top100.lp")
    else:
        m.Params.MIPGap = 1e-6
        m.optimize()
        # fileName = str(time.time()) + ".lp"
        # print("Saving problem to {}".format(fileName))
        # m.write(fileName)

        # prob.writeLP("pulp.lp")
        # input("Press enter to continue")
        # prob.solve()

    # model.writeBestSol("tickets-ffb.sol")
    optimalCombinations = []
    for courseMap in combinationsToVariables:
        for c in courseMap:
            variable = courseMap[c]
            if OR_TOOLS:
                isSelected = (abs(variable.solution_value() - 1) < 0.0001)
                # isSelected = (abs(model.getSolVal(sol, variable) - 1) < 0.0001)
            else:
                isSelected = (abs(variable.X - 1) < 0.0001)
                # isSelected = (variable.varValue and (abs(variable.varValue - 1.0) < 0.0001))
            if isSelected:
                optimalCombinations.append([c[1].gameItem.id, c[1].level, c[1].uncaps, c[2].gameItem.id, c[2].level, c[2].uncaps, c[3].gameItem.id, c[3].level, c[3].uncaps])

    print("Done solving model!")
    return optimalCombinations


def solveProblem(courses, combinationsOnCourses, originalInventoryIdToItem, tickets):
    combinations = []
    for i in range(len(courses)):
        course = courses[i]
        combinations.append(combinationsOnCourses[course])
    return solve(combinations, originalInventoryIdToItem, tickets)


def constructUpgradeTableStrings(solutionCombinations, inventory, courses):
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
                        ltn = base.calculateLevelTicketsNeeded(d, dl)
                        utn = base.calculateCapTicketsNeeded(d,du)
                        color = base.rarityToColor(d.gameItem.rarity)
                        usage = 0
                        for c in solutionCombinations:
                            if c[0] == did:
                                usage += 1
                        driverUpgrades.append([d.englishName, d.level, d.uncaps, dl, du, ltn, utn, usage, color])
        for k in inventory.karts:
            if k.gameItem.id == kid:
                newCombination.append(copy.deepcopy(k))
                if k.level != kl or k.uncaps != ku:
                    newCombination[-1].level = kl
                    newCombination[-1].uncaps = ku
                    newCombination[-1].basePoints = base.calculateBasePoints("K", k.gameItem.rarity, ku, False,
                                                                             inventory.numberOfMiis)
                    if kid not in processedIds:
                        ltn = base.calculateLevelTicketsNeeded(k, kl)
                        utn = base.calculateCapTicketsNeeded(k,ku)
                        color = base.rarityToColor(k.gameItem.rarity)
                        usage = 0
                        for c in solutionCombinations:
                            if c[3] == kid:
                                usage += 1
                        kartUpgrades.append([k.englishName, k.level, k.uncaps, kl, ku, ltn, utn, usage, color])
        for g in inventory.gliders:
            if g.gameItem.id == gid:
                newCombination.append(copy.deepcopy(g))
                if g.level != gl or g.uncaps != gu:
                    newCombination[-1].level = gl
                    newCombination[-1].uncaps = gu
                    newCombination[-1].basePoints = base.calculateBasePoints("G", g.gameItem.rarity, gu, False,
                                                                             inventory.numberOfMiis)
                    if gid not in processedIds:
                        ltn = base.calculateLevelTicketsNeeded(g, gl)
                        utn = base.calculateCapTicketsNeeded(g,gu)
                        color = base.rarityToColor(g.gameItem.rarity)
                        usage = 0
                        for c in solutionCombinations:
                            if c[6] == gid:
                                usage += 1
                        gliderUpgrades.append([g.englishName, g.level, g.uncaps, gl, gu, ltn, utn, usage, color])
        processedIds.add(did)
        processedIds.add(kid)
        processedIds.add(gid)
        finalCombinations.append(newCombination)

    upgradeStrings = []

    for l in [driverUpgrades, kartUpgrades, gliderUpgrades]:
        for item in l:
            upgradeStrings.append([item[0], str(item[1]) + "/" + str(item[2]), str(item[3]) + "/" + str(item[4]), str(item[5]), str(item[6]), str(item[7]), str(item[8])])

    tableRows = []
    for i in range(len(finalCombinations)):
        [d, k, g] = finalCombinations[i]
        course = courses[i]
        tableRows.append([unidecode.unidecode(d.englishName), calculator.getShelf(course, d),
                                                                      d.level, d.basePoints, unidecode.unidecode(k.englishName),
                                                                      calculator.getShelf(course, k), k.level,
                                                                      k.basePoints, unidecode.unidecode(g.englishName),
                                                                      calculator.getShelf(course, g), g.level,
                                                                      g.basePoints])
    return upgradeStrings, tableRows
