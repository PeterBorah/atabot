import sys
import random
from PyQt4 import QtGui

class Cell(QtGui.QLabel):
    
    def __init__(self):
        super(Cell, self).__init__()
        
        self.initUI()
        
    def initUI(self):
        self.setMargin(0)
        self.setPixmap(QtGui.QPixmap('0.png'))
        self.on = False
        
    def mousePressEvent(self, click):
        if self.on:
            self.setPixmap(QtGui.QPixmap('0.png'))
            self.on = False
        else:
            self.setPixmap(QtGui.QPixmap('1.png'))
            self.on = True

class Board(QtGui.QWidget):
    
    def __init__(self, x, y):
        super(Board, self).__init__()
        
        self.initUI(x, y)
        
    def initUI(self, x, y):
        self.x = x
        self.y = y
        
        
        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(1)

        for i in range(x):
            for j in range(y):
                cell = Cell()
                self.grid.addWidget(cell, i, j)
            
        self.setLayout(self.grid)   
        
        self.setWindowTitle('Test!')    
        self.show()
        
        
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Board(int(sys.argv[1]), int(sys.argv[2]))
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()