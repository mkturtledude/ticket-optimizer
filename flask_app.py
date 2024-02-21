import copy

# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, request, redirect, url_for
import os, csv, codecs, re, sys, datetime, time



#https://stackoverflow.com/questions/56904775/how-to-redirect-while-keeping-form-data-using-flask-and-wtforms
from flask import session
from werkzeug.datastructures import MultiDict

from flask_wtf import FlaskForm
from wtforms import IntegerField, FileField, SelectField, TextAreaField, BooleanField, SelectMultipleField, widgets
import base, util, reader

pastTours = [
    ("current", "Doctor"),
    ("12-mario.json", "Mario"),
    ("13-ninja.json", "Ninja"),
    ("14-yoshi.json", "Yoshi"),
    ("15-spring.json", "Spring"),
    ("16-bowser.json", "Bowser"),
    ("17-mii.json", "Mii"),
    ("18-princess.json", "Princess"),
    ("19-mario-vs-luigi.json", "Mario vs. Luigi"),
    ("20-night.json", "Night"),
    ("21-pipe.json", "Pipe"),
    ("22-sunshine.json", "Sunshine"),
    ("23-vacation.json", "Vacation"),
    ("24-summer.json", "Summer"),
    ("25-sundae.json", "Sundae"),
    ("26-anniversary.json", "Anniversary"),
    ("01-battle.json", "Battle"),
    ("02-halloween.json", "Halloween"),
    ("03-autumn.json", "Autumn"),
    ("04-animal.json", "Animal"),
    ("05-peach-vs-bowser.json", "Peach vs. Bowser"),
    ("06-holiday.json", "Holiday"),
    ("07-new-years.json", "New Year's"),
    ("08-space.json", "Space"),
    ("09-winter.json", "Winter"),
    ("10-exploration.json", "Exploration"),
]

rankedWeeks = [
    ("11-doctor.json1", "Doctor 1"),
    ("11-doctor.json2", "Doctor 2"),
    ("12-mario.json1", "Mario 1"),
    ("12-mario.json2", "Mario 2"),
    ("13-ninja.json1", "Ninja 1"),
    ("13-ninja.json2", "Ninja 2"),
    ("14-yoshi.json1", "Yoshi 1"),
    ("14-yoshi.json2", "Yoshi 2"),
    ("15-spring.json1", "Spring 1"),
    ("15-spring.json2", "Spring 2"),
    ("16-bowser.json1", "Bowser 1"),
    ("16-bowser.json2", "Bowser 2"),
    ("17-mii.json1", "Mii 1"),
    ("17-mii.json2", "Mii 2"),
    ("18-princess.json1", "Princess 1"),
    ("18-princess.json2", "Princess 2"),
    ("19-mario-vs-luigi.json1", "Mario vs. Luigi 1"),
    ("19-mario-vs-luigi.json2", "Mario vs. Luigi 2"),
    ("20-night.json1", "Night 1"),
    ("20-night.json2", "Night 2"),
    ("21-pipe.json1", "Pipe 1"),
    ("21-pipe.json2", "Pipe 2"),
    ("22-sunshine.json1", "Sunshine 1"),
    ("22-sunshine.json2", "Sunshine 2"),
    ("23-vacation.json1", "Vacation 1"),
    ("23-vacation.json2", "Vacation 2"),
    ("24-summer.json1", "Summer 1"),
    ("24-summer.json2", "Summer 2"),
    ("25-sundae.json1", "Sundae 1"),
    ("25-sundae.json2", "Sundae 2"),
    ("26-anniversary.json1", "Anniversary 1"),
    ("26-anniversary.json2", "Anniversary 2"),
    ("01-battle.json1", "Battle 1"),
    ("01-battle.json2", "Battle 2"),
    ("02-halloween.json1", "Halloween 1"),
    ("02-halloween.json2", "Halloween 2"),
    ("03-autumn.json1", "Autumn 1"),
    ("03-autumn.json2", "Autumn 2"),
    ("04-animal.json1", "Animal 1"),
    ("04-animal.json2", "Animal 2"),
    ("05-peach-vs-bowser.json1", "Peach vs. Bowser 1"),
    ("05-peach-vs-bowser.json2", "Peach vs. Bowser 2"),
    ("06-holiday.json1", "Holiday 1"),
    ("06-holiday.json2", "Holiday 2"),
    ("07-new-years.json1", "New Year's 1"),
    ("07-new-years.json2", "New Year's 2"),
    ("08-space.json1", "Space 1"),
    ("08-space.json2", "Space 2"),
    ("09-winter.json1", "Winter 1"),
    ("09-winter.json2", "Winter 2"),
    ("10-exploration.json1", "Exploration 1"),
    ("10-exploration.json2", "Exploration 2"),
]

class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


app = Flask(__name__)
app.secret_key = 'secret'



def stringToCups(cupsString):
    if cupsString == "rankedFirst":
        return {0}
    elif cupsString == "rankedSecond":
        return {2}
    elif cupsString == "rankedBoth":
        return {0,2}
    else:
        return range(15)

def optimize(workDir, inventoryLines, tickets, playerLevel, wellFoughtFlags, simulatedItems, tourFile, toursAndCups):
    coverageFile = os.path.join(workDir, "data", "alldata.json")
    tourPath = os.path.join(workDir, "data", "pastTours", tourFile) if tourFile and tourFile != "current" else ""
    tourPaths = []
    for i in range(len(toursAndCups)):
        tourFileName = toursAndCups[i][0]
        cupNumber = toursAndCups[i][1]
        if tourFileName == "curren":
            path = os.path.join(workDir, "data", "alldata.json")
            cupNumber = 2
        else:
            path = os.path.join(workDir, "data", "pastTours", tourFileName)
        tourPaths.append([path, cupNumber])
    courses, items = reader.readJson(coverageFile, wellFoughtFlags, tourPath, tourPaths)
    # if tourFile in {"current", "02-halloween.json", }
    considerPumpkins = False
    reader.readActions(courses, considerPumpkins)
    inventory = reader.readInventory(inventoryLines, items, simulatedItems)
    upgrades, rows, courseLoadouts, totalScores = util.optimize(inventory, courses, tickets, playerLevel)

    return upgrades, rows, courseLoadouts, totalScores

class MyForm(FlaskForm):
    inventoryFile = FileField('Inventory file')
    inventoryText = TextAreaField('Inventory', render_kw={"rows": 5, "cols": 35})
    playerLevel = IntegerField('Player level')
    mode = SelectField("Optimization mode: ", choices=[('ranked', 'Ranked'), ('acr', 'ACR')])
    weeks = MultiCheckboxField("Ranked weeks to consider: ", choices=rankedWeeks)
    tour = SelectField("Tour to consider", choices=pastTours)
    # Ticket counts
    lnd = IntegerField()
    lnk = IntegerField()
    lng = IntegerField()
    lsd = IntegerField()
    lsk = IntegerField()
    lsg = IntegerField()
    lhd = IntegerField()
    lhk = IntegerField()
    lhg = IntegerField()
    und = IntegerField()
    unk = IntegerField()
    ung = IntegerField()
    usd = IntegerField()
    usk = IntegerField()
    usg = IntegerField()
    uhd = IntegerField()
    uhk = IntegerField()
    uhg = IntegerField()
    # Well fought flags
    wf1 = BooleanField('Battle course #1')
    wf2 = BooleanField('Battle course #2')
    wf3 = BooleanField('Battle course #3')
    wf4 = BooleanField('Battle course #4')
    # Optional items to add
    spotlight = MultiCheckboxField('Spotlight')
    dailySpotlightNonGold = MultiCheckboxField('Daily Spotlight (Non Gold)')
    dailySpotlightGold = MultiCheckboxField('Daily Spotlight (Gold)')
    goldPass = MultiCheckboxField('Gold Pass')
    paywalled = MultiCheckboxField('Paywalled (Commemorative, Gold Challenges)')
    miiShop = MultiCheckboxField('Mii Shop')
    other = MultiCheckboxField('Other (Ranked, Challenge Cards, Token Shop, etc.)')



@app.route('/faq')
def faq():
    return render_template('faq.html')

def throwError(message):
    return render_template('error.html', message=message)

@app.route('/', methods = ['GET'])
def home():
    form = MyForm()

    with open(os.path.join(app.root_path, "data/obtainable-items", 'spotlight.csv'), newline='', encoding='utf-8-sig') as csvfile:
        choices = [(row[0], row[0]) for row in csv.reader(csvfile)]
        form.spotlight.choices = choices
    with open(os.path.join(app.root_path, "data/obtainable-items", 'daily-spotlight-non-gold.csv'), newline='', encoding='utf-8-sig') as csvfile:
        choices = [(row[0], row[0]) for row in csv.reader(csvfile)]
        form.dailySpotlightNonGold.choices = choices
    with open(os.path.join(app.root_path, "data/obtainable-items", 'daily-spotlight-gold.csv'), newline='', encoding='utf-8-sig') as csvfile:
        choices = [(row[0], row[0]) for row in csv.reader(csvfile)]
        form.dailySpotlightGold.choices = choices
    with open(os.path.join(app.root_path, "data/obtainable-items", 'gold-pass.csv'), newline='', encoding='utf-8-sig') as csvfile:
        choices = [(row[0], row[0]) for row in csv.reader(csvfile)]
        form.goldPass.choices = choices
    with open(os.path.join(app.root_path, "data/obtainable-items", 'paywalled.csv'), newline='', encoding='utf-8-sig') as csvfile:
        choices = [(row[0], row[0]) for row in csv.reader(csvfile)]
        form.paywalled.choices = choices
    with open(os.path.join(app.root_path, "data/obtainable-items", 'mii-shop.csv'), newline='', encoding='utf-8-sig') as csvfile:
        choices = [(row[0], row[0]) for row in csv.reader(csvfile)]
        form.miiShop.choices = choices
    with open(os.path.join(app.root_path, "data/obtainable-items", 'other.csv'), newline='', encoding='utf-8-sig') as csvfile:
        choices = [(row[0], row[0]) for row in csv.reader(csvfile)]
        form.other.choices = choices

    return render_template('index.html', form=form)


@app.route('/results/', methods = ['POST','GET'])
def results():
    form = MyForm()
    invFile = form.inventoryFile
    playerLevel = form.playerLevel.data
    tourFile = ""
    toursAndCups = []
    mode = form.mode
    weekStrings = []
    if mode.data == "acr":
        tourFile = form.tour.data
    else:
        weekStrings = request.form.getlist("weeks")
        for elem in weekStrings:
            filename = elem[:-1]
            cupNumber = 0 if elem[-1] == '1' else 2
            toursAndCups.append([filename, cupNumber])

    tickets = base.TicketStash()
    tickets.lnd = form.lnd.data if form.lnd.data else 0
    tickets.lnk = form.lnk.data if form.lnk.data else 0
    tickets.lng = form.lng.data if form.lng.data else 0
    tickets.lsd = form.lsd.data if form.lsd.data else 0
    tickets.lsk = form.lsk.data if form.lsk.data else 0
    tickets.lsg = form.lsg.data if form.lsg.data else 0
    tickets.lhd = form.lhd.data if form.lhd.data else 0
    tickets.lhk = form.lhk.data if form.lhk.data else 0
    tickets.lhg = form.lhg.data if form.lhg.data else 0
    tickets.und = form.und.data if form.und.data else 0
    tickets.unk = form.unk.data if form.unk.data else 0
    tickets.ung = form.ung.data if form.ung.data else 0
    tickets.usd = form.usd.data if form.usd.data else 0
    tickets.usk = form.usk.data if form.usk.data else 0
    tickets.usg = form.usg.data if form.usg.data else 0
    tickets.uhd = form.uhd.data if form.uhd.data else 0
    tickets.uhk = form.uhk.data if form.uhk.data else 0
    tickets.uhg = form.uhg.data if form.uhg.data else 0

    wellFoughtFlags = [form.wf1.data, form.wf2.data, form.wf3.data, form.wf4.data]

    simulatedItems = request.form.getlist("spotlight") # TODO: Add other obtainable items
    simulatedItems += request.form.getlist("dailySpotlightNonGold")
    simulatedItems += request.form.getlist("dailySpotlightGold")
    simulatedItems += request.form.getlist("goldPass")
    simulatedItems += request.form.getlist("paywalled")
    simulatedItems += request.form.getlist("miiShop")
    simulatedItems += request.form.getlist("other")

    if not playerLevel or not str(playerLevel).isdigit() or int(playerLevel) < 1 or int(playerLevel) > 400:
        return throwError("Please enter a player level between 1 and 400")

    lines = []
    if invFile.data:
        inventoryLines = codecs.iterdecode(invFile.data, 'utf-8-sig')
        try:
            for line in inventoryLines:
                lines.append(line)
        except UnicodeDecodeError:
            return throwError("Couldn't read inventory file. Are you sure it's in CSV format and can be opened with a spreadsheet program?")
    else:
        lines = form.inventoryText.data.splitlines()
        if not lines:
            return throwError("No inventory data was provided")

    # Save the inventory file for research purposes
    user_ip = request.remote_addr
    if user_ip != "127.0.0.1":
        user_ip = request.headers['X-Real-IP']
        fileName = user_ip + datetime.datetime.now().strftime('-%H%M%S.csv')
        outputPath = os.path.join(app.root_path, "inventories", fileName)
        with open(outputPath, 'w', encoding='utf-8-sig') as f:
            for line in lines:
                line = line.rstrip() + '\n'
                f.write(line + '\n')

    # upgrades, rows, courseLoadouts, totalScores = optimize(app.root_path, lines, tickets, playerLevel, wellFoughtFlags, simulatedItems, tourFile, toursAndCups)
    try:
        startTime = time.time()
        upgrades, rows, courseLoadouts, totalScores = optimize(app.root_path, lines, tickets, playerLevel, wellFoughtFlags, simulatedItems, tourFile, toursAndCups)
        endTime = time.time()
        print("Runtime: {} seconds".format(endTime - startTime))
    except Exception as e:
        return throwError(e.args[0])
    coursesList = [(i, course, data) for i, (course, data) in enumerate(courseLoadouts.items())]
    weekLabels = dict(rankedWeeks)
    selectedLabels = [weekLabels[key] for key in weekStrings]
    return render_template('results.html', form=form, upgrades=upgrades, rows=rows, courses=coursesList, scores=totalScores, weeks=selectedLabels)

if __name__ == "__main__":
   app.run(debug=True)
