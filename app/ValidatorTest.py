import pandas as pd
import numpy as np
import datetime
import io
import json
import pyodbc
from os import path
import os

class Validator:    
    def __init__(self, fileName, fileType, settingsPath):
        self.fileName = fileName
        self.fileType = fileType
        self.settings = dict()
        self.SETTINGS_FILE = settingsPath
        self.dict = dict()
        self.message = ""
        self.companies = []

        self.parseJSON()
        self.parseCSV()

    def parseJSON(self):
         with open(self.SETTINGS_FILE) as json_file:  
            self.settings = json.load(json_file)


    def parseCSV(self):
        df = pd.read_csv(self.fileName, dtype='str') #we want strings because some are not ints
        df.columns = df.columns.str.strip()
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        if df.isnull().values.any():  #if there are empty cells it will not work
            df1 = df[df.isna().any(axis=1)].index
            self.message += "There are empty cells on row(s): "
            for i in df1:
                self.message += str(i + 2) + " "
            self.dict = None
            return
        self.dict = df.to_dict(orient='list')

    def getValidCoIDs(self):
        connection = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                                        'Server=sdbidinazsdbsx002.database.windows.net;'
                                        'Database=RBG_DM;'
                                        'uid=kmahajan@reyesholdings.com;pwd=Welcome9399!;'
                                        "authentication=ActiveDirectoryPassword;")
        cursor = connection.cursor()

        SQLCommand = ("SELECT DSR_SALES_ORG_ID FROM RBD.D_SALES_ORG_EXT")

        cursor.execute(SQLCommand)
        companies = []

        for row in cursor.fetchall():
            #print(row[1])
            companies.append(row[0])


        connection.close()
        self.companies = companies
      
        return companies
    
    def checkLabels(self):    
        valid = True
       
        for validType in self.settings.keys():
            if self.fileType.lower() == validType.lower():
                valid = list(self.dict.keys()) == list(self.settings[validType].keys())
        
        if (valid == False):
            self.message += "The labels are not valid for filetype " + self.fileType + "! Check if some columns are swapped or a label is misspelled."
        return valid

    def validateDateFormat(self, date_text, date_format):
        try:
            datetime.datetime.strptime(date_text, date_format)
            
            return True
        
        except ValueError:
            return False
            #raise ValueError("Incorrect data format, should be MM-DD-YYYY")


    #checks if the input has any numbers
    def hasNumber(self, inputString):
        return any(char.isdigit() for char in inputString)

    def is_percentage(self,n):
        if '%' in n:
            return True
        return False

    #checks that the input can be converted to float (all numbers)
    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def is_string(self,i):
        try:
            int(i)
            return False
        except ValueError:
            return True
            
    def checkColInteger(self, key, token):
        col = list(self.dict.keys()).index(key)
        values = self.dict[key]
        for index, raw_value in enumerate(values):
            value = raw_value.replace(',','')
            try:
                int(value)
            except ValueError:
                self.message += "Not a valid integer on row " + str(index + 2) + " col " + str(col+1) + " (" + key +"): " + value + "<br>"
                return False
            
            if token > 0:
                if int(value) < 0:
                    self.message += "Number less than 0 on row " + str(index + 2) + " col " + str(col+1) + " (" + key +"): " + value + "<br>"
                    return False
            elif token < 0:
                if int(value) > 0:
                    self.message += "Number greater than 0 on row " + str(index + 2) + " col " + str(col+1) + ": " + " (" + key +"): " + value + "<br>"
                    return False

        return True

    def checkColFloat(self, key, token):
        col = list(self.dict.keys()).index(key)
        values = self.dict[key]
        for index, raw_value in enumerate(values):
            value = raw_value.replace(',','')
            if self.is_number(value) == False:
                self.message += "Not a valid float on row " + str(index + 2) + " col " + str(col+1) + " (" + key +"): " + value + "<br>"
                return False
            
            if token > 0:
                if float(value) < 0:
                    self.message = ''
                    self.message += "Number less than 0 on row " + str(index + 2) + " col " + str(col+1) + " (" + key +"): " + value + "<br>"
                    return False
            elif token < 0:
                if float(value) > 0:
                    self.message = ''
                    self.message += "Number greater than 0 on row " + str(index + 2) + " col " + str(col+1) + " (" + key +"): " + value + "<br>"
                    return False

        return True
    
    def checkColIsString(self, key, format):
        col = list(self.dict.keys()).index(key)
        values = self.dict[key]
        for index, value in enumerate(values):
            if self.hasNumber(value):
                self.message += "Not a valid string on row " + str(index + 2) + " col " + str(col+1) + " (" + key +"): " + value + "<br>"
                return False

        if (format == "companys"):
            validCos = self.getValidCoIDs()
            for index, value in enumerate(values):
                if value not in validCos:
                    self.message = ''
                    self.message += "Not a valid company ID on row " + str(index + 2) + " col " + str(col+1) + " (" + key +"): " + value + "<br>"
                    return False
        
        return True

    def checkColIsPercentage(self, key):
        col = list(self.dict.keys()).index(key)
        values = self.dict[key]
        for index, raw_value in enumerate(values):
            value = raw_value.replace(',','')
            if self.is_percentage(value) == False:
                self.message += "Not a percentage on row " + str(index + 2) + " col " + str(col+1) + " (" + key +"): " + value + "<br>"
                return False

        return True

    def checkColDates(self, key, date_format):
        col = list(self.dict.keys()).index(key)
        values = self.dict[key]
        now = datetime.datetime.now()
        for index, value in enumerate(values):
            if self.validateDateFormat(value, date_format) == False:
                self.message = ''
                self.message += "Not a date on row " + str(index + 2) + " col " + str(col+1) + " (" + key +"): " + value + "<br>"
                return False
            if str(now.year) != value[-4:] :
                self.message = ''
                self.message += "Date does not have the current year on row " + str(index + 2) + " col " + str(col+1) + " (" + key +"): " + value + "<br>"
                return False

        return True

    def compareFileNameandType(self):
        if self.fileType.lower() not in self.fileName.lower():   
            if self.fileType == "Static Percentages":
                if ("static_percentage" or "static percentage") in self.fileName.lower():
                    return True
            self.message = ""
            self.message += self.fileName + " is not a(n) " + self.fileType + " file! Try again"
            return False
        else:
            return True

    def verifyFile(self):

        if (self.compareFileNameandType() == False or self.dict == None or self.checkLabels() == False):
            return False

        if (self.checkLabels() == True):
            
            for coID in self.companies:
                if coID == 'FGC' and ('FGC' in self.fileName): 
                    for label in self.dict.keys():
                        if label == 'CostCtr':
                            col = list(self.dict.keys()).index(label)
                            for index,val in enumerate(self.dict['CostCtr']):
                                try:
                                    int(val)
                                except ValueError:
                                    self.message = ''
                                    self.message += "Not a valid integer on row " + str(index + 2) + " col " + str(col+1) + " (" + label +"): " + val + "<br>"
                                    return False
                                if int(val) < 2100 or int(val) > 7410:
                                    self.message += "Not a valid CostCtr on row " + str(index + 2) + " col " + str(col+1) + " (" + label + " has to be between 2100 and 7410 for FGC" + "): " + val + "<br>"
                                    return False
                if coID == 'HJL' and ('HJL' in self.fileName):           
                    for label in self.dict.keys():
                      
                        if label == 'CostCtr':
                            col = list(self.dict.keys()).index(label)
                            for index,val in enumerate(self.dict['CostCtr']):
                                try:
                                    int(val)
                                except ValueError:
                                    self.message += "Not a valid integer on row " + str(index + 2) + " col " + str(col+1) + " (" + label +"): " + val + "<br>"
                                    return False
                                if int(val) < 2100 or int(val) > 7110:
                                    self.message += "Not a valid CostCtr on row " + str(index + 2) + " col " + str(col+1) + " (" + label + " has to be between 2100 and 7110 for HJL" + "): " + val + "<br>"
                                    return False

        #loop through the column parameters
        for index, (key, value) in enumerate(self.settings[self.fileType].items()):
            #print(value['type'] + " in col " + str(index))
            if (value['type'] == "string"):
                if (self.checkColIsString(key, value['format']) == False):
                    print("There is an issue with dates in col " + str(index))
                    return False
            if (value['type'] == "int"):
                if (self.checkColInteger(key, int(value['format'])) == False):
                    print("There is an issue with integers in col " + str(index))
                    return False
            if (value['type'] == "float"):
                if (self.checkColFloat(key, float(value['format'])) == False):
                    print("There is an issue in col " + str(index))
                    return False
            if (value['type'] == "date"):
                if (self.checkColDates(key, value['format']) == False):
                    print("There is an issue in col " + str(index))
                    return False
            if (value['type'] == "percentage"):
                if (self.checkColIsPercentage(key) == False):
                    print("There is an issue in col " + str(index))
                    return False

        return True
                

    def verifyFileToStr(self):
        
        if self.verifyFile() == True:
            return self.fileName + " is valid! Uploaded to /VERIFIED_FILES"
        else:
            return self.fileName + ": <br>" + self.message
        
      
    