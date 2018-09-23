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

count = 0

def getFileDir():
    ''' Gets the list of data directories '''
    csv_dir = os.listdir("data")

    list_data = []

    for i, elem in enumerate(csv_dir):
        if '.csv' == elem[-4:]:
            list_data.append("data/" + elem)

    return list_data


def getDataFromFile():
    ''' Scrapes the data from the list of directories '''
    # TODO: Fix the data & make it so that you can get more data from the .csv file
    global count
    count = 0
    init_text = ''

    for csvFile in getFileDir():
        strArr = ""
        startCount = False
        timeBuffer = 0
        with open(csvFile, 'r', encoding='latin-1') as f:
            myCsv = csv.reader(f,delimiter = ',')
            for row in myCsv:
                if row:
                    if row[2].strip() == 'Title_t':
                        if row[3].strip() == '"Piano right"':
                            startCount = True
                            continue
                    if startCount == True:
                        if row[2].strip() == 'End_track':
                            break
                        if row[2].strip() == 'Note_on_c':
                            if row[5].strip() != '0':
                                pitch = chr(int(row[4].strip())+12)
                            else:
                                continue
                        else:
                            continue
                        if timeBuffer != int(row[1].strip()):
                            strArr += ' '
                        strArr += pitch
                        timeBuffer = int(row[1].strip())
                        if row[2].strip().find("off") != -1:
                            continue
            init_text += strArr
            count += 1

    return init_text

def train(x_data_set, y_data_set, init_text):
    ''' Train using x dataset and y dataset '''
    generated_song = []

    for iteration in range(501):
        print('iteration - ',iteration)
        model.fit(x_data_set, y_data_set, batch_size=128, epochs=1, verbose=1)
        start_index = random.randint(0, len(init_text) - seqLen - 1)
        
        gener = ''
        sentence = init_text[start_index: start_index + seqLen]
        gener += sentence
        print('Seed: "' + sentence + '"')
        
        sys.stdout.write(gener)
        
        for i in range(aver_len):
            x_pred = np.zeros((1, seqLen, len(chars)))
            for t, char in enumerate(sentence):
                x_pred[0, t, char_ind[char]] = 1.
            preds = model.predict(x_pred, verbose=0)[0]
            nextInd = np.random.choice(len(chars),p=preds)
            nextChar = ind_char[nextInd]
            gener += nextChar
            sentence = sentence[1:] + nextChar

        if iteration%100 == 0:
            generated_song.append(gener)

    return generated_song[len(generated_song)-1]


def translateToCsv(raw_data_set):
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

    listText = list(raw_data_set)
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
    return True



init_text = getDataFromFile()

aver_len = int(len(init_text)/count)
chars = list(set(init_text))
list(set(init_text)).sort()

ind_char = {ind:char for ind, char in enumerate(chars)}
char_ind = {char:ind for ind, char in enumerate(chars)}

''' Gets the training data '''
section = []
next_char = []
seqLen = 40
    
for i in range(len(init_text) - seqLen):
    section.append(init_text[i: i + seqLen])
    next_char.append(init_text[i + seqLen])

x_training_data_set = np.zeros((len(section), seqLen, len(chars)))
y_training_data_set = np.zeros((len(section), len(chars)))

''' Vectorize the x_training_data_set and y_training_data_set '''
for i, sent in enumerate(section):
    for j, char in enumerate(sent):
        x_training_data_set[i, j, char_ind[char]] = 1
    y_training_data_set[i, char_ind[next_char[i]]] = 1

''' Create a LSTM Model '''
# TODO Look at the dropout, see what you can do better
model = Sequential([
                    LSTM(124, input_shape=(seqLen, len(chars)),return_sequences = True),
                    Dropout(0.25),
                    LSTM(124, input_shape=(seqLen, len(chars))),
                    Dropout(0.5),
                    Dense(len(chars),activation='softmax'),
                    ])
optimize = optimizers.rmsprop(lr=0.015)
model.compile(loss='categorical_crossentropy', optimizer=optimize)

raw_data = train(x_training_data_set, y_training_data_set, init_text)

if translateToCsv(raw_data):
    print("Finished")
