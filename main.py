import sys
import matplotlib
import numpy as np
from lcard.python import e502
import time
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import  pyqtSignal as Signal, pyqtSlot as Slot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=6, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class Worker(QtCore.QObject):
    progress = Signal(np.ndarray)
    work=True
    @Slot(dict)
    def do_work(self, param):
        dev=param["dev"]
        t=param["t"]
        sender = param["running"]
        while (sender.running):
            dev.streams_start()
            dev.recive(t)
            dev.streams_stop()
            data, _=dev.get_data()
            self.progress.emit(data)
            time.sleep(1)

    @Slot()
    def stop(self,param):
        self.work=False
        print("stop")
        
class MainWindow(QtWidgets.QMainWindow):
    work_requested = Signal(dict)
    stop_requested = Signal(int)
    running=True

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.fs=2e6
        self.f=24695
        self.t=0.1 
        self.dev=e502.E502()
        self.dev.connect_byUsb()
        self.dev.configure_channels(channels=[1], modes=['comm'],ranges=[10])
        self.dev.set_adc_freq(self.fs)
        self.dev.set_sync_start_mode("syn1_rise")
        self.dev.configure_device()
        self.dev.enable_streams()
        self.Xk=[]

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
        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        toolbar = NavigationToolbar(self.sc, self)

        
        #quickbar = NavigationToolbar(self.sc, self)
        #self.startButton = QtWidgets.QPushButton("Start", self)
        #quickbar.addWidget(self.startButton)
        #self.startButton.clicked.connect(self.startRecive)

        #self.stopButton = QtWidgets.QPushButton("Stop", self)
        #quickbar.addWidget(self.stopButton)
        #self.startButton.clicked.connect(self.stopRecive)
        #self.stopButton.setEnabled(False)
        layout.addWidget(toolbar)

        
 
        layout.addWidget(self.sc)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
  
  
        
        self.worker = Worker()
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

    def stopRecive(self):
        self.stopButton.setEnabled(False)
        self.startButton.setEnabled(True)
        self.running=False
        #self.stop_requested.emit(0)
        #self.worker_thread.quit()
        #self.worker_thread.wait()


    def updateProgress(self, data):
        N=len(data)
        x=data.reshape((N,))
        k=self.f*N/self.fs
        w=np.array([np.exp(-2*np.pi*1j/N*k*n) for n in range(N)])
        Xk=2*np.dot(x,w)/N
        self.Xk.append(Xk)
        self.sc.axes.cla()
        self.sc.axes.plot(np.real(self.Xk))
        self.sc.axes.plot(np.imag(self.Xk))
        #self.sc.axes.plot(np.abs(self.Xk))
        #self.sc.axes.plot(np.angle(self.Xk))
        self.sc.draw()
        n=len(self.Xk)
        np.save(str(n)+".npy", data)

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()