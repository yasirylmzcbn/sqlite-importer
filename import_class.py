import sqlite3
import os.path
import csv
import xml.etree.ElementTree as ET 
import json
import dateutil.parser
import re

class Import:

    # executes an sqlite command
    def execute(self, command):
        _conn = sqlite3.connect('data.sqlite')
        cursor = _conn.cursor()
        cursor.execute(command)
        cursor.close()
        _conn.commit()
        _conn.close()


    # converts a type to either
    def get_type(self, val):
        pattern = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}")
        if(pattern.fullmatch(val)):
            return "DATE NOT NULL, "
        try: 
            int(val)
            if len(val) <= 6:
                return "INTEGER NOT NULL, "
            else:
                return "TEXT NOT NULL, "
        except ValueError:
            try:
                float(val)
                return "REAL NOT NULL, "
            except ValueError:
                return "TEXT NOT NULL, "


    # name is the tag name; values is just the value of each name type
    def create_table(self, filename, names, values):
        self.execute('DROP TABLE IF EXISTS "' + filename + '"')
        command = 'CREATE TABLE "' + filename + '" ("id" INTEGER NOT NULL, '
        for i in range(len(names)):
            command += '"' + names[i] +  '" '
            command += self.get_type(values[i])
        command += 'PRIMARY KEY("id" AUTOINCREMENT) );'
        self.execute(command)


    # inserts each data point individually
    def insert_data(self, filename, names, values):
        command = 'INSERT INTO "' + filename + '" ('
        for i in range(len(names)-1):
            command += names[i] + ', '
        command += names[len(names)-1]
        command += ') VALUES ('
        for i in range(len(values)-1): 
            command += '"' + values[i] + '", '
        command += '"' + values[len(values)-1] + '"'
        command += ');'
        self.execute(command)


    def importall(self, filename):
        ext = os.path.splitext(filename)[1]
        if ext == ".csv":
            self.import_csv(filename)
        elif ext == ".json":
            self.import_json(filename)
        elif ext == ".xml":
            self.import_xml(filename)


    def import_csv(self, filename):
        f = open(filename, 'r', encoding="utf-8")
        csv_file = csv.DictReader(f)
        first = True
        for row in csv_file:
            names = []
            values = []
            for key in row:
                names.append(key)
                values.append(str(row[key]))
            if first: # create table
                self.create_table(filename, names, values)
            self.insert_data(filename, names, values)
            first = False


    def import_json(self, filename):
        with open(filename, 'r', encoding='UTF-8') as json_file:
            data = json.load(json_file)
            first = True
            for row in data:
                names = []
                values = []
                for key in row:
                    names.append(key)
                    values.append(str(row[key]))
                if first: # create table
                    self.create_table(filename, names, values)
                self.insert_data(filename, names, values)
                first = False
                

    def import_xml(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        first = True
        for r in root.findall("./record"):
            names = []
            values = []
            for child in r:
                names.append(child.tag)
                values.append(str(child.text))
            if first: # create table
                self.create_table(filename, names, values)
            self.insert_data(filename, names, values)
            first = False