import json
import time
import random
import bottle
import bottle.ext.sqlite
from bottle import route, run, request, abort, static_file
import face
import Queue
import random
import train

app = bottle.Bottle()
plugin = bottle.ext.sqlite.Plugin(dbfile='/Users/xavierpouyollon/Documents/Imgs/test/test.lrcat')
app.install(plugin)

progress_queue = None
process_index = 0
	
@app.route('/demo/<filepath:path>')
def server_static(filepath):
	return static_file(filepath, root='./Files/')


def low_bound ( v, m):
	return v - (v%m)

def returnChart (graph, rows, totalCount, rangeCount):
	r =  {
	"type": graph,
	"displayed": True,
	  "cssStyle": "height:600px; width:100%;",
	  "data": {
		"cols": [
		  {
			"id": "Focal",
			"label": "Focal",
			"type": "string"
		  },
		  {
			"id": "Number",
			"label": "Numbers",
			"type": "number"
		  }
		],
		"rows" : rows
	  },
	  "options": {
		"title": "Focals",
		"is3D" : True,
		"isStacked": "true",
		"fill": 20,
		"displayExactValues": True
	  },
	  "formatters": {},
	  "totalCount" : totalCount,
	  "rangeCount": rangeCount
	}
	return r
		
@app.route('/graphs/<graph>/<camid>/<minFoc:int>/<maxFoc:int>/<mod:int>', method='GET')
def donne_graph(db,graph, camid,minFoc,maxFoc,mod):
	query = 'SELECT focalLength, COUNT(focalLength) FROM AgHarvestedExifMetadata WHERE cameraModelRef=:camId GROUP BY focalLength ORDER BY focalLength' 
	result = []
	resultq =  db.execute(query, {"camId":camid}).fetchall()
	#print resultq
	ix = -1
	last_foc = -1
	totalCount = 0
	rangeCount = 0
	for couple in resultq:
		if (couple[0] == None):
			continue
		totalCount += couple[1]
		foc = int (couple[0])
		if ((foc < minFoc) or (foc >= maxFoc)):
			continue
		low = low_bound(foc, mod)
		key = str(low) + '-' + str(low+mod) + ' mm'
				
		if (last_foc != low):
			ix += 1
			result.append((key, (couple[1],low, low+mod)))
			rangeCount += couple[1]
		else:
			c = result [ix]
			#print ix, c
			c = (key, (c[1][0] + couple[1], low, low+mod))
			result [ix] = c
			rangeCount += couple[1]
		last_foc = low
		
	#print result
	rows = 	[{"c": [{'v':k, 'low':v[1], 'high':v[2]}, {'v':v[0]}]} for k,v in result]
	r =  returnChart(graph, rows, totalCount,rangeCount)

	return r
		
@app.route('/cameras/models', method ='GET')
def camera_models(db):
	query = 'SELECT id_local,value FROM AgInternedExifCameraModel  ORDER BY value'
	resultq =  db.execute(query).fetchall()
	res = [{"id": e[0], "name":e[1]} for e in resultq]
	return {'cams':res}
	
@app.route('/collections/getlist', method='GET')
def getcollectionList(db):
	query = 'SELECT id_local,name FROM AgLibraryCollection  ORDER BY name'
	resultq =  db.execute(query).fetchall()
	res = [{"id": e[0], "name": e[1]} for e in resultq]	
	return {'colls': res}
		
@app.route('/collections/getImages/<colid>', method='GET')
def getcollection(db,colid):
	global progress_queue
	try:
		query = """select i.id_local, i.developSettingsIDCache ,rf.absolutePath || fo.pathFromRoot || fi.baseName || '.' || fi.extension as fullName, i.orientation 
	from Adobe_images i 
	join AgLibraryFile fi on i.rootFile = fi.id_local
	join AgLibraryFolder fo on fi.folder = fo.id_local 
	join AgLibraryRootFolder rf on fo.rootFolder = rf.id_local
	join AgLibraryCollectionImage col on col.collection =:colId  and col.image = i.id_local and i.copyName is not null"""
	
		resultq =  db.execute(query,{"colId": colid}).fetchall()
		res = [{"id_local": e[0], "developSettingsIDCache": e[1], "fullName": e[2], "orientation" : e[3]} for e in resultq]	
		return {'imgs':res}
	except:
		return []
	
@app.route('/collections/processImage', method='POST')	
def processImage(db):
	global process_index
	try:
		vpict = request.json['img']
		ok, name = face.crop (db,vpict)
		print name
		if not ok:
			return {'result':False}
		else:
			process_index += 1
			img = '/demo/img/' + str(vpict['id_local']) + '.jpg?' + str (process_index)
			return {'result' : True, 'imgSrc' : img, 'id_local':vpict['id_local'], 'recog': name}
	except:
		return {'result' : False}

@app.route('/collections/train/<IdLocal>/<name>')
def Train(db, IdLocal, name):
	train.AddTrain(name, IdLocal)
	return {'result' :True}

progress_queue = Queue.Queue(0)	
train.ReadHeads()
train.Train()

bottle.run(app, host='localhost', port=8080, server='cherrypy')
#bottle.run(app, host='localhost', port=8080)
