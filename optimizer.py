import base
import reader
import calculator
import util
import copy
import os


def optimize(workDir, inventoryLines, tickets, playerLevel):
    coverageFile = os.path.join(workDir, "data", "alldata.json")
    actionsFile = os.path.join(workDir, "data", "actions.csv")
    courses, items = reader.readJson(coverageFile)
    reader.readActions(actionsFile, courses)
    inventory = reader.readInventory(inventoryLines, items)
    result = ""
    result += "The inventory has " + str(len(inventory.drivers)) + " drivers"
    return result