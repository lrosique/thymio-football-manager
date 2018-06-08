# -*- coding: utf-8 -*-
import utils.detection_utils as du
import utils.detection_parameters as p
import shutil
import cv2

reset = "0"
name_img_train='allthymio.png'

positions = None
crops = None
angles = None
total_results = None
results = None

crops_img = None

def get_calibrate_football_fields(image):
    global positions,crops,crops_img,angles
    positions,angles = du.calibrate_football_fields(image,p.parameters_fields_ld)
    crops, crops_img = du.crop_rotate_image(image,positions,angles)
    return crops, crops_img

def get_calibrate_image(image):
    global positions,crops,crops_img,angles
    crops, crops_img = du.crop_rotate_image(image,positions,angles)
    return crops, crops_img

def get_football_field():
    global total_results,results,angles,positions,crops_img
    total_results, positions,angles, results = du.analyse_all_fields(angles,positions,p.teams_hsv_to_analyse,p.parameters_thymio_ld,p.parameters_dots_ld,crops_img)
    return total_results,results

def download_image(name):
    global reset
    path_img = 'data/'+name+'.png'
    if reset == '1':
        du.get_image(path_img,"http://192.168.1.60:1880/"+name)
    else:
        shutil.copyfile("data/train/"+name_img_train,path_img)
    return path_img

##
download_image('calibration')
img = cv2.imread('data/calibration.png')

get_calibrate_football_fields(img)

get_football_field()

############