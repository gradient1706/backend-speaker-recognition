import nltk
#nltk.download('punkt')
import nltk.data
import pickle
import numpy as np

from scipy.io.wavfile import read
import pyaudio
import wave
import sys
from pynput import keyboard
import sounddevice as sd
import soundfile as sf
import time
import os
from featureextraction import extract_features
import warnings
warnings.filterwarnings("ignore")
import time

source   = "SampleData/"   

modelpath = "Speakers_models/"

gmm_files = [os.path.join(modelpath,fname) for fname in 
              os.listdir(modelpath) if fname.endswith('.gmm')]


			
models = [pickle.load(open(fname,'rb')) for fname in gmm_files]
speakers = [fname.split("/")[-1].split(".gmm")[0] for fname 
              in gmm_files]


filename = 'SampleData/'
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

print("Press s to start record, q to quit record, esc to exit program")

path = ""

all = []


def on_press(key):
    global path
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
        filewavname = filename + 'test.wav'
        path = filewavname
        wf = wave.open(filewavname, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(data)
        wf.close()
        stream.close()
        p.terminate()
        return False



listener = keyboard.Listener(on_press=on_press)
listener.start()  # start to listen on a separate thread
listener.join()  # remove if main thread is polling self.keys

print ("Testing Audio : ", path)
sr,audio = read( path)
vector   = extract_features(audio,sr)

log_likelihood = np.zeros(len(models)) 

for i in range(len(models)):
    gmm = models[i]  #checking with each model one by one
    scores = np.array(gmm.score(vector))
    log_likelihood[i] = scores.sum()

winner = np.argmax(log_likelihood)
print ("\tdetected as - ", speakers[winner])

time.sleep(1.0)