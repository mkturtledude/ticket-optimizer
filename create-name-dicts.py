import json

def remove_prefix(stringA, stringB):
    if stringB.startswith(stringA):
        return stringB[len(stringA):].lstrip()
    else:
        return stringB


def createCourseDicts(data):
    dictHydra = dict()
    dictSam = dict()
    for internalName in data["courses"]:
        courseData = data["courses"][internalName]
        type = courseData["type"]
        platform = courseData["platform"]
        englishName = courseData["Translations"]["USen"]
        if "Rainbow Road" in englishName:
            dictHydra[internalName] = englishName
        else:
            dictHydra[internalName] = remove_prefix(platform, englishName)
        dictSam[internalName] = {"type": type, "platform": platform, "englishName": englishName}

    with open("jsons-for-frida-output/course_names_hydra.json", "w") as outfile:
        json.dump(dictHydra, outfile, indent=4)

    with open("jsons-for-frida-output/course_names_sam.json", "w") as outfile:
        json.dump(dictSam, outfile, indent=4)

def createItemDicts(data):
    namesDict = dict()
    itemCategories = ["drivers", "karts", "gliders"]
    for category in itemCategories:
        itemList = data[category]
        for itemData in itemList:
            id = itemData["Id"]
            englishName = itemData["Translations"]["USen"]
            namesDict[id] = englishName

    with open("jsons-for-frida-output/item_names.json", "w") as outfile:
        json.dump(namesDict, outfile, indent=4)


file = "data/alldata.json"
f = open(file, encoding="utf-8")
data = json.load(f)

createCourseDicts(data)
createItemDicts(data)




