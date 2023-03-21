from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
import math

class SignalCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=6, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax_real = fig.add_subplot(121)
        self.ax_imaq = fig.add_subplot(122)
        super(SignalCanvas, self).__init__(fig)


class FFTCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=6, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.fft = fig.add_subplot(111)
        super(FFTCanvas, self).__init__(fig)
    
    def fft_intensity_plot(self, samples: np.ndarray, fft_len: int = 256, fft_div: int = 2, mag_steps: int = 100, cmap: str = 'plasma'):
    
        num_ffts = math.floor(len(samples)/fft_len)
        
        fft_array = []
        for i in range(num_ffts):
            temp = np.fft.fftshift(np.fft.fft(samples[i*fft_len:(i+1)*fft_len]))
            temp_mag = 20.0 * np.log10(np.abs(temp))
            fft_array.append(temp_mag)
            
        max_mag = np.amax(fft_array)
        min_mag = np.abs(np.amin(fft_array))
        
        norm_fft_array = fft_array
        for i in range(num_ffts):
            norm_fft_array[i] = (fft_array[i]+(min_mag))/(max_mag+(min_mag)) 
            
        mag_step = 1/mag_steps

        hitmap_array = np.random.random((mag_steps+1,int(fft_len/fft_div)))*np.exp(-10)

        for i in range(num_ffts):
            for m in range(fft_len):
                hit_mag = int(norm_fft_array[i][m]/mag_step)
                hitmap_array[hit_mag][int(m/fft_div)] = hitmap_array[hit_mag][int(m/fft_div)] + 1

        hitmap_array_db = 20.0 * np.log10(hitmap_array+1)
        
        self.fft.imshow(hitmap_array_db, origin='lower', cmap=cmap, interpolation='bilinear')
        