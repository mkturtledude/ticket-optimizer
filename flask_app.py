import copy

# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, request, redirect, url_for
import os, csv, codecs, re, sys, datetime



#https://stackoverflow.com/questions/56904775/how-to-redirect-while-keeping-form-data-using-flask-and-wtforms
from flask import session
from werkzeug.datastructures import MultiDict

from flask_wtf import FlaskForm
from wtforms import IntegerField, FileField, SelectField
import base, util, reader

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

def optimize(workDir, inventoryLines, tickets, playerLevel, cups):
    coverageFile = os.path.join(workDir, "data", "alldata.json")
    actionsFile = os.path.join(workDir, "data", "actions.csv")
    courses, items = reader.readJson(coverageFile, cups)
    reader.readActions(actionsFile, courses)
    inventory = reader.readInventory(inventoryLines, items)
    upgrades, rows, courseLoadouts, totalScores = util.optimize(inventory, courses, tickets, playerLevel)

    return upgrades, rows, courseLoadouts, totalScores

class MyForm(FlaskForm):
    inventoryFile = FileField('Inventory file')
    playerLevel = IntegerField('Player level')
    cups = SelectField('Cups to consider', choices=[('all', 'All'), ('rankedFirst', 'First week ranked'), ('rankedSecond', 'Second week ranked'), ('rankedBoth', 'Both ranked cups')])
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


@app.route('/faq')
def faq():
    return render_template('faq.html')

def throwError(message):
    return render_template('error.html', message=message)

@app.route('/', methods = ['GET'])
def home():
    form = MyForm()
    return render_template('index.html', form=form)


@app.route('/results/', methods = ['POST','GET'])
def results():
    form = MyForm()
    invFile = form.inventoryFile
    playerLevel = form.playerLevel.data
    cups = stringToCups(form.cups.data)
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

    if not invFile.data:
        return throwError("No inventory file selected")
    if not playerLevel or not str(playerLevel).isdigit() or int(playerLevel) < 1 or int(playerLevel) > 400:
        return throwError("Please enter a player level between 1 and 400")


    inventoryLines = codecs.iterdecode(invFile.data, 'utf-8-sig')
    lines = []
    try:
        for line in inventoryLines:
            lines.append(line)
    except UnicodeDecodeError:
        return throwError("Couldn't read inventory file. Are you sure it's in CSV format and can be opened with a spreadsheet program?")

    # Save the inventory file for research purposes
    fileName = datetime.datetime.now().strftime('%H%M%S.csv')
    outputPath = os.path.join(app.root_path, "inventories", fileName)
    with open(outputPath, 'w', encoding='utf-8-sig') as f:
        f.writelines(lines)

    # upgrades, rows, courseLoadouts, totalScores = optimize(app.root_path, lines, tickets, playerLevel, cups)
    try:
        upgrades, rows, courseLoadouts, totalScores = optimize(app.root_path, lines, tickets, playerLevel, cups)
    except Exception as e:
        return throwError(e.args[0])
    return render_template('results.html', form=form, upgrades=upgrades, rows=rows, courses=courseLoadouts, scores=totalScores)

if __name__ == "__main__":
   app.run(debug=True)
