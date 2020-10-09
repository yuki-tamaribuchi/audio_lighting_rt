import sys
import numpy as np
import sounddevice as sd
import librosa
import time
from phue import Bridge


sd.default.device=8,2

b=Bridge('192.168.11.99')

chroma_rgb=np.array([
            #Kari Ziets' research 1931
            #Color Name to RGB Reference -> https://web.njit.edu/~walsh/rgb.html

            #C,ド,Red
            [255,0,0],

            #C#,ド#(レb),Purple
            [160,32,240],

            #D,レ,Violet
            [238,130,238],

            #D#,レ#(ミb),LightBlue
            [173,216,230],

            #E,ミ,Gold
            [255,215,0],

            #F,ファ,Pink
            [255,192,203],

            #F#,ファ#(ソb),turquoise4
            [0,134,139],

            #G,ソ,SkyBlue
            [135,206,235],

            #G#,ソ#(ラb),Unknown -> mean of G and A
            [195,230,79],

            #A,ラ,冷たい黄 -> Yellow
            [255,255,0],

            #A#,ラ#(シb),Orange
            [255,165,0],

            #B,シ,Copper
            [184,115,51],

            #None,WHite
            [255,255,255]
        ])

def convert_rgb_to_xy(data):
        r_gamma = pow( ((data[0]/256) + 0.055) / (1.0 + 0.055), 2.4 ) if (data[0]/256) > 0.04045 else ((data[0]/256) / 12.92)
        g_gamma = pow( ((data[1]/256) + 0.055) / (1.0 + 0.055), 2.4 ) if (data[1]/256) > 0.04045 else ((data[1]/256) / 12.92)
        b_gamma = pow( ((data[2]/256) + 0.055) / (1.0 + 0.055), 2.4 ) if (data[2]/256) > 0.04045 else ((data[2]/256) / 12.92)

        x = r_gamma * 0.649926 + g_gamma * 0.103455 + b_gamma * 0.197109
        y = r_gamma * 0.234327 + g_gamma * 0.743075 + b_gamma * 0.022598
        z = g_gamma * 0.053077 + b_gamma * 1.035763

        x=x/(x+y+z)
        y=y/(x+y+z)

        return x,y


def audio_callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    i=0
    if i%10==0:
        chroma_stft=librosa.feature.chroma_stft(y=indata[:,0],sr=44100)
        left_xy=convert_rgb_to_xy(chroma_rgb[np.append(chroma_stft.real.mean(axis=1),[0.00000000001]).argmax()])
        cmd={
            'xy':left_xy,
            'transitiontime':0,
        }
        b.set_light(3,cmd)
        i+=1


stream = sd.InputStream(
    samplerate=44100, callback=audio_callback,blocksize=4410
)

stream.start()


time.sleep(1000)