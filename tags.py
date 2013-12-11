

def GetTagsList(db):
    # Retrive the base genealogy
    query = "SELECT genealogy FROM AgLibraryKeyword i WHERE i.name = 'Faces'"
    resultq =  db.execute(query).fetchone()
    gene = str(resultq[0])
    genea = gene + '/%'
    print genea
    # Retrieve the list of names descendant of it
    query = 'SELECT * FROM AgLibraryKeyword i WHERE i.genealogy LIKE :genEA'
    resultq = db.execute(query, {"genEA": genea}).fetchall()
    print resultq
    return {'res':'ok'}