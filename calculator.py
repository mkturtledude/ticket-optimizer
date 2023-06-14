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

def calculateBonusPoints(level, course, driver, kart, glider):
    sum = action(level, course, driver, kart, glider) + kartSkill(course, kart) + gliderSkill(course, driver, glider) + combo(course, driver, glider)
    # if abs(sum - 9811.5) < 1 and abs(action(level, course, driver, kart, glider) - 3116.4999) < 1:
    #     action(level, course, driver, kart, glider)
    # if abs(sum - 13458.8) < 1:
    #     print(course.englishName)
    #     print("action: {}".format(action(level,course, driver, kart, glider)))
    #     print("kart skill: {}".format(kartSkill(course, kart)))
    #     print("glider skill: {}".format(gliderSkill(course, driver, glider)))
    #     print("combo: {}".format(combo(course, driver, glider)))
    #     print("total actions: {}".format(totalActions(course, driver)))
    #     exit(0)
    return sum

def calculateBonusPointsBoostPerAction(course, driver, kart, glider):
    oColumn = bonusPointsBoostMultiplier(course, driver)
    oColumn += bonusPointsBoostMultiplier(course, kart)
    oColumn += bonusPointsBoostMultiplier(course, glider)
    oColumn *= 150.0 / 30000
    return oColumn

def calculateBonusPointsBoost(course, driver, kart, glider):
    oColumn = calculateBonusPointsBoostPerAction(course, driver, kart, glider)
    multiplier = min(200, totalActions(course, driver))
    return (math.ceil(oColumn) + oColumn) * multiplier

def calculateWellFoughtPoints(level, course, driver, kart, glider):
    if course.type != "Battle" or not course.wellFought:
        return 0
    # if driver.skill == "Coin Box":
    #     return 0
    bpbpa = calculateBonusPointsBoostPerAction(course, driver, kart, glider)
    positionPoints = calculatePositionPoints(level)
    actions = totalActions(course, driver)
    return math.ceil(0.5 * (positionPoints + bpbpa * actions))

def action(level, course, driver, kart, glider):
    result = lapDependent(course)
    result += course.courseActions.miniTurbos * 5
    result += course.courseActions.jumpBoosts * 10
    result += course.courseActions.dashPanels * 10
    result += course.courseActions.glideTime * 10
    result += course.courseActions.courseCoins * 5
    result += coinboxCoins(course, driver) * 5
    result += itemBoxCoins(course, driver) * 5
    result += boomerangActions(driver) * 25
    result += bananaActions(course, driver) * 25
    balloonActions =  6 if course.type == "Battle" else 0
    result += 150 * balloonActions
    remainingActions = totalActions(course, driver) - course.courseActions.miniTurbos - course.courseActions.jumpBoosts - course.courseActions.dashPanels - course.courseActions.glideTime - course.courseActions.courseCoins - itemBoxCoins(course, driver) - coinboxCoins(course, driver) - boomerangActions(driver) - bananaActions(course,driver) - balloonActions
    if remainingActions > 0:
        result += remainingActions * (15 if course.type == "Battle" else 8)
    result *= trackMultiplier(course, kart)
    result *= skillMultiplier(kart)
    result += calculateWellFoughtPoints(level, course, driver, kart, glider)

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
            return 10 * bananaActions(course,driver)
        elif r == "S":
            return 20 * bananaActions(course,driver)
        else:
            return 30 * bananaActions(course,driver)
    return 0

def combo(course, driver, glider):
    # print("shelf: {}".format(getShelf(course, glider)))
    # print("total actions: {}".format(totalActions(course, driver)))
    return getShelf(course, glider) * (120+15*((totalActions(course, driver)-16)))

def lapDependent(course):
    result = 30
    if course.englishName in {"3DS Rainbow Road","3DS Rainbow Road R","3DS Rainbow Road T","3DS Rainbow Road R/T","GCN Baby Park T"}:
        result += 400
    elif course.englishName in {"GCN Baby Park","GCN Baby Park R","GCN Baby Park R/T"}:
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
        return 8
    return 0

def bananaActions(course, driver):
    if driver.skill == "Giant Banana":
        return 35
    elif course.type == "Battle":
        return 6
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

    if course.type == "Battle" and course.wellFought:
        if driver.skill in {"Coin Box", "Boomerang Flower"}:
            result -= 40
        else:
            result -= 20

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
    bonusPoints = calculateBonusPoints(playerLevel, course, driver, kart, glider)
    bonusPointsBoost = calculateBonusPointsBoost(course, driver, kart, glider)
    sum = basePoints + posPoints + bonusPoints + bonusPointsBoost

    # if abs(sum - 54075.4) < 1:
    #     print("{}, {}, {}, {}".format(driver.englishName, kart.englishName, glider.englishName, course.englishName))
    #     print("total actions: {}".format(totalActions(course, driver)))
    #     print("basePoints: {}".format(basePoints))
    #     print("posPoints: {}".format(posPoints))
    #     print("bonusPoints: {}".format(bonusPoints))
    #     print("bonusPointsBoost: {}".format(bonusPointsBoost))
    #     exit(0)
    return sum