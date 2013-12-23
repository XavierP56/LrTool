# Copyright Xavier Pouyollon 2013
# GPL v3 License

def CreateNewCollection(db, col):
    name = col['name']
    id = col['id']
    newName = name + '-noFaces'
    print "Creating new collection {0}".format(newName)
    # Get the current entry for the collection
    query = "SELECT * FROM AgLibraryCollection a WHERE a.id_local = :colId"
    resultq =  db.execute(query,{"colId": id}).fetchone()
    print resultq
    # Create a new entry from it
    query = "INSERT INTO AgLibraryCollection VALUES(NULL,:c1, :c2, :c3, :c4, :c5, :c6)"
    res = db.execute(query,{"c1":resultq[1],
                            "c2": resultq[2] + '/1', 
                            "c3": resultq[3],
                            "c4": newName,
                            "c5": resultq[5],
                            "c6": resultq[6]})
    newId = res.lastrowid
    return newId
    
def MoveUndetect(db, col, list):
    print "Moving to undetect"
    newId = CreateNewCollection(db, col)
    # For all errors, add them in newId
    for entry in list:
        query = 'INSERT INTO AgLibraryCollectionImage VALUES(NULL,:colId,:imgId,0,NULL)'
        res = db.execute(query,{"colId": newId, 
                                "imgId": entry['id']})