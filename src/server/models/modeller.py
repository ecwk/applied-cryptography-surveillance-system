# This modeller is inspired from a Javascript library 
import csv
from pprint import pprint
from datetime import datetime

from util.config import config


class Model():
  def __init__(self, schema, path):
    self.schema = schema
    self.path = path
    self.headers = getCsvHeaders(self.path)
    self.rows = applyType(
      self.schema,
      openCsv(self.path)
      )

  def getAll(self):
    return self.rows

  def find(self, query={}):
    results = []
    for row in self.rows:
      addResult = True
      for searchField, searchValue in query.items():
        if row[searchField] != searchValue:
          addResult = False
          break

      if addResult:   
        results.append(row)
    return results

  def add(self, newRow):
    rows = self.rows
    newRow = addConstraints(self.schema, newRow)
    rows.append(newRow)

    primaryKey = self.schema.getPrimaryKey()
    if primaryKey:
      rows = sorted(rows, key=lambda row: row[primaryKey])
    addCsvRows(self.path , self.headers, rows)
    return newRow

  def update(self, query={}, update={}):
    rows = self.rows

    for key, val in query.items():
      toUpdate = [
        updateConstraints(self.schema, row)
        for row in rows if row[key] == val
      ]
    for row in toUpdate:
      for key, val in update.items():
        row[key] = val
    primaryKey = self.schema.getPrimaryKey()
    if primaryKey:
      rows = sorted(rows, key=lambda row: row[primaryKey])
    addCsvRows(self.path , self.headers, rows)
    
    return toUpdate
    

  def delete(self, query={}):
    rows = self.rows

    for key, val in query.items():
      toDelete = [row for row in rows if row[key] == val]
    
    for row in toDelete:
      rows.remove(row)
    primaryKey = self.schema.getPrimaryKey()
    if primaryKey:
      rows = sorted(rows, key=lambda row: row[primaryKey])
    addCsvRows(self.path , self.headers, rows)

    return toDelete

  def generateUid(self):
    rows = self.rows
    primaryKey = self.schema.getPrimaryKey()
    existingUids = []
    for row in rows:
      existingUids.append(row[primaryKey])
    existingUids = sorted(existingUids)

    uid = 1
    for id_ in existingUids:
      if id_ == uid:
        uid += 1

    return uid

# only used when reading
def applyType(schema, rows):
  for row in rows:
    for field, value in row.items():
      fieldType = schema.fields[field]['type']
      if fieldType == 'int':
        row[field] = int(value)
        
      elif fieldType == 'str':
        row[field] = str(value)

      elif fieldType == 'bool':
        if row[field] == 'True':
          row[field] = True
        elif row[field] == 'False':
          row[field] = False
        else:
          raise Exception('Invalid boolean value: ' + row[field])
  
      elif fieldType == 'list' or fieldType == 'dict':
        row[field] = eval(value)
  
  return rows

def addConstraints(schema, row):
  constraints = schema.fields

  # default value constraint
  for key, value in constraints.items():
    defaultValue = constraints[key]['default']
    if defaultValue and row.get(key) is None:
      row[key] = defaultValue

  # required value constraint
  requiredFields = []
  for key, value in constraints.items():
    required = constraints[key]['required']
    if required and row.get(key) is None:
      requiredFields.append(key)
  if requiredFields:
    raise Exception('The following are required to have values: ' + str(requiredFields))

  return row

def updateConstraints(schema, row):
  constraints = schema.fields

  # apply default on update constraint
  for key, value in constraints.items():
    hasToUpdate = constraints[key]['defaultUpdate']
    defaultValue = constraints[key]['default']
    if hasToUpdate:
      row[key] = defaultValue

  return row

class Schema():
  def __init__(self, fields):
    self.fields = self.fillDefaultFieldConstraints(fields)

  defaultFieldConstraints = {
    'type': 'str',
    'primaryKey': False,
    'required': False,
    'default': None, # not implemented yet
    'defaultUpdate': False # not implemented yet
  }

  def fillDefaultFieldConstraints(self, fields):
    for field, constraints in fields.items():
      for constraint in self.defaultFieldConstraints:
        if constraint not in constraints:
          constraints[constraint] = self.defaultFieldConstraints[constraint]
    return fields

  def getPrimaryKey(self):
    for field, constraints in self.fields.items():
      if constraints.get('primaryKey') == True:
        return field
    return None
    

def openCsv(csvFilePath):
  with open(csvFilePath, 'r') as f:
    rows = list(csv.DictReader(f))
    return rows


def getCsvHeaders(csvFilePath):
  with open(csvFilePath, 'r') as f:
    rows = csv.reader(f)
    headers = next(rows)
    return headers


def addCsvRows(csvFilePath, headers, rows):
  with open(csvFilePath, 'w', newline='') as f:
    writer = csv.DictWriter(f, headers)
    writer.writeheader()
    writer.writerows(rows)




def removeCsvRow(csvFilePath, sortKey, delRow):
  if not isinstance(delRow, dict):
    return
  
  headers = getCsvHeaders(csvFilePath)
  rows = openCsv(csvFilePath)
  for row in rows:
    if int(row[sortKey]) == int(delRow[sortKey]):
      rows.remove(row)
  with open(csvFilePath, 'w', newline='') as f:
    writer = csv.DictWriter(f, headers)
    writer.writeheader()
    writer.writerows(rows)



def getCurrentDateTime():
  now = datetime.now()
  strFormat = '%d-%m-%Y %H:%M:%S'
  return now.strftime(strFormat)