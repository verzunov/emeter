import sys
import matplotlib
import numpy as np
import scipy.stats as st
from lcard.python import e502
#from emul import e502
import time
matplotlib.use('Qt5Agg')
import pylab as plb
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import  pyqtSignal as Signal, pyqtSlot as Slot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import pandas as pd
from canvases.signal_canvas import SignalCanvas, FFTCanvas
import pylab
#import gofft

class Worker(QtCore.QObject):
    progress = Signal(list)
    work=True
    buf=[]
    @Slot(dict)
    def do_work(self, param):
        dev=param["dev"]
        t=param["t"]
        sender = param["running"]
        while (sender.running):
            dev.send_data(data1=self.dac1, data2=self.dac2)
            dev.streams_start()

            dev.recive(t)
            dev.streams_stop()
            data, _=dev.get_data()
            #sender.running=False
            #plb.plot(data)
            #plb.show()
            self.buf.append([data])
            if len(self.buf)==3:
                self.progress.emit(self.buf)
                self.buf.clear()
                time.sleep(1.0)

    @Slot()
    def stop(self,param):
        self.work=False

        
class MainWindow(QtWidgets.QMainWindow):
    work_requested = Signal(dict)
    stop_requested = Signal(int)
    running=True

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
      
        self.f=24800
        self.fs=1000000
        self.dacfs=1000000
        self.t=0.05 
        self.dev=e502.E502()
        self.dev.connect_byUsb()
        self.dev.configure_channels(channels=[1], modes=['comm'],ranges=[2])
        self.dev.set_adc_freq(self.fs)
        self.dev.set_out_freq(self.dacfs)
        #self.dev.set_sync_start_mode("syn1_rise")
        self.dev.configure_device()
        self.dev.enable_streams(stream_adc=True,stream_dac1=True,stream_dac2=True)
        dt=1/self.dev._out_freq
        t=np.arange(0,self.t,dt,np.float)
        omega=2*np.pi*self.f
        a=5.0
        data1=a*np.cos(omega*t)
        data2=a*np.cos(omega*t+np.pi)
        #self.dev.send_data(data1=data1,data2=data2)
        self.data=pd.DataFrame(columns=["Real","Imag" "Real std", "Imag std"])
        #self.sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])
        layout = QtWidgets.QVBoxLayout()
        self.toolBar=QtWidgets.QToolBar()
        layout.addWidget(self.toolBar)
        self.startButton=QtWidgets.QToolButton()
        self.startButton.setText("Start")
        self.toolBar.addWidget(self.startButton)
        self.startButton.clicked.connect(self.startRecive)
        self.stopButton=QtWidgets.QToolButton()
        self.stopButton.setText("Stop")
        self.toolBar.addWidget(self.stopButton)
        self.stopButton.clicked.connect(self.stopRecive)
        self.clearButton=QtWidgets.QToolButton()
        self.clearButton.setText("Clear")
        self.toolBar.addWidget(self.clearButton)
        self.clearButton.clicked.connect(self.clearRecive)

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        self.sc = SignalCanvas(self, width=5, height=4, dpi=100)
        toolbar = NavigationToolbar(self.sc, self)
        layout.addWidget(toolbar)
        layout.addWidget(self.sc)
        self.fc=FFTCanvas(self,width=10, height=5, dpi=100)
        toolbar = NavigationToolbar(self.fc, self)
        layout.addWidget(toolbar)
        layout.addWidget(self.fc)
        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
  
  
        
        self.worker = Worker()
        self.worker.dac1=data1
        self.worker.dac2=data2
        self.worker_thread = QtCore.QThread()
        self.worker.progress.connect(self.updateProgress)

        self.work_requested.connect(self.worker.do_work)
        self.stop_requested.connect(self.worker.stop)
        # move worker to the worker thread
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()
        self.show()

    def startRecive(self):
        self.running=True
        self.work_requested.emit({"dev":self.dev, "t":self.t, "running":self})
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        #self.clearButton.setEnabled(False)

    def stopRecive(self):
        self.stopButton.setEnabled(False)
        self.startButton.setEnabled(True)
        #self.clearButton.setEnabled(True)
        self.running=False
        #self.stop_requested.emit(0)
        #self.worker_thread.quit()
        #self.worker_thread.wait()

    def ft(self, data):
        N=len(data)
        print(N)
        x=data.reshape((N,))
        k=self.f*N/self.fs
        n=np.arange(N)
        w=np.exp(-2*np.pi*1j/N*k*n)
        Xk=2*np.dot(x,w)/N
        #print(np.abs(Xk))
        #print(np.angle(Xk))
        return Xk

    def plot(self, plt, data,std):
        plt.cla()
        ci = 1.96 * np.array(std)/np.sqrt(len(data))
        df = pd.DataFrame({"data":data, "error":ci})
        ma=df["data"].rolling(window=3).mean()        
        plt.errorbar(np.arange(len(data)),data,yerr=ci,marker='o',linestyle = 'None',markersize =1)
        plt.plot(ma)
        plt.grid()
        #plt.draw()  
        
    def updateProgress(self, data):
        ft=[self.ft(sample[0]) for sample in data]
        Xk_avg=np.average(ft)
        Xk_std_r=np.real(np.std(np.real(ft)))
        Xk_std_i=np.real(np.std(np.imag(ft)))
        Xk_std_m=np.real(np.std(np.abs(ft)))
        Xk_std_p=np.real(np.std(np.angle(ft)))
        self.data=self.data.append({"Real":np.real(Xk_avg),"Imag":np.imag(Xk_avg),"Mag":np.abs(Xk_avg), "Angle":np.angle(Xk_avg),
                                     "Real std":Xk_std_r, "Imag std":Xk_std_i, "Mag std":Xk_std_m, "Angle std":Xk_std_p},ignore_index = True)
        self.plot(self.sc.ax_real, np.real(self.data["Real"]), np.real(self.data["Real std"]))
        self.plot(self.sc.ax_imag, np.real(self.data["Imag"]), np.real(self.data["Imag std"]))
        self.plot(self.sc.ax_mag, np.real(self.data["Mag"]), np.real(self.data["Mag std"]))
        self.plot(self.sc.ax_angle, np.real(self.data["Angle"]), np.real(self.data["Angle std"]))

        self.sc.ax_real.set_title("Real")
        self.sc.ax_imag.set_title("Imaginary")
        self.sc.ax_mag.set_title("Magnitude")
        self.sc.ax_angle.set_title("Phase")
        self.sc.draw()
        samples=[sample[0] for sample in data]
        samples=np.concatenate(samples)
        N=samples.shape[0]
        samples=np.reshape(samples,(N,))
        #fft=np.log10(np.fft.fft(samples, norm='ortho')/N*2)

        #freqs=np.fft.fftfreq(N,1/self.fs)
        #print(freqs)

        self.fc.spectr(samples, self.fs)

    def clearRecive(self):
        self.data.drop(self.data.index, inplace=True)


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()