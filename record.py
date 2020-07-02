import nltk
#nltk.download('punkt')
import nltk.data
import pyaudio
import wave
import pickle
import numpy as np
from sklearn import mixture
import sys
from pynput import keyboard
import sounddevice as sd
import soundfile as sf
import time
import os
from scipy.io.wavfile import read
from featureextraction import extract_features
import warnings
warnings.filterwarnings("ignore")

index = 1
username = "Abc"
filename = 'trainingData/'
train_file = "newmodeltrain.txt" 
fileopen = open(train_file, 'w+')

chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

p = pyaudio.PyAudio()

stream = p.open(format = FORMAT,
                channels = CHANNELS,
                rate = RATE,
                input = True,
                frames_per_buffer = chunk)

print("Repeatedly record 3 times for speaker-recognition")
print("Press s to start record, q to quit record, esc to exit program")

filename = filename+username
if not os.path.exists(filename):
    os.makedirs(filename)

all = []


def on_press(key):
    global index
    if key == keyboard.Key.esc:
        stream.close()
        p.terminate()
        return False  # stop listener
    try:
        k = key.char  # single-char keys
    except:
        k = key.name  # other keys

    if k in ['s']:
        print('Key pressed: ' + k)
        data = stream.read(chunk) # Record data
        all.append(data)

    if k in ['q']:
        print('Key pressed: ' + k)
        
        data = b''.join(all)
        filewavname = filename +'/'+username+'_'+str(index) + '.wav'
        wf = wave.open(filewavname, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(data)
        wf.close()
        fileopen.write(username+'/'+username+'_'+str(index) + '.wav\n')
        index = index+1
        if index == 4:
            return False


listener = keyboard.Listener(on_press=on_press)
listener.start()  # start to listen on a separate thread
listener.join()  # remove if main thread is polling self.keys
fileopen.close()

source   = "trainingData/"   
dest = "Speakers_models/"
#file_paths = open(train_file,'r')
file_paths = open(train_file,'r')


count = 1
# Extracting features for each speaker (5 files per speakers)
features = np.asarray(())
for path in file_paths:    
    path = path.strip()   
    print (path)
    
    # read the audio
    sr,audio = read(source + path)
    
    # extract 40 dimensional MFCC & delta MFCC features
    vector   = extract_features(audio,sr)
    
    if features.size == 0:
        features = vector
    else:
        features = np.vstack((features, vector))
    # when features of 5 files of speaker are concatenated, then do model training
	# -> if count == 5: --> edited below
    if count == 3:    
        gmm = mixture.GaussianMixture(n_components = 9, max_iter = 200, covariance_type='diag',n_init = 3)
        gmm.fit(features)
        
        # dumping the trained gaussian model
        picklefile = path.split("/")[0]+".gmm"
        #pickle.dump(gmm,open(dest + picklefile,'wb'))
        with open(dest + picklefile,'wb') as file:
            pickle.dump(gmm, file)
        print ('+ modeling completed for speaker:',picklefile," with data point = ",features.shape)
        features = np.asarray(())
        count = 0
    count = count + 1
