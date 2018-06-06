# -*- coding: utf-8 -*-
import utils.detection_utils as du
import utils.detection_parameters as p
import shutil
import redis
import pickle
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
r = redis.StrictRedis(host='localhost', port=6379, db=0)

du.create_folder("data")
du.delete_content_folder("output")
du.delete_file("data/image.png")
du.delete_file("data/calibration.png")

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

def download_image(name):
    reset = r.get("reset").decode("utf-8")
    path_img = 'data/'+name+'.png'
    if reset == '1':
        du.get_image(path_img,"http://192.168.1.60:1880/"+name)
    else:
        shutil.copyfile("data/train/"+name+"_ld.png",path_img)
    return path_img

def get_calibrate_football_fields():
    global positions,crops,angles
    path_img = download_image('calibration')
    positions,angles = du.calibrate_football_fields(path_img,p.parameters_fields_ld)
    crops = du.crop_rotate_image(positions,angles,path_img)
    return crops

def get_calibrate_image():
    global positions,crops,angles
    path_img = download_image("image")
    crops = du.crop_rotate_image(positions,angles,path_img,save_img=True)
    return crops

def get_football_field():
    global total_results,results,angles,positions
    save_img = r.get("save_img").decode("utf-8")
    if save_img == "1": save_img = True
    else: save_img = False
    total_results, positions,angles, results = du.analyse_all_fields(angles,positions,p.hsv_green,p.hsv_rose,p.hsv_blue,p.parameters_thymio_ld,p.parameters_dots_ld,save_img)
    return total_results,results

def print_start_stop(prev_start, start):
    if start != None and start.decode("utf-8") != prev_start.decode("utf-8"):
        if prev_start.decode("utf-8") == "0":
            print("Server started !") 
        else: 
            print("Server stopped !")

def loop_scanner_redis():
    global positions,crops,angles,total_results,results
    start = r.get("start")
    while True:
        print_start_stop(start, r.get("start"))
        start = r.get("start")
        calibrate_fields = r.get("calibrate_fields")
        calibrate_image = r.get("calibrate_image")
        if calibrate_fields != None and calibrate_fields.decode("utf-8") == '1':
            print("Début de calibration des terrains")
            get_calibrate_football_fields()
            r.set('crops',pickle.dumps(crops))
            r.set("calibrate_fields",'0')
            print("Calibration des terrains terminée")
        if calibrate_image != None and calibrate_image.decode("utf-8") == '1':
            print("Début de calibration de l'image")
            get_calibrate_image()
            r.set('crops',pickle.dumps(crops))
            r.set("calibrate_image",'0')
            print("Calibration de l'image terminée")
        if start != None and start.decode("utf-8") == '1':
            get_calibrate_image()
            get_football_field()
            r.set('total_results',pickle.dumps(total_results))
            r.set('results',pickle.dumps(results))

print("Scanner loaded... and loop started.")
loop_scanner_redis()