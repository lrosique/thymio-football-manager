### GUI ###
#pip3 install tk_tools
import tkinter as tk
import tk_tools
import redis

r = redis.StrictRedis(host="localhost", port=6379, db=0)

window = tk.Tk()
window.geometry('800x600')
window.title("Commande de contrôle du Thymio-II")

leftFrame = tk.Frame(window, width=350,height=300)
leftFrame.grid(row=0, column=0)

bottomFrame = tk.Frame(window, width=350,height=300)
bottomFrame.grid(row=2, column=0)

def arrow_button(img_name,row=0,col=0,on_press=None):
    photo = tk.PhotoImage(file="images/"+img_name)
    btn = tk.Button(leftFrame, compound=tk.TOP, width=100, height=100, image=photo, bg='#51e886')
    btn.grid(column=col, row=row)
    btn.bind("<ButtonPress>", on_press)
    btn.bind("<ButtonRelease>", stop)
    btn.image = photo
    return btn

def on_press_up(event):
    global vitesse, thymio,r
    print("UP")
    r.set("action","up")
    #thymio.setMotors(vitesse,vitesse)
    
def on_press_down(event):
    global vitesse, thymio,r
    print("DOWN")
    r.set("action","down")
    #thymio.setMotors(-vitesse,-vitesse)

def on_press_left(event):
    global vitesse, thymio,r
    print("LEFT")
    r.set("action","left")
    #thymio.setMotors(-vitesse,vitesse)
    
def on_press_right(event):
    global vitesse, thymio,r
    print("RIGHT")
    r.set("action","right")
    #thymio.setMotors(vitesse,-vitesse)

def stop(event):
    global thymio,r
    print("STOP")
    r.set("action","stop")
    #thymio.setMotors(0,0)

btn_up = arrow_button("up_resize.png",row=4,col=1,on_press=on_press_up)
btn_down = arrow_button("down_resize.png",row=8,col=1,on_press=on_press_down)
btn_right = arrow_button("right_resize.png",row=6,col=2,on_press=on_press_right)
btn_left = arrow_button("left_resize.png",row=6,col=0,on_press=on_press_left)

gauge = tk_tools.Gauge(bottomFrame, max_value=20, label='Vitesse', unit='cm/s')
gauge.grid(column=1, row=0)
gauge.set_value(0)

slider = tk.StringVar()
slider.set('0.00')
r.set("vitesse",0)
r.set("action","stop")

def change_scale(s):
    global gauge, vitesse
    vitesse = 500*float(s)/20
    slider.set('%0.2f' % float(s))
    gauge.set_value(float(s))
    r.set("vitesse",vitesse)
    
tk.Scale(bottomFrame, from_=0, to_=20, length=320, bd=3, orient=tk.HORIZONTAL, resolution=0.5, command=change_scale).grid(column=0, row=1, columnspan=3)

window.mainloop()