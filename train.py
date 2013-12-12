import os
import cv2
import numpy
import uuid

IMAGE_SIZE = 100

identities = []
images = []
images_index = []
model = None

def ReadHeads():
    global identities
    global images
    global images_index
    
    identities = []
    images = []
    images_index = []    
    c = 0
    ImagesPath = 'Files/train'
    for dirname, dirnames, filenames in os.walk(ImagesPath):
        for subdirname in dirnames:
            identities.append(subdirname)
            subject_path = os.path.join(dirname, subdirname)
            for filename in os.listdir(subject_path):
                    try:
                        im = cv2.imread(os.path.join(subject_path, filename), cv2.IMREAD_GRAYSCALE)
                        images.append(numpy.asarray(im, dtype=numpy.uint8))
                        images_index.append(c)
                        print 'Head read'
                    except:
                        print 'Error for' + os.path.join(subject_path, filename)
            c = c+1
    print 'Head reads !'
 
def Train():
    global identities
    global images
    global images_index
    global model
    try:
        model = cv2.createLBPHFaceRecognizer()
        #model = cv2.createEigenFaceRecognizer()
        #model = cv2.createFisherFaceRecognizer()
        model.train(numpy.asarray(images),numpy.asarray(images_index))
        print 'Training done !'
    except:
        print 'No training yet !'
                 
def AddTrain (curHead):
    headFileName = curHead['cropHead']
    directory = 'Files/train/' + curHead['name']
    if not os.path.exists(directory):
        os.makedirs(directory)
    # Create a miniature for recognition
    head = cv2.imread(headFileName,cv2.IMREAD_GRAYSCALE)
    head = cv2.resize(head, (IMAGE_SIZE,IMAGE_SIZE))
    headName = directory + '/' + 'head_' + str(uuid.uuid4())  + '.jpg'
    cv2.imwrite(headName, head)
    
def Identify (image):
    global model
    global identities
    
    try:
        imageSz = cv2.resize(image,(IMAGE_SIZE,IMAGE_SIZE))
        [pid, pconfidence] = model.predict(imageSz)
        print pid
        name = identities[pid]
        print name
        print pconfidence
        return name, pconfidence
    except:
        return None,0
 