#!/usr/bin/env python
import sqlite3
import bitalino
import time
import numpy
from scipy import signal

def highpass(data, BUTTER_ORDER=3, sampling_rate=100, cut_off=0.7):
    Wn = (float(cut_off) / (float(sampling_rate) / 2.0), 0.95)
    b, a = signal.butter(BUTTER_ORDER, Wn, 'pass')
    return signal.filtfilt(b, a, data, axis=0)

print("BITalino Data Collection")
#time.sleep(2)

# Database
database = "data.db"
#database = "C:\Users\User\Desktop\Teste\SQlite_example"

# Device MacAddress: Blt1 = 98:D3:81:FD:61:22, Blt2 = 20:15:12:22:81:68
macAddress = "98:D3:81:FD:61:22"

# Acquisition Channels ([0-5])
acqChannels = [0,1,2,3,4,5]

# Sampling Frequency (Hz)
samplingFreq = 10

# Compute Average Time (s)
timeCycle = 1

# Acquisition Time (s) - None for Infinite
acquisitionTime = 5


database = sqlite3.connect(database)
cursor = database.cursor()

# Restart Database
cursor.execute("Drop table Configuration")
cursor.execute("Drop table Data")

try:
    cursor.execute("CREATE TABLE Configuration(Id INTEGER PRIMARY KEY, MacAddress TEXT, SamplingFreq INT, InitTime TEXT, timeCycle INT, acqChannels TEXT, channelSize INT)")
    cursor.execute("CREATE TABLE Data(Configuration INT, Time INT, Channel0 REAL, Channel1 REAL, Channel2 REAL, Channel3 REAL, Channel4 REAL, Channel5 REAL, FOREIGN KEY(Configuration) REFERENCES Configuration(Id))")
except Exception as e:
    pass

device = bitalino.BITalino(macAddress)
device.start(samplingFreq, acqChannels)
print("Device connected.")

cursor.execute("INSERT INTO Configuration(MacAddress, SamplingFreq, InitTime, timeCycle, acqChannels, channelSize) VALUES" +
               "('" + macAddress + "'," + str(samplingFreq) + ",'" + time.strftime("%c") + "', " + str(timeCycle) + ",'" + str(acqChannels) + "'," + str(len(acqChannels)) + ");")
database.commit()

lastIndex = cursor.lastrowid
print("Current Configuration ID: " + str(lastIndex))
print("Collecting data.")

currentTime = 0
while (acquisitionTime is None) or (acquisitionTime > 0):
    avg_data = [lastIndex, currentTime, None, None, None, None, None, None]
    data = device.read(samplingFreq*timeCycle)
    """
    Values acquired per second:
    	Frequency = 10Hz => 10 values
    	Frequency = 100Hz => 100 values
    	...
    	...
    	data[:,5] => Channel 1 (on BITalino)
    	data[:,6] => Channel 2
    	data[:,7] => Channel 3
    	data[:,8] => Channel 4
    	data[:,9] => Channel 5
    	data[:,10] => Channel 5
    """
    y_acc = data[:,5]
    #yhat = highpass(y_acc,3,1000,0.7)
    print("%=====================%")
    #print("data[:,5]")
    #print(y_acc)	# acc data for channel 1
    #print(y_acc[2])	# acc data for channel 1
    #print(yhat[2])	# acc data for channel 1
    #print(y_acc.shape)
    print("%=====================%")

    min_acc = min(data[:,5])
    max_acc = max(data[:,5])

    print(min_acc)
    print(max_acc)
    
    """
    Apply filter to acc data here
    """

    for ind in range(5, data.shape[1]):
        avg_data[acqChannels[ind - 5] + 2] = numpy.mean(numpy.fabs(data[:,ind]))
        # print(ind)
        # Aply transfer functions here;
        #avg_data[2] = ((avg_data[2] - 208)/(312 - 208))*2-1
        avg_data_conv = ((avg_data[2]-min_acc)/(max_acc-min_acc))*2-1
    print("Acc mean: = ", avg_data[2])
    print("Acc mean conv: = ", abs(avg_data_conv))
    cursor.execute("INSERT INTO Data(Configuration, Time, Channel0, Channel1, Channel2, Channel3, Channel4, Channel5) VALUES" +
                    "(" + str(avg_data).replace("None", "null")[1:-1] + ");")
    database.commit()
    currentTime += timeCycle
    if acquisitionTime is not None:
        acquisitionTime -= timeCycle

device.stop()
device.close()
print("Connection closed.")

# UnComment to Print Tables

"""
print("")
print("Configurations:")
cursor.execute("Select * from Configuration where Configuration ")
for config in cursor.fetchall():
    print(config)
print("")
print("Data:")
cursor.execute("Select * from Data")
for data in cursor.fetchall():
    print(data)
"""
print("Program will close.")
time.sleep(1)
