# Reads coverage data from JSON file

import csv
import json
import os
import unidecode
import re

import pandas as pd

import base

FIRST_WEEK_SPOTLIGHTS = {"Mario (Samurai)", "Luigi (Knight)", "Warrior Wagon", "Shielded Speedster", "Origami Glider", "Silver Luigi's Mustache"}
SECOND_WEEK_SPOTLIGHTS = {"Peach (Yukata)", "Daisy (Yukata)", "Sakura Quickshaw", "Festival Girl", "Boo Masks", "Yukata Ribbon"}

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

def collectCourses(data):
    courses = []
    cupsData = data["tour"]["Cups"]
    for cup in cupsData:
        cupDriverIds = []
        for driver in cup["Drivers"]:
            if driver["Name"]: # There are boosted unassigned Mii suit IDs
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

def fillCourseNames(courses, data):
    for course in courses:
        englishName = data["courses"][course.internalName]["Translations"]["USen"]
        course.englishName = englishName


def readJson(file):
    f = open(file, encoding="utf-8")
    data = json.load(f)
    courses = collectCourses(data)
    allItems = readItems(courses, FIRST_WEEK_SPOTLIGHTS, SECOND_WEEK_SPOTLIGHTS, data)
    fillCourseNames(courses,data)
    return courses, allItems

def readActions(file, courses):
    with open(file) as f:
        reader = csv.DictReader(f, delimiter=",")
        for row in reader:
            name = row["Course"]
            for course in courses:
                if course.englishName == name:
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
                    course.courseActions.lanterns = int(row["Lanterns"]) if row["Lanterns"] else 0

def countMiis(allItems, inventoryItems):
    result = 0
    for item in inventoryItems:
        if allItems[item].isMii:
            result += 1
    return result


def makeInventory(allItems, inventoryItems):
    result = base.Inventory()
    result.numberOfMiis = countMiis(allItems, inventoryItems)
    for item in inventoryItems:
        name = inventoryItems[item]["name"]
        type = inventoryItems[item]["type"]
        level = inventoryItems[item]["level"]
        uncaps = inventoryItems[item]["uncaps"]
        progress = inventoryItems[item]["partialLevels"]
        gameItem = allItems[name]
        basePoints = base.calculateBasePoints(type, gameItem.rarity, uncaps, gameItem.isMii, result.numberOfMiis)
        invItem = base.InventoryItem(gameItem, level, basePoints, uncaps, progress)
        if type == "D":
            result.drivers.add(invItem)
        elif type == "K":
            result.karts.add(invItem)
        else:
            result.gliders.add(invItem)
    return result


def readInventory(inventoryLines, allItems):
    result = {}
    upperToNormal = dict()
    for item in allItems:
        # We need the unidecode to get rid of accents, as in Strawberry Cr^epe
        upperToNormal[unidecode.unidecode(item.upper())] = item


    for line in inventoryLines:
        if not line:
            continue
        row = re.split('[,;\t]', line)
        if row and row[2] != '0':
            assert(len(row) in {4,5})
            if row[2] == 0:
                continue
            itemDict = dict()
            itemDict["name"] = upperToNormal[unidecode.unidecode(row[0].upper())]
            itemDict["type"] = row[1]
            itemDict["level"] = int(row[2])
            itemDict["uncaps"] = int(row[3])
            if len(row) == 5 and row[4].isdigit():
                itemDict["partialLevels"] = int(row[4])
            else:
                itemDict["partialLevels"] = 0
            result[itemDict["name"]] = itemDict


    # with open(file, encoding='utf-8-sig') as csvfile:
    #     for line in csvfile.read().splitlines():
    #         if not line:
    #             continue
    #         row = re.split('[,;\t]', line)
    #         if row and row[2] != '0':
    #             assert(len(row) == 4)
    #             if row[2] == 0:
    #                 continue
    #             itemDict = dict()
    #             itemDict["name"] = upperToNormal[unidecode.unidecode(row[0].upper())]
    #             itemDict["type"] = row[1]
    #             itemDict["level"] = int(row[2])
    #             itemDict["uncaps"] = int(row[3])
    #             result[itemDict["name"]] = itemDict

    return makeInventory(allItems, result)

def readSolutionFile(file):
    f = open(file, "r")
    combinations = dict()
    for line in f.readlines():
        if line[0] == "#" or line[0] == 'o':
            continue
        varAndValue = line.split()
        print(varAndValue)
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
