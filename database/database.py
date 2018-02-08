'''
Created on 23.02.2016

@author: hendrik
'''

import pymysql as db
import sys
from time import sleep

from threading import Lock

from databasemodel import databasemodel

class Database(object):
  
    configuration = None
    connection = None
    mutex = Lock()

    def __init__(self, configuration):
        self.configuration = configuration
        
        if self._openDatabase() == False:
            print("Could not open database. Abort!")
            sys.exit(-1)
        
        
        
    # connect to database
    def _openDatabase(self):
        try:
            self.connection = db.connect(host=self.configuration['mysql-host'], 
                                         user=self.configuration['mysql-user'], 
                                         passwd=self.configuration['mysql-password'], 
                                         db=self.configuration['mysql-database'],
                                         use_unicode=True,
                                         charset="utf8")
            
            # create table if not exists
            # self._createDatabaseModel()
            
        except db.Error as e:
            print(e)
            return False
        
        return True
    
    
    def _createDatabaseModel(self):
        self.mutex.acquire()
        
        model = databasemodel.getDatabaseModel()
        for table in list(model.keys()):
            statement = ''
            for col in list(model[table].keys()):
                statement = col + ' ' + model[table][col] + ', ' + statement
            statement = statement[:-2]
            
            statement = 'CREATE TABLE IF NOT EXISTS ' + table + ' (' + statement + ')'

            errorcounter = 0
            while errorcounter < 10:
                try:
                    cursor = self.connection.cursor()
                    cursor.execute(statement)
                    self.connection.commit()
                    
                    break
                except db.Error as e:
                    errorcounter = errorcounter + 1
                    sleep(0.5)
                    if errorcounter > 10:
                        self.mutex.release()
                        return False
                    
        self.mutex.release()
        return True
            
            
    def insertRow(self, table, data):
        self.mutex.acquire()
        
        values = list()
                
        statement = "INSERT INTO " + table + "(" + ", ".join(list(data.keys())) +  ") VALUES("
        for d in list(data.keys()):
            statement = statement + "%s, "
            values.append(data[d])
            
        statement = statement[:-2]
        statement = statement + ")"
        
        errorcounter = 0
        while errorcounter < 10:
            try:
                cursor = self.connection.cursor()
                cursor.execute(statement, tuple(values))
                self.connection.commit()
                
                self.mutex.release()
                return self._getDatabaseId(table, cursor.lastrowid)
            except db.Error as e:
                errorcounter = errorcounter + 1
                sleep(0.5)
                if errorcounter > 10:
                    self.mutex.release()
                    return -1
        
        self.mutex.release()
        return -1
    
    
    def updateRow(self, tableid, table, data):

        self.mutex.acquire()
        
        for d in list(data.keys()):
            statement = "UPDATE " + table + " SET "
            statement = statement + d + " = %s"
            statement = statement + " WHERE id = " + str(tableid)

            errorcounter = 0
            while errorcounter < 10:
                try:
                    cursor = self.connection.cursor()
                    cursor.execute(statement, [data[d]])
                    self.connection.commit()
                    break
                except db.Error as e:
                    errorcounter = errorcounter + 1
                    sleep(0.5)
                    if errorcounter > 10:
                        self.mutex.release()
                        return False
        
        self.mutex.release()
        return True    
        
            
    def deleteRow(self, tableid, table):
        self.mutex.acquire()
        
        errorcounter = 0
        while errorcounter < 10:
            try:
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM " + table + " WHERE id = " + str(tableid))
                self.connection.commit()
            except db.Error as e:
                errorcounter = errorcounter + 1
                sleep(0.5)
                if errorcounter > 10:
                    self.mutex.release()
                    return False
        
        self.mutex.release()
        return True
    
    
    def selectRows(self, entity, condition=None, order=None, limit=None):
        errorcounter = 0
        while errorcounter < 10:
            try:
                self.mutex.acquire()
                
                statement = "SELECT " + ', '.join(entity.getTableColumns()) + " FROM " + entity.getTableName()
                if condition != None:
                    statement = statement + " WHERE " + condition
                    
                if order != None:
                    statement = statement + " ORDER BY " + order
                    
                if limit != None:
                    statement = statement + " LIMIT " + str(limit)
                    
                result = list()
                cursor = self.connection.cursor()
                
                query = cursor.execute(statement)
                if query == 0:
                    self.mutex.release()
                    return [];
                
                for row in cursor.fetchall():
                    d = dict()
                    i = 0
                    for c in entity.getTableColumns():
                        d[c] = row[i]
                        i = i + 1
                    
                    result.append(d)
                    
                self.mutex.release()
                return result
            
            except db.Error as e:
                errorcounter = errorcounter + 1
                sleep(0.5)
                if errorcounter > 10:
                    break
                
        self.mutex.release()
        return []
        
        
    def _getDatabaseId(self, tableName, rowId):
        self.mutex.acquire()
        cursor = self.connection.cursor()
        cursor.execute("SELECT last_insert_id();")
        result = cursor.fetchone()
        if len(result) > 0:
            self.mutex.release()
            return result[0]
        
        self.mutex.release()
        return -1


        