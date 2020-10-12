import sys
import numpy as np
import sounddevice as sd
import librosa
import time
from phue import Bridge

class RtLighting():
    
    def __init__(self,ip_addr,inputdevice):
        self.__b=Bridge(ip_addr)
        sd.default.device=inputdevice

    def __color(self):
        pass

    def __brightness(self):
        pass

    def __audio_callback(self,indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)

        harmonics_left,percussive_left=librosa.effects.hpss(indata[:,0])
        harmonics_right,percussive_right=librosa.effects.hpss(indata[:,1])




    def start_stream(self):
        pass