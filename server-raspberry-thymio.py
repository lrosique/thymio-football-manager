# -*- coding: utf-8 -*-
import shutil
import detectionutils as du
import os
import numpy as np
import json
from flask import Flask, request
app = Flask(__name__)

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

hsv_green={"low":(30, 50, 0),"high":(80, 255,255)}
hsv_orange={"low":(5, 80, 100),"high":(28, 255,255)}

parameters_fields_hd={"canny_min_threshold":250, "canny_max_threshold":400, "threshold_min":200, "threshold_max":255, "erode_iter":5, "dilate_iter":10, "number_pixels_per_field":50000 }
parameters_fields_ld={"canny_min_threshold":150, "canny_max_threshold":300, "threshold_min":150, "threshold_max":255, "erode_iter":2, "dilate_iter":4, "number_pixels_per_field":5000 }

parameters_thymio_hd={"threshold_min":100, "threshold_max":255, "number_pixels_per_field":1000, "min_radius":7}
parameters_thymio_ld={"threshold_min":100, "threshold_max":255, "number_pixels_per_field":100, "min_radius":7}

parameters_dots_hd={"threshold_min":100, "threshold_max":255, "number_pixels_per_field":200}
parameters_dots_ld={"threshold_min":100, "threshold_max":255, "number_pixels_per_field":2}

def default(o):
    if isinstance(o, np.int64): return int(o)  
    raise TypeError

@app.route('/calibration/football_field', methods=['GET', 'POST'])
def get_calibrate_football_fields():
    global positions,parameters_fields,crops,angles
    path_img = 'data/calibration.png'
    reset = request.args.get('reset')
    if reset != None and reset != '' and (reset == True or reset == 1 or reset == '1'):
        du.get_image(path_img,"http://192.168.1.60:1880/calibration")
    else:
        shutil.copyfile("data/calibration_ld.png",path_img)
    positions,angles = du.calibrate_football_fields(path_img,parameters_fields_ld)
    crops = du.crop_rotate_image(positions,angles,path_img)
    return json.dumps({'Fields': crops,'Total':len(crops)}, default=default)

@app.route('/calibration/image', methods=['GET', 'POST'])
def get_calibrate_image():
    global positions,parameters_fields,crops,angles
    path_img = "data/image.png"
    reset = request.args.get('reset')
    if reset != None and reset != '' and (reset == True or reset == 1 or reset == '1'):
        du.get_image(path_img,"http://192.168.1.60:1880/image")
    else:
        shutil.copyfile("data/image_ld.png",path_img)
    crops = du.crop_rotate_image(positions,angles,path_img,save_img=True)
    return json.dumps({'Fields': crops,'Total':len(crops)}, default=default)

@app.route('/football_field', methods=['GET', 'POST'])
def get_football_field():
    global total_results,angles,positions,hsv_green,hsv_orange,parameters_thymio_ld,parameters_dots_ld
    total_results, positions,angles, results = du.analyse_all_fields(angles,positions,hsv_green,hsv_orange,parameters_thymio_ld,parameters_dots_ld)
    numero = request.args.get('numero')
    if numero != None and numero != '':
        numero = int(numero)
        return json.dumps({'Field': total_results[numero], 'Results': results}, default=default)
    else:
        return json.dumps({'Fields': total_results, 'Results': results}, default=default)