import pyfirmata2
import time
import numpy as np
from qcodes.instrument import Instrument
from qcodes import validators as vals

pins = np.linspace(2,11,10,dtype=int)
pins_gain = np.array([2,4,6],dtype=int)
pins_LPF = np.array([3,5,7,9],dtype=int)


class Baspi(Instrument):
    def __init__(self, port: str, gain, LPF, **kwargs):
        super().__init__(port, **kwargs)
        start = time.time()
        self.board = pyfirmata2.Arduino(port)
        for i in pins:
            self.board.digital[i].mode = pyfirmata2.OUTPUT
        self.board.digital[10].write(1)
        self.board.digital[11].write(0)  
        end = time.time()
        connection_time = np.round(end-start,3)
        print("Connected to baspi IV amplifier in " + str(connection_time) + " seconds")   
    
        self.gain = self.add_parameter(
            name='gain',
            label='gain',
            unit= None,
            initial_value = gain,
            get_cmd=self.getGain,
            get_parser=float,
            set_cmd=self.setGain,
            vals=vals.Enum(1E9, 1E8, 1E7, 1E6, 1E5)
        )
        self.LPF = self.add_parameter(
            name='LPF',
            label='LPF',
            unit='Hz',
            initial_value = LPF,
            get_cmd=self.getLPF,
            get_parser=float,
            set_cmd=self.setLPF,
            vals=vals.Enum(1E6, 100E3, 30E3, 10E3, 3E3, 1E3, 300, 100, 30)
        )


    def get_idn(self):
        return {
            "vendor": "Basel Precision Instruments",
            "model": "SP893C",
            "serial": None,
            "firmware": "Designed by Dennis van der Bovenkamp",
        }       
    

    def setGain(self,gain):
        for i in pins_gain:
                self.board.digital[i].write(0)
        if gain == 1E9:
            self.board.digital[6].write(1)
            print("gain set to 1E" + str(len(str(gain))-3))
        elif gain == 1E8:
            self.board.digital[4].write(1)
            self.board.digital[2].write(1)
            print("gain set to 1E" + str(len(str(gain))-3))
        elif gain == 1E7:
            self.board.digital[4].write(1)
            print("gain set to 1E" + str(len(str(gain))-3))
        elif gain == 1E6:
            self.board.digital[2].write(1)
            print("gain set to 1E" + str(len(str(gain))-3))
        elif gain == 1E5:
            print("gain set to 1E" + str(len(str(gain))-3))
        else:
            print("unrecognized gain, choose: 1E9, 1E8, 1E7, 1E6 or 1E5")

    def setLPF(self,cutoff):
        unit = "Hz"
        cutoff = int(cutoff)
        for i in pins_LPF:
                self.board.digital[i].write(0)
        if cutoff == 1E6:
            self.board.digital[9].write(1)
            print("LPF set to " + str(int(cutoff/1000000)) + "M" + unit)
        elif cutoff == 100E3:
            self.board.digital[7].write(1)
            self.board.digital[5].write(1)
            self.board.digital[3].write(1)
            print("LPF set to " + str(int(cutoff/1000)) + "k" + unit)
        elif cutoff == 30E3:
            self.board.digital[7].write(1)
            self.board.digital[5].write(1)
            print("LPF set to " + str(int(cutoff/1000)) + "k" + unit)
        elif cutoff == 10E3:
            self.board.digital[7].write(1)
            self.board.digital[3].write(1)
            print("LPF set to " + str(int(cutoff/1000)) + "k" + unit)
        elif cutoff == 3E3:
            self.board.digital[7].write(1)
            print("LPF set to " + str(int(cutoff/1000)) + "k" + unit)
        elif cutoff == 1E3:
            self.board.digital[5].write(1)
            self.board.digital[3].write(1)
            print("LPF set to " + str(int(cutoff/1000)) + "k" + unit)
        elif cutoff == 300:
            self.board.digital[5].write(1)
            print("LPF set to " + str(cutoff) + unit)
        elif cutoff == 100:
            self.board.digital[3].write(1)
            print("LPF set to " + str(cutoff) + unit)
        elif cutoff == 30:
            print("LPF set to " + str(cutoff) + unit)
        else:
            print("unrecognized cutoff, choose: 1M, 100K, 30K, 10K, 3K, 1K, 300, 100, 30")

    def getGain(self):
        settings = []
        for i in pins_gain:
            settings.append(self.board.digital[i].read())
        if settings == [0,0,1]:
            gain = 1E9
        elif settings == [1,1,0]:
            gain = 1E8
        elif settings == [0,1,0]:
            gain = 1E7
        elif settings == [1,0,0]:
            gain = 1E6
        elif settings == [0,0,0]:
            gain = 1E5
        else:
            gain = 0
        return gain

    def getLPF(self):
        settings = []
        for i in pins_LPF:
            settings.append(self.board.digital[i].read())
        if settings == [0,0,0,1]:
            cutoff = 1E6
        elif settings == [1,1,1,0]:
            cutoff = 100E3
        elif settings == [0,1,1,0]:
            cutoff = 30E3
        elif settings == [1,0,1,0]:
            cutoff = 10E3
        elif settings == [0,0,1,0]:
            cutoff = 3E3
        elif settings == [1,1,0,0]:
            cutoff = 1E3
        elif settings == [0,1,0,0]:
            cutoff = 300
        elif settings == [1,0,0,0]:
            cutoff = 100
        elif settings == [0,0,0,0]:
            cutoff = 30
        else: 
            cutoff = 0
        return cutoff

    def allOff(self):
        for i in pins:
            self.board.digital[i].write(0)
