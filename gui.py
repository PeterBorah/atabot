import sys
import random
from PyQt4 import QtGui, QtCore

import tools
from search import Search

class Worker(QtCore.QThread):

    def __init__(self, search, function, *args):
    
        super(Worker, self).__init__()
        
        self.exiting = False
        self.search = search
        self.function = function
        self.args = args
    
    def __del__(self):
    
        self.exiting = True
        self.wait()
        
    def run(self):
        while not self.exiting and self.search.total_needy > 0:
            args = self.args
            self.function(*args)
            
        if self.search.total_needy == 0:
            self.search.cleanup()
            self.emit(QtCore.SIGNAL('success'))
        else:
            self.emit(QtCore.SIGNAL('failure'))
        
class Cell(QtGui.QLabel):
    
    def __init__(self, i, j, pattern):
        super(Cell, self).__init__()
        
        self.i = i
        self.j = j
        self.pattern = pattern
        self.initUI()
        
    def initUI(self):
        
        if self.pattern[self.j][self.i]:
            self.setPixmap(QtGui.QPixmap('1.png'))
        else:
            self.setPixmap(QtGui.QPixmap('0.png'))
        
        self.setStyleSheet("border: 1px solid black;")
        
    def mousePressEvent(self, click):
        if mainw.central.run.isEnabled():
            if self.pattern[self.j][self.i]:
                self.setPixmap(QtGui.QPixmap('0.png'))
                self.pattern[self.j][self.i] = False
            else:
                self.setPixmap(QtGui.QPixmap('1.png'))
                self.pattern[self.j][self.i] = True

class Board(QtGui.QWidget):
    
    def __init__(self, pattern):
        super(Board, self).__init__()
        
        self.pattern = pattern
        self.initUI()
        
    def initUI(self):
    
        if not self.pattern:
            self.pattern = tools.create_blank(7, 7)
        
        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(1)

        for i in range(self.pattern["x_size"]):
            for j in range(self.pattern["y_size"]):
                cell = Cell(i, j, self.pattern)
                self.grid.addWidget(cell, j, i)
            
        self.setLayout(self.grid)   

        
class centralArea(QtGui.QWidget):

    def __init__(self, pattern={}):
        super(centralArea, self).__init__()
        
        self.initUI(pattern)
        self.border = 1
        self.algorithm = "Jittery Hillclimbing Algorithm"
        
    def initUI(self, pattern):
    
        self.board = Board(pattern)
    
        self.clear = QtGui.QPushButton("Clear", self)
        self.run = QtGui.QPushButton("Atavise me!", self)
        self.cancel = QtGui.QPushButton("Cancel", self)
        self.cancel.setEnabled(False)
        
        self.algo_chooser = QtGui.QComboBox(self)
        self.algo_chooser.addItem("Jittery Hillclimbing Algorithm")
        self.algo_chooser.addItem("Pogo Algorithm")
    
        hbox1 = QtGui.QHBoxLayout()
        hbox1.addWidget(self.board)
        hbox1.addStretch(1)
        
        hbox2 = QtGui.QHBoxLayout()
        hbox2.addStretch(1)
        hbox2.addWidget(self.clear)
        hbox2.addWidget(self.algo_chooser)
        hbox2.addStretch(1)

        hbox3 = QtGui.QHBoxLayout()
        hbox3.addStretch(1)
        hbox3.addWidget(self.run)
        hbox3.addWidget(self.cancel)
        hbox3.addStretch(1)
        
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addStretch(1)
        
        self.clear.clicked.connect(self.cleared)
        self.run.clicked.connect(self.run_algo)
        self.cancel.clicked.connect(self.canceled)
        self.algo_chooser.activated[str].connect(self.chosen)
        
        self.setLayout(vbox)
        
    def run_algo(self):
        self.cancel.setEnabled(True)
        self.run.setEnabled(False)
        self.clear.setEnabled(False)
        self.search = Search(self.board.pattern)
        mainw.statusBar().showMessage('Working!')
        if self.algorithm == "Pogo Algorithm":
            self.thread = Worker(self.search, self.search.use_pogo)
        else:
            self.thread = Worker(self.search, self.search.use_jittery)
        self.thread.start()
        self.connect(self.thread, QtCore.SIGNAL("success"), self.success)
        self.connect(self.thread, QtCore.SIGNAL("failure"), self.failure)
        
    def chosen(self, algorithm):
        self.algorithm = algorithm
        
    def cleared(self):
        new = tools.create_blank(self.board.pattern["x_size"], self.board.pattern["y_size"])
        mainw.central = centralArea(new)
        mainw.setCentralWidget(mainw.central)
        mainw.update()
        
    def canceled(self):
        self.thread.exiting = True
        self.cancel.setEnabled(False)
        self.run.setEnabled(True)
        self.clear.setEnabled(True)
        mainw.statusBar().showMessage('')
    
    def success(self):
        mainw.statusBar().showMessage('Success!')
        mainw.central = centralArea(self.search.candidate)
        mainw.setCentralWidget(mainw.central)
        self.cancel.setEnabled(False)
        self.run.setEnabled(True)
        mainw.update()
        
    def failure(self):
        mainw.statusBar().showMessage('Failure :(')
        
       
class MainW(QtGui.QMainWindow):

    def __init__(self):
        super(MainW, self).__init__()
        
        self.initUI()
        
    def initUI(self):
        
        self.central = centralArea()
        self.setCentralWidget(self.central)
        self.statusBar()
        
        openFile = QtGui.QAction('Open .rle file', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open GoL pattern stored as an .rle file')
        openFile.triggered.connect(self.open_rle)
        
        saveFile = QtGui.QAction('Save pattern', self)
        saveFile.setShortcut('Ctrl+S')
        saveFile.setStatusTip('Save current pattern as an .rle file')
        saveFile.triggered.connect(self.save_rle)
        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)       
        fileMenu.addAction(saveFile)
        
        self.setWindowTitle('Atabot')
        self.show()
        
    def open_rle(self):

        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 
                '*.rle', "GoL Patterns (*.rle)")
        
        if fname:
        
            pattern = tools.open_rle(fname, self.central.border)
            self.central = centralArea(pattern)
            self.setCentralWidget(self.central)
            self.update()
        
    def save_rle(self):
        fname = QtGui.QFileDialog.getSaveFileName(self, 'Save file', 
                '*.rle', "GoL Patterns (*.rle)")
        
        if fname:
            f = open(fname, 'w')
            
            with f:        
                f.write(tools.export(self.central.board.pattern))


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mainw = MainW()
    sys.exit(app.exec_())