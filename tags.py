names = {}

def GetTagsList(db):
    global names
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
    names = {e[1]:e[0] for e in resultq}
    print res 
    return {'res':res}

# idlocal is the picture being tagged with name as tag
def TagThis (db, idlocal, name):
    global names
    tagid = names[name]
    # Put back in the Lightroom database
    query = """INSERT INTO AgLibraryKeywordImage(image,tag)
                 VALUES(:imageId , :tagId)
                 """
    db.execute(query,{"imageId": idlocal, "tagId": tagid})

    print "Tagge picture !"