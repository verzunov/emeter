import time
import numpy as np
import math
class E502:
    f=24716
    amp=1
    def __init__(self):
        pass
    def connect_byUsb(self):
        pass
    def configure_channels(self,channels, modes,ranges):
        pass
    def set_adc_freq(self,fs):
        self.fs=fs
    def set_sync_start_mode(self,sync_mode):
        pass
    def configure_device(self):
        pass
    def enable_streams(self):
        pass
    def streams_start(self):
        pass
    def recive(self,t):
        time.sleep(t)
        N=int(self.fs*t)+np.random.randint(-2,2)
        f=self.f+np.random.uniform(-5,5)
        k=f*N/self.fs
        self.w=np.array([np.cos(2*np.pi/N*k*n) for n in range(N)])
        return N
    def streams_stop(self):
        pass
    def get_data(self):
        return self.w, None




