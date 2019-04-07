from tkinter import *
from tkinter import messagebox
from tkinter.messagebox import showerror

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib import style

import serial
import serial.tools.list_ports

import scipy
from scipy.interpolate import make_interp_spline, BSpline

import numpy as np

# define the USB serial port that is normally used by PuTTy 
BAUDRATE = 115200

BACKGROUND = '#F4F4F4'
DEFAULT_SIZE = 100
TIMEOUT = 50

t = 4

class Window(Frame):
    def __init__(self, master = None):
        Frame.__init__(self, master)

        self.master = master

        self.init_window() # run initialization code once a Window object is defined

    # initialize the window being created 
    def init_window(self):
        self.master.title("Wind Turbine Power Tracking") # set the title for this window
        
        menu = Menu(self.master)
        self.master.config(menu = menu)

        # create the "File" menu
        fileMenu = Menu(menu)
        menu.add_cascade(label = "File", menu = fileMenu) # add the cascade to the main menu
        fileMenu.add_command(label = "Quit", command = self.exit_program)


    def exit_program(self):
        if messagebox.askokcancel("Quit", "Are you sure you would like to quit?"):
            if portFound: # if a serial port was found, close it 
                serialPort.close()
            root.destroy() # destroy the application

portFound = 0 # global flag for port detection

"""
Check if a valid serial port connection has been established. The function
will continue updating the main window while waiting for a serial connection 
to be established.
"""
def wait_serial():
    while portFound == 0:
        root.update_idletasks()
        root.update()

    errorLabel.grid_forget() # remove the error message label
    retryButton.grid_forget() #remove the retry button

    #update string var
    succMsgSV.set(successMsg.format(port = portList[0][0]))

"""
Use the methods in the pyserial library to check for a valid
serial port connection. The ports being checked are specifically 
the COM ports.
"""
def check_serial():
    try: 
        global portList, serialPort, portFound
        portList = list(serial.tools.list_ports.comports()) # check the available COM ports

        serialPort = serial.Serial(portList[0][0], BAUDRATE, timeout = TIMEOUT) # connect to the first available COM port

        portFound = 1 # update flag
    except:
        pass

"""
Read the data coming in through the serial port and split it into
a list. The data is converted from its respective format to a 
useable string.
"""
def read_serial():
    serialOut = serialPort.readline() # read the next line of the serial port
    data = str(serialOut[:-2], "utf-8") # decode the input data received

    serialData = data.split(" ") # split the string into a set of individual strings and add it to a list

    return serialData

"""
Draw a new line in the graph with the new data read through the 
serial port. The repeated calling of this function creates a
'live' matplotlib graph.
"""
def draw_volttime(voltage):
    global timeArray, voltageArray, t

    timeArray = np.append(timeArray, t) # add the new time to the list 
    voltageArray = np.append(voltageArray, voltage) # add the new voltage reading to the list
    t += 1 # increase the time counter  

    timeNew = np.linspace(timeArray.min(), timeArray.max(), 300)

    spl = make_interp_spline(timeArray, voltageArray, k = 3)
    voltageNew = spl(timeNew)

    volttime.clear() # remove the previous line

    # configure the plot
    volttime.set_ylabel("Voltage")
    volttime.set_xlabel("Time")

    if(t > DEFAULT_SIZE):
        volttime.set_xlim(t-DEFAULT_SIZE, t)
    else:
        volttime.set_xlim(0, DEFAULT_SIZE)
        
    volttime.set_ylim(0.0, 17.5)
    volttime.plot(timeNew, voltageNew, color = "black") 
    vtcanvas.draw()

def draw_voltpower(voltage, power):
    global vpVoltageArray, vpPowerArray
    voltpowerDict[voltage] = power # add the new voltage : power pair to the dictionary

    # recreate the voltage and power arrays
    vpVoltageArray = np.array(sorted(list(voltpowerDict.keys())))
    vpPowerArray = np.array(list(voltpowerDict.values()))

    voltNew = np.linspace(vpVoltageArray.min(), vpVoltageArray.max(), 300)

    spl = make_interp_spline(vpVoltageArray, vpPowerArray, k = 3)
    powNew = spl(voltNew)

    # delete the old plot
    voltpower.clear()

    # recreate labels
    voltpower.set_ylabel("Power")
    voltpower.set_xlabel("Voltage")

    # reset the limits for the graph
    voltpower.set_xlim(0, 17.5)
    voltpower.set_ylim(0.0, 2.0)

    # draw the new graph
    voltpower.plot(voltNew, powNew, color = "red")
    vpcanvas.draw()

root = Tk() # define the root 
root.tk_setPalette(background = BACKGROUND)

initialWindow = Window(root) # define the main window

for i in range(6):
    initialWindow.grid_rowconfigure(i, weight = 1)


initialWindow.grid_columnconfigure(0, weight = 1)
initialWindow.grid_columnconfigure(1, weight = 1)

successMsg = "Connected to port {port}"
errorMsg = "Could not connect to serial port. Make sure your device is connected and try again." 

# create a retry button that checks for the availability of a serial port
retryButton = Button(text = "Retry", command = check_serial)

# create the success message label using a text variable
succMsgSV = StringVar()
successLabel = Label(root, textvariable = succMsgSV, font = ("Helvetica", 10))

# generate the root window
root.update_idletasks()
root.update()

# initial check for COM ports
try: 
    portList = list(serial.tools.list_ports.comports()) # check the available COM ports

    serialPort = serial.Serial(portList[0][0], BAUDRATE, timeout = TIMEOUT) # connect to the first available COM port

    #create and place a label showing the success message
    succMsgSV.set(successMsg.format(port = portList[0][0]))
except IndexError:
    # create and place a label for the error message
    errorLabel = Label(root, text = errorMsg, anchor = CENTER)
    errorLabel.grid(row = 0, column = 0)

    retryButton.grid(row = 2, column = 0, sticky = S) # place the retry button for the user to use

    wait_serial() # wait for serial port connection

#create and place labels for the values read
inVolts = StringVar()
Label(root, textvariable = inVolts, bg = "white", font = ("Arial", 16)).grid(row = 0, column = 1, sticky = E+W, pady = 2)

inCurrent = StringVar()
Label(root, textvariable = inCurrent, bg = "white", font = ("Arial", 16)).grid(row = 1, column = 1, sticky = E+W, pady = 2)

inPower = StringVar()
Label(root, textvariable = inPower, bg = "white", font = ("Arial", 16)).grid(row = 2, column = 1, sticky = E+W, pady = 2)

outVolts = StringVar()
Label(root, textvariable = outVolts, bg = "white", font = ("Arial", 16)).grid(row = 3, column = 1, sticky = E+W, pady = 2)

dutyCyc = StringVar()
Label(root, textvariable = dutyCyc, bg = "white", font = ("Arial", 16)).grid(row = 4, column = 1, sticky = E+W, pady = 2)

inAngle = StringVar()
Label(root, textvariable = inAngle, bg = "white", font = ("Arial", 16)).grid(row = 5, column = 1, sticky = E+W, pady = 2)

# place the success message label
successLabel.grid(row = 6, column = 0, sticky = N+S+E+W, columnspan = 5)

# create and place labels for each reading
Label(root, text = "Input Voltage (V):", font = ("Helvetica", 16), anchor = W).grid(row = 0, column = 0, sticky = N+S+E+W, pady = 2, padx = 3)
Label(root, text = "Input Current (A):", font = ("Helvetica", 16), anchor = W).grid(row = 1, column = 0, sticky = N+S+E+W, pady = 2, padx = 3)
Label(root, text =  "Input Power(W):", font = ("Helvetica", 16), anchor = W).grid(row = 2, column = 0, sticky = N+S+E+W, pady = 2, padx = 3)
Label(root, text = "Output Voltage(V):", font = ("Helvetica", 16), anchor = W).grid(row = 3, column = 0, sticky = N+S+E+W, pady = 2, padx = 3)
Label(root, text = "Duty Cycle:", font = ("Helvetica", 16), anchor = W).grid(row = 4, column = 0, sticky = N+S+E+W, pady = 2, padx = 3)
Label(root, text =  "Angle:", font = ("Helvetica", 16)).grid(row = 5, column = 0, sticky = N+S+E+W, pady = 2, padx = 3)

"""
    Voltage-Time graph

"""
# create the figures for the voltage-time graph
vtfig = Figure(figsize=(5,4), dpi=100)
vtfig.patch.set_facecolor(BACKGROUND)

# initialize voltage and time arrays
timeArray = np.array(sorted([0, 1, 2, 3]))
voltageArray = np.array([0.20, 0.20, 0.20, 0.20])

# create voltage-time subplot
volttime = vtfig.add_subplot(111)
volttime.set_ylabel("Voltage")
volttime.set_xlabel("Time")
volttime.set_xlim(3, 20)
volttime.set_ylim(0.0, 15.0)

# create and drag the canvas
vtcanvas = FigureCanvasTkAgg(vtfig, master = root)
vtcanvas.get_tk_widget().grid(row = 0, column = 4, rowspan = 6, padx = 15)
vtcanvas.draw()

"""
    Voltage-Power graph
    
"""
# create figure
vpfig = Figure(figsize=(5,4), dpi=100)
vpfig.patch.set_facecolor(BACKGROUND)

# initialize the voltage-power dictionary
voltpowerDict = {0: 0.00, 0.1: 0.01, 0.2: 0.01, 0.3 : 0.02}

# create arrays using the dictionary key-value pairs
vpVoltageArray = np.array(sorted(list(voltpowerDict.keys())))
vpPowerArray = np.array(list(voltpowerDict.values()))

# create the subplot
voltpower = vpfig.add_subplot(111)
voltpower.set_ylabel("Power")
voltpower.set_xlabel("Voltage")


# create canvas for subplot
vpcanvas = FigureCanvasTkAgg(vpfig, master = root)
vpcanvas.get_tk_widget().grid(row = 0, column = 3, rowspan = 6, padx = 15)
vpcanvas.draw()

while 1: # main program loop
         
    sensorData = read_serial()
    
    try:
        if sensorData[1]: # this is done so the first field isnt rendered blank in the case of a disconnection
            pass 

        # set the text variable data
        inVolts.set(sensorData[0])
        inCurrent.set(sensorData[1])
        inPower.set(sensorData[2])
        outVolts.set(sensorData[3])
        inAngle.set(sensorData[4])
        dutyCyc.set(sensorData[5])
    except IndexError: # when serial port is disconnected, an IndexError is raised 
        messagebox.showerror(title = "Connection Error", message = "Lost connection to serial port.")

        succMsgSV.set("Lost connection to port {port}".format(port = portList[0][0])) 
        successLabel.config(foreground = "#E30000")
        while 1:
            # keep updating idle tasks after connection is lost
            root.update_idletasks()
            root.update()
    
    # draw the graphs in their corresponding canvas
    draw_volttime(float(sensorData[3])) 
    draw_voltpower(float(sensorData[3]), float(sensorData[2])) 

    # update the root window
    root.update_idletasks()
    root.update()