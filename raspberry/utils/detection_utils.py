# -*- coding: utf-8 -*-
import utils.file_utils as fu
import cv2
import numpy as np
from imutils import contours
from skimage import measure
import imutils
import math

def convert_rgb_to_hsv(r,g,b, delta=5):
    target_color = np.uint8([[[b, g, r]]])
    target_color_hsv = cv2.cvtColor(target_color, cv2.COLOR_BGR2HSV)
    target_color_h = target_color_hsv[0,0,0]

    lower_hsv = np.array([max(0, target_color_h - delta), 10, 10])
    upper_hsv = np.array([min(179, target_color_h + delta), 250, 250])

    return target_color_h, lower_hsv, upper_hsv

def calibrate_football_fields(img, parameters):
    if img is None:
        raise Exception("[Error] calibrate_football_fields")

    fu.save_image(img,'data/calibration.png')
    positions = []
    angles = []
    rectangles = np.copy(img)

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    fu.save_image(gray,'output/gray.png')

    blurred = cv2.GaussianBlur(gray, (25, 25), 0)
    fu.save_image(blurred,'output/blurred.png')

    thresh = cv2.threshold(blurred, parameters["threshold_min"], parameters["threshold_max"], cv2.THRESH_BINARY)[1]
    fu.save_image(thresh,'output/thresh.png')

    thresh = cv2.erode(thresh, None, iterations=parameters["erode_iter"])
    thresh = cv2.dilate(thresh, None, iterations=parameters["dilate_iter"])
    fu.save_image(thresh,'output/thresh2.png')

    labels = measure.label(thresh, neighbors=8, background=0)
    mask = np.zeros(thresh.shape, dtype="uint8")

    # loop over the unique components
    for label in np.unique(labels):
        # if this is the background label, ignore it
        if label == 0:
            continue

        # otherwise, construct the label mask and count the number of pixels
        labelMask = np.zeros(thresh.shape, dtype="uint8")
        labelMask[labels == label] = 255
        numPixels = cv2.countNonZero(labelMask)

        # if the number of pixels in the component is sufficiently large, then add it to our mask of "large blobs"
        if numPixels > parameters["number_pixels_per_field"]:
            mask = cv2.add(mask, labelMask)

    # find the contours in the mask, then sort them from left to right
    cnts = cv2.findContours(np.copy(mask), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    cnts = contours.sort_contours(cnts)[0]

    # loop over the contours
    for (i, c) in enumerate(cnts):
        ((cX, cY), radius) = cv2.minEnclosingCircle(c)
        rect = cv2.minAreaRect(c)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(rectangles,[box],0,(0,0,255),2)
        cv2.putText(rectangles,'Terrain '+str(i), (max(0,int(cX)-70),int(cY)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

        positions.append(box)
        angles.append(rect[2])

    fu.save_image(rectangles,'output/field_detection.png')
    return positions,angles

def find_x_y_rectangle(box):
    x0,y0 = np.min(box,axis=0)
    x1,y1 = np.max(box,axis=0)
    return x0,x1,y0,y1

def crop_rotate_image(img,positions,angles):
    if img is None:
        raise Exception("[Error] crop_rotate_image")
    crops = []
    crops_img = []
    for i in range(0,len(positions)):
        x0,x1,y0,y1 = find_x_y_rectangle(positions[i])
        crop_img = img[y0:y1, x0:x1]
        crops.append([x0,x1,y0,y1])
        rows,cols,chan = crop_img.shape
        if rows > 0 and cols > 0:
            M = cv2.getRotationMatrix2D((cols/2,rows/2),angles[i]-180,1)
            rotate_img = cv2.warpAffine(crop_img,M,(cols,rows))

            fu.save_image(rotate_img,'output/field_'+str(i)+'/field_'+str(i)+'.png')
            crops_img.append(rotate_img)
    return crops, crops_img

def filter_by_team(img,parameters_hsv):
    ## convert to hsv
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    ## mask of green (36,0,0) ~ (70, 255,255)
    mask = cv2.inRange(hsv, parameters_hsv["low"], parameters_hsv["high"])
    ## slice the green
    imask = mask>0
    img_team = np.zeros_like(img, np.uint8)
    img_team[imask] = img[imask]
    return img_team

def find_thymios(img,parameters,angles,path_folder,team_name):
    details=[]
    src=np.copy(img)
    rectangles = np.copy(img)
    
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    th =255- cv2.threshold(gray, parameters['threshold_min'], parameters['threshold_max'],cv2.THRESH_BINARY_INV|cv2.THRESH_OTSU)[1]
    fu.save_image(th,path_folder+"/teams/thresh_team_"+team_name+".png")
    thresh = 255-th
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
    cnts = cv2.findContours(np.copy(mask), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]

    centers=[]
    if cnts != None and len(cnts) > 0:
        cnts = contours.sort_contours(cnts)[0]
        # loop over the contours
        cpt = 0
        for (i, c) in enumerate(cnts):
            ((cX, cY), radius) = cv2.minEnclosingCircle(c)
            if radius >= parameters["min_radius"]  and radius <= parameters["max_radius"] :
                rect = cv2.minAreaRect(c)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                cv2.drawContours(rectangles,[box],0,(0,0,255),2)

                x_max = max(abs(box[0][0]-box[1][0]),abs(box[0][0]-box[3][0]))
                y_max = max(abs(box[0][1]-box[1][1]),abs(box[0][1]-box[3][1]))
                if x_max != 0 and y_max != 0:  
                    mask = np.zeros(src.shape[:2],np.uint8)
                    cv2.drawContours(mask, [c],-1, 255, -1)
                    dst = cv2.bitwise_and(src, src, mask=mask)
                    fu.save_image(th,path_folder+"/details/"+team_name+"_thymio_"+str(cpt)+".png")
                    details.append(dst)
    
                    centers.append([int(cX),int(cY)])
                    cpt += 1

    fu.save_image(rectangles,path_folder+"/detections_team_"+team_name+".png")
    return centers,details

def distance(x,y):
    return math.sqrt((x[1]-x[0])**2 + (y[1]-y[0])**2)

def count_dots_thymio(img, center_position, parameters, path_img):
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    ## threshold
    th =255- cv2.threshold(gray, parameters['threshold_min'], parameters['threshold_max'],cv2.THRESH_BINARY_INV|cv2.THRESH_OTSU)[1]
    fu.save_image(th,path_img)
    ## findcontours
    _,cnts,_ = cv2.findContours(th, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    ## filter by area
    s1= 0
    s2 = 20
    xcnts = []
    rectangles = np.copy(img)
    # loop over the contours
    farther_dot = None
    farther_distance = None
    farther_box = None
    for (i, c) in enumerate(cnts):
        if s1<cv2.contourArea(c) <s2:
            xcnts.append(c)
            ((cX, cY), radius) = cv2.minEnclosingCircle(c)
            rect = cv2.minAreaRect(c)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(rectangles,[box],0,(0,0,255),1)
            dist_center_dot = distance((int(cX), int(cY)),center_position)
            if farther_dot is None or dist_center_dot > farther_distance:
                farther_distance = dist_center_dot
                farther_dot = (int(cX),int(cY))
                farther_box = box
    if farther_box is not None:
        cv2.drawContours(rectangles,[box],0,(0,255,0),1)
    fu.save_image(rectangles,path_img)
    return xcnts, farther_dot

def determine_direction(farther_dot, center_position):
    sens = ""
    if farther_dot is not None:
        if farther_dot[1] > center_position[1]:
            sens += "haut"
        elif farther_dot[1] == center_position[1]:
            sens += "vertical"
        else:
            sens += "bas"
        sens += "-" 
        if farther_dot[0] > center_position[0]:
            sens += "droite"
        elif farther_dot[0] == center_position[0]:
            sens += "horizontal"
        else:
            sens += "gauche"
    return sens

def analyse_all_fields(angles,positions,hsv,parameters_thymio_ld,parameters_dots_ld,crops_img):
    total_results = []
    results = "### RESULTS ###\r\n"
    for i in range(len(crops_img)):
        results +="# Field "+str(i)+" :\r\n"
        field = {"number":i}
        path_folder = "output/field_"+str(i)
        for j in range(len(hsv)):
            team_name = hsv[j]["team"]
            name_img = path_folder+"/teams/team_"+team_name+".png"

            team_img = filter_by_team(crops_img[i],hsv[j])
            fu.save_image(team_img,name_img)
            centers,details = find_thymios(team_img,parameters_thymio_ld,angles,path_folder, team_name)

            results += "** Team "+team_name+"  : "+str(len(centers))+" detections\r\n"
            team=[]
            for k in range(len(centers)):
                path_img=path_folder+"/details/dots_"+team_name+"_thymio_"+str(k)+".png"
                center_position = centers[k]
                numero_thymio,farther_dot = count_dots_thymio(details[k],center_position,parameters_dots_ld,path_img)
                numero_thymio = len(numero_thymio)
                sens = determine_direction(farther_dot,center_position)
                team.append((numero_thymio,center_position,sens))
                results+="    - n°"+str(numero_thymio)+" (x="+str(center_position[0])+";y="+str(center_position[1])+") sens : "+sens+"\r\n"

            field[team_name]=team

        total_results.append(field)
    return total_results, positions,angles, results
