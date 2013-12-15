# Not used in this project. Some code for performing lookForFaces within the database.

LOOK_KEY = 1
LOOK_VALUE = 3

CROP_LEFT = 'CropLeft'
CROP_RIGHT = 'CropRight'
CROP_BOTTOM = 'CropBottom'
CROP_TOP = 'CropTop'
CROP_WIDTH = 'CropWidth'
CROP_HEIGHT = 'CropHeight'

def convert2Json (dbtext):
    res = ''
    openb = 0
    res = {}
    state = LOOK_KEY
    key = ''
    value = ''
    inarray = False
    
    for c in dbtext:
        if (c == '\n'):
            if (inarray == True):
                value += c
            continue
                
        if (c == ' '):
            if (state == LOOK_KEY):
                continue
                
        if (c == '{'):
            openb += 1    
            if (openb > 1):
                state = LOOK_VALUE
                value = '{'
                inarray = True
            continue
            
        if (c == '}'):
            openb -= 1
            if (openb == 1):
                state = LOOK_KEY
                value += '}'
                inarray = False
            continue
                
        if (c == '='):
            state = LOOK_VALUE
            continue
            
        if (c == ','):
            if (state == LOOK_VALUE) and (inarray == True):
                value += c
                continue
                
            #print key + ':' + value
            res[key] = value
            key = ''
            value = ''
            state = LOOK_KEY;
            continue
                
        if (state == LOOK_KEY):
            key += c
        if (state == LOOK_VALUE):
             value += c         
    return res
    
def convert2LR(p):
    res = 's = { '
    cnt = 0
    for k in p:
        if (cnt > 0):
            res += ',\n'
        v = p[k]
        res += k
        res += '='
        res += v
        cnt += 1
    res += ' }'
    return res


def lookForFaces(db, vpict):
    idlocal = vpict['id_local']
    devid = vpict['developSettingsIDCache']
    query = """select text from Adobe_imageDevelopSettings d where d.id_local =:devId"""
    result =  db.execute(query,{"devId": devid}).fetchall()
    resultq = result[0][0]
    if resultq != None:
        r = resultq[4:]
        res = convert2Json(r)
        #cr,name = recog(vpict)
        if (not CROP_LEFT in cr):
        #    print "NO FACE DETECTED !"
            return False,name
        res[CROP_LEFT] = cr[CROP_LEFT]
        res[CROP_RIGHT] = cr[CROP_RIGHT]
        res[CROP_BOTTOM] = cr[CROP_BOTTOM]
        res[CROP_TOP] = cr[CROP_TOP]
        cropStr = convert2LR(res)
        query = """UPDATE Adobe_imageDevelopSettings
                SET text=:cropEd , croppedWidth=:cropWidth, croppedHeight=:cropHeight 
                WHERE id_local =:devId"""
        db.execute(query,{"devId": devid, "cropEd": cropStr, "cropWidth":cr[CROP_WIDTH], "cropHeight":cr[CROP_HEIGHT]})
        #print "CROP UPDATED " + str(devid)
        return True,name
        
  