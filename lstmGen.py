import keras
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Activation
from keras.layers import Dropout
from keras.layers import LSTM
from keras import optimizers

import os 
import csv
import numpy as np
import sys
import io
import random

print('-'*10,end='')
print('Starting to get all files and making them into a String',end='')
print('-'*10)

csvDir = os.listdir("data")

arr = []

for i, elem in enumerate(csvDir):
    if '.csv' == elem[-4:]:
        arr.append("data/" + elem)

initText = ''
count = 0

for csvFile in arr:
    strArr = ""
    startCount = False
    timeBuffer = 0
    #print('in for loop',csvFile)
    with open(csvFile, 'r', encoding='latin-1') as f:
        myCsv = csv.reader(f,delimiter = ',')
        for row in myCsv:
            if row:
                #print(row)
                if row[2].strip() == 'Title_t':
                    if row[3].strip() == '"Piano right"':
                        #print('Start Counting')
                        startCount = True
                        continue
                if startCount == True:
                    if row[2].strip() == 'End_track':
                        #print('Ending')
                        break
                    if row[2].strip() == 'Note_on_c':
                        if row[5].strip() != '0':
                            #print('Adding-',row[4].strip(),end='')
                            pitch = chr(int(row[4].strip())+12)
                            #print(' and its note ', pitch)
                        else:
                            continue
                    else:
                        continue
                    if timeBuffer != int(row[1].strip()):
                        strArr += ' '
                    #print('"'+ pitch+'"')
                    strArr += pitch
                    timeBuffer = int(row[1].strip())
                    if row[2].strip().find("off") != -1:
                        #print('off is here',row[2])
                        continue
        initText += strArr
        count += 1

#print(initText)

print('-'*10,end='')
print('Finished getting all files and making them into a String',end='')
print('-'*10)

print('-'*10,end='')
print('Starting LSTM',end='')
print('-'*10)

averLen = int(len(initText)/count)
chars = list(set(initText))
chars = sorted(chars)
#print(chars)

ind_char = {ind:char for ind, char in enumerate(chars)}
#print('ind_char' + ind_char)
char_ind = {char:ind for ind, char in enumerate(chars)}
#print('char_ind' + char_ind)

section = []
next_char = []
seqLen = 40

for i in range(len(initText) - seqLen):
    section.append(initText[i: i + seqLen])
    next_char.append(initText[i + seqLen])

xTrainD = np.zeros((len(section), seqLen, len(chars)))
yTrainD = np.zeros((len(section),len(chars)))

print('-'*15,end='')
print('Vectorizing the Data for Easy Input',end='')
print('-'*15)

for i, sent in enumerate(section):
    for j, char in enumerate(sent):
        xTrainD[i, j, char_ind[char]] = 1
    yTrainD[i, char_ind[next_char[i]]] = 1

print('-'*17,end='')
print('Finished Vectorizing',end='')
print('-'*17)

print('-'*15,end='')
print('Creating the LSTM Model',end='')
print('-'*15)

model = Sequential([
    LSTM(124, input_shape=(seqLen, len(chars)),return_sequences = True),
    Dropout(0.25),
    LSTM(124, input_shape=(seqLen, len(chars))),
    Dropout(0.5),
    Dense(len(chars),activation='softmax'),
])
optimize = keras.optimizers.rmsprop(lr=0.015)
model.compile(loss='categorical_crossentropy', optimizer=optimize)

print('-'*10,end='')
print('Finished Creating the LSTM Model',end='')
print('-'*10)

generatedSong = []

print('-'*25,end='')
print('Training',end='')
print('-'*25)

for iteration in range(501):
    print('iteration - ',iteration)
    model.fit(xTrainD, yTrainD, batch_size=128, epochs=1, verbose=1)
    start_index = random.randint(0, len(initText) - seqLen - 1)
    
    gener = ''
    sentence = initText[start_index: start_index + seqLen]
    gener += sentence
    print('Seed: "' + sentence + '"')
    
    sys.stdout.write(gener)
    
    for i in range(averLen):
        x_pred = np.zeros((1, seqLen, len(chars)))
        for t, char in enumerate(sentence):
            x_pred[0, t, char_ind[char]] = 1.
        preds = model.predict(x_pred, verbose=0)[0]
        nextInd = np.random.choice(len(chars),p=preds)
        nextChar = ind_char[nextInd]
        gener += nextChar
        sentence = sentence[1:] + nextChar
        print(nextChar,end="")    
    print()
    if iteration%100 == 0:
        generatedSong.append(gener)

finalS = generatedSong[len(generatedSong)-1]

print('-'*23,end='')
print('Done Training',end='')
print('-'*23)

# Translating back
fileN = 'lstmFile.csv'
filename = open(fileN,'w')
filename.writelines([
    '0, 0, Header, 1, 2, 480\n',
    '1, 0, Start_track\n',
    '1, 0, Title_t, "LSTM Generated Music"\n',
    '1, 0, Time_signature, 3, 2, 24, 8,\n',
    '1, 0, End_track\n'
    '1, 0, Tempo, 375000\n',
    '2, 0, Start_track\n',
    '2, 0, Title_t, "Piano right"\n',
    '2, 0, Program_c, 1, 20\n'
])

listText = list(finalS)
ite = 0
bufPit = []
time = 0
indIte = 0
while ite < len(listText):
    if listText[ite] != ' ':
        pitch = ord(listText[ite]) - 12
        filename.write('2, '+str(time)+', Note_on_c, 0, '+str(pitch)+', 50\n')
        bufPit.append(pitch)
    else:
        indIte += 1
        time = 480 * indIte
        for pitch in bufPit:
            filename.write('2, '+str(time)+', Note_on_c, 0, '+str(pitch)+', 0\n')
        del bufPit[:]
    ite += 1

filename.writelines([
    '2, '+str(time) +', End_track\n',
    '0, 0, End_of_file\n'
])
print('Finished')
