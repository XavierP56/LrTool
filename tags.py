# Copyright Xavier Pouyollon 2013
# GPL v3 License

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

def TagThis (db, curHead):
    global names
    name = curHead['name']
    idlocal = curHead['id_img']
    tagid = names[name]
    # Do we already have it ?
    query = "SELECT id_local FROM AgLibraryKeywordImage i WHERE i.image=:imageId AND i.tag =:tagId"
    r = db.execute(query,{"imageId": idlocal, "tagId": tagid}).fetchall()
    print r
    if (len(r) == 0):
        print "Tagge picture !"
        # Put back in the Lightroom database
        query = """INSERT INTO AgLibraryKeywordImage(image,tag)
                     VALUES(:imageId , :tagId)
                     """
        db.execute(query,{"imageId": idlocal, "tagId": tagid})
    else:
        print 'Tag already there'

