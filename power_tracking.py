from tkinter import *
from tkinter import messagebox
from tkinter.messagebox import showerror

import serial
import serial.tools.list_ports

# define the USB serial port that is normally used by PuTTy 
BAUDRATE = 115200

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

    #create and place a label showing the success message
    Label(root, text = successMsg.format(port = portList[0][0]), font = ("Helvetica", 10)).grid(row = 5, column = 0, sticky = N+S+E+W, columnspan = 2)

"""
Use the methods in the pyserial library to check for a valid
serial port connection. The ports being checked are specifically 
the COM ports.
"""
def check_serial():
    try: 
        global portList
        portList = list(serial.tools.list_ports.comports()) # check the available COM ports

        global serialPort
        serialPort = serial.Serial(portList[0][0], BAUDRATE, timeout = 100) # connect to the first available COM port

        global portFound # modify the global flag in the function
        portFound = 1
    except:
        pass

def read_serial():
    serialOut = serialPort.readline() # read the next line of the serial port
    data = str(serialOut[:-2], "utf-8") # decode the input data received

    serialData = data.split(" ") # split the string into a set of individual strings and add it to a list

    return serialData

root = Tk() # define the root 
#root.geometry("1000x500") # set the default size of the root

initialWindow = Window(root) # define the main window

for i in range(6):
    initialWindow.grid_rowconfigure(i, weight = 1)


initialWindow.grid_columnconfigure(0, weight = 1)
initialWindow.grid_columnconfigure(1, weight = 1)


successMsg = "Connected to port {port}"
errorMsg = "Could not connect to serial port. Make sure your device is connected and try again." 

# create a retry button that checks for the availability of a serial port
retryButton = Button(text = "Retry", command = check_serial)

# generate the root window
root.update_idletasks()
root.update()

# initial check for COM ports
try: 
    portList = list(serial.tools.list_ports.comports()) # check the available COM ports

    serialPort = serial.Serial(portList[0][0], BAUDRATE, timeout = 100) # connect to the first available COM port

    #create and place a label showing the success message
    Label(root, text = successMsg.format(port = portList[0][0]), font = ("Helvetica", 10)).grid(row = 5, column = 0, sticky = N+S+E+W, columnspan = 2)
except:
    # create and place a label for the error message
    errorLabel = Label(root, text = errorMsg, anchor = CENTER)
    errorLabel.grid(row = 0, column = 0)

    retryButton.grid(row = 2, column = 0, sticky = S) # place the retry button for the user to use

    wait_serial() # wait for serial port connection

#create and place labels for the values read
inVolts = StringVar()
Label(root, textvariable = inVolts, bg = "white", font = ("Arial", 16)).grid(row = 0, column = 1, sticky = N+S+E+W, pady = 2)

inCurrent = StringVar()
Label(root, textvariable = inCurrent, bg = "white", font = ("Arial", 16)).grid(row = 1, column = 1, sticky = N+S+E+W, pady = 2)

outVolts = StringVar()
Label(root, textvariable = outVolts, bg = "white", font = ("Arial", 16)).grid(row = 2, column = 1, sticky = N+S+E+W, pady = 2)

inPower = StringVar()
Label(root, textvariable = inPower, bg = "white", font = ("Arial", 16)).grid(row = 3, column = 1, sticky = N+S+E+W, pady = 2)

inAngle = StringVar()
Label(root, textvariable = inAngle, bg = "white", font = ("Arial", 16)).grid(row = 4, column = 1, sticky = N+S+E+W, pady = 2)

# create and place labels for each reading
Label(root, text = "Input Voltage (V):", font = ("Helvetica", 16), anchor = W).grid(row = 0, column = 0, sticky = N+S+E+W, pady = 2, padx = 3)
Label(root, text = "Input Current (A):", font = ("Helvetica", 16), anchor = W).grid(row = 1, column = 0, sticky = N+S+E+W, pady = 2, padx = 3)
Label(root, text =  "Input Power(W):", font = ("Helvetica", 16), anchor = W).grid(row = 2, column = 0, sticky = N+S+E+W, pady = 2, padx = 3)
Label(root, text = "Output Voltage(V):", font = ("Helvetica", 16), anchor = W).grid(row = 3, column = 0, sticky = N+S+E+W, pady = 2, padx = 3)
Label(root, text =  "Angle:", font = ("Helvetica", 16)).grid(row = 4, column = 0, sticky = N+S+E+W, pady = 2, padx = 3)

while 1: # main program loop
         
    sensorData = read_serial()
        
    try:
        # set the text variable data
        inVolts.set(sensorData[0])
        inCurrent.set(sensorData[1])
        outVolts.set(sensorData[2])
        inPower.set(sensorData[3])
        inAngle.set(sensorData[4])
    except:
        messagebox.showerror(title = "Connection Error", message = "Lost connection to serial port.") 
        while 1:
            # keep updating idle tasks after connection is lost
            root.update_idletasks()
            root.update()
            

    # update the root window
    root.update_idletasks()
    root.update()