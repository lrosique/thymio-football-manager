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
import os

from flask import Flask, jsonify
app = Flask(__name__)

if not os.path.exists("data"):
    os.makedirs("data")
if not os.path.exists("output"):
    os.makedirs("output")

positions = None
crops = None
angles = None

hsv_green={"low":(30, 50, 0),"high":(80, 255,255)}
hsv_orange={"low":(5, 80, 100),"high":(28, 255,255)}
parameters_fields_hd={"canny_min_threshold":250, "canny_max_threshold":400, "threshold_min":200, "threshold_max":255, "erode_iter":5, "dilate_iter":10, "number_pixels_per_field":50000 }
parameters_fields_ld={"canny_min_threshold":150, "canny_max_threshold":300, "threshold_min":150, "threshold_max":255, "erode_iter":2, "dilate_iter":4, "number_pixels_per_field":5000 }
parameters_image_ld={"threshold_min":100, "threshold_max":255, "number_pixels_per_field":2}
#parameters_image_ld={"canny_min_threshold":150, "canny_max_threshold":300, "threshold_min":150, "threshold_max":255, "erode_iter":2, "dilate_iter":4, "number_pixels_per_field":5000 }

def get_image(name,url):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(name, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f) 

def calibrate_football_fields(path_img, parameters, save_img=False):
    positions = []
    angles = []
    img = cv2.imread(path_img)
    if img is None:
        raise Exception("Calibration non trouvée : "+path_img)

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    if save_img: cv2.imwrite('output/gray.png', gray)

    edges = cv2.Canny(gray,parameters["canny_min_threshold"],parameters["canny_max_threshold"])
    if save_img: cv2.imwrite('output/edges.png', edges)

    blurred = cv2.GaussianBlur(gray, (25, 25), 0)
    if save_img: cv2.imwrite('output/blurred.png', blurred)

    thresh = cv2.threshold(blurred, parameters["threshold_min"], parameters["threshold_max"], cv2.THRESH_BINARY)[1]
    if save_img: cv2.imwrite('output/thresh.png', thresh)

    thresh = cv2.erode(thresh, None, iterations=parameters["erode_iter"])
    thresh = cv2.dilate(thresh, None, iterations=parameters["dilate_iter"])
    if save_img: cv2.imwrite('output/thresh2.png', thresh)

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

    cv2.imwrite('output/rectangles.png', rectangles)
    return positions,angles

def find_x_y_rectangle(box):
    x0,y0 = np.min(box,axis=0)
    x1,y1 = np.max(box,axis=0)
    return x0,x1,y0,y1

def crop_rotate_image(positions,angles,path_img,save_img=False):
    img = cv2.imread(path_img)
    if img is None:
        raise Exception("Crop non trouvé : "+path_img)
    crops = []
    for i in range(0,len(positions)):
        x0,x1,y0,y1 = find_x_y_rectangle(positions[i])
        crop_img = img[y0:y1, x0:x1]
        crops.append([x0,x1,y0,y1])
        rows,cols,chan = crop_img.shape
        M = cv2.getRotationMatrix2D((cols/2,rows/2),angles[i]-180,1)
        rotate_img = cv2.warpAffine(crop_img,M,(cols,rows))
        if save_img: 
            if not os.path.exists("output/field_"+str(i)):
                os.makedirs("output/field_"+str(i))
            cv2.imwrite('output/field_'+str(i)+'/field_'+str(i)+'.png', rotate_img)
    return crops

def filter_by_team(path_img,parameters_hsv,name):
    img = cv2.imread(path_img)
    if img is None:
        raise Exception("Filter_team non trouvé : "+path_img)
    ## convert to hsv
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    ## mask of green (36,0,0) ~ (70, 255,255)
    mask = cv2.inRange(hsv, parameters_hsv["low"], parameters_hsv["high"])
    ## slice the green
    imask = mask>0
    img_team = np.zeros_like(img, np.uint8)
    img_team[imask] = img[imask]
    ## save 
    cv2.imwrite(name, img_team)
    
def count_dots_thymio(path_img, parameters, name, path_folder, number):
    gray = cv2.imread(path_img, 0)
    if gray is None:
        raise Exception("Count_dots non trouvé : "+path_img)
    ## threshold
    th =255- cv2.threshold(gray, parameters['threshold_min'], parameters['threshold_max'],cv2.THRESH_BINARY_INV|cv2.THRESH_OTSU)[1]
    cv2.imwrite(path_folder+"/"+name+"_thymio_"+number+".png", th)
    ## findcontours
    _,cnts,_ = cv2.findContours(th, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    ## filter by area
    s1= 0
    s2 = 20
    xcnts = []
    for cnt in cnts:
        if s1<cv2.contourArea(cnt) <s2:
            xcnts.append(cnt)
    return xcnts

def find_thymios(path_img, path_thresh, parameters, name, path_folder):
    img=cv2.imread(path_img)
    src=img.copy()
    if img is None:
        raise Exception("Find_thymios non trouvé : "+path_img)
    
    gray = cv2.imread(path_img, 0)
    th =255- cv2.threshold(gray, parameters['threshold_min'], parameters['threshold_max'],cv2.THRESH_BINARY_INV|cv2.THRESH_OTSU)[1]
    cv2.imwrite(path_thresh, th)
    
    thresh = 255-cv2.imread(path_thresh,0)
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

    # find the contours in the mask, then sort them from left to right
    mask = 255-mask
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    
    centers=[]
    rectangles = img
    if cnts != None and len(cnts) > 0:
        cnts = contours.sort_contours(cnts)[0]
        # loop over the contours
        for (i, c) in enumerate(cnts):
            ((cX, cY), radius) = cv2.minEnclosingCircle(c)
            rect = cv2.minAreaRect(c)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(rectangles,[box],0,(0,0,255),2)
            #cv2.putText(img,name+' '+str(i), (max(0,int(cX)-50),int(cY)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
            
            mask = np.zeros(src.shape[:2],np.uint8)
            cv2.drawContours(mask, [c],-1, 255, -1)
            dst = cv2.bitwise_and(src, src, mask=mask)
            cv2.imwrite(path_folder+"/"+name+"_thymio_"+str(i)+".png", dst)
            
            centers.append([int(cX),int(cY)])
            angles.append(rect[2])

    #find_x_y_rectangle(positions[0])
    cv2.imwrite(path_folder+'/rectangles_team_'+name+'.png', rectangles)
    return centers

@app.route('/calibration/football_field', methods=['GET', 'POST'])
def get_calibrate_football_fields():
    global positions,parameters_fields,crops,angles
    path_img = "data/calibration_ld.png"
    get_image(path_img,"http://192.168.1.60:1880/calibration")
    positions,angles = calibrate_football_fields(path_img,parameters_fields_ld)
    crops = crop_rotate_image(positions,angles,path_img)
    return jsonify(positions=positions, crops=crops)    

@app.route('/calibration/image', methods=['GET', 'POST'])
def get_calibrate_image():
    global positions,parameters_fields,crops,angles
    path_img = "data/image_ld.png"
    get_image(path_img,"http://192.168.1.60:1880/image")
    crops = crop_rotate_image(positions,angles,path_img)
    return jsonify(positions=positions, crops=crops) 

@app.route('/football_field', methods=['GET', 'POST'])
def get_football_fields():
    global positions,crops
    return jsonify(positions=positions,crops=crops)







# CALIBRATION
path_img = "data/calibration_ld.png"
positions,angles = calibrate_football_fields(path_img,parameters_fields_ld)
crops = crop_rotate_image(positions,angles,path_img)

# GET IMAGE
path_img = "data/image_ld.png"
crops = crop_rotate_image(positions,angles,path_img,save_img=True)


# TEST 1 FIELD
i = 1
path_folder = "output/field_"+str(i)
path_img = path_folder+"/field_"+str(i)+".png"

filter_by_team(path_img,hsv_green,path_folder+"/team_green.png")
filter_by_team(path_img,hsv_orange,path_folder+"/team_orange.png")

centers_green=find_thymios(path_folder+"/team_green.png",path_folder+"/thresh_team_green.png",parameters_image_ld,"green",path_folder)
centers_orange=find_thymios(path_folder+"/team_orange.png",path_folder+"/thresh_team_orange.png",parameters_image_ld,"orange",path_folder)

j = 0
numero_thymio_green = len(count_dots_thymio(path_folder+"/green_thymio_"+str(j)+".png",parameters_image_ld,"green",path_folder,str(j)))
numero_thymio_orange = len(count_dots_thymio(path_folder+"/orange_thymio_"+str(j)+".png",parameters_image_ld,"orange",path_folder,str(j)))



# FILTER TEAM
total_results = []
for i in range(len(crops)):
    field = {"number":i}   
    path_folder = "output/field_"+str(i)
    path_img = path_folder+"/field_"+str(i)+".png"
    filter_by_team(path_img,hsv_green,path_folder+"/team_green.png")
    filter_by_team(path_img,hsv_orange,path_folder+"/team_orange.png")

    centers_green=find_thymios(path_folder+"/team_green.png",path_folder+"/thresh_team_green.png",parameters_image_ld,"green",path_folder)
    centers_orange=find_thymios(path_folder+"/team_orange.png",path_folder+"/thresh_team_orange.png",parameters_image_ld,"orange",path_folder)

    greens = []
    oranges = []
    for j in range(len(centers_green)):
        center_position = centers_green[j]
        numero = len(count_dots_thymio(path_folder+"/green_thymio_"+str(j)+".png",parameters_image_ld,"green",path_folder,str(j)))
        greens.append((numero,center_position))
    
    for j in range(len(centers_orange)):
        center_position = centers_orange[j]
        numero = len(count_dots_thymio(path_folder+"/orange_thymio_"+str(j)+".png",parameters_image_ld,"orange",path_folder,str(j)))
        oranges.append((numero,center_position))
    
    field["team_green"]=greens
    field["team_orange"]=oranges
    total_results.append(field)

print(total_results)


# Méthode TEST CONFIGURATION (avec des assert par rapport à ce qu'on a placé)
# Revoir pour que ça détecte correctement...
# Revoir pour générer beaucoup moins d'images
# Simplifier le code !