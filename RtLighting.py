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

    def color(self):
        pass

    def brightness(self):
        pass

    def audio_callback(self):
        if status:
            print(status, file=sys.stderr)

        i=0
        if i%10==0:
            harmonics,percussive=librosa.effects.hpss(indata[:,0])

    def start_stream(self):
        pass