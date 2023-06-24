# Reads coverage data from JSON file

import csv
import json
import os
import io
import unidecode
import re
import requests

import pandas as pd

import base

FIRST_WEEK_SPOTLIGHTS = {}
SECOND_WEEK_SPOTLIGHTS = {}

def skillIdToString(id):
    # Drivers
    if (id == 130):
        return "Boomerang Flower"
    elif (id == 454):
        return "Bubble"
    elif (id == 100):
        return "Triple Green Shells"
    elif (id == 101):
        return "Double Bob-ombs"
    elif (id == 455):
        return "Dash Ring"
    elif (id == 66):
        return "Giant Banana"
    elif (id == 98):
        return "Heart"
    elif (id == 68):
        return "Fire Flower"
    elif (id == 70):
        return "Yoshi's Egg"
    elif (id == 358):
        return "Triple Mushroom"
    elif (id == 68):
        return "Fire Flower"
    elif (id == 360):
        return "Ice Flower"
    elif (id == 67):
        return "Bowser's Shell"
    elif (id == 128):
        return "Banana Barrels"
    elif (id == 65):
        return "Lucky Seven"
    elif (id == 127):
        return "Bob-omb Cannon"
    elif (id == 464):
        return "Birdo's Egg"
    elif (id == 357):
        return "Hammer"
    elif (id == 359):
        return "Mushroom Cannon"
    elif (id == 129):
        return "Coin Box"
    elif (id == 463):
        return "Super Bell"
    elif (id == 99):
        return "Triple Bananas"
    elif (id == 126):
        return "Giga Bob-omb"
    elif (id == 468):
        return "Capsule"
    elif (id == 465):
        return "Tanooki Leaf"
    elif (id == 380):
        return "Coin Vacuum"
    # Karts
    elif (id == 445):
        return "Dash Panel Plus"
    elif (id == 447):
        return "Jump Boost Plus"
    elif (id == 443):
        return "Rocket Start Plus"
    elif (id == 444):
        return "Mini-Turbo Plus"
    elif (id == 446):
        return "Slipstream Plus"
    # Gliders
    elif (id == 56):
        return "Mushroom Plus"
    elif (id == 61):
        return "Blooper Plus"
    elif (id == 57):
        return "Green Shell Plus"
    elif (id == 59):
        return "Banana Plus"
    elif (id == 345):
        return "Giant Mushroom Plus"
    elif (id == 58):
        return "Red Shell Plus"
    elif (id == 62):
        return "Lightning Plus"
    elif (id == 346):
        return "Super Horn Plus"
    elif (id == 64):
        return "Coin Plus"
    elif (id == 60):
        return "Bob-omb Plus"
    elif (id == 63):
        return "Bullet Bill Plus"
    else:
        print("Unknown skill {}!".format(id))
        exit(0)

def collectCourses(data, cupsToConsider):
    courses = []
    cupsData = data["tour"]["Cups"]
    cupNumber = -1
    for cup in cupsData:
        cupNumber += 1
        if cupsToConsider and (not cupNumber in cupsToConsider):
            continue
        cupDriverIds = []
        for driver in cup["Drivers"]:
            cupDriverIds.append(driver["Id"])
        for course in cup["Courses"]:
            internalName = course["Key"]
            sortId = course["SortId"]
            courses.append(base.TourCourse(internalName, cupDriverIds, sortId))
    return courses

def rarityToString(r):
    temp = int(r)
    if r == 0:
        return "N"
    elif r == 1:
        return "S"
    else:
        return "HE"

def readItemsAndShelves(course, firstWeekSpotlights, secondWeekSpotlights, data, type):
    topShelf = []
    middleShelf = []
    allItems = dict()
    for item in data:
        currentTopShelfSize = len(topShelf)
        itemId = item["Id"]
        itemName = item["Translations"]["USen"]
        if not itemName:
            continue
        skillName = skillIdToString(int(item["skill"]["Id"]))
        rarity = rarityToString(item["Rarity"])
        try:
            isMii = bool(item["IsMiiSuit"])
        except:
            isMii = False
        allItems[itemName] = base.GameItem(itemName, itemId, type, rarity, skillName, isMii)
        hasCupBoost = (itemId in course.cupDriverIds)
        hasMiiBoost = (isMii and (course.sortId == 0))
        hasSpotlightBoost = False
        if (itemName in firstWeekSpotlights) and (course.sortId == 1):
            hasSpotlightBoost = True
        elif (itemName in secondWeekSpotlights) and (course.sortId == 2):
            hasSpotlightBoost = True
        if (hasCupBoost and hasSpotlightBoost) or (hasCupBoost and hasMiiBoost) or (hasMiiBoost and hasSpotlightBoost):
            topShelf.append(base.CupItem(itemName,1))
            continue
        hasSingleBoost = hasCupBoost or hasMiiBoost or hasSpotlightBoost
        for c in item["CourseMoreGoodAtDetail"]:
            if c == course.internalName:
                topShelf.append(base.CupItem(itemName,1))
        for c in item["CourseGoodAtDetail"]:
            if c["Key"] == course.internalName:
                if hasSingleBoost:
                    topShelf.append(base.CupItem(itemName, 1))
                elif c["PromotionLevel"] > 0:
                    topShelf.append(base.CupItem(itemName,int(c["PromotionLevel"])))
                    middleShelf.append(base.CupItem(itemName, 1))
                else:
                    middleShelf.append(base.CupItem(itemName, 1))
        if len(topShelf) == currentTopShelfSize: # Item hasn't been added to top shelf
            if hasSingleBoost:
                middleShelf.append(base.CupItem(itemName, 1))
    return topShelf, middleShelf, allItems

