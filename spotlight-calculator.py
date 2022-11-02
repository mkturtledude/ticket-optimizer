import copy
import math


def comb(n, r):
    f = math.factorial
    return f(n) // f(r) // f(n - r)


baseWeights = [100, 50, 3]

originalPoolDrivers = [3, 16, 8]
originalPoolKarts = [6, 25, 10]
originalPoolGliders = [2, 17, 9]

toDraw = 6


def probabilityOfType(type, numberWanted, completePool, originalPool):
    # print("type: {}. numberWanted: {}".format(type, numberWanted))
    # print("completePool: {}".format(completePool))
    sumRemaining = sum(completePool)
    if sumRemaining + toDraw <= sum(originalPool):
        return 0
    if numberWanted > 0 and completePool[type] == 0:
        return 0
    weightByType = [w * i for w, i in zip(baseWeights, completePool)]
    totalWeight = sum(weightByType)
    probByType = [w / totalWeight for w in weightByType]
    # If we have only one item left to draw
    if sumRemaining + toDraw - 1 == sum(originalPool):
        if numberWanted == 1:
            return probByType[type]
        elif numberWanted == 0:
            return 1 - probByType[type]
        else:
            return 0
    # Else, there are at least 2 items left
    totalProbability = 0
    for t in range(len(baseWeights)):
        # print("for t={}".format(t))
        probOfSingle = probByType[t]
        if probOfSingle == 0:
            # print("probOfSingle is 0, skipping")
            continue
        newPool = copy.deepcopy(completePool)
        newPool[t] -= 1
        newWanted = copy.deepcopy(numberWanted)
        if t == type:
            if numberWanted == 0:
                # print("type is {} and numberWanted is 0, skipping".format(t, numberWanted))
                continue
            newWanted -= 1
        # print("Continuing with newWanted={} and newPool={}".format(newWanted, newPool))
        totalProbability += probabilityOfType(type, newWanted, newPool, originalPool) * probByType[t]
    return totalProbability


def probOfSpecificItemInDay(type, originalPool):
    complementProb = 0
    for i in range(toDraw + 1):
        probOfI = probabilityOfType(type, i, originalPool, originalPool)
        if probOfI == 0 or originalPool[type] - 1 < i:
            continue
        numCombinations = comb(originalPool[type], i)
        numCombinationsWithoutTargetItem = comb(originalPool[type] - 1, i)
        complementProb += numCombinationsWithoutTargetItem * probOfI / numCombinations
    return 1 - complementProb


def probOfSpecificItemInDays(type, originalPool, numberOfDays):
    dailyProb = probOfSpecificItemInDay(type, originalPool)
    return 1 - pow(1 - dailyProb, numberOfDays)


finalResults = []

for originalPool in [originalPoolDrivers, originalPoolKarts, originalPoolGliders]:
    # print("For following pool: {}".format(originalPool))
    for type in range(len(baseWeights)):
        odds = []
        # print("\tFor type {}:".format(type))
        # total = 0
        # for i in range(toDraw+1):
        #     p = probabilityOfType(type,i,originalPool, originalPool)
        #     # print("{}: {:.2f}".format(i, p*100))
        #     total += p
        # # print("total: {}\n".format(total))
        # print("\tType {}:".format(type))
        for days in range(1, 29):
            # print("{:.2f}".format(probOfSpecificItemInDays(type, originalPool, days) * 100))
            odds.append(probOfSpecificItemInDays(type, originalPool, days) * 100)
        # print("\tP(specific item in day): {:.2f}".format(probOfSpecificItemInDay(type, originalPool)*100))
        finalResults.append(odds)

for i in range(len(finalResults[0])):
    for column in finalResults:
        print("{:.1f}\t".format(column[i]), end="")
    print()