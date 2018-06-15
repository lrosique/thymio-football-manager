# -*- coding: utf-8 -*-
import utils.detection_utils as du
import utils.detection_parameters as p
import redis
import pickle
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
r = redis.StrictRedis(host=p.parameters_redis["host"], port=p.parameters_redis["port"], db=0)

r.set("start",'0')
r.set("calibrate_fields",'0')
r.set("calibrate_image",'0')
r.set("calibrate_goals",'0')
r.set("crops",pickle.dumps(None))
r.set("total_results",pickle.dumps(None))
r.set("results",pickle.dumps(None))
r.set("goals_positions",pickle.dumps({}))
r.set("goals_definitions",pickle.dumps(None))

positions = None
crops = None
angles = None
total_results = None
results = None

crops_img = None
goals_positions = {}
goals_definitions = None

def get_calibrate_football_fields(image):
    global positions,crops,crops_img,angles
    positions,angles = du.calibrate_football_fields(image,p.parameters_fields_ld)
    crops, crops_img = du.crop_rotate_image(image,positions,angles)
    return crops

def get_calibrate_image(image):
    global positions,crops,crops_img,angles
    crops, crops_img = du.crop_rotate_image(image,positions,angles)
    return crops, crops_img

def get_football_field():
    global total_results,results,angles,positions,crops_img
    total_results, positions,angles, results = du.analyse_all_fields(angles,positions,p.hsv_ball,p.parameters_ball,p.teams_hsv_to_analyse,p.parameters_thymio_ld,p.parameters_dots_ld,p.parameters_directions,crops_img)
    return total_results,results

def get_position(field=None, team=None, thymio_number=None):
    total_results, results = get_football_field()
    if total_results is not None:
        if field < len(total_results):
            if team in total_results[field]:
                for th in total_results[field][team]:
                    if thymio_number == th[0]:
                        return th
    return None

def get_football_goals():
    global goals_definitions,total_results,goals_definitions
    goals_definitions = pickle.loads(r.get('goals_definitions'))
    get_football_field()
    for g in goals_definitions:
        pos = get_position(field=g[0],team=g[1],thymio_number=g[2])
        if pos is not None and pos[3] is not None:
            if g[0] not in goals_positions:
                goals_positions[g[0]] = {}
            goals_positions[g[0]][g[3]] = pos[3]
    return goals_positions

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
    global positions,crops,angles,total_results,results,crops_img
    start = r.get("start")
    camera, rawCapture = init_camera()

    # allow the camera to warmup
    time.sleep(0.1)

    # capture frames from the camera
    for frame in camera.capture_continuous(rawCapture, format=p.picamera['format'], use_video_port=True):
        # VARIABLES
        image = frame.array
        image = image[::-1,...,:]
        print_start_stop(start, r.get("start"))
        start = r.get("start")
        calibrate_fields = r.get("calibrate_fields")
        calibrate_image = r.get("calibrate_image")
        calibrate_goals = r.get("calibrate_goals")

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
            get_calibrate_image(image)
            r.set('crops',pickle.dumps(crops))
            r.set("calibrate_image",'0')
            print("Calibration de l'image terminée")

        # GOALS CALIBRATION
        if calibrate_goals != None and calibrate_goals.decode("utf-8") == '1':
            print("Début de la calibration des buts")
            get_football_goals()
            r.set("goals_positions",goals_positions)
            r.set('calibrate_goals','0')
            print("Calibration des buts terminée")

        # REAL TIME DETECTION
        if start != None and start.decode("utf-8") == '1':
            get_calibrate_image(image)
            get_football_field()
            r.set('total_results',pickle.dumps(total_results))
            r.set('results',pickle.dumps(results))

        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)

print("Scanner loaded... and loop started.")
loop_camera_redis()