def readItems(courses, firstWeekSpotlights, secondWeekSpotlights, data):
    allItems = dict()
    for course in courses:
        ts, ms, ai = readItemsAndShelves(course, firstWeekSpotlights, secondWeekSpotlights, data["drivers"], "D")
        course.topShelf += ts
        course.middleShelf += ms
        allItems |= ai
        ts, ms, ai = readItemsAndShelves(course, firstWeekSpotlights, secondWeekSpotlights, data["karts"], "K")
        course.topShelf += ts
        course.middleShelf += ms
        allItems |= ai
        ts, ms, ai = readItemsAndShelves(course, firstWeekSpotlights, secondWeekSpotlights, data["gliders"], "G")
        course.topShelf += ts
        course.middleShelf += ms
        allItems |= ai
    return allItems

def fillCourseNames(courses, data, wellFoughtFlags):
    battleCourseNumber = 0
    for course in courses:
        englishName = data["courses"][course.internalName]["Translations"]["USen"]
        type = data["courses"][course.internalName]["type"]
        course.englishName = englishName
        course.type = type
        if course.type == "Battle":
            course.wellFought = wellFoughtFlags[battleCourseNumber]
            battleCourseNumber += 1


def readJson(file, cups, wellFoughtFlags):
    f = open(file, encoding="utf-8")
    data = json.load(f)
    courses = collectCourses(data, cups)
    allItems = readItems(courses, FIRST_WEEK_SPOTLIGHTS, SECOND_WEEK_SPOTLIGHTS, data)
    fillCourseNames(courses,data, wellFoughtFlags)
    return courses, allItems

def readActions(courses):
    # Google Sheet owned by myself, which copies the data from DKR's master sheet
    url = f'https://docs.google.com/spreadsheets/d/19xo0WBLORLU8Xz_W2J7H3KnLAjE3__ejVG32xD2Pk0M/gviz/tq?tqx=out:csv&sheet=Sheet1'
    # fetch the data from the sheet
    response = requests.get(url)

    # decode the response as CSV
    csv_data = response.content.decode('utf-8')

    # treat it as a file
    f = io.StringIO(csv_data)
    # with open(file) as f: # To read from file = actions.csv

    reader = csv.DictReader(f, delimiter=",")
    for row in reader:
        name = row["Course"]
        for course in courses:
            if course.englishName == name:
                try:
                    course.courseActions.miniTurbos = int(row["Mini-Turbos"])
                    course.courseActions.normal = int(row["Normal"])
                    course.courseActions.giantBanana = int(row["Giant Banana"])
                    course.courseActions.lucky7 = int(row["Lucky 7"])
                    course.courseActions.boomerangFlower = int(row["Boomerang Flower"])
                    course.courseActions.coinbox = int(row["Coin Box"])
                    course.courseActions.itemBoxes = int(row["Item Boxes"])
                    course.courseActions.miniTurbos = int(row["Mini-Turbos"])
                    course.courseActions.jumpBoosts = int(row["Jump Boosts"])
                    course.courseActions.dashPanels = int(row["Dash Panels"])
                    course.courseActions.glideTime = int(row["Glide Time"])
                    course.courseActions.courseCoins = int(row["Coins (Course)"])
                    course.courseActions.itemCoins = int(row["Coins (Items)"])
                    # course.courseActions.lanterns = int(row["Pumpkins"]) if row["Pumpkins"] else 0
                except:
                    raise Exception("Action counts for " + course.englishName + " are incomplete")


def countMiis(allItems, inventoryItems):
    result = 0
    for item in inventoryItems:
        if allItems[item].isMii:
            result += 1
    return result


def makeInventory(allItems, inventoryItems, simulatedItems):
    inventoryItemsSet = set()
    for item in inventoryItems:
        inventoryItemsSet.add(inventoryItems[item]["name"])
    for item in simulatedItems:
        if item not in inventoryItemsSet:
            inventoryItems[item] = {"name": item, "level": 1, "uncaps": 0, "partialLevels": 0, "levelCap": 8, "uncapCap": 4}
    result = base.Inventory()
    result.numberOfMiis = countMiis(allItems, inventoryItems)
    for item in inventoryItems:
        name = inventoryItems[item]["name"]
        level = inventoryItems[item]["level"]
        uncaps = inventoryItems[item]["uncaps"]
        progress = inventoryItems[item]["partialLevels"]
        levelCap = inventoryItems[item]["levelCap"]
        uncapCap = inventoryItems[item]["uncapCap"]
        gameItem = allItems[name]
        type = gameItem.type
        basePoints = base.calculateBasePoints(type, gameItem.rarity, uncaps, gameItem.isMii, result.numberOfMiis)
        invItem = base.InventoryItem(gameItem, level, basePoints, uncaps, progress, levelCap, uncapCap)
        if type == "D":
            result.drivers.add(invItem)
        elif type == "K":
            result.karts.add(invItem)
        else:
            result.gliders.add(invItem)
    return result


def readInventory(inventoryLines, allItems, simulatedItems):
    result = {}
    upperToNormal = dict()
    for item in allItems:
        # We need the unidecode to get rid of accents, as in Strawberry Cr^epe
        upperToNormal[unidecode.unidecode(item.upper())] = item
    lineNumber = 0
    for line in inventoryLines:
        lineNumber += 1
        if not line:
            continue
        row = re.split('[,;\t]', line.strip()) # split to remove the newline
        if len(row) < 4:
            raise Exception("Row number " + str(lineNumber) + " in the inventory file has less than 4 columns:   " + line)
        if len(row) > 7:
            raise Exception("Row number " + str(lineNumber) + " in the inventory file has more than 5 columns:   " + line)
        if row and row[2] != '0':
            assert(len(row) in {4,5,6,7})
            if row[2] == 0:
                continue
            itemDict = dict()
            if len(row[1]) != 1:
                raise Exception("The second element in row number " + str(lineNumber) + " should be a single letter (D/K/G):   " + line)
            if not row[2].isdigit() or len(row[2]) != 1:
                raise Exception("The third element in row number " + str(lineNumber) + " should be a single digit, representing the item's level:   " + line)
            if not row[3].isdigit() or len(row[3]) != 1:
                raise Exception("The fourth element in row number " + str(lineNumber) + " should be a single digit, representing the item's uncaps:   " + line)
            upper = unidecode.unidecode(row[0].upper())
            if upper not in upperToNormal:
                raise Exception("Row number " + str(lineNumber) + " has an invalid item name:\n" + line)
            itemDict["name"] = upperToNormal[upper]
            itemDict["level"] = int(row[2])
            itemDict["uncaps"] = int(row[3])
            if itemDict["uncaps"] < 0 or itemDict["uncaps"] > 4:
                raise Exception("The number of uncaps of " + itemDict["name"] + " is " + str(itemDict["uncaps"]) + ", but it should be a number between 0 and 4")
            if len(row) >= 5 and row[4].isdigit():
                itemDict["partialLevels"] = int(row[4])
            else:
                itemDict["partialLevels"] = 0
            if len(row) >= 6 and row[5].isdigit():
                itemDict["levelCap"] = int(row[5])
                if itemDict["levelCap"] > 0 and itemDict["levelCap"] < itemDict["level"]:
                    raise Exception("The maximum level allowed for {} is {}, which is smaller than the current level ({})!".format(itemDict["name"], itemDict["levelCap"], itemDict["level"]))
            else:
                itemDict["levelCap"] = 8
            if len(row) >= 7 and row[6].isdigit():
                itemDict["uncapCap"] = int(row[6])
                if itemDict["uncapCap"] > 0 and itemDict["uncapCap"] < itemDict["uncaps"]:
                    raise Exception("The maximum uncaps allowed for {} are {}, which is smaller than the current uncaps ({})!".format(itemDict["name"], itemDict["uncapCap"], itemDict["uncaps"]))
            else:
                itemDict["uncapCap"] = 4
            result[itemDict["name"]] = itemDict

    result = makeInventory(allItems, result, simulatedItems)
    if not result.drivers:
        raise Exception("Couldn't find any owned drivers in the inventory file! Make sure that the third column contains the levels of your drivers.")
    if not result.karts:
        raise Exception("Couldn't find any owned karts in the inventory file! Make sure that the third column contains the levels of your karts.")
    if not result.gliders:
        raise Exception("Couldn't find any owned gliders in the inventory file! Make sure that the third column contains the levels of your gliders.")
    return result

def readSolutionFile(file):
    f = open(file, "r")
    combinations = dict()
    for line in f.readlines():
        if line[0] == "#" or line[0] == 'o':
            continue
        varAndValue = line.split()
        assert(len(varAndValue) >= 2)
        variable = varAndValue[0]
        value = int(varAndValue[1])
        if value == 0:
            continue
        variableElements = variable.split("_")
        if variableElements[0] == "y":
            combNumber = int(variableElements[1])
            did = int(variableElements[2])
            dl =  int(variableElements[3])
            du =  int(variableElements[4])
            kid = int(variableElements[5])
            kl =  int(variableElements[6])
            ku =  int(variableElements[7])
            gid = int(variableElements[8])
            gl =  int(variableElements[9])
            gu =  int(variableElements[10])
            combinations[combNumber] = tuple([did,dl,du,kid,kl,ku,gid,gl,gu])
    finalCombinations = []
    for i in range(len(combinations)):
        finalCombinations.append(combinations[i])
    return finalCombinations
