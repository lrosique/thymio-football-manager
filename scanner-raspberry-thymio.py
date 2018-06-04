# -*- coding: utf-8 -*-
import detectionutils as du
import detectionparameters as p
import shutil
import os
import redis
import pickle
r = redis.StrictRedis(host='localhost', port=6379, db=0)

if not os.path.exists("data"):
    os.makedirs("data")
if os.path.exists("output"):
    shutil.rmtree('output')
os.makedirs("output")
if os.path.exists("data/image.png"):
    os.remove("data/image.png")
if os.path.exists("data/calibration.png"):
    os.remove("data/calibration.png")

r.set("start",'0')
r.set("calibrate_fields",'0')
r.set("calibrate_image",'0')
r.set("reset",'0')
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
        shutil.copyfile("data/"+name+"_ld.png",path_img)
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
    total_results, positions,angles, results = du.analyse_all_fields(angles,positions,p.hsv_green,p.hsv_rose,p.hsv_blue,p.parameters_thymio_ld,p.parameters_dots_ld)
    return total_results,results

print("Scanner loaded... and loop started.")

start = r.get("start")
while True:
    if r.get("start") != None and r.get("start").decode("utf-8") != start.decode("utf-8"):
        print("Server started !") if start.decode("utf-8") == "0" else print("Server stopped !")
    start = r.get("start")
    calibrate_fields = r.get("calibrate_fields")
    calibrate_image = r.get("calibrate_image")
    reset = r.get("reset")
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