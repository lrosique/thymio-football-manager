# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 09:41:02 2018

@author: zgjw1263
"""

# Python 2

# For Python 3 use:
from tkinter import *
import tk_tools
import redis
import math

r = redis.StrictRedis(host="localhost", port=6379, db=0)

r.set("vitesse",10)
r.set("action","stop")
r.set("x_joystick",0)
r.set("y_joystick",0)
r.set("angle_joystick",None)

root = Tk()
root.geometry('1920x1080')
###############################JOYSTICK##################################

x_joystick,y_joystick = 200,200
image_joystick = PhotoImage(file = 'images/button.png')
image_socle = PhotoImage(file = 'images/canvas.png')

canvas_joystick = Canvas(root, width = 400, height = 400, bg="white")
canvas_joystick.pack(side=RIGHT)

image_socle_finale = canvas_joystick.create_image(x_joystick, y_joystick, image = image_socle)
image_joystick_finale = canvas_joystick.create_image(x_joystick, y_joystick, image = image_joystick)

def stay_in_circle(x,y):
    d = math.sqrt(x**2 + y**2)
    new_x,new_y = x,y
    if x != 0 and y != 0: angle = math.atan2(y,x)
    elif x == 0: angle = math.pi / 2 if y > 0 else - math.pi / 2
    elif y == 0: angle = 0 if x > 0 else math.pi
    else: angle = None
    if d > 120 and angle is not None:
        new_x = 120*math.cos(angle)
        new_y = 120*math.sin(angle)
    return new_x+200,200-new_y, angle

def move(event):
    global x_joystick,y_joystick,canvas_joystick,image_joystick_finale
    x, y = event.x, event.y
    r.set("action","joystick")
    r.set("action","up")
    relative_x = x - 200
    relative_y = 200 - y
    x,y,angle=stay_in_circle(relative_x,relative_y)
    canvas_joystick.move(image_joystick_finale, x-x_joystick,y-y_joystick)
    x_joystick = x
    y_joystick = y
    canvas_joystick.update()
    r.set("x_joystick",x-200)
    r.set("y_joystick",200-y)
    r.set("angle_joystick",angle)

def release(event):
    global x_joystick,y_joystick,canvas_joystick,image_joystick_finale
    r.set("action","stop")
    x,y=200,200
    canvas_joystick.move(image_joystick_finale, x-x_joystick,y-y_joystick)
    x_joystick = x
    y_joystick = y
    canvas_joystick.update()

#move
canvas_joystick.bind('<B1-Motion>', move)
#release
canvas_joystick.bind('<ButtonRelease-1>', release)
#click


###############################CONTROLLER##################################
canvas_controle = Canvas(root, width = 400, height = 400, bg="white")
canvas_controle.pack(side=LEFT)

def arrow_button(img_name,position=TOP,row=0,col=0,on_press=None):
    photo = PhotoImage(file="images/"+img_name)
    btn = Button(canvas_controle, compound=TOP, width=100, height=100, image=photo, bg='#51e886')
    btn.pack(side=position)
    btn.bind("<ButtonPress>", on_press)
    btn.bind("<ButtonRelease>", stop)
    btn.image = photo
    return btn

def on_press_up(event):
    global r
    print("UP")
    r.set("action","up")
    
def on_press_down(event):
    global r
    print("DOWN")
    r.set("action","down")

def on_press_left(event):
    global r
    print("LEFT")
    r.set("action","left")
    
def on_press_right(event):
    global r
    print("RIGHT")
    r.set("action","right")

def stop(event):
    global r
    print("STOP")
    r.set("action","stop")

btn_up = arrow_button("up_resize.png",position=TOP,row=4,col=1,on_press=on_press_up)
btn_down = arrow_button("down_resize.png",position=BOTTOM,row=8,col=1,on_press=on_press_down)
btn_right = arrow_button("right_resize.png",position=RIGHT,row=6,col=2,on_press=on_press_right)
btn_left = arrow_button("left_resize.png",position=LEFT,row=6,col=0,on_press=on_press_left)


###############################CONTROLLER##################################
canvas_speed = Canvas(root, width = 400, height = 400, bg="white")
canvas_speed.pack(side=BOTTOM)

gauge = tk_tools.Gauge(canvas_speed, max_value=20, label='Vitesse', unit='cm/s')
gauge.pack(side=TOP)
gauge.set_value(10)

slider = StringVar()
slider.set('10.00')

def change_scale(s):
    global gauge, vitesse
    vitesse = 500*float(s)/20
    slider.set('%0.2f' % float(s))
    gauge.set_value(float(s))
    r.set("vitesse",vitesse)
    
speed = Scale(canvas_speed, from_=0, to_=20, length=320, bd=3, orient=HORIZONTAL, resolution=1, command=change_scale)
speed.set(10)
speed.pack(side=BOTTOM)


###############################MAIN##################################
root.mainloop()