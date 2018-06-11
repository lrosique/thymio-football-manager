# -*- coding: utf-8 -*-
import utils.detection_utils as du
import utils.detection_parameters as p
import shutil
import cv2

reset = "0"
name_img_train='capture_15h.png'

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
img = img[::-1,...,:]

get_calibrate_football_fields(img)

get_football_field()

############
def get_position(field=None, team=None, thymio_number=None):
    total_results, results = get_football_field()
    if total_results is not None:
        if field < len(total_results):
            if team in total_results[field]:
                for th in total_results[field][team]:
                    if thymio_number == th[0]:
                        return th
    return None

import time
def track_position(field=None, team=None, thymio_number=None, duration=0):
    positions = []
    delay = 0.5
    for i in range(0,duration):
        pos = get_position(field,team,thymio_number)
        print("t="+str(i*delay)+"s ->",pos)
        positions.append(pos)
        time.sleep(delay)
    return positions


validation = []
validation.append(get_position(field=0,team="green",thymio_number=2) is not None)
validation.append(get_position(field=0,team="rose",thymio_number=2) is not None)

validation.append(get_position(field=1,team="green",thymio_number=1) is not None)
validation.append(get_position(field=1,team="ball",thymio_number=0) is not None)

validation.append(get_position(field=2,team="green",thymio_number=3) is not None)
validation.append(get_position(field=2,team="rose",thymio_number=3) is not None)
validation.append(get_position(field=2,team="blue",thymio_number=3) is not None)

validation.append(get_position(field=3,team="blue",thymio_number=1) is not None)

validation.append(get_position(field=4,team="rose",thymio_number=0) is not None)

validation.append(get_position(field=5,team="blue",thymio_number=2) is not None)
validation.append(get_position(field=5,team="rose",thymio_number=1) is not None)
    
print(validation)
print("score :",str(sum(validation))+"/"+str(len(validation)))