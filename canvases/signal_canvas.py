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
        self.freq = fig.add_subplot(111)
        super(FFTCanvas, self).__init__(fig)
    
    def spectr(self, x, fs):
        self.freq.cla()
        self.freq.magnitude_spectrum(x,Fs=fs)
        self.draw()
        