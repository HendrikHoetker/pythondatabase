'''
Created on 24.02.2016

@author: hendrik
'''

#from .databaseclass import DatabaseClass

def getDatabaseModel():
    
    model = dict()
    
    for o in [DatabaseClass()]:
        model[o.getTableName()] = o.getTableModel()
        
    return model


def getDatabaseEntities(db, entitytype, condition=None, order=None, limit=None):
    result = list()
    for values in db.selectRows(entitytype(), condition, order, limit):
        result.append(entitytype(values))
        
    return result

def getFirstDatabaseEntity(db, entitytype, condition=None, order=None):
    result = getDatabaseEntities(db, entitytype, condition, order, None)
    if len(result) > 0:
        return result[0]
    
    return None


def deleteDatabaseEntity(db, entity):
    db.deleteRow(entity.id, entity.getTableName())
