from PyQt4.QtCore import *
import mmap
import ctypes
import struct

MAX_GAINS=8
GAINNAME_SIZE=32
MAX_GAINVALUES=256
OFS_RESULT=0
OFS_COMMAND=4
OFS_CURRENTGAINS=8
OFS_SETGAINS=OFS_CURRENTGAINS+MAX_GAINS*4
OFS_GAINNAMES=OFS_SETGAINS+MAX_GAINS*4
OFS_GAINVALUES=OFS_GAINNAMES+MAX_GAINS*GAINNAME_SIZE
OFS_GAINMODE=OFS_GAINVALUES+MAX_GAINS*MAX_GAINVALUES*4

class MMIF( QObject ):
    def __init__ ( self, parent = None, mmif_fn='/dev/shm/rtlsdr0' ):
        QObject.__init__( self, parent )
        self.fn=mmif_fn
    
    def _init(self):
        with open(self.fn,'r+b') as f:
            #self.mmif_fh=f
            self.mmif=mmif=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_WRITE)
        self.gainnames=[]
        self.gainvalues=[];
        for t in range(MAX_GAINS):
            offset=OFS_GAINNAMES+t*GAINNAME_SIZE
            gainname=str(ctypes.create_string_buffer(mmif[offset:offset+GAINNAME_SIZE]).value)
            if len(gainname)==0: break
            self.gainnames.append(gainname)
            
        for stage in range(len(self.gainnames)):
            values=[]
            self.gainvalues.append(values)
            for t in range(MAX_GAINVALUES):
                offset=OFS_GAINVALUES+stage*MAX_GAINVALUES*4+t*4
                gain=struct.unpack('i', self.mmif[offset:offset+4])[0]
                if (gain<=-2000): break
                values.append(gain)
        print(self.gainnames)
        print(self.gainvalues)
        self.ticktimer=QBasicTimer()
    
    def gain_index(self,stage):
        offset=OFS_CURRENTGAINS+stage*4
        return struct.unpack('i', self.mmif[offset:offset+4])[0]
        mainwin.ui.s0gain.setText("%d fdB" % (self.gain_index(0)))

    def gain(self,stage):
        gi=self.gain_index(stage)
        return self.gainvalues[stage][gi]/10.0
        
    def start(self):
        self._init()
        self.ticktimer.start(100,self)
        
    def timerEvent(self, event):
        mainwin=self.parent()
        mainwin.ui.s0gain.setText("% 2.1f dB" % (self.gain(0)))
        mainwin.ui.s1gain.setText("% 2.1f dB" % (self.gain(1)))
        mainwin.ui.s2gain.setText("% 2.1f dB" % (self.gain(2)))
        #print("yay")
