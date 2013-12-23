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

index = 0


confirmCascades = []
faceCascade = None

def Raw2Jpg (vpict):
	filepath = vpict['fullName']					
	dcraw_opts = ["/usr/local/bin/dcraw", "-e", "-c", filepath]
	dcraw_proc = Popen(dcraw_opts, stdout=PIPE)
	image = dcraw_proc.communicate()[0]
	f = open ('/tmp/lr.jpg', 'wb')
	f.write(image)
	f.close()

def rotateImage(image,angle):
	dst = cv2.transpose(image)
	res = cv2.flip(dst,0)
	return res
 	
def ConfirmHead(img):
	global confirmCascades
	res = False
	for c in confirmCascades:
		v = c.detectMultiScale(img)
		detected = len(v) > 0
		res = res or detected
	print res
	return res
	

def ComputeScale(width, height):
	if (width > height):
		scale = width / 640
	else:
		scale = height / 480
	return scale

def recog(vpict):
	global index
	global faceCascade
	
	Raw2Jpg(vpict)
	# Make a small version in colorFull.
	colorFull = cv2.imread('/tmp/lr.jpg')
	width = colorFull.shape[1]
	height = colorFull.shape[0]
	scale = ComputeScale (width, height)
	sz = (width / scale, height / scale)
	colorSmall = cv2.resize(colorFull,sz)
	if (vpict['orientation'] == 'DA'):
		colorSmall = rotateImage(colorSmall, 90)
	colorspath = 'img/color_' + str(uuid.uuid4()) + '.jpg'
	cv2.imwrite('Files/'+colorspath, colorSmall)
	
	grayFull = cv2.cvtColor(colorFull, cv2.COLOR_BGR2GRAY)
	graySmall = cv2.cvtColor(colorSmall, cv2.COLOR_BGR2GRAY)

	detectFace = faceCascade.detectMultiScale(graySmall,scaleFactor=1.1,minNeighbors=3)

	print 'Faces:' + str(len(detectFace))
	imgCrop = None
	faces = []
	found = 0
	
	for face in detectFace:	
		imgCrop = colorSmall[face[1]:face[1]+face[3], face[0]:face[0]+face[2]]
		if (ConfirmHead(imgCrop) == False):
			imgCrop = None
			continue
		# We can safely assume it is an head for this image.
		basepath = 'img/head_' + str(uuid.uuid4()) + '.jpg'
		fname = 'Files/' + basepath
		htmlpath =  basepath
		cv2.imwrite(fname,imgCrop)
		found += 1
		myname, confid = train.Identify(imgCrop)
		# Try to make it a percentage...
		confid = int(confid)
		if (confid > 100):
			confid = 100
		confid = 100 - confid
		face = { "name": myname, "headPict":fname, "headPath":htmlpath, "confid":confid}
		faces.append(face)

	result = {"id_img":vpict['id_local'], "colorpath":colorspath, "detect":faces}
	print "Found faces " + str (found)
	print result
	return result
	
def lookForFaces(db, vpict):
	init()
	idlocal = vpict['id_local']
	devid = vpict['developSettingsIDCache']
	query = """select text from Adobe_imageDevelopSettings d where d.id_local =:devId"""
	result =  db.execute(query,{"devId": devid}).fetchall()
	resultq = result[0][0]
	if resultq != None:
		r = resultq[4:]
		res = recog(vpict)
		return res;
	else:
		return None

def init():
	global confirmCascades
	global faceCascade
	
	directory = 'Files/img'
	if not os.path.exists(directory):
		os.makedirs(directory)
	# Load the confirm cascades
	Cascades = ["/usr/local/share/OpenCV/haarcascades/haarcascade_eye.xml",
				"/usr/local/share/OpenCV/haarcascades/haarcascade_mcs_nose.xml",
				"/usr/local/share/OpenCV/haarcascades/haarcascade_mcs_mouth.xml"
				]
	for c in Cascades:
		confirmCascades.append(cv2.CascadeClassifier(c))
	# Load the face cascade
	faceCascade = cv2.CascadeClassifier("/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_alt2.xml")
				
def finish():
	shutil.rmtree ('Files/img')
	


		


		