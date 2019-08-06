from app import app
from app import ValidatorTest as vdt
from flask import Flask, render_template, render_template_string, request, flash, redirect, make_response, jsonify, session, url_for, send_from_directory, send_file
from flask_simpleldap import LDAP
from flask_login import current_user
import ldap as l
from flask import Flask, g, request, session, redirect, url_for
from werkzeug.utils import secure_filename
from shutil import copyfile
from datetime import datetime, timedelta
import json
import time
import ssl
import os, os.path

app.config['LDAP_HOST'] = 'rhldap.reyesholdings.com'
app.config['LDAP_BASE_DN'] = 'OU=Reyes Holdings Enterprise, dc=reyesholdings,dc=com'
app.config['LDAP_USERNAME'] = 'BIFileValidator'
app.config['LDAP_PASSWORD'] = 'Welcome0805!'
app.config['LDAP_USE_SSL'] = True


ldap = LDAP(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__)) 

VERIFIED_FILE_PATH = os.path.join(APP_ROOT, 'VERIFIED_FILES')

JSON_FILE_PATH = "app/formatSettings.json"

with open(JSON_FILE_PATH) as json_file:
    directorySettings = json.load(json_file)
    reyesPath = directorySettings['reyesPath']

USER_UPLOADING = "Some User"

def numPreviousUploads(fileName):
    listOfFiles = os.listdir(VERIFIED_FILE_PATH)
    count = 0
    for file in listOfFiles:
        if fileName in file:
            count = count + 1

    return count

def stripExtension(fileNameWithExt):
    return os.path.splitext(fileNameWithExt)[0]

def stripDate(fileName):
    return fileName.rsplit("_", 1)[0]

def getUsername(fileName):
    rawName = stripExtension(fileName)
    rawName = stripDate(rawName)

    username = rawName.rsplit("_", 1)[1]

    if len(username) == 0:
        return "Some User"
    else:
        return username
    

def getRawName(fileName):
    rawName = stripExtension(fileName)
    rawName = stripDate(rawName)
    return rawName.rsplit("_", 1)[0]

def dateUploaded(fileName):
    raw_name = stripExtension(fileName)

    raw_date = raw_name.rsplit("_", 1)[1]

    myTime = datetime.strptime(raw_date, "%Y%m%d-%H%M%S")

    return myTime.strftime("%m/%d/%Y -- %H:%M:%S")

def getFileType(fileName):
    if "sales" in fileName.lower():
        return "Sales"
    if "payroll" in fileName.lower():
        return "Payroll"
    if "sales" in fileName.lower():
        return "Sales"
    if "static percentage" or "static_percentage" in fileName.lower():
        return "Static Percentages"

def getCoID(fileName):
    return fileName[0:3]

#view functions go here

@app.before_request
def before_request():
    if (session.get("logged_in") == True):
        user = {"name": session["username"]}
        g.user = user
    else:
        session['logged_in'] = False
        g.user = {"name": "undefined"}

@app.route('/login')
@ldap.basic_auth_required
def login():
    session['logged_in'] = True
    session['username'] = g.ldap_username
    return redirect('/uploads')

@app.route('/', methods = ["GET", "POST"])
@app.route('/uploads', methods = ["GET", "POST"])
def index():
    if (session.get("logged_in") == False or 'logged_in' not in session):
        return redirect('/login')

    if request.method == "POST":
        
        file = request.files["file"]
        fileType = request.form.get("fileTypeData")
        username = request.form.get("usernameData")



        filename = secure_filename(file.filename)
        file.save(filename)

        verifier = vdt.Validator(filename, fileType, JSON_FILE_PATH)

        raw_name = os.path.splitext(filename)[0]

        #create end string
        output = " Username: " + username + "<br>"
        output += verifier.verifyFileToStr()
        if (numPreviousUploads(raw_name) > 0):
            output += "<br>" + filename + " has " + str(numPreviousUploads(raw_name)) + " previously verified version(s). Check the history tab to view/download previous versions."
        else:
            output += "<br>" + filename + " has never been verified."

        verified = verifier.verifyFile()
        #raw_name + time.strftime("%Y%m%d-%H%M%S") + ".csv"
        if (verified == True):
            localName = raw_name + "_" + username + "_" + time.strftime("%Y%m%d-%H%M%S") + ".csv"
            copyfile(filename, VERIFIED_FILE_PATH + "/" + localName)
            copyfile(VERIFIED_FILE_PATH + '/' + localName, reyesPath + raw_name + '.csv')
                
        os.remove(filename)
        
        res = make_response(jsonify({"message": output, "valid": verified}), 200)

        return res
    return render_template('index.html')

@app.route('/history')
@ldap.login_required
def history():
    if (session.get("logged_in") == False or 'logged_in' not in session):
        return redirect('/login')

    listOfFiles = os.listdir(VERIFIED_FILE_PATH)
    output=""  
    for file in listOfFiles:
        raw_name = getRawName(file)
        fileType = getFileType(raw_name)
        coID = getCoID(raw_name)
        date = dateUploaded(file)
        username = getUsername(file)
        output = ("<tr><td><a href= '/uploads/VERIFIED_FILES/" + file + "'>" + raw_name + "</a></td>" +
        "<td>" + coID + "</td>" + 
        "<td>" + fileType + "</td>" + 
        "<td>" + username + "</td>" + 
        "<td>" + date + "</td>" + 
        "</tr>")
        flash(output)
    
    return render_template('history.html')

@app.route("/uploads/<path:file_name>", methods = ['GET', 'POST'])
def download(file_name):
    try:
        #return("Hello")
        return send_from_directory(APP_ROOT, file_name, as_attachment=True)
        #return send_file(APP_ROOT + file_name, as_attachment=True)
    except Exception as e:
        return str(e)

@app.route("/settings", methods = ["GET", "POST"])
@ldap.login_required
def settings():
    if (session.get("logged_in") == False or 'logged_in' not in session):
        return redirect('/login')

    if request.method == "POST":
        #use the request object to get the file from the file input in index.html
        jsonFile = request.files['jsonFileInput']

        filename = secure_filename(jsonFile.filename)

        print(filename)
        jsonFile.save(JSON_FILE_PATH)
    
        return ('', 204)

    flash("<a href= '/uploads/formatSettings.json'>Current Settings File</a>")
    return render_template("settings.html")