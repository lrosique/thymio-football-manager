#pip3 install tk_tools

import tkinter as tk
import tk_tools
 
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


def on_press(event):
    print("button was pressed")

def on_release(event):
    print("button was released")

btn_up.bind("<ButtonPress>", on_press)
btn_up.bind("<ButtonRelease>", on_release)
btn_down.bind("<ButtonPress>", on_press)
btn_down.bind("<ButtonRelease>", on_release)
btn_left.bind("<ButtonPress>", on_press)
btn_left.bind("<ButtonRelease>", on_release)
btn_right.bind("<ButtonPress>", on_press)
btn_right.bind("<ButtonRelease>", on_release)


gauge = tk_tools.Gauge(bottomFrame, max_value=20, label='Vitesse', unit='cm/s')
gauge.grid(column=1, row=0)
gauge.set_value(0)

slider = tk.StringVar()
slider.set('0.00')

def change_scale(s):
    global gauge
    slider.set('%0.2f' % float(s))
    gauge.set_value(float(s))
    
tk.Scale(bottomFrame, from_=0, to_=20, length=320, bd=3, orient=tk.HORIZONTAL, resolution=0.5,
    command=change_scale).grid(column=0, row=1, columnspan=3)

#tk.Label(rightFrame, textvariable=slider).grid(column=1, row=0, columnspan=5)

window.mainloop()