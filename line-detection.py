# -*- coding: utf-8 -*-
# pip3 install opencv-python
# pip3 install numpy
# pip3 install imutils
# pip3 install scikit-image
# pip3 install flask
# pip3 install requests
# pip3 install scipy

import cv2
import numpy as np
from imutils import contours
from skimage import measure
import imutils
import requests
import shutil

from flask import Flask, jsonify
app = Flask(__name__)

path_img = 'data/image1.png'
positions = None
crops = []
parameters_fields={
            "canny_min_threshold":250,
            "canny_max_threshold":400,
            "threshold_min":200,
            "threshold_max":255,
            "erode_iter":5,
            "dilate_iter":10,
            "number_pixels_per_field":50000
            }

def get_image(name,url):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(name, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f) 

def calibrateFootballField(path_img, parameters):
    positions = []
    angles = []
    img = cv2.imread(path_img)

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    cv2.imwrite('output/gray.jpg', gray)

    edges = cv2.Canny(gray,parameters["canny_min_threshold"],parameters["canny_max_threshold"])
    cv2.imwrite('output/edges.jpg', edges)

    blurred = cv2.GaussianBlur(gray, (25, 25), 0)
    cv2.imwrite('output/blurred.jpg', blurred)

    thresh = cv2.threshold(blurred, parameters["threshold_min"], parameters["threshold_max"], cv2.THRESH_BINARY)[1]
    cv2.imwrite('output/thresh.jpg', thresh)

    thresh = cv2.erode(thresh, None, iterations=parameters["erode_iter"])
    thresh = cv2.dilate(thresh, None, iterations=parameters["dilate_iter"])
    cv2.imwrite('output/thresh2.jpg', thresh)

    labels = measure.label(thresh, neighbors=8, background=0)
    mask = np.zeros(thresh.shape, dtype="uint8")

    # loop over the unique components
    for label in np.unique(labels):
        # if this is the background label, ignore it
        if label == 0:
            continue

        # otherwise, construct the label mask and count the
        # number of pixels
        labelMask = np.zeros(thresh.shape, dtype="uint8")
        labelMask[labels == label] = 255
        numPixels = cv2.countNonZero(labelMask)

        # if the number of pixels in the component is sufficiently
        # large, then add it to our mask of "large blobs"
        if numPixels > parameters["number_pixels_per_field"]:
            mask = cv2.add(mask, labelMask)

    # find the contours in the mask, then sort them from left to
    # right
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    cnts = contours.sort_contours(cnts)[0]

    # loop over the contours
    rectangles = img
    for (i, c) in enumerate(cnts):
        ((cX, cY), radius) = cv2.minEnclosingCircle(c)
        rect = cv2.minAreaRect(c)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(rectangles,[box],0,(0,0,255),2)
        cv2.putText(img,'Terrain '+str(i), (max(0,int(cX)-70),int(cY)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        
        positions.append(box)
        angles.append(rect[2])

    cv2.imwrite('output/rectangles.jpg', rectangles)
    return positions,angles

def crop_rotate_image(positions,angles,path_img):
    img = cv2.imread(path_img)
    crops = []
    for i in range(0,len(positions)):
        x0 = positions[i][0][0]
        x1 = x0
        y0 = positions[i][0][1]
        y1 = y0
        for j in range(1,len(positions[i])):
            if positions[i][j][0] < x0:
                x0 = positions[i][j][0]
            if positions[i][j][0] > x1:
                x1 = positions[i][j][0]
            if positions[i][j][1] < y0:
                y0 = positions[i][j][1]
            if positions[i][j][1] > y1:
                y1 = positions[i][j][1]
        crop_img = img[y0:y1, x0:x1]
        crops.append([x0,x1,y0,y1])
        rows,cols,chan = crop_img.shape
        M = cv2.getRotationMatrix2D((cols/2,rows/2),angles[i]-180,1)
        rotate_img = cv2.warpAffine(crop_img,M,(cols,rows))
        cv2.imwrite('output/field_'+str(i)+'.jpg', rotate_img)
    return crops

@app.route('/calibration/football_field', methods=['GET', 'POST'])
def calibrate_center_football_field():
    global positions,parameters_fields,crops
    path_img = "data/calibration.png"
    get_image(path_img,"http://192.168.1.60:1880/calibration")
    positions,angles = calibrateFootballField(path_img,parameters_fields)
    crops = crop_rotate_image(positions,angles,path_img)
    return jsonify(positions=positions, crops=crops)    

@app.route('/calibration/image', methods=['GET', 'POST'])
def calibrate_image():
    global positions,parameters_fields,crops
    path_img = "data/image.png"
    get_image(path_img,"http://192.168.1.60:1880/image")
    #positions,angles = calibrateFootballField(path_img,parameters_fields)
    #crops = crop_rotate_image(positions,angles,path_img)
    return jsonify(positions=positions, crops=crops) 

@app.route('/football_field', methods=['GET', 'POST'])
def get_center_football_field():
    global center_football_field,crops
    return jsonify(positions=positions,crops=crops)
