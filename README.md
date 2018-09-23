# LSTMSongGenerator
Using TensorFlow as backend on top of Keras. Imitates Chopin's right hand melody.

[Gotten all the midi files from the website](http://www.piano-midi.de/chopin.htm)

[Converted the midi files to .csv files](http://www.fourmilab.ch/webtools/midicsv/)

Utilized the .csv files to train the LSTM Model. LSTM  was chosen as I've need a neural network that actively maintained a self connected loop without any degradation. Next, I might experiment using other Neural Network such as Char-RNN or GRU.
