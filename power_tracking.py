from tkinter import *
from tkinter import messagebox

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
        self.pack(fill = BOTH, expand = 1) # fill up window and adjust as necessary

        menu = Menu(self.master)
        self.master.config(menu = menu)

        # create the "File" menu
        fileMenu = Menu(menu)
        menu.add_cascade(label = "File", menu = fileMenu) # add the cascade to the main menu
        fileMenu.add_command(label = "Quit", command = self.exit_program)


    def exit_program(self):
        root.destroy()

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

    errorLabel.place_forget() # remove the error message label
    retryButton.place_forget() #remove the retry button

    # create and place the success message label
    successLabel = Label(root, text = successMsg.format(port = portList[0][0]))
    successLabel.place(x = 0, y = 0)

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

        print(successMsg.format(port = portList[0][0]))

        global portFound # modify the global flag in the function
        portFound = 1
    except:
        pass
    

root = Tk() # define the root 
root.geometry("500x200") # set the default size of the root

initialWindow = Window(root) # define the main window

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
    successLabel = Label(root, text = successMsg.format(port = portList[0][0]))
    successLabel.place(x = 0, y = 0)
except:
    # create and place a label for the error message
    errorLabel = Label(root, text = errorMsg)
    errorLabel.place(x = 0, y = 0)

    retryButton.place(x = 0, y = 20) # place the retry button for the user to use

    wait_serial() # wait for serial port connection


while 1: # main program loop
    dataIn = serialPort.readline() # read the current line in the serial port

    dataLabel = Label(root, text = dataIn) # create a label for the current data in the serial port
    dataLabel.place(x = 0, y = 25) # place the label containing the serial port data

    # update the display
    root.update_idletasks()
    root.update()

    dataLabel.place_forget()