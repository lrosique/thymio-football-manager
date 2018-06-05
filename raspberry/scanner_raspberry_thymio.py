# -*- coding: utf-8 -*-
import utils.detection_utils as du
import utils.detection_parameters as p
import redis
import pickle
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
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

def get_calibrate_football_fields(image):
    global positions,crops,angles
    positions,angles = du.calibrate_football_fields(image,p.parameters_fields_ld)
    crops = du.crop_rotate_image(positions,angles,image)
    return crops

def get_calibrate_image():
    global positions,crops,angles
    #path_img = download_image("image")
    #crops = du.crop_rotate_image(positions,angles,path_img,save_img=True)
    return crops

def get_football_field():
    global total_results,results,angles,positions
    #save_img = r.get("save_img").decode("utf-8")
    #if save_img == "1": save_img = True
    #else: save_img = False
    #total_results, positions,angles, results = du.analyse_all_fields(angles,positions,p.hsv_green,p.hsv_rose,p.hsv_blue,p.parameters_thymio_ld,p.parameters_dots_ld,save_img)
    return total_results,results

def init_camera():
    camera = PiCamera()
    camera.resolution = p.picamera['resolution']
    camera.framerate = p.picamera['framerate']
    rawCapture = PiRGBArray(camera, size=p.picamera['resolution'])
    return camera, rawCapture

def print_start_stop(prev_start, start):
    if start != None and start.decode("utf-8") != prev_start.decode("utf-8"):
        if prev_start.decode("utf-8") == "0":
            print("Server started !") 
        else: 
            print("Server stopped !")
    
def loop_camera_redis():
    global positions,crops,angles,total_results,results
    start = r.get("start")
    camera, rawCapture = init_camera()
    
    # allow the camera to warmup
    time.sleep(0.1)
    
    # capture frames from the camera
    for frame in camera.capture_continuous(rawCapture, format=p.picamera['format'], use_video_port=True):
        # VARIABLES
        image = frame.array
        print_start_stop(start, r.get("start"))
        start = r.get("start")
        calibrate_fields = r.get("calibrate_fields")
        calibrate_image = r.get("calibrate_image")
        
        # FIELD CALIBRATION
        if calibrate_fields != None and calibrate_fields.decode("utf-8") == '1':
            print("Début de calibration des terrains")
            get_calibrate_football_fields(image)
            r.set('crops',pickle.dumps(crops))
            r.set("calibrate_fields",'0')
            print("Calibration des terrains terminée")
            
        # IMAGE CALIBRATION
        if calibrate_image != None and calibrate_image.decode("utf-8") == '1':
            print("Début de calibration de l'image")
            get_calibrate_image()
            r.set('crops',pickle.dumps(crops))
            r.set("calibrate_image",'0')
            print("Calibration de l'image terminée")
        
        # REAL TIME DETECTION
        if start != None and start.decode("utf-8") == '1':
            get_calibrate_image()
            get_football_field()
            r.set('total_results',pickle.dumps(total_results))
            r.set('results',pickle.dumps(results))
            
        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)

print("Scanner loaded... and loop started.")
loop_camera_redis()