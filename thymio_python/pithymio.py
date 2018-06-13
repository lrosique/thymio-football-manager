import dbus
import dbus.mainloop.glib
from gi.repository import GObject

# sudo apt install python-gi python-gi-cairo python3-gi python3-gi-cairo gir1.2-gtk-3.0

proxSensorsVal=[0,0,0,0,0]

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


    def get_proxSensors(self):
        network.GetVariable("thymio-II", "prox.horizontal",reply_handler=get_variables_reply,error_handler=get_variables_error)

def get_variables_reply2(r):
    global proxSensorsVal
    proxSensorsVal=r
    print('rrrrrrrrrrr')
    print(r)
    return r

def get_variables_error(e):
    print('error:')
    print(str(e))

def Braitenberg():
    network.GetVariable("thymio-II", "prox.horizontal",reply_handler=get_variables_reply2,error_handler=get_variables_error)
    print(proxSensorsVal[0],proxSensorsVal[1],proxSensorsVal[2],proxSensorsVal[3],proxSensorsVal[4])
    return True

if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()

    #Create Aseba network
    network = dbus.Interface(bus.get_object('ch.epfl.mobots.Aseba', '/'), dbus_interface='ch.epfl.mobots.AsebaNetwork')

    thymio = Thymio()
    thymio.setMotors(100,100)
    loop = GObject.MainLoop()
    handle = GObject.timeout_add (1000, Braitenberg)
    loop.run()
