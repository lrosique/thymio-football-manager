# -*- coding: utf-8 -*-
import redis
import pickle
r = redis.StrictRedis(host='192.168.1.60', port=6379, db=0)

def get_all_detections():
    total_results = pickle.loads(r.get("total_results"))
    return total_results

def get_position(field, team, thymio_number):
    return get_all_detections()[field][team][thymio_number]

def hello_world(name="Mr Robot"):
    return "Hello "+name+", nice to meet you !"