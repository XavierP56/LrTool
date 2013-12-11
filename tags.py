

def GetTagsList(db):
    # Retrive the base genealogy
    query = "SELECT genealogy FROM AgLibraryKeyword i WHERE i.name = 'Faces'"
    resultq =  db.execute(query).fetchone()
    gene = str(resultq[0])
    genea = gene + '/%'
    print genea
    # Retrieve the list of names descendant of it
    query = 'SELECT id_local, lc_name FROM AgLibraryKeyword i WHERE i.genealogy LIKE :genEA'
    resultq = db.execute(query, {"genEA": genea}).fetchall()
    res = [{"id": e[0], "name": e[1]} for e in resultq]   
    print res 
    return {'res':res}