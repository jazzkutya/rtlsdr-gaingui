from PyQt4 import uic
from PyQt4.QtCore import *

from mmifstuff import MMIF

( Ui_MainWindow, QMainWindow ) = uic.loadUiType( 'mainwindow.ui' )

class MainWindow ( QMainWindow ):
    """MainWindow inherits QMainWindow"""

    def __init__ ( self, parent = None ):
        QMainWindow.__init__( self, parent )
        self.ui = Ui_MainWindow()
        self.ui.setupUi( self )
        self.mmif=MMIF(self)
        self.mmif.start()

    def __del__ ( self ):
        self.ui = None

