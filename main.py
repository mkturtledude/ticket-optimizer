import pyscipopt as scip

import base
import reader
import calculator
import util
import copy
import solver
import timeit

start = timeit.default_timer()

courses, items = reader.readJson(base.COVERAGE_FILE)

reader.readActions(base.ACTIONS_FILE, courses)

with open(base.INVENTORY_FILE, encoding='utf-8-sig') as file:
    inventoryLines = file.read().splitlines()
inventory = reader.readInventory(inventoryLines, items)

tickets = base.TicketStash()
tickets.lnd = 50
tickets.lnk = 50
tickets.lng = 50
tickets.lsd = 50
tickets.lsk = 50
tickets.lsg = 50
tickets.lhd = 50
tickets.lhk = 50
tickets.lhg = 50
tickets.und = 50
tickets.unk = 50
tickets.ung = 50
tickets.usd = 50
tickets.usk = 50
tickets.usg = 50
tickets.uhd = 50
tickets.uhk = 50
tickets.uhg = 50

solverTime = 0

currentInventory = copy.deepcopy(inventory)
currentTickets = copy.deepcopy(tickets)
currentTickets.setKartsToZero()
currentTickets.setGlidersToZero()
originalInventoryIdToItem = util.createOriginalInventoryIdToItem(currentInventory)
totalScore, optWithCurrent = util.calculateOptWithCurrent(courses, currentInventory)
print("The total score without any upgrades is {}".format(totalScore))
expandedInventory = util.expandInventory(currentInventory, currentTickets)
combinationsOnCourses = util.createCombinationsOnCourses(courses, optWithCurrent, expandedInventory)
solverStart = timeit.default_timer()
solutionCombinations = solver.solveProblem(courses, combinationsOnCourses, originalInventoryIdToItem, currentTickets)
solverEnd = timeit.default_timer()
solverTime += (solverEnd - solverStart)

currentInventory = util.updateInventory(currentInventory, solutionCombinations)
currentTickets = copy.deepcopy(tickets)
currentTickets.setDriversToZero()
currentTickets.setGlidersToZero()
originalInventoryIdToItem = util.createOriginalInventoryIdToItem(currentInventory)
totalScore, optWithCurrent = util.calculateOptWithCurrent(courses, currentInventory)
print("The total score after driver upgrades is {}".format(totalScore))
expandedInventory = util.expandInventory(currentInventory, currentTickets)
combinationsOnCourses = util.createCombinationsOnCourses(courses, optWithCurrent, expandedInventory)
solverStart = timeit.default_timer()
solutionCombinations = solver.solveProblem(courses, combinationsOnCourses, originalInventoryIdToItem, currentTickets)
solverEnd = timeit.default_timer()
solverTime += (solverEnd - solverStart)

currentInventory = util.updateInventory(currentInventory, solutionCombinations)
currentTickets = copy.deepcopy(tickets)
currentTickets.setDriversToZero()
currentTickets.setKartsToZero()
originalInventoryIdToItem = util.createOriginalInventoryIdToItem(currentInventory)
totalScore, optWithCurrent = util.calculateOptWithCurrent(courses, currentInventory)
print("The total score after driver and kart upgrades is {}".format(totalScore))
expandedInventory = util.expandInventory(currentInventory, currentTickets)
combinationsOnCourses = util.createCombinationsOnCourses(courses, optWithCurrent, expandedInventory)

solverStart = timeit.default_timer()
solutionCombinations = solver.solveProblem(courses, combinationsOnCourses, originalInventoryIdToItem, currentTickets)
solverEnd = timeit.default_timer()
solverTime += (solverEnd - solverStart)

currentInventory = util.updateInventory(currentInventory, solutionCombinations)
totalScore, optWithCurrent = util.calculateOptWithCurrent(courses, currentInventory)
print("The total score after all upgrades is {}".format(totalScore))

upgrades, rows = solver.constructUpgradeTableStrings(solutionCombinations, inventory, courses)

print("Upgrades:")
for upgrade in upgrades:
    print(upgrade)

print("\nTable:")
for row in rows:
    print(row)

stop = timeit.default_timer()

print('Time: ', stop - start)
print("Solver time: {}".format(solverTime))