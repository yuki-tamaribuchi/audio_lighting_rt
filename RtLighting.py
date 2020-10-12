import sys
import numpy as np
import sounddevice as sd
import librosa
import time
from phue import Bridge
from multiprocessing import Process

class RtLighting():
    
    def __init__(self,ip_addr,inputdevice):
        self.__b=Bridge(ip_addr)
        sd.default.device=inputdevice,None

    def __color(self):
        pass

    def __brightness(self):
        pass

    def __left_execute(self,indata):
        harmonics,percussive=librosa.effects.hpss(indata)

    def __right_execute(self,indata):
        harmonics,percussive=librosa.effects.hpss(indata)

    def __audio_callback(self,indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        processes=[
            Process(target=self.__left_execute,args=)
        ]





    def start_stream(self):
        pass