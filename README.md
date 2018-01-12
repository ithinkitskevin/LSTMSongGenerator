# LSTMSongGenerator
Using TensorFlow as backend on top of Keras, the computer can simulate music

Initially, I've gotten all the midi files from the website http://www.piano-midi.de/chopin.htm
After downloading the midi files, I translated the files into .csv format for an easier read. I did this by getting a folder from the website http://www.fourmilab.ch/webtools/midicsv/ 
After getting the folder, I used the bash shell to run the compiled C program i got from the website with the folder full of .mid files

As of now, I'm only getting the right hand part of the piano. This is due to the right hand usually playing the melody.
I've translated the right hand melody into its ASCII letter counterpart, than verctorized the letters for the LSTM to read. 
I have chosen LSTM as I've need a neural network that actively maintained a self connected loop without any degradation. Next, I might experiment using other Neural Network such as Char-RNN or GRU.
