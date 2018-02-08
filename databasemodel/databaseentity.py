'''
Created on 24.02.2016

@author: hendrik
'''

class DatabaseEntity(object):
    
    databaseEntity_TableModel = {
              'id' : 'INTEGER PRIMARY KEY AUTO_INCREMENT'
               }


    id = None
        
    def getTableName(self):
        return None
    
    # defines the model
    def getTableModel(self):
        return self.databaseEntity_TableModel
    
    
    def getTableColumns(self):
        return list(self.databaseEntity_TableModel.keys())
    
    def getTableValues(self):
        if self.id == None:
            return None
        else:
            return {'id' : self.id}
    
    def setTableValues(self, values):
        self.id = values['id']
    
    def saveToDatabase(self, db):
        if self.id == None:
            self.id = db.insertRow(self.getTableName(), self.getTableValues())
        else:
            db.updateRow(self.id, self.getTableName(), self.getTableValues())
            
