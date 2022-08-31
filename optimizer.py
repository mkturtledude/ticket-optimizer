import base
import reader
import calculator
import util
import copy
import os

class Tickets:
    def __init__(self):
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


def optimize(inventoryLines, tickets, playerLevel):
    coverageFile = os.getcwd() + "/data/alldata.json"
    actionsFile = os.getcwd() + "/data/actions.csv"
    courses, items = reader.readJson(coverageFile)
    reader.readActions(base.ACTIONS_FILE, courses)
    inventory = reader.readInventory(inventoryLines, items)
    result = ""
    result += "The inventory has " + str(len(inventory.drivers)) + " drivers"
    return result