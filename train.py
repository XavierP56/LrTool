import os
import cv2

IMAGE_SIZE = 128

def AddTrain (name, id):
    headFileName = 'Files/img/' + str(id) + '.jpg'
    directory = 'Files/train/' + name
    if not os.path.exists(directory):
        os.makedirs(directory)
    # Create a miniature for recognition
    head = cv2.imread(headFileName,cv2.IMREAD_GRAYSCALE)
    head = cv2.resize(head, (IMAGE_SIZE,IMAGE_SIZE))
    headName = directory + '/' + 'head_' + str(id)  + '.jpg'
    cv2.imwrite(headName, head)