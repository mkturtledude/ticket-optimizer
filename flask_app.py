
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, request, redirect, url_for
import os, csv, codecs, re, sys



#https://stackoverflow.com/questions/56904775/how-to-redirect-while-keeping-form-data-using-flask-and-wtforms
from flask import session
from werkzeug.datastructures import MultiDict

from flask_wtf import FlaskForm
from wtforms import IntegerField, FileField

import base, util, reader

app = Flask(__name__)
app.secret_key = 'secret'


def optimize(workDir, inventoryLines, tickets, playerLevel):
    coverageFile = os.path.join(workDir, "data", "alldata.json")
    actionsFile = os.path.join(workDir, "data", "actions.csv")
    courses, items = reader.readJson(coverageFile)
    reader.readActions(actionsFile, courses)
    inventory = reader.readInventory(inventoryLines, items)

    upgrades, rows = util.optimize(inventory, courses, tickets, playerLevel)

    return upgrades, rows

class MyForm(FlaskForm):
    inventoryFile = FileField('Inventory file')
    playerLevel = IntegerField('Player level')
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

@app.route('/', methods = ['POST','GET'])
def home():
    form = MyForm()
    if request.method == 'GET':
        formdata = session.get('formdata', None)
        if formdata:
            form = MyForm(MultiDict(formdata))
            #form.validate()
            session.pop('formdata')
        return render_template('index.html', form=form, message="")
    else:
        invFile = form.inventoryFile
        playerLevel = form.playerLevel.data
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

        inventoryLines = codecs.iterdecode(invFile.data, 'utf-8-sig')

        upgrades, rows = optimize(app.root_path, inventoryLines, tickets, playerLevel)
        # splittedRows = []
        # for row in rows:
        #     splittedRow = []
        #     for element in row:
        #         splittedRow.append(element)
        #     splittedRows.append(splittedRow)
        return render_template('index.html', form=form, upgrades=upgrades, rows=rows)


#    upload     = request.files.get('upload')
#    name, ext = os.path.splitext(upload.filename)
#    if ext != '.csv':
#        info["errMessage"] = 'File extension needs to be csv.'
#    else:
#        info["errMessage"] = ""
#        result = ""
#        reader = csv.reader(codecs.iterdecode(upload.file, 'utf-8-sig'))
#        for line in reader:
#            for element in line:
#                result += str(element)
#                result += "\t"
#            result += "\n"
#        info["result"] = result
#    return template("/",info=info)
#
if __name__ == "__main__":
   app.run(debug=True)