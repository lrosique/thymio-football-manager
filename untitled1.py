# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 18:54:11 2018

@author: soldier
"""

import requests, json

g = requests.get("http://127.0.0.1:5000/calibration/football_field")
g_json = json.loads(g.text)

g = requests.get("http://127.0.0.1:5000/calibration/image")
g_json = json.loads(g.text)


g = requests.get("http://127.0.0.1:5000/start")
g_json = json.loads(g.text)

g = requests.get("http://127.0.0.1:5000/football_field?numero=1")
g_json = json.loads(g.text)


# CALIBRATION
path_img = "data/calibration_ld.png"
positions,angles = du.calibrate_football_fields(path_img,parameters_fields_ld)
crops = du.crop_rotate_image(positions,angles,path_img)

# GET IMAGE
path_img = "data/image_ld.png"
crops = du.crop_rotate_image(positions,angles,path_img,save_img=True)


# TEST 1 FIELD
i = 1
path_folder = "output/field_"+str(i)
path_img = path_folder+"/field_"+str(i)+".png"

du.filter_by_team(path_img,hsv_green,path_folder+"/team_green.png")
du.filter_by_team(path_img,hsv_orange,path_folder+"/team_orange.png")

centers_green=du.find_thymios(path_folder+"/team_green.png",path_folder+"/thresh_team_green.png",parameters_thymio_ld,"green",path_folder)
centers_orange=du.find_thymios(path_folder+"/team_orange.png",path_folder+"/thresh_team_orange.png",parameters_thymio_ld,"orange",path_folder)

j = 0
numero_thymio_green = len(du.count_dots_thymio(path_folder+"/green_thymio_"+str(j)+".png",parameters_dots_ld,"green",path_folder,str(j)))
numero_thymio_orange = len(du.count_dots_thymio(path_folder+"/orange_thymio_"+str(j)+".png",parameters_dots_ld,"orange",path_folder,str(j)))
































## Read
hsv_green={"low":(30, 50, 0),"high":(80, 255,255)}
hsv_orange={"low":(5, 80, 100),"high":(28, 255,255)}

def filter_by_team(path_img,parameters_hsv,name):
    img = cv2.imread(path_img)
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

filter_by_team("output/field_1.jpg",hsv_green,"output/team_green.png")
filter_by_team("output/field_1.jpg",hsv_orange,"output/team_orange.png")


#parameters_image_ld={"canny_min_threshold":20, "canny_max_threshold":300, "threshold_min":20, "threshold_max":255, "erode_iter":2, "dilate_iter":4, "number_pixels_per_field":50 }
#calibrate_football_fields("green.png", parameters_image_ld)

parameters_image={"threshold_min":100, "threshold_max":255,"number_pixels_per_field":2}

def count_dots_thymio(path_img, parameters):
    gray = cv2.imread(path_img, 0)
    ## threshold
    th =255- cv2.threshold(gray, parameters['threshold_min'], parameters['threshold_max'],cv2.THRESH_BINARY_INV|cv2.THRESH_OTSU)[1]
    cv2.imwrite("output/thresh_team.png", th)
    ## findcontours
    _,cnts,_ = cv2.findContours(th, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    ## filter by area
    s1= 0
    s2 = 20
    xcnts = []
    for cnt in cnts:
        if s1<cv2.contourArea(cnt) <s2:
            xcnts.append(cnt)
    
    print("Dots number: {}".format(len(xcnts)))
    
count_dots_thymio("output/team_orange.png",parameters_image)






find_thymios("output/team_orange.png","output/thresh_team.png",parameters_image)
def find_thymios(path_img, path_thresh, parameters):
    img=cv2.imread(path_img)
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
    cnts = contours.sort_contours(cnts)[0]
    
    positions=[]
    # loop over the contours
    rectangles = img
    for (i, c) in enumerate(cnts):
        ((cX, cY), radius) = cv2.minEnclosingCircle(c)
        rect = cv2.minAreaRect(c)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(rectangles,[box],0,(0,0,255),2)
        cv2.putText(img,'Rouge '+str(i), (max(0,int(cX)-50),int(cY)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        
        positions.append(box)
        angles.append(rect[2])

    #find_x_y_rectangle(positions[0])

    cv2.imwrite('output/team_rectangles.jpg', rectangles)

def find_x_y_rectangle(box):
    x0,y0 = np.min(box,axis=0)
    x1,y1 = np.max(box,axis=0)
    return x0,x1,y0,y1













img = cv2.imread('output/field_2/field_2.png',0)
img = cv2.medianBlur(img,5)
cimg = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)

circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,1,20,param1=50,param2=30,minRadius=0,maxRadius=0)

circles = np.uint16(np.around(circles))
for i in circles[0,:]:
    # draw the outer circle
    cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)
    # draw the center of the circle
    cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3)

cv2.imshow('detected circles',cimg)
cv2.waitKey(0)
cv2.destroyAllWindows()





image = cv2.imread('output/field_2/field_2.png')
output = image.copy()
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 5, 30,param1=30,param2=20,minRadius=10,maxRadius=200)
if circles is not None:
	# convert the (x, y) coordinates and radius of the circles to integers
	circles = np.round(circles[0, :]).astype("int")
 
	# loop over the (x, y) coordinates and radius of the circles
	for (x, y, r) in circles:
		# draw the circle in the output image, then draw a rectangle
		# corresponding to the center of the circle
		cv2.circle(output, (x, y), r, (0, 255, 0), 4)
		#cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
 
	# show the output image
	cv2.imwrite('compare.jpg', np.hstack([image, output]))
