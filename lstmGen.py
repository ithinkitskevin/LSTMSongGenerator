from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Activation
from keras.layers import Dropout
from keras.layers import LSTM
from keras.optimizers import RMSprop

import os 
import csv
import numpy as np
import sys
import io

csvDir = os.listdir("data")

arr = []

for i, elem in enumerate(csvDir):
    if '.csv' == elem[-4:]:
        arr.append("data/" + elem)

translated = []

for csvFile in arr:
    strArr = ""
    startCount = False
    timeBuffer = 0
    #print('in for loop',csvFile)
    with open(csvFile) as f:
        myCsv = csv.reader(f,delimiter = ',')
        for row in myCsv:
            if row:
                if row[2].strip().find("off") != -1:
                    #print('off is here',row[2])
                    continue
#                print(row[2].strip())
                if row[2].strip() == 'Program_c':
#                    print('Start Counting')
                    startCount = True
                    continue
                if startCount == True:
                    if row[2].strip() == 'End_track':
#                       print('Ending')
                        break
#                    print('Adding-',row[4].strip())
                    pitch = chr(int(row[4].strip())+12)
                    if timeBuffer != int(row[1].strip()):
                        strArr += ' '
#                    print('"'+ pitch+'"')
                    strArr += pitch
                    timeBuffer = int(row[1].strip())
        translated.append(strArr)

print(translated)

#All the midi files are now translated now.

