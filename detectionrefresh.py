# -*- coding: utf-8 -*-
import detectionutils as du
import detectionparameters as p
import shutil
import os
import numpy as np
import json
import time
import redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)
#r = redis.StrictRedis(host='54.37.10.254', port=6379, db=0)

if not os.path.exists("data"):
    os.makedirs("data")
if os.path.exists("output"):
    shutil.rmtree('output')
os.makedirs("output")
if os.path.exists("data/image.png"):
    os.remove("data/image.png")
if os.path.exists("data/calibration.png"):
    os.remove("data/calibration.png")

positions = None
crops = None
angles = None
total_results = None
results = None

def get_calibrate_football_fields():
    global positions,parameters_fields,crops,angles
    path_img = 'data/calibration.png'
    positions,angles = du.calibrate_football_fields(path_img,p.parameters_fields_ld)
    crops = du.crop_rotate_image(positions,angles,path_img)
    return crops

def get_calibrate_image():
    global positions,parameters_fields,crops,angles
    path_img = "data/image.png"
    crops = du.crop_rotate_image(positions,angles,path_img,save_img=True)
    return crops

def get_football_field():
    global total_results,results,angles,positions,hsv_green,hsv_orange,parameters_thymio_ld,parameters_dots_ld
    total_results, positions,angles, results = du.analyse_all_fields(angles,positions,p.hsv_green,p.hsv_orange,p.parameters_thymio_ld,p.parameters_dots_ld)
    return total_results,results

while True:
    start = r.get("start")
    calibrate_fields = r.get("calibrate_fields")
    calibrate_image = r.get("calibrate_image")
    if calibrate_fields != None and calibrate_fields.decode("utf-8") == '1':
        print("Début de calibration des terrains")
        get_calibrate_football_fields()
        r.set('crops',crops)
        r.set("calibrate_fields",'0')
        print("Calibration des terrains terminée")
    if calibrate_image != None and calibrate_image.decode("utf-8") == '1':
        print("Début de calibration de l'image")
        get_calibrate_image()
        r.set('crops',crops)
        r.set("calibrate_image",'0')
        print("Calibration de l'image terminée")
    if start != None and start.decode("utf-8") == '1':
        get_calibrate_image()
        get_football_field()
        r.set('total_results',total_results)
        r.set('results',results)