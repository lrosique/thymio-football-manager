# -*- coding: utf-8 -*-
import utils.detection_parameters as p
import cv2
import shutil
import os
import redis
r = redis.StrictRedis(host=p.parameters_redis["host"], port=p.parameters_redis["port"], db=0)

def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)

def delete_content_folder(folder):
    if os.path.exists(folder):
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)
    else:
        os.makedirs(folder)
    return True
    
def delete_file(path):
    if os.path.exists(path):
        os.remove(path)

def initiate_save_folders():
    create_folder("data")
    delete_content_folder("output")
    delete_file("data/image.png")
    delete_file("data/calibration.png")

def save_image(image,path):
    if (p.save_images and path != None) or (path in p.critical_images_names) :
        folder = "/".join(map(str,path.split("/")[:-1]))
        if folder != "":
            create_folder(folder)
        cv2.imwrite(path, image)
        
if p.save_images:
    initiate_save_folders()
