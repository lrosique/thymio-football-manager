import dbus
import dbus.mainloop.glib
from gi.repository import GObject
import redis
import time

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

while True:
    if r.get("vitesse") is None:
        r.set("vitesse",0)
    vitesse = int(r.get("vitesse").decode("utf-8"))
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
    time.sleep(0.1)