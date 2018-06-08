# -*- coding: utf-8 -*-
import utils.detection_utils as du
import utils.detection_parameters as p
import redis
import pickle
r = redis.StrictRedis(host=p.parameters_redis["host"], port=p.parameters_redis["port"], db=0)

r.set("start",'0')
r.set("calibrate_fields",'0')
r.set("calibrate_image",'0')
r.set("reset",'0')
r.set("save_img",'0')
r.set("crops",pickle.dumps(None))
r.set("total_results",pickle.dumps(None))
r.set("results",pickle.dumps(None))

positions = None
crops = None
angles = None
total_results = None
results = None

crops_img = None

def get_calibrate_football_fields(image):
    global positions,crops,angles
    positions,angles = du.calibrate_football_fields(image,p.parameters_fields_ld)
    crops, crops_img = du.crop_rotate_image(image,positions,angles)
    return crops

def get_calibrate_image(image):
    global positions,crops,crops_img,angles
    crops, crops_img = du.crop_rotate_image(image,positions,angles)
    return crops, crops_img

def get_football_field():
    global total_results,results,angles,positions,crops_img
    total_results, positions,angles, results = du.analyse_all_fields(angles,positions,[p.hsv_green,p.hsv_rose,p.hsv_blue],p.parameters_thymio_ld,p.parameters_dots_ld,crops_img)
    return total_results,results

############
import shutil
import cv2

name_img_train='allthymio.png'

def download_image(name):
    reset = r.get("reset").decode("utf-8")
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