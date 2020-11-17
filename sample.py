from RtLighting import RtLighting

rl=RtLighting(ip_addr='192.168.11.99',mode='stft',inputdevice=8,left_light_no=4)
rl.start_stream(240)
