READ_SOLUTION = False

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
        self.type = ""
        self.cupDriverIds = cupDriverIds
        self.sortId = sortId # Within the cup
        self.wellFought = False
        self.topShelf = []
        self.middleShelf = []
        self.courseActions = CourseActions()

class InventoryItem:
    def __init__(self, gameItem, level, basePoints, uncaps, partialLevels, levelCap, uncapCap):
        self.gameItem = gameItem
        self.englishName = gameItem.name
        self.skill = gameItem.skill
        self.rarity = gameItem.rarity
        self.isMii = gameItem.isMii
        self.level = level
        self.basePoints = basePoints
        self.uncaps = uncaps
        self.partialLevels = partialLevels
        self.levelCap = levelCap
        self.uncapCap = uncapCap

    def print(self):
        print("{}:".format(self.englishName))
        print("\tSkill: {}".format(self.skill))
        print("\tRarity: {}".format(self.rarity))
        print("\tIs Mii: {}".format(self.isMii))
        print("\tLevel: {}".format(self.level))
        print("\tBase Points: {}".format(self.basePoints))
        print("\tUncaps: {}".format(self.uncaps))
        print("\tPartial Levels: {}".format(self.partialLevels))
        print("\tLevel cap: {}".format(self.levelCap))
        print("\tUncap cap: {}".format(self.uncapCap))


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


def rarityToColor(rarity):
    if rarity == "HE":
        return "#FDE3FC"
    elif rarity == "S":
        return "#fbf4d0"
    else:
        return "#f6f6f6"

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
            elif uncaps == 3:
                result += 1430
            else:
                assert(uncaps == 4)
                result += 1610
        elif rarity == "S":
            if uncaps == 0:
                result += 675
            elif uncaps == 1:
                result += 765
            elif uncaps == 2:
                result += 870
            elif uncaps == 3:
                result += 990
            else:
                assert(uncaps == 4)
                result += 1080
        elif rarity == "N":
            if uncaps == 0:
                result += 600
            elif uncaps == 1:
                result += 648
            elif uncaps == 2:
                result += 704
            elif uncaps == 3:
                result += 768
            else:
                assert(uncaps == 4)
                result += 816
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
            elif uncaps == 3:
                result += 715
            else:
                assert(uncaps == 4)
                result += 805
        elif rarity == "S":
            if uncaps == 0:
                result += 330
            elif uncaps == 1:
                result += 366
            elif uncaps == 2:
                result += 408
            elif uncaps == 3:
                result += 456
            else:
                assert(uncaps == 4)
                result += 492
        elif rarity == "N":
            if uncaps == 0:
                result += 300
            elif uncaps == 1:
                result += 324
            elif uncaps == 2:
                result += 352
            elif uncaps == 3:
                result += 384
            else:
                assert(uncaps == 4)
                result += 408
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
    result -= oldItem.partialLevels
    if result <= 0:
        raise Exception("The inventory file is incorrect: {} at level {} with {} partial level-ups is impossible.".format(oldItem.gameItem.name, oldItem.level, oldItem.partialLevels))
    assert(result > 0)
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
        elif uu == 3:
            return 16
        else:
            assert(uu == 4)
            return 28
    elif ou == 1:
        if uu == 2:
            return 5
        elif uu == 3:
            return 15
        else:
            assert(uu == 4)
            return 27
    elif ou == 2:
        if uu == 3:
            return 10
        else:
            assert(uu == 4)
            return 22
    else:
        assert(ou == 3 and uu == 4)
        return 12
