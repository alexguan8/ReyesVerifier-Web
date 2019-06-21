from app import app
from app import ValidatorTest as vdt
from flask import render_template, request, flash, redirect, make_response, jsonify, session, url_for, send_from_directory
from werkzeug.utils import secure_filename
from shutil import copyfile
import json
import time
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__)) 

VERIFIED_FILE_PATH = os.path.join(APP_ROOT, 'VERIFIED_FILES')

def numPreviousUploads(fileName):
    listOfFiles = os.listdir(VERIFIED_FILE_PATH)
    count = 0
    for file in listOfFiles:
        if fileName in file:
            count = count + 1

    return count
    

#view functions go here

@app.route('/', methods = ["GET", "POST"])
@app.route('/index', methods = ["GET", "POST"])
def index():
    if request.method == "POST":

        file = request.files["file"]

        print("File uploaded")
        print(file)

        filename = secure_filename(file.filename)
        file.save(filename)

        res = make_response(jsonify({"message": filename + " uploaded. You will be automatically redirected."}), 200)

        return res
        
    return render_template('index.html')


@app.route('/verify', methods = ['GET', 'POST'])
def verify():
    if request.method == 'POST':
        filetype = request.form.get("selectedHidden", None)
        f = request.files['csvFileInput']
        print(type(f))
        f.save(secure_filename(f.filename))
       
        verifier = vdt.Validator(f.filename, filetype)

        raw_name = os.path.splitext(secure_filename(f.filename))[0]

        output = verifier.verifyFileToStr()
        if (numPreviousUploads(raw_name) > 0):
            output += "<br> This file name has " + str(numPreviousUploads(raw_name)) + " verified version(s). Check the history tab to view/download previous versions."
        else:
            output += "<br> This file name has never been verified."
        
        flash(output)

        #raw_name + time.strftime("%Y%m%d-%H%M%S") + ".csv"
        if (verifier.verifyFile() == True):
            copyfile(f.filename, VERIFIED_FILE_PATH + "/" + raw_name + time.strftime("%Y%m%d-%H%M%S") + ".csv")

        return redirect(url_for('.index'))
        #return f.filename + ' uploaded successfully'


@app.route('/history')
def history():
    listOfFiles = os.listdir(VERIFIED_FILE_PATH)
    for file in listOfFiles:
        flash("<a href= '/download/" + file + "'> " + file + "</a>")
    
    return render_template('history.html')

@app.route("/download/<file_name>", methods = ['GET', 'POST'])
def download(file_name):
    try:
        return send_from_directory(VERIFIED_FILE_PATH, file_name, as_attachment=True)
    except Exception as e:
        return str(e)


