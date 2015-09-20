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
        ui=parent.ui
        self.setters=[ui.s0set,ui.s1set,ui.s2set]
        self.glabels=[ui.s0gain,ui.s1gain,ui.s2gain]
        self.doitbutt=ui.doitbutt
        ui.doitbutt.clicked.connect(self.doSet)
        self.prevcommand=0
    
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
        #print(self.gainvalues)
        for t in range(len(self.gainnames)):
            nvals=len(self.gainvalues[t])
            for i in range(nvals): self.setters[t].insertItem(i,"% 2.1f dB" % (self.gainvalues[t][nvals-1-i]/10.0))
            self.setters[t].setCurrentIndex(nvals-1-self.gain_index(t))
        self.ticktimer=QBasicTimer()
    
    def selected_gain_index(self,stage):
        nvals=len(self.gainvalues[stage])
        return nvals-1-self.setters[stage].currentIndex()
    
    def selected_gain(self,stage):
        return self.gainvalues[stage][self.selected_gain_index(stage)]
    
    def gain_index(self,stage):
        offset=OFS_CURRENTGAINS+stage*4
        return struct.unpack('i', self.mmif[offset:offset+4])[0]

    def gain(self,stage):
        gi=self.gain_index(stage)
        return self.gainvalues[stage][gi]/10.0
        
    def doSet(self):
        gains2set=[]
        for t in range(len(self.gainnames)): gains2set.append(self.selected_gain_index(t))
        #print "set happens: ",gains2set
        for t in range(len(gains2set)):
            offset=OFS_SETGAINS+t*4
            self.mmif[offset:offset+4]=struct.pack('i',gains2set[t])
        self.mmif[OFS_COMMAND:OFS_COMMAND+4]=struct.pack('i',1)      # signal librtlsdr to set teh gains
        self.doitbutt.setEnabled(0)
        
    def start(self):
        self._init()
        self.ticktimer.start(100,self)
        
    def timerEvent(self, event):
        for t in range(3): self.glabels[t].setText("% 2.1f dB" % (self.gain(t)))
        command=struct.unpack('i', self.mmif[OFS_COMMAND:OFS_COMMAND+4])[0]
        if command!=self.prevcommand and command==0:
            self.doitbutt.setEnabled(1)
