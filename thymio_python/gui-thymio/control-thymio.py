import dbus
import dbus.mainloop.glib
from gi.repository import GObject
import redis
import time
import math

r = redis.StrictRedis(host="localhost", port=6379, db=0)

r.set("action","stop")

class Thymio:
    motorLeft=0
    motorRight=0
    proxSensorsVal=[0,0,0,0,0]

    def __init__(self, nom='Thymio'):
        self.nom = nom

    def setMotorLeft(self,motor_left):
        network.SetVariable("thymio-II", "motor.left.target", [motor_left])
        self.motorLeft = motor_left

    def setMotorRight(self,motor_right):
        network.SetVariable("thymio-II", "motor.right.target", [motor_right])
        self.motorRight = motor_right

    def setMotors(self,motor_left, motor_right):
        self.setMotorLeft(motor_left)
        self.setMotorRight(motor_right)

    #def get_proxSensors(self):
    #    network.GetVariable("thymio-II", "prox.horizontal",reply_handler=get_variables_reply2,error_handler=get_variables_error)

#def get_variables_reply2(r):
#    global proxSensorsVal
#    proxSensorsVal=r
#    return r

#def get_variables_error(e):
#    print(str(e))
    
    
### OPENING BUS ###
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()
# ASEBA NETWORK #
network = dbus.Interface(bus.get_object('ch.epfl.mobots.Aseba', '/'), dbus_interface='ch.epfl.mobots.AsebaNetwork')

#Variables
thymio = Thymio()

def calculate_speed(x,y):
    speed = math.sqrt(x**2 + y**2)*500/120
    if speed < 0 : speed = 0
    if speed > 500 : speed = 500
    print(speed)
    return speed
    
while True:
    if r.get("vitesse") is None:
        r.set("vitesse",10)
    if r.get("x_joystick") is None:
        r.set("x_joystick",0)
    if r.get("y_joystick") is None:
        r.set("y_joystick",0)
    vitesse = float(r.get("vitesse").decode("utf-8"))
    x = int(r.get("x_joystick").decode("utf-8"))
    y = int(r.get("y_joystick").decode("utf-8"))
    action = r.get("action").decode("utf-8")
    if (action == "stop"):
        thymio.setMotors(0,0)
    elif (action == "up"):
        thymio.setMotors(vitesse,vitesse)
    elif (action == "down"):
        thymio.setMotors(-vitesse,-vitesse)
    elif (action == "left"):
        thymio.setMotors(-vitesse,vitesse)
    elif (action == "right"):
        thymio.setMotors(vitesse,-vitesse)
    elif (action == "joystick"):
        speed = calculate_speed(x,y)
        if y < 0: speed = - speed
        percent = (120-x)/120*100
        if x > 0:
            thymio.setMotors(percent*speed,speed)
        if x < 0:
            thymio.setMotors(speed,percent*speed)
       
    time.sleep(0.1)