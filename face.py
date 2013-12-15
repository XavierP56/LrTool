# Copyright Xavier Pouyollon 2013
# GPL v3 License

import cv2
import numpy as np
import getopt
import sys
from subprocess import Popen, PIPE
from StringIO import StringIO
import time
import train
import uuid
import shutil
import os

scale = 5

LOOK_KEY = 1
LOOK_VALUE = 3

CROP_LEFT = 'CropLeft'
CROP_RIGHT = 'CropRight'
CROP_BOTTOM = 'CropBottom'
CROP_TOP = 'CropTop'
CROP_WIDTH = 'CropWidth'
CROP_HEIGHT = 'CropHeight'

index = 0

def Raw2Jpg (vpict):
	filepath = vpict['fullName']					
	dcraw_opts = ["/usr/local/bin/dcraw", "-e", "-c", filepath]
	dcraw_proc = Popen(dcraw_opts, stdout=PIPE)
	image = dcraw_proc.communicate()[0]
	f = open ('/tmp/lr.jpg', 'wb')
	f.write(image)
	f.close()

def rotateImage(image, angle):
  image_center = ((image.shape[1]-1)/2, (image.shape[1]-1)/2)
  rot_mat = cv2.getRotationMatrix2D(image_center,angle,1.0)
  result = cv2.warpAffine(image, rot_mat, image.shape,flags=cv2.INTER_LINEAR)
  return result
 	
def findeyes(img):
	eyeCascade = cv2.CascadeClassifier("/usr/local/share/OpenCV/haarcascades/haarcascade_eye.xml")
	detectEyes = eyeCascade.detectMultiScale(img)
	return len(detectEyes)

def recog(vpict):
	global index
	
	Raw2Jpg(vpict)
	# Make a small version in color.
	color = cv2.imread('/tmp/lr.jpg')
	colors = cv2.resize(color,(640,480))
	#if (vpict['orientation'] == 'DA'):
	#	colors = rotateImage(colors, 90)
	colorspath = 'img/color_' + str(uuid.uuid4()) + '.jpg'
	cv2.imwrite('Files/'+colorspath, colors)
	
	imgf = cv2.imread('/tmp/lr.jpg',cv2.IMREAD_GRAYSCALE)
	width = imgf.shape[1]
	height = imgf.shape[0]
	sz = (width / scale, height / scale)
	img = cv2.resize(imgf,sz)
 	if (vpict['orientation'] == 'DA'):
 		img = rotateImage(img, 90)
 		width = imgf.shape[0]
 		height = imgf.shape[1]

	faceCascade = cv2.CascadeClassifier("/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_alt2.xml")
	detectFace = faceCascade.detectMultiScale(img,scaleFactor=1.1,minNeighbors=3)

	print 'Faces:' + str(len(detectFace))
	imgCrop = None
	faces = []
	found = 0
	
	for face in detectFace:	
		imgCrop = img[face[1]:face[1]+face[3], face[0]:face[0]+face[2]]
		if (findeyes(imgCrop) == 0):
			imgCrop = None
			continue
		# We can safely assume it is an head for this image.
		basepath = 'img/head_' + str(uuid.uuid4()) + '.jpg'
		fname = 'Files/' + basepath
		htmlpath =  basepath
		cv2.imwrite(fname,imgCrop)
		found += 1
		myname, confid = train.Identify(imgCrop)
		face = { "name": myname, "headPict":fname, "headPath":htmlpath}
		faces.append(face)

	result = {"id_img":vpict['id_local'], "colorpath":colorspath, "detect":faces}
	print "Found faces " + str (found)
	print result
	return result
	
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
	
def crop(db, vpict):
	init()
	idlocal = vpict['id_local']
	devid = vpict['developSettingsIDCache']
	query = """select text from Adobe_imageDevelopSettings d where d.id_local =:devId"""
	result =  db.execute(query,{"devId": devid}).fetchall()
	resultq = result[0][0]
	if resultq != None:
		r = resultq[4:]
		res = convert2Json(r)
		res = recog(vpict)
		return res;
	else:
		return None

def init():
	directory = 'Files/img'
	if not os.path.exists(directory):
		os.makedirs(directory)
	
def finish():
	shutil.rmtree ('Files/img')
	
# 		res[CROP_LEFT] = cr[CROP_LEFT]
# 		res[CROP_RIGHT] = cr[CROP_RIGHT]
# 		res[CROP_BOTTOM] = cr[CROP_BOTTOM]
# 		res[CROP_TOP] = cr[CROP_TOP]
# 		cropStr = convert2LR(res)
# 		query = """UPDATE Adobe_imageDevelopSettings
# 				SET text=:cropEd , croppedWidth=:cropWidth, croppedHeight=:cropHeight 
# 				WHERE id_local =:devId"""
# 		db.execute(query,{"devId": devid, "cropEd": cropStr, "cropWidth":cr[CROP_WIDTH], "cropHeight":cr[CROP_HEIGHT]})
		#print "CROP UPDATED " + str(devid)

		


		