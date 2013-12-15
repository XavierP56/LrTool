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
	directory = 'Files/img'
	if not os.path.exists(directory):
		os.makedirs(directory)
	
def finish():
	shutil.rmtree ('Files/img')
	


		


		