# Copyright Xavier Pouyollon 2013
# GPL v3 License

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
import tags
import argparse
import collection

app = bottle.Bottle()
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
		"displayExactValues": True,
		"backgroundColor" : "darkgrey"
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
	join AgLibraryCollectionImage col on col.collection =:colId  and col.image = i.id_local"""
	
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
		res = face.lookForFaces (db,vpict)
		return res
	except:
		return None

@app.route('/collections/train', method='POST')
def Train(db):
	curHead = request.json['face']
	train.AddTrain(curHead)
	print 'Added to train'
	train.ReadHeads()
	train.Train()
	tags.TagThis (db, curHead)
	return {'result' :True}

@app.route('/collections/tag', method='POST')
def Tag(db):
	print 'Tag'
	curHead = request.json['face']
	tags.TagThis (db, curHead)
	return {'result' :True}
		
# Retrieve a list of names under the Faces keyword.
@app.route('/tags/getList')
def GetTagList(db):
	return tags.GetTagsList(db)

@app.route('/collections/finish')
def Finish(db):
	print 'Finish. Purge temp dir'
	face.finish()

@app.route('/collections/undetected', method='POST')
def Undetected(db):
	col = request.json['col']
	errors = request.json['errors']
	collection.MoveUndetect (db, col, errors)
	
parser = argparse.ArgumentParser()
parser.add_argument("dbpath",help="Path to .lrcat database")
args = parser.parse_args()
plugin = bottle.ext.sqlite.Plugin(dbfile=args.dbpath)
progress_queue = Queue.Queue(0)	
train.ReadHeads()
train.Train()
app.install(plugin)
bottle.run(app, host='localhost', port=8080, server='cherrypy')

