READ_SOLUTION = False

COVERAGE_FILE = "/home/marco/ticketOptimizer/data/BowserTour_alldata_multilang.json"
ACTIONS_FILE = "/home/marco/ticketOptimizer/data/actions.csv"
INVENTORY_FILE = "/home/marco/ticketOptimizer/data/inventory.csv"
# INVENTORY_FILE = "/home/marco/ticketOptimizer/data/ffb-inventory-fixed-drivers.csv"
# INVENTORY_FILE = "/home/marco/ticketOptimizer/data/elle-inventory.csv"
# INVENTORY_FILE = "/home/marco/ticketOptimizer/data/Justin_C_inventory.csv"
# INVENTORY_FILE = "/home/marco/ticketOptimizer/data/inventory.csv"
SOLUTION_FILE = "/home/marco/ticketOptimizer/tickets-elle.sol"
# SOLUTION_FILE = "/home/marco/ticketOptimizer/tickets-justin.sol"

# Justin
# PLAYER_LEVEL = 202
#
# ND_LEVEL_TIX = 16
# NK_LEVEL_TIX = 39
# NG_LEVEL_TIX = 77
# SD_LEVEL_TIX = 16
# SK_LEVEL_TIX = 15
# SG_LEVEL_TIX = 4
# HD_LEVEL_TIX = 28
# HK_LEVEL_TIX = 0
# HG_LEVEL_TIX = 0
#
# ND_UNCAP_TIX = 173
# NK_UNCAP_TIX = 138
# NG_UNCAP_TIX = 156
# SD_UNCAP_TIX = 48
# SK_UNCAP_TIX = 16
# SG_UNCAP_TIX = 8
# HD_UNCAP_TIX = 32
# HK_UNCAP_TIX = 0
# HG_UNCAP_TIX = 0
# FFB
# PLAYER_LEVEL = 216
#
# ND_LEVEL_TIX = 72
# NK_LEVEL_TIX = 77
# NG_LEVEL_TIX = 41
# SD_LEVEL_TIX = 33
# SK_LEVEL_TIX = 36
# SG_LEVEL_TIX = 38
# HD_LEVEL_TIX = 0
# HK_LEVEL_TIX = 45
# HG_LEVEL_TIX = 52
#
# ND_UNCAP_TIX = 173
# NK_UNCAP_TIX = 138
# NG_UNCAP_TIX = 156
# SD_UNCAP_TIX = 78
# SK_UNCAP_TIX = 51
# SG_UNCAP_TIX = 80
# HD_UNCAP_TIX = 0
# HK_UNCAP_TIX = 48
# HG_UNCAP_TIX = 55 # 49 + 6 from ranked# FFB

#Elle
PLAYER_LEVEL = 208

# ND_LEVEL_TIX = 0
# NK_LEVEL_TIX = 0
# NG_LEVEL_TIX = 64
# SD_LEVEL_TIX = 0
# SK_LEVEL_TIX = 0
# SG_LEVEL_TIX = 32
# HD_LEVEL_TIX = 0
# HK_LEVEL_TIX = 0
# HG_LEVEL_TIX = 16
#
# ND_UNCAP_TIX = 0
# NK_UNCAP_TIX = 0
# NG_UNCAP_TIX = 64
# SD_UNCAP_TIX = 0
# SK_UNCAP_TIX = 0
# SG_UNCAP_TIX = 32
# HD_UNCAP_TIX = 0
# HK_UNCAP_TIX = 0
# HG_UNCAP_TIX = 16

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

    def setDriversToZero(self):
        self.lnd = 0
        self.lsd = 0
        self.lhd = 0
        self.und = 0
        self.usd = 0
        self.uhd = 0

    def setKartsToZero(self):
        self.lnk = 0
        self.lsk = 0
        self.lhk = 0
        self.unk = 0
        self.usk = 0
        self.uhk = 0

    def setGlidersToZero(self):
        self.lng = 0
        self.lsg = 0
        self.lhg = 0
        self.ung = 0
        self.usg = 0
        self.uhg = 0

class CupItem:
    def __init__(self, name, promotionLevel):
        self.name = name
        self.topShelfAtLevel = promotionLevel

class GameItem:
    def __init__(self, name, id, type, rarity, skill, isMii):
        self.name = name
        self.id = id
        self.type = type
        self.rarity = rarity
        self.skill = skill
        self.isMii = isMii

class CourseActions:
    def __init__(self):
        self.normal = 0
        self.giantBanana = 0
        self.lucky7 = 0
        self.boomerangFlower = 0
        self.coinbox = 0
        self.itemBoxes = 0
        self.miniTurbos = 0
        self.jumpBoosts = 0
        self.dashPanels = 0
        self.glideTime = 0
        self.courseCoins = 0
        self.itemCoins = 0
        self.lanterns = 0

class TourCourse:
    def __init__(self, internalName, cupDriverIds, sortId):
        self.internalName = internalName
        self.englishName = ""
        self.cupDriverIds = cupDriverIds
        self.sortId = sortId # Within the cup
        self.topShelf = []
        self.middleShelf = []
        self.courseActions = CourseActions()

class InventoryItem:
    def __init__(self, gameItem, level, basePoints, uncaps, partialUncaps):
        self.gameItem = gameItem
        self.englishName = gameItem.name
        self.skill = gameItem.skill
        self.rarity = gameItem.rarity
        self.isMii = gameItem.isMii
        self.level = level
        self.basePoints = basePoints
        self.uncaps = uncaps
        self.partialUncaps = partialUncaps

    def print(self):
        print("{}:".format(self.englishName))
        print("\tSkill: {}".format(self.skill))
        print("\tRarity: {}".format(self.rarity))
        print("\tIs Mii: {}".format(self.isMii))
        print("\tLevel: {}".format(self.level))
        print("\tBase Points: {}".format(self.basePoints))
        print("\tUncaps: {}".format(self.uncaps))
        print("\tPartial Uncaps: {}".format(self.partialUncaps))


class Inventory:
    def __init__(self):
        self.drivers = set()
        self.karts = set()
        self.gliders = set()
        self.numberOfMiis = 0

    def print(self):
        for d in self.drivers:
            d.print()
        for d in self.karts:
            d.print()
        for d in self.gliders:
            d.print()


def calculateBasePoints(type, rarity, uncaps, isMii, numberOfMiis):
    result = 0
    if isMii:
        result += (numberOfMiis - 1) * 10
    if type == "D":
        if rarity == "HE":
            if uncaps == 0:
                result += 800
            elif uncaps == 1:
                result += 980
            elif uncaps == 2:
                result += 1190
            else:
                assert(uncaps == 3)
                result += 1400
        elif rarity == "S":
            if uncaps == 0:
                result += 675
            elif uncaps == 1:
                result += 765
            elif uncaps == 2:
                result += 870
            else:
                assert(uncaps == 3)
                result += 975
        elif rarity == "N":
            if uncaps == 0:
                result += 600
            elif uncaps == 1:
                result += 648
            elif uncaps == 2:
                result += 704
            else:
                assert(uncaps == 3)
                result += 760
    else:
        assert(type in ["K", "G"])
        assert(not isMii)
        if rarity == "HE":
            if uncaps == 0:
                result += 400
            elif uncaps == 1:
                result += 490
            elif uncaps == 2:
                result += 595
            else:
                assert(uncaps == 3)
                result += 700
        elif rarity == "S":
            if uncaps == 0:
                result += 330
            elif uncaps == 1:
                result += 366
            elif uncaps == 2:
                result += 408
            else:
                assert(uncaps == 3)
                result += 450
        elif rarity == "N":
            if uncaps == 0:
                result += 300
            elif uncaps == 1:
                result += 324
            elif uncaps == 2:
                result += 352
            else:
                assert(uncaps == 3)
                result += 380
    return result

def calculateLevelTicketsUsed(item, level):
    rarity = item.rarity
    if rarity == "HE":
        if level == 1:
            return 0
        elif level == 2:
            return 1
        elif level == 3:
            return 2
        elif level == 4:
            return 4
        elif level == 5:
            return 6
        elif level == 6:
            return 9
        elif level == 7:
            return 14
        else:
            assert(level == 8)
            return 22
    elif rarity == "S":
        if level == 1:
            return 0
        elif level == 2:
            return 1
        elif level == 3:
            return 3
        elif level == 4:
            return 6
        elif level == 5:
            return 10
        elif level == 6:
            return 15
        elif level == 7:
            return 23
        else:
            assert(level == 8)
            return 39
    else:
        assert(rarity == "N")
        if level == 1:
            return 0
        elif level == 2:
            return 2
        elif level == 3:
            return 7
        elif level == 4:
            return 15
        elif level == 5:
            return 26
        elif level == 6:
            return 40
        elif level == 7:
            return 60
        else:
            assert(level == 8)
            return 100

def calculateLevelTicketsNeeded(oldItem, targetLevel):
    assert(oldItem.level <= targetLevel)
    if oldItem.level == targetLevel:
        return 0
    result = calculateLevelTicketsUsed(oldItem, targetLevel) - calculateLevelTicketsUsed(oldItem, oldItem.level)
    if oldItem.englishName == "Kamek":
        result -= 4
    elif oldItem.englishName == "Meowser":
        result -= 3
    elif oldItem.englishName == "Gold Koopa (Freerunning)":
        result -= 4
    elif oldItem.englishName == "Pink Shy Guy (Ninja)":
        result -= 2
    elif oldItem.englishName == "Red Offroader":
        result -= 2
    return result

def calculateCapTicketsNeeded(oldItem, targetUncaps):
    assert(oldItem.uncaps <= targetUncaps)
    ou = oldItem.uncaps
    uu = targetUncaps
    if ou == uu:
        return 0
    if ou == 0:
        if uu == 1:
            return 1
        elif uu == 2:
            return 6
        else:
            assert(uu == 3)
            return 16
    elif ou == 1:
        if uu == 2:
            return 5
        else:
            assert(uu == 3)
            return 15
    else:
        assert(ou == 2 and uu == 3)
        return 10