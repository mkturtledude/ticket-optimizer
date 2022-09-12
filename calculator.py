# The calculations in this file were all taken from the DKR.exe scoresheet

import base
import math

def calculatePositionPoints(level):
    constantPoints = 3000 # No idea why 3000
    if level <= 150:
        return constantPoints + level * 20
    elif level <= 200:
        return constantPoints + 150*20 + (level - 150)*10
    else:
        return constantPoints + 150*20 + 50*10 + (level - 200)*5

def calculateBonusPoints(course, driver, kart, glider):
    sum = action(course, driver, kart) + kartSkill(course, kart) + gliderSkill(course, driver, glider) + combo(course, driver, glider)
    if abs(sum - 14959) < 1:
        print("action: {}".format(action(course, driver, kart)))
        print("kart skill: {}".format(kartSkill(course, kart)))
        print("glider skill: {}".format(gliderSkill(course, driver, glider)))
        print("combo: {}".format(combo(course, driver, glider)))
        print("total actions: {}".format(totalActions(course, driver)))
    return sum

def calculateBonusPointsBoost(course, driver, kart, glider):
    oColumn = bonusPointsBoostMultiplier(course, driver)
    oColumn += bonusPointsBoostMultiplier(course, kart)
    oColumn += bonusPointsBoostMultiplier(course, glider)
    oColumn *= 150.0 / 30000
    multiplier = min(200, totalActions(course, driver))
    return (math.ceil(oColumn) + oColumn) * multiplier

def action(course, driver, kart):
    result = lapDependent(course)
    result += course.courseActions.miniTurbos * 5
    result += course.courseActions.jumpBoosts * 10
    result += course.courseActions.dashPanels * 10
    result += course.courseActions.glideTime * 10
    result += course.courseActions.courseCoins * 5
    result += coinboxCoins(course, driver) * 5
    result += itemBoxCoins(course, driver) * 5
    result += boomerangActions(driver) * 25
    result += bananaActions(driver) * 25
    remainingActions = totalActions(course, driver) - course.courseActions.miniTurbos - course.courseActions.jumpBoosts - course.courseActions.dashPanels - course.courseActions.glideTime - course.courseActions.courseCoins - itemBoxCoins(course, driver) - coinboxCoins(course, driver) - boomerangActions(driver) - bananaActions(driver)
    if remainingActions > 0:
        result += remainingActions * 10
    result *= trackMultiplier(course, kart)
    result *= skillMultiplier(kart)

    return result

def kartSkill(course, kart):
    r = kart.rarity
    s = kart.skill
    if s == "Mini-Turbo Plus":
        if r == "N":
            return 2 * course.courseActions.miniTurbos
        elif r == "S":
            return 3 * course.courseActions.miniTurbos
        else:
            return 4 * course.courseActions.miniTurbos
    elif s == "Jump Boost Plus":
        if r == "N":
            return 4 * course.courseActions.jumpBoosts
        elif r == "S":
            return 6 * course.courseActions.jumpBoosts
        else:
            return 8 * course.courseActions.jumpBoosts
    elif s == "Dash Panel Plus":
        if r == "N":
            return 5 * course.courseActions.dashPanels
        elif r == "S":
            return 10 * course.courseActions.dashPanels
        else:
            return 15 * course.courseActions.dashPanels
    elif s == "Rocket Start Plus":
        if r == "N":
            return 30
        elif r == "S":
            return 50
        else:
            return 80
    elif s == "Slipstream Plus":
        if r == "N":
            return 2*10
        elif r == "S":
            return 2*20
        else:
            return 2*40
    assert(False)


def gliderSkill(course, driver, glider):
    r = glider.rarity
    s = glider.skill
    if s == "Coin Plus":
        if r == "N":
            return 1 * itemBoxCoins(course, driver)
        elif r == "S":
            return 2 * itemBoxCoins(course, driver)
        else:
            return 3 * itemBoxCoins(course, driver)
    elif s == "Banana Plus":
        if r == "N":
            return 10 * bananaActions(driver)
        elif r == "S":
            return 20 * bananaActions(driver)
        else:
            return 30 * bananaActions(driver)
    return 0

def combo(course, driver, glider):
    # print("shelf: {}".format(getShelf(course, glider)))
    # print("total actions: {}".format(totalActions(course, driver)))
    return getShelf(course, glider) * (120+15*((totalActions(course, driver)-16)))

def lapDependent(course):
    result = 30
    if course.englishName in {"3DS Rainbow Road","3DS Rainbow Road R","3DS Rainbow Road T","3DS Rainbow Road R/T","GCN Baby Park T"}:
        result += 400
    elif course.englishName in {"GCN Baby Park","GCN Baby Park R"}:
        result += 800
    else:
        result += 200
    return result

def itemBoxCoins(course, driver):
    result = course.courseActions.itemCoins
    if driver.skill == "Boomerang Flower":
        result += 25
    elif driver.skill == "Coin Box":
        result += 25
    elif driver.skill == "Lucky Seven":
        result += 35
    else:
        result += 40
    return result

def coinboxCoins(course, driver):
    if driver.skill == "Boomerang Flower":
        return 40
    elif driver.skill == "Coin Box":
        if course.courseActions.itemBoxes < 6:
            return 35
        else:
            return 55
    return 0

def boomerangActions(driver):
    if driver.skill == "Boomerang Flower":
        return 15
    return 0

def bananaActions(driver):
    if driver.skill == "Giant Banana":
        return 35
    return 10

def totalActions(course, driver):
    result = course.courseActions.normal
    if driver.skill == "Giant Banana":
        result = course.courseActions.giantBanana
    elif driver.skill == "Lucky Seven":
        result = course.courseActions.lucky7
    elif driver.skill == "Boomerang Flower":
        result = course.courseActions.boomerangFlower
    elif driver.skill == "Coin Box":
        result = course.courseActions.coinbox

    shelf = getShelf(course, driver)
    if shelf == 2:
        result = course.courseActions.normal - 40
    elif shelf == 1:
        result -= course.courseActions.normal - 50
    return result

def getShelf(course, item):
    for i in course.topShelf:
        if i.name == item.englishName and i.topShelfAtLevel <= item.level:
            return 3
    for i in course.middleShelf:
        if i.name == item.englishName:
            return 2
    return 1

def trackMultiplier(course, kart):
    shelf = getShelf(course, kart)
    if shelf == 3:
        return 2
    elif shelf == 2:
        return 1.5
    else:
        return 1

def skillMultiplier(kart):
    r = kart.rarity
    l = kart.level
    if r == "N":
        if l == 1:
            return 1
        elif l in {2,3}:
            return 1.05
        elif l in {4,5}:
            return 1.1
        elif l in {6,7}:
            return 1.15
        elif l == 8:
            return 1.2
    if r == "S":
        if l == 1:
            return 1.05
        elif l in {2,3}:
            return 1.1
        elif l in {4,5}:
            return 1.15
        elif l in {6,7}:
            return 1.2
        elif l == 8:
            return 1.25
    if r == "HE":
        if l == 1:
            return 1.1
        elif l in {2,3}:
            return 1.15
        elif l in {4,5}:
            return 1.2
        elif l in {6,7}:
            return 1.25
        elif l == 8:
            return 1.3
    assert(False)

def bonusPointsBoostMultiplier(course, item):
    if getShelf(course, item) == 3:
        return item.basePoints * (item.level - 1)
    return 0

def calculateScore(driver, kart, glider, playerLevel, course):
    basePoints = driver.basePoints + kart.basePoints + glider.basePoints
    posPoints = calculatePositionPoints(playerLevel)
    bonusPoints = calculateBonusPoints(course, driver, kart, glider)
    bonusPointsBoost = calculateBonusPointsBoost(course, driver, kart, glider)
    sum = basePoints + posPoints + bonusPoints + bonusPointsBoost

    # if abs(sum - 48911.75) < 1:
    #     print("basePoints: {}".format(basePoints))
    #     print("posPoints: {}".format(posPoints))
    #     print("bonusPoints: {}".format(bonusPoints))
    #     print("bonusPointsBoost: {}".format(bonusPointsBoost))
    return sum