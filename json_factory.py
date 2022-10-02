import csv
import json

# import reader

# with open('reich-buffs-anniv.csv', newline='') as csvfile:
#     spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
#     for row in spamreader:
#         print(', '.join(row))

cups = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}
oldJson = "/home/marco/ticketOptimizer/data/BowserTour_alldata_multilang.json"

f = open(oldJson, encoding="utf-8")
data = json.load(f)

# Write courses to file
with open("/home/marco/ticketOptimizer/data/new-courses.csv") as f:
    reader = csv.DictReader(f,delimiter=',')
    for row in reader:
        name = row['Name']
        platform = row['Platform']
        data["courses"][name] = {}
        data["courses"][name]["platform"] = platform
        data["courses"][name]["Translations"] = {"USen":name}
    with open("temp-1.json", 'w', encoding = "utf-8") as outfile:
        json.dump(data,outfile,indent=4, ensure_ascii=False)

# Write new items to file
with open("/home/marco/ticketOptimizer/data/new-items.csv") as f:
    reader = csv.DictReader(f,delimiter=',')
    for row in reader:
        name = row['Name']
        type = row['Type']
        rarity = int(row['Rarity'])
        isMii = True if row['IsMii'] == "1" else False
        skill = int(row["Skill"])
        id = int(row["Id"])
        itemDict = {}
        itemDict["Id"] = id
        itemDict["Name"] = name
        itemDict["Rarity"] = rarity
        itemDict["IsMiiSuit"] = isMii
        itemDict["skill"] = {"Id":skill}
        itemDict["Translations"] = {"USen":name}
        if type == "D":
            data["drivers"].append(itemDict)
        elif type == "K":
            data["karts"].append(itemDict)
        else:
            assert(type == "G")
            data["gliders"].append(itemDict)
    with open("temp-2.json", 'w', encoding = "utf-8") as outfile:
        json.dump(data,outfile,indent=4, ensure_ascii=False)


f = open("temp-2.json", encoding="utf-8")
data = json.load(f)

# Write cups to file
with open("/home/marco/ticketOptimizer/data/new-cups.csv") as f:
    reader = csv.DictReader(f,delimiter=',')
    cupId = 0
    data["tour"]["Cups"].clear()
    for row in reader:
        course1 = row["Course1"]
        course2 = row["Course2"]
        course3 = row["Course3"]
        driver = row["Driver"]
        drivers = []
        for driverDict in data["drivers"]:
            if (driverDict["IsMiiSuit"] and driver == "Mii") or driverDict["Translations"]["USen"] == driver:
                drivers.append({"Id":driverDict["Id"]})
        course1internal = ""
        course2internal = ""
        course3internal = ""
        for course in data["courses"]:
            courseDict = data["courses"][course]
            if course1 == courseDict["Translations"]['USen']:
                course1internal = course
            if course2 == courseDict["Translations"]["USen"]:
                course2internal = course
            if course3 == courseDict["Translations"]["USen"]:
                course3internal = course
        assert(course1internal)
        assert(course2internal)
        assert(course3internal)
        assert(drivers)
        cupDict = {}
        cupDict["SortId"] = cupId
        cupDict["Drivers"] = drivers
        cupDict["Courses"] = [{"SortId":0, "Key":course1internal}, {"SortId":1, "Key":course2internal}, {"SortId":2, "Key":course3internal}]

        data["tour"]["Cups"].append(cupDict)
        cupId += 1
    with open("temp-3.json", 'w', encoding = "utf-8") as outfile:
        json.dump(data,outfile,indent=4, ensure_ascii=False)

exit(0)


# data["courses"][B]

# courses, items = reader.readJson(oldJson, cups)


with open('reich-buffs-anniv.csv') as f:
    reader = csv.DictReader(f, delimiter=',')
    for row in reader:
        name = row['ITEM']
        topShelf = list(filter(None,[row['TOPSHELF BUFF 1'], row['BUFF 2'], row['BUFF 3'], row['BUFF 4'], row['BUFF 5'], row['BUFF 6']]))
        l3unlocks = list(filter(None,[row['L3 UNLOCK 1'], row['L3 UNLOCK 2']]))
        l6unlocks = list(filter(None,[row['L6 UNLOCK 1'], row['L6 UNLOCK 2']]))
        midShelf = list(filter(None,[row['MIDSHELF 1'], row['MIDSHELF 2'], row['MIDSHELF 3'], row['MIDSHELF 4'], row['MIDSHELF 5'], row['MIDSHELF 6'], row['MIDSHELF 7'], row['MIDSHELF 8'], row['MIDSHELF 9'], row['MIDSHELF 10']]))

        if topShelf:
            print(name)
            print(topShelf)
            if l3unlocks:
                print("L3:")
                print(l3unlocks)
            if l6unlocks:
                print("L6:")
                print(l6unlocks)
            if midShelf:
                print("Mid:")
                print(midShelf)