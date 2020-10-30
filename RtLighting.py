import sys
import numpy as np
import sounddevice as sd
import librosa
import time
from phue import Bridge
from multiprocessing import Process

class RtLighting():
    
    def __init__(self,ip_addr,mode,inputdevice,left_light_no=None,right_light_no=None):
        self.__b=Bridge(ip_addr)
        self.__mode=mode
        sd.default.device=inputdevice,None
        self.__left_light_no=left_light_no
        self.__right_light_no=right_light_no


    def __color(self,y,light_no):


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

        if self.__mode=='stft':
            N_FFT_SIZE=4096
            HOP_LENGTH=1048

            S=librosa.stft(y=y,n_fft=N_FFT_SIZE,hop_length=HOP_LENGTH)
            chroma_stft=librosa.feature.chroma_stft(S=S)

            chroma=librosa.util.normalize(chroma_stft,norm=1,axis=0)

            QUANT_STEPS=[0.4,0.2,0.1,0.05]
            QUANT_WEIGHTS = [0.25, 0.25, 0.25, 0.25]

            chroma_quant = np.zeros_like(chroma)

            for cur_quant_step_idx, cur_quant_step in enumerate(QUANT_STEPS):
                chroma_quant += (chroma > cur_quant_step) * QUANT_WEIGHTS[cur_quant_step_idx]

            chroma_stft=librosa.util.normalize(chroma_quant,axis=0)

            xy=convert_rgb_to_xy(chroma_rgb[np.append(chroma_stft.real.mean(axis=1),[0.00000000001]).argmax()])
        elif self.__mode=='cqt':
            HOP_LENGTH=4096
            FMIN=130.816
            N_BINS=84
            BPO=12

            C=librosa.cqt(y=y,sr=44100,hop_length=HOP_LENGTH,fmin=FMIN,n_bins=N_BINS,bins_per_octave=BPO)
            chroma_cens=librosa.feature.chroma_cens(C=C,hop_length=HOP_LENGTH)
            xy=convert_rgb_to_xy(chroma_rgb[np.append(chroma_cens.real.mean(axis=1),[0.00000000001]).argmax()])

        cmd={
            'xy':xy,
            'transitiontime':0,
        }
        self.__b.set_light(light_no,cmd)


    def __brightness(self,indata,light_no):
        print(np.average(np.absolute(indata)))
        ave=int((np.average(np.absolute(indata))/0.0025)*255)
        bri=255 if 255<ave else ave
        cmd={
            'bri':bri,
            'transitiontime':0
        }
        print(cmd)
        self.__b.set_light(light_no,cmd)


    def __left_execute(self,indata):
        margin=(7,6)
        harmonics,percussive=librosa.effects.hpss(y=indata,margin=margin)

        '''
        self.__color(y=harmonics,light_no=self.__left_light_no)
        self.__brightness(indata=indata,light_no=self.__left_light_no)

        '''
        processes=[
            Process(target=self.__color,args=(harmonics,self.__left_light_no)),
            Process(target=self.__brightness,args=(percussive,self.__left_light_no))
        ]

        for p in processes:
            p.start()
        


    def __right_execute(self,indata):
        margin=(7,3)
        harmonics,percussive=librosa.effects.hpss(y=indata,margin=margin)

        '''
        self.__color(y=harmonics,light_no=self.__right_light_no)
        self.__brightness(indata=percussive,light_no=self.__right_light_no)
        '''
        processes={
            Process(target=self.__color,args=(harmonics,self.__right_light_no)),
            Process(target=self.__brightness,args=(percussive,self.__right_light_no))
        }
        for p in processes:
            p.start()

    def __audio_callback(self,indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        processes=[
            Process(target=self.__left_execute,args=(indata[:8192,0],)),
            #Process(target=self.__right_execute,args=(indata[:8192,1],))
        ]
        for p in processes:
            p.start()





    def start_stream(self,sleeptime=10):
        stream=sd.InputStream(
            samplerate=44100,
            blocksize=8820,
            callback=self.__audio_callback
        )
        stream.start()
        time.sleep(sleeptime)