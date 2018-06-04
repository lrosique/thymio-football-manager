# -*- coding: utf-8 -*-
import redis
import pickle
r = redis.StrictRedis(host='localhost', port=6379, db=0)

def calibrate_fields(reset='0'):
    r.set("reset",reset)
    r.set("calibrate_fields",'1')

def calibrate_image(reset='0'):
    r.set("reset",reset)
    r.set("calibrate_image",'1')
    
def start():
    r.set('start','1')

def stop():
    r.set('start','0')
    
def full_start_server():
    calibrate_fields(reset='1')
    calibrate_image(reset='1')
    start()

def get_detections(summary=False):
    total_results = pickle.loads(r.get("total_results"))
    results = pickle.loads(r.get("results"))
    if summary: return total_results, results
    else: return total_results
    
    
total_results[1]["team_green"]