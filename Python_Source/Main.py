#############################################################################
# 				Documentation				    #
#############################################################################

"""A WebApi for SKBank facerecognizer to select image that achieve our standard.

"""
import sys
import cv2
import dlib
import os
import re
import numpy as np
from flask import Flask, request, jsonify

# Use Flask Object to set web framework.
app = Flask(__name__)

# Setting the route url for page "index".
@app.route('/') 
def index():
	return 'This is for pictures select'

# Set the route url for page "SelectPictures" and set http request method into "GET".
@app.route('/skb/api/v1.0/imgselect', methods=['GET'])
def SelectPictures():
	# Through HTTP GET to load the img on server. 
	img = cv2.imread("C:\\WWWRoot\\IMGUP\\images\\" + request.args.get('filename'))
	# Get the result about if use the picture and its clearness.
	acceptable, clearness = GetFace(img)
	return jsonify({'acceptable': acceptable, 'clearness': clearness}), 200
	
def GetFace(img):
	detector = dlib.get_frontal_face_detector()
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	angle = 0
	Flag = 0
	# Because the picture upload by phone will let picutre horizontal, need to turn angle al least two times.
	for times in range(2):
		(h, w) = img.shape[:2]
		center = (w / 2, h / 2)
		M = cv2.getRotationMatrix2D(center, angle, 1.0)
		img = cv2.warpAffine(img, M, (w, h))
		
		try:
			dets = detector(img, 1)
			# Get the face information. i = face count. d = face locat.
			for i, d in enumerate(dets):
				x1 = d.top() if d.top() > 0 else 0
				y1 = d.bottom() if d.bottom() > 0 else 0
				x2 = d.left() if d.left() > 0 else 0
				y2 = d.right() if d.right() > 0 else 0

				if i <= 0:
					x = 0
					face = img[x1:y1,x2:y2]
					face = cv2.resize(face, (224,224))
				else:
					x = 1

			if x == 0:
				acept, clear = DpiCheck(face)
				if acept == True:
					flag = True
					break
		except:
			angle -= 90
			continue		
				
	(h, w) = img.shape[:2]
	center = (w / 2, h / 2)
	M = cv2.getRotationMatrix2D(center, angle, 1.0)
	img = cv2.warpAffine(img, M, (w, h))	

	try:
		dets = detector(img, 1)

		for i, d in enumerate(dets):
			x1 = d.top() if d.top() > 0 else 0
			y1 = d.bottom() if d.bottom() > 0 else 0
			x2 = d.left() if d.left() > 0 else 0
			y2 = d.right() if d.right() > 0 else 0

			if i <= 0:
				x = 0
				face = img[x1:y1,x2:y2]
				face = cv2.resize(face, (224,224))
			else:
				x = 1

		if x == 0:
			acept, clear = DpiCheck(face)
			return acept, clear
		else:
			return False, "Can't find face"
	except:
		return False, "Can't find face"


def DpiCheck(img):
	"""Will calculate the clearness of pictures, and check if picture achieve goal."""
	blur=cv2.GaussianBlur(img,(5,5),0)
	img=cv2.addWeighted(img,1.5,blur,-0.5,0)

	x = cv2.Sobel(img, cv2.CV_16S,1,0)
	y = cv2.Sobel(img, cv2.CV_16S,0,1)

	absX = cv2.convertScaleAbs(x)
	absY = cv2.convertScaleAbs(y)

	dst = cv2.addWeighted(absX, 0.5, absY, 0.5, 0)
	sobel = cv2.addWeighted(absX, 0.5, absY, 0.5, 0).var()
	# Set your standard of clearness.
	if sobel > 700:
		return True, sobel
	else:
		return False, sobel	
	
if __name__ == '__main__':
	app.run()
