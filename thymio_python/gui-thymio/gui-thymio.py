#pip3 install tk_tools

import tkinter as tk
import tk_tools
import dbus
import dbus.mainloop.glib
from gi.repository import GObject
import time

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
    
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()

#Create Aseba network
network = dbus.Interface(bus.get_object('ch.epfl.mobots.Aseba', '/'), dbus_interface='ch.epfl.mobots.AsebaNetwork')


thymio = Thymio()

def avancer(vitesse,temps):
	thymio.setMotors(vitesse,vitesse)
	time.sleep(temps)

def tournerAngle(angle):
	if angle<=0:
		thymio.setMotors(300,-300)
		time.sleep(abs(angle)/112)
	if angle>0:
		thymio.setMotors(-300,300)
		time.sleep(abs(angle)/112)

def avancerCourbe(vitessegauche,vitessedroite,temps):
	thymio.setMotors(vitessegauche,vitessedroite)
	time.sleep(temps)

def arret():
	thymio.setMotors(0,0)
 
window = tk.Tk()
window.geometry('800x600')
window.title("Commande de contrôle du Thymio-II")
window.config(background = "#FFFFFF")

leftFrame = tk.Frame(window, width=350,height=300)
leftFrame.grid(row=0, column=0)

bottomFrame = tk.Frame(window, width=350,height=300)
bottomFrame.grid(row=2, column=0)

#Label(leftFrame, text="Commande de contrôle du Thymio-II").grid(row=0, column=0)


photo_up = tk.PhotoImage(file="up_resize.png")
btn_up = tk.Button(leftFrame, compound=tk.TOP, width=100, height=100, image=photo_up, bg='#51e886')
btn_up.grid(column=1, row=4)

photo_down = tk.PhotoImage(file="down_resize.png")
btn_down = tk.Button(leftFrame, compound=tk.TOP, width=100, height=100, image=photo_down, bg='#51e886')
btn_down.grid(column=1, row=8)

photo_left = tk.PhotoImage(file="left_resize.png")
btn_left = tk.Button(leftFrame, compound=tk.TOP, width=100, height=100, image=photo_left, bg='#51e886')
btn_left.grid(column=0, row=6)

photo_right = tk.PhotoImage(file="right_resize.png")
btn_right = tk.Button(leftFrame, compound=tk.TOP, width=100, height=100, image=photo_right, bg='#51e886')
btn_right.grid(column=2, row=6)


def on_press1(event):
	global vitesse
	print("button was pressed")
	thymio.setMotors(vitesse,vitesse)

def on_release1(event):
	print("button was released")
	arret()
    
def on_press2(event):
	global vitesse
	print("button was pressed")
	thymio.setMotors(-vitesse,-vitesse)

def on_release2(event):
	print("button was released")
	arret()
    
def on_press3(event):
	global vitesse
	print("button was pressed")
	thymio.setMotors(-vitesse,vitesse)

def on_release3(event):
	print("button was released")
	arret()
    
def on_press4(event):
	global vitesse
	print("button was pressed")
	thymio.setMotors(vitesse,-vitesse)

def on_release4(event):
    print("button was released")
    arret()

btn_up.bind("<ButtonPress>", on_press1)
btn_up.bind("<ButtonRelease>", on_release1)
btn_down.bind("<ButtonPress>", on_press2)
btn_down.bind("<ButtonRelease>", on_release2)
btn_left.bind("<ButtonPress>", on_press3)
btn_left.bind("<ButtonRelease>", on_release3)
btn_right.bind("<ButtonPress>", on_press4)
btn_right.bind("<ButtonRelease>", on_release4)


gauge = tk_tools.Gauge(bottomFrame, max_value=20, label='Vitesse', unit='cm/s')
gauge.grid(column=1, row=0)
gauge.set_value(0)

slider = tk.StringVar()
slider.set('0.00')

def change_scale(s):
    global gauge, vitesse
    vitesse = 500*float(s)/20
    slider.set('%0.2f' % float(s))
    gauge.set_value(float(s))
    
tk.Scale(bottomFrame, from_=0, to_=20, length=320, bd=3, orient=tk.HORIZONTAL, resolution=0.5,
    command=change_scale).grid(column=0, row=1, columnspan=3)

#tk.Label(rightFrame, textvariable=slider).grid(column=1, row=0, columnspan=5)

window.mainloop()
