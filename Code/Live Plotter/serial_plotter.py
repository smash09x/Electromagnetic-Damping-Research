# this is the final code for voltage time graph function
import matplotlib.pyplot as plt
import numpy as np
import sys
import serial 
#returns the numpy array for plotting
def ConvertIntoArray(raw_list: list):
    x= list()
    y= list()
    for line in raw_list: #the loop will go through all the elements
        if("," in line):
            try:
                temp_line= line.strip().split(",") # split returns a list with the word being the element 
                x0 = float(temp_line[0])/1000
                yout = float(temp_line[1])/1000 # firmware already sends input-referred µV; convert to mV
                y.append(yout)
                x.append(x0)
            except ValueError:
                pass
    return np.array(x), np.array(y)
#records the raw data 
def RecordData(micro_controller:serial.Serial):
    raw_list= list()
    print("Press del or Ctrl+C to escape")
    try:
        print("Recording has started.....")
        while True:
             raw_line= micro_controller.readline().decode("utf-8", errors= "ignore").strip() #errors= "ignore" ignores any kind of noise and unrelated value. The strip() function removes whitespaces, if any parameter is given it will remove those in the string
             raw_list.append(raw_line)
    except KeyboardInterrupt:
        print("User has terminated recording")
    finally:
        micro_controller.close()
    return raw_list

if __name__ == "__main__":
    port = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0" # e.g. COM3 on Windows
    Com= serial.Serial(port, 115200, timeout=3) #the timeout tells the communication channel to wait for 3 seconds
    raw_data= RecordData(Com)
    t,v = ConvertIntoArray(raw_data)
    plt.title("Volt-Time graph, 0 OHMS", size= 25, fontweight= "bold")
    plt.plot(t,v , color= "darkblue", linewidth= 1, label= "Experimental Graph")
    plt.xlabel("Time/msec", size= 15, color= "darkgreen")
    plt.ylabel("Voltage/ mV", size= 15, color= "darkgreen")
    plt.minorticks_on()
    plt.grid(True, which="both")
    plt.legend()
    plt.show()
