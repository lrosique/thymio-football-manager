# -*- coding: utf-8 -*-
import redis
import pickle
import time
r = redis.StrictRedis(host='192.168.1.60', port=6379, db=0)
delay = 0.5

def get_all_detections():
    total_results = pickle.loads(r.get("total_results"))
    return total_results

def get_position(field=None, team=None, thymio_number=None):
    total_results = get_all_detections()
    if total_results is not None:
        if field < len(total_results):
            if team in total_results[field]:
                for th in total_results[field][team]:
                    if thymio_number == th[0]:
                        return th
    return None

def track_position(field=None, team=None, thymio_number=None, duration=0):
    positions = []
    for i in range(0,duration):
        pos = get_position(field,team,thymio_number)
        print("t="+str(i*delay)+"s ->",pos)
        positions.append(pos)
        time.sleep(delay)
    return positions
