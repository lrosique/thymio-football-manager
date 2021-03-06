# -*- coding: utf-8 -*-
import redis
import time
import pickle
import sys
r = redis.StrictRedis(host='192.168.1.60', port=6379, db=0)
reset = '0'
goals = [(3,"rose",1,"blue"),(3,"rose",3,"green")] #(field,goal_color,nb_dots_goal,team_goal)

def calibrate_fields():
    r.set("calibrate_fields",'1')

def calibrate_image():
    r.set("calibrate_image",'1')

def calibrate_goals():
    global goals
    r.set("goals_definitions",pickle.dumps(goals))
    r.set("calibrate_goals",'1')

def start():
    r.set('start','1')

def stop():
    r.set('start','0')

def full_start_server():
    global reset
    r.set("reset",reset)
    calibrate_fields()
    time.sleep(3)
    calibrate_image()
    time.sleep(3)
    calibrate_goals()
    time.sleep(3)
    start()

def get_detections(summary=False):
    total_results = pickle.loads(r.get("total_results"))
    results = pickle.loads(r.get("results"))
    print(total_results)
    print(results)
    if summary: return total_results, results
    else: return total_results
    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        fct = sys.argv[1]
        if fct == "field":
            calibrate_fields()
        elif fct == "image":
            calibrate_image()
        elif fct == "goal":
            calibrate_goals()
        elif fct == "start":
            start()
        elif fct == "stop":
            stop()
        elif fct == "fstart":
            full_start_server()
        elif fct == "get":
            get_detections(summary=True)
        elif fct == "help":
            print("Arguments : field, image, goal, start, stop, fstart, get")
        else:
            print("Arguments : field, image, goal, start, stop, fstart, get")
    else:
        print("Arguments : field, image, goal, start, stop, fstart, get")