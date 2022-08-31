import base

def isFeasible(originalItem, targetLevel, targetUncaps):
    t = originalItem.gameItem.type
    r = originalItem.gameItem.rarity
    ltn = base.calculateLevelTicketsNeeded(originalItem, targetLevel)
    utn = base.calculateCapTicketsNeeded(originalItem, targetUncaps)
    if t == "D":
        if r == "N":
            if ltn > base.ND_LEVEL_TIX or utn > base.ND_UNCAP_TIX:
                return False
        elif r == "S":
            if ltn > base.SD_LEVEL_TIX or utn > base.SD_UNCAP_TIX:
                return False
        else:
            assert(r == "HE")
            if ltn > base.HD_LEVEL_TIX or utn > base.HD_UNCAP_TIX:
                return False
    elif t == "K":
        if r == "N":
            if ltn > base.NK_LEVEL_TIX or utn > base.NK_UNCAP_TIX:
                return False
        elif r == "S":
            if ltn > base.SK_LEVEL_TIX or utn > base.SK_UNCAP_TIX:
                return False
        else:
            assert(r == "HE")
            if ltn > base.HK_LEVEL_TIX or utn > base.HK_UNCAP_TIX:
                return False
    else:
        assert(t == "G")
        if r == "N":
            if ltn > base.NG_LEVEL_TIX or utn > base.NG_UNCAP_TIX:
                return False
        elif r == "S":
            if ltn > base.SG_LEVEL_TIX or utn > base.SG_UNCAP_TIX:
                return False
        else:
            assert(r == "HE")
            if ltn > base.HG_LEVEL_TIX or utn > base.HG_UNCAP_TIX:
                return False
    return True

def expandInventoryByType(items, itemType, numberOfMiis):
    result = set()
    for item in items:
        minLevel = item.level
        minUncaps = item.uncaps
        for level in range(minLevel,8+1):
            for uncaps in range(minUncaps, 3+1):
                if isFeasible(item, level, uncaps):
                    basePoints = base.calculateBasePoints(itemType, item.rarity, uncaps, item.isMii, numberOfMiis)
                    result.add(base.InventoryItem(item.gameItem, level, basePoints, uncaps, 0))
    print("Input inventory has size {}".format(len(items)))
    print("Output inventory has size {}".format(len(result)))
    return result

def expandInventory(inventory):
    result = base.Inventory()
    result.drivers = expandInventoryByType(inventory.drivers, "D", inventory.numberOfMiis)
    result.karts = expandInventoryByType(inventory.karts, "K", inventory.numberOfMiis)
    result.gliders = expandInventoryByType(inventory.gliders, "G", inventory.numberOfMiis)
    return result
