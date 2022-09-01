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
tickets.lnd = 10
tickets.lnk = 10
tickets.lng = 10
tickets.lsd = 10
tickets.lsk = 10
tickets.lsg = 10
tickets.lhd = 10
tickets.lhk = 10
tickets.lhg = 10
tickets.und = 10
tickets.unk = 10
tickets.ung = 10
tickets.usd = 10
tickets.usk = 10
tickets.usg = 10
tickets.uhd = 10
tickets.uhk = 10
tickets.uhg = 10

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

solver.printFinalOutput(solutionCombinations, inventory, courses)



stop = timeit.default_timer()

print('Time: ', stop - start)
print("Solver time: {}".format(solverTime))