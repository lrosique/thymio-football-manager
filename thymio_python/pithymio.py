import dbus
import dbus.mainloop.glib
import gobject
from optparse import OptionParser

proxSensorsVal=[0,0,0,0,0]


def motors(motor_right, motor_left):
    network.SetVariable("thymio-II", "motor.left.target", [motor_left])
    network.SetVariable("thymio-II", "motor.right.target", [motor_right])

def get_proxSensors():
    network.GetVariable("thymio-II", "prox.horizontal",reply_handler=get_variables_reply,error_handler=get_variables_error)

def get_variables_reply(r):
    global proxSensorsVal
    proxSensorsVal=r

def get_variables_error(e):
    print('error:')
    print(str(e))
    loop.quit()

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-s", "--system", action="store_true", dest="system", default=False,help="use the system bus instead of the session bus")

    (options, args) = parser.parse_args()

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    if options.system:
        bus = dbus.SystemBus()
    else:
        bus = dbus.SessionBus()

    #Create Aseba network
    network = dbus.Interface(bus.get_object('ch.epfl.mobots.Aseba', '/'), dbus_interface='ch.epfl.mobots.AsebaNetwork')

    #print in the terminal the name of each Aseba NOde
    print(network.GetNodesList())

    #GObject loop
    print('starting loop')
    loop = gobject.MainLoop()
    #call the callback of Braitenberg algorithm
    handle = gobject.timeout_add (100, Braitenberg) #every 0.1 sec
    loop.run()
