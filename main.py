import sys
import matplotlib
import numpy as np
from lcard.python import e502
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
    @Slot(dict)
    def do_work(self, param):
        while True:
            dev=param["dev"]
            t=param["t"]
            dev.streams_start()
            dev.recive(t)
            dev.streams_stop()
            data, _=dev.get_data()
            self.progress.emit(data)
        
class MainWindow(QtWidgets.QMainWindow):
    work_requested = Signal(dict)
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.fs=2e6
        self.f=24697 
        self.dev=e502.E502()
        self.dev.connect_byUsb()
        self.dev.configure_channels(channels=[1], modes=['comm'],ranges=[10])
        self.dev.set_adc_freq(self.fs)
        self.dev.set_sync_start_mode("syn1_rise")
        self.dev.configure_device()
        self.dev.enable_streams()
        self.Xk=[]
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        #self.sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar(self.sc, self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.sc)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.startButton = QtWidgets.QPushButton("Start", self)
        toolbar.addWidget(self.startButton)
        self.startButton.clicked.connect(self.startRecive)

        self.worker = Worker()
        self.worker_thread = QtCore.QThread()
        self.worker.progress.connect(self.updateProgress)

        self.work_requested.connect(self.worker.do_work)

        # move worker to the worker thread
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()
        self.show()

    def startRecive(self):
        self.work_requested.emit({"dev":self.dev, "t":0.1})


    def updateProgress(self, data):
        N=len(data)
        x=data.reshape((N,))
        k=self.f*N/self.fs
        w=np.array([np.exp(-2*np.pi*1j/N*k*n) for n in range(N)])
        Xk=x*w
        Xk=np.sum(Xk)
        self.Xk.append(Xk)
        self.sc.axes.cla()
        self.sc.axes.plot(np.real(self.Xk))
        self.sc.axes.plot(np.imag(self.Xk))
        self.sc.draw()

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()