from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
import math

class SignalCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=6, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax_real = fig.add_subplot(221)
        self.ax_real.set_title("Real")
        self.ax_imag = fig.add_subplot(222)
        self.ax_imag.set_title("Imaginary")
        self.ax_mag = fig.add_subplot(223)
        self.ax_mag.set_title("Magnitude")
        self.ax_angle= fig.add_subplot(224)
        self.ax_angle.set_title("Phase")
        super(SignalCanvas, self).__init__(fig)
        self.figure.tight_layout(pad=1.0)


class FFTCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=6, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.freq = fig.add_subplot(111)
        super(FFTCanvas, self).__init__(fig)
    
    def spectr(self, x, fs):
        self.freq.cla()
        self.freq.magnitude_spectrum(x,Fs=fs)
        self.draw()
        