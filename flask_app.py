
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, request, redirect, url_for
import os, csv, codecs, re, sys



#https://stackoverflow.com/questions/56904775/how-to-redirect-while-keeping-form-data-using-flask-and-wtforms
from flask import session
from werkzeug.datastructures import MultiDict

from flask_wtf import FlaskForm
from wtforms import IntegerField, FileField

import optimizer

app = Flask(__name__)
app.secret_key = 'secret'

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
        tickets = optimizer.Tickets()
        tickets.lnd = form.lnd.data
        tickets.lnk = form.lnk.data
        tickets.lng = form.lng.data
        tickets.lsd = form.lsd.data
        tickets.lsk = form.lsk.data
        tickets.lsg = form.lsg.data
        tickets.lhd = form.lhd.data
        tickets.lhk = form.lhk.data
        tickets.lhg = form.lhg.data
        tickets.und = form.und.data
        tickets.unk = form.unk.data
        tickets.ung = form.ung.data
        tickets.usd = form.usd.data
        tickets.usk = form.usk.data
        tickets.usg = form.usg.data
        tickets.uhd = form.uhd.data
        tickets.uhk = form.uhk.data
        tickets.uhg = form.uhg.data

        # with open(invFile.data, encoding='utf-8-sig') as csvfile:
        # for line in invFile.data.read().splitlines():
        inventoryLines = codecs.iterdecode(invFile.data, 'utf-8-sig')
        # for line in request.files[invFile.name]:
        #     result2 += line
        #     result2 += "\n"
        result = optimizer.optimize(app.root_path, inventoryLines, tickets, playerLevel)
        message = str(result)
        return render_template('index.html', form=form, message=message)


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