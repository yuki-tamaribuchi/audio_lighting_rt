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