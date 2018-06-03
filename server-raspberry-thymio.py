# -*- coding: utf-8 -*-
import detectionutils as du
import detectionparameters as p
import shutil
import os
import numpy as np
import json
import redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)
#r = redis.StrictRedis(host='54.37.10.254', port=6379, db=0)
r.set('start',False)

from flask import Flask, request
app = Flask(__name__)

positions = None
crops = None
angles = None
total_results = None

def default(o):
    if isinstance(o, np.int64): return int(o)  
    raise TypeError

@app.route('/calibration/football_field', methods=['GET', 'POST'])
def get_calibrate_football_fields():
    path_img = 'data/calibration.png'
    reset = request.args.get('reset')
    if reset != None and reset != '' and (reset == True or reset == 1 or reset == '1'):
        du.get_image(path_img,"http://192.168.1.60:1880/calibration")
    else:
        shutil.copyfile("data/calibration_ld.png",path_img)
    r.set("calibrate_fields",'1')
    calib = r.get("calibrate_fields")
    while calib.decode("utf-8") != '1':
        calib = r.get("calibrate_fields")
    crops = r.get("crops").decode("utf-8")
    return json.dumps({'Fields': crops,'Total':len(crops)}, default=default)

@app.route('/calibration/image', methods=['GET', 'POST'])
def get_calibrate_image():
    path_img = "data/image.png"
    reset = request.args.get('reset')
    if reset != None and reset != '' and (reset == True or reset == 1 or reset == '1'):
        du.get_image(path_img,"http://192.168.1.60:1880/image")
    else:
        shutil.copyfile("data/image_ld.png",path_img)
    r.set("calibrate_image",'1')
    calib = r.get("calibrate_image")
    while calib.decode("utf-8") != '1':
        calib = r.get("calibrate_image")
    crops = r.get("crops").decode("utf-8")
    return json.dumps({'Fields': crops,'Total':len(crops)}, default=default)

@app.route('/football_field', methods=['GET', 'POST'])
def get_football_field():
    total_results = r.get("total_results").decode("utf-8")
    results = r.get("results").decode("utf-8")
    numero = request.args.get('numero')
    if numero != None and numero != '':
        numero = int(numero)
        return json.dumps({'Field': total_results[numero], 'Results': results}, default=default)
    else:
        return json.dumps({'Fields': total_results, 'Results': results}, default=default)
    
@app.route('/start', methods=['GET', 'POST'])
def start_loop_detection():
    r.set('start','1')
    return 'START'

@app.route('/stop', methods=['GET', 'POST'])
def stop_loop_detection():
    r.set('start','0')
    return 'STOP'
    
#if __name__ == '__main__':
#    app.debug = False
#    app.run(host = '0.0.0.0',port=5005)