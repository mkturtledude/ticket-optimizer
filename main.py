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

playerLevel = 167

upgrades, rows = util.optimize(inventory, courses, tickets, playerLevel)


print("Upgrades:")
for upgrade in upgrades:
    print(upgrade)

print("\nTable:")
for row in rows:
    print(row)

stop = timeit.default_timer()

print('Time: ', stop - start)