# this is the final code for voltage time graph function
import matplotlib.pyplot as plt
import numpy as np
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
                # y0 = (float(temp_line[1])3.3/((2*12)-1))/1000 #gives the 2nd element in the list
                y0 =((float(temp_line[1]))/4095)*3.3 
                gain= 35
                yout= ((y0-1.65)/gain)*1000 #this our voltage :)
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

if(_name=="main_"):
    Com= serial.Serial("/dev/ttyACM0", 115200, timeout=3) #the timeout tells the communication channel to wait for 3 seconds
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
