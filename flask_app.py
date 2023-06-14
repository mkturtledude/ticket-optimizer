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

def optimize(workDir, inventoryLines, tickets, playerLevel, cups, wellFoughtFlags):
    coverageFile = os.path.join(workDir, "data", "alldata.json")
    # actionsFile = os.path.join(workDir, "data", "actions.csv")
    courses, items = reader.readJson(coverageFile, cups, wellFoughtFlags)
    reader.readActions(courses)
    inventory = reader.readInventory(inventoryLines, items)
    upgrades, rows, courseLoadouts, totalScores = util.optimize(inventory, courses, tickets, playerLevel)

    return upgrades, rows, courseLoadouts, totalScores

class MyForm(FlaskForm):
    inventoryFile = FileField('Inventory file')
    inventoryText = TextAreaField('Inventory', render_kw={"rows": 5, "cols": 35})
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
    # Well fought flags
    wf1 = BooleanField('Battle course #1')
    wf2 = BooleanField('Battle course #2')
    wf3 = BooleanField('Battle course #3')
    wf4 = BooleanField('Battle course #4')
    # Optional items to add
    # tourItems = MultiCheckboxField('Tour items')
    spotlightShopItems = MultiCheckboxField('Spotlight Shop Items')

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

    wellFoughtFlags = [form.wf1.data, form.wf2.data, form.wf3.data, form.wf4.data]

    # form.tourItems.choices = [1, 12, 523]
    # form.spotlightShopItems.choices = [42, 123, 64]

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

    # upgrades, rows, courseLoadouts, totalScores = optimize(app.root_path, lines, tickets, playerLevel, cups, wellFoughtFlags)
    try:
        startTime = time.time()
        upgrades, rows, courseLoadouts, totalScores = optimize(app.root_path, lines, tickets, playerLevel, cups, wellFoughtFlags)
        endTime = time.time()
        print("Runtime: {} seconds".format(endTime - startTime))
    except Exception as e:
        return throwError(e.args[0])
    return render_template('results.html', form=form, upgrades=upgrades, rows=rows, courses=courseLoadouts, scores=totalScores)

if __name__ == "__main__":
   app.run(debug=True)
