import numpy as np
import matplotlib.pyplot as plt


class Coincidences():
    def __init__(self, timesA, timesB, calibration_range, calibration_binwidth):
        self.timesA = timesA
        self.timesB = timesB
        self.calibration_range = calibration_range
        self.calibration_binwidth = calibration_binwidth
        self.offset = 0

        self.timesA = timesA - self.offset
        self.timesB   = timesB

    def calibration(self, range_ns, width_ns):
        Afloor   = np.int64(np.floor(self.timesA/(range_ns*1000/2)))
        Bfloor   = np.int64(np.floor(self.timesB/(range_ns*1000/2)))
        coinc0    = np.intersect1d(Afloor,Bfloor, return_indices = True)
        coinc1    = np.intersect1d(Afloor,Bfloor-1, return_indices = True)
        coinc2    = np.intersect1d(Afloor,Bfloor+1, return_indices = True)
        self.coinc     = np.hstack((coinc0, coinc1, coinc2))
        #self.coinc = coinc0
        Atime    = self.timesA[self.coinc[1]]
        Btime    = self.timesB[self.coinc[2]]
        dtime    = Atime-Btime
        bins     = np.arange(-range_ns/2,range_ns/2+width_ns/2,width_ns)*1000
        [histo, edges]  = np.histogram(dtime, bins)
        mx = bins[np.where(histo == max(histo))[0][0]]
        return [histo, edges, mx]

    def get_offset(self,range_ns,width_ns):      
        self.H_rough, self.edge_rough, self.mxp = self.calibration(range_ns, width_ns)
        self.offset = self.mxp

    def CoincidenceAndRates(self,range_ns):
        radius= 4 # coincidence window radius in ns
        accidental_offset= 20 # offset from peak to find accidentals in ns
        resolution= 10
        peak= 6
        self.timesA = self.timesA-self.offset
        self.H, self.edge, self.mx = self.calibration(range_ns, resolution/1000)
        
        # find values for singles and coincidences
        
        self.mxtim = self.edge[np.int32(np.mean(np.where(max(self.H)==self.H)[0]))]/1000
        
        #self.mxtim = self.dicty["coin_window"]["peak"]
    
        self.coin_edge_lo = float(self.mxtim - radius)# in ns
        if self.coin_edge_lo < -range_ns/2:
            self.coin_edge_lo = self.coin_edge_lo + range_ns
        if self.coin_edge_lo > range_ns/2:
            self.coin_edge_lo = self.coin_edge_lo - range_ns
        
                    
        self.coin_edge_hi = float(self.mxtim + radius) # in ns
        if self.coin_edge_hi > range_ns/2:
            self.coin_edge_hi = self.coin_edge_hi - range_ns
        if self.coin_edge_hi < -range_ns/2:
            self.coin_edge_hi = self.coin_edge_hi + range_ns
        
        self.acc_edge_lo  = float(self.coin_edge_lo + accidental_offset)
        if self.acc_edge_lo < -range_ns/2:
            self.acc_edge_lo = self.acc_edge_lo + range_ns
        if self.acc_edge_lo > range_ns/2:
            self.acc_edge_lo = self.acc_edge_lo - range_ns
        
        self.acc_edge_hi  = float(self.coin_edge_hi + accidental_offset)
        if self.acc_edge_hi > range_ns/2:
            self.acc_edge_hi = self.acc_edge_hi - range_ns
        if self.acc_edge_hi < -range_ns/2:
            self.acc_edge_hi = self.acc_edge_hi + range_ns

        self.coin_idx1 = np.where(self.edge > self.coin_edge_lo*1000)[0][0]
        self.coin_idx2 = np.where(self.edge > self.coin_edge_hi*1000)[0][0]
        self.acc_idx1 = np.where(self.edge > self.acc_edge_lo*1000)[0][0]
        self.acc_idx2 = np.where(self.edge > self.acc_edge_hi*1000)[0][0]


        if self.coin_edge_lo < self.coin_edge_hi:            
            self.totalCoincidences = sum(self.H[self.coin_idx1:self.coin_idx2])
        else:
            self.totalCoincidences = sum(self.H[0:self.coin_idx2]) + sum(self.H[self.coin_idx1:])
            
        if self.acc_edge_lo < self.acc_edge_hi:            
            self.totalAccidentals  = sum(self.H[self.acc_idx1:self.acc_idx2])            
        else:
            self.totalCoincidences = sum(self.H[0:self.coin_idx2]) + sum(self.H[self.coin_idx1:])
            self.totalAccidentals  = sum(self.H[0:self.acc_idx2]) + sum(self.H[self.acc_idx1:])
        
        self.totalAccidentals  = sum(self.H[self.acc_idx1:self.acc_idx2])
        self.totalSinglestimesA = len(self.timesA)
        self.totalSinglestimesB   = len(self.timesB)

        # per second        
        self.tA = (self.timesA[-1:]-self.timesA[0])/1e12
        self.tB = (self.timesB[-1:]-self.timesB[0])/1e12
        
        '''print('timesA collection time: %.8f'%self.tA)
        print('timesB collection time: %.8f'%self.tB)'''
        
        
        self.coincidencesPerSecond = self.totalCoincidences/np.mean([self.tA, self.tB])
        self.accidentalsPerSecond  = self.totalAccidentals/np.mean([self.tA, self.tB])
        self.singlestimesAPerSecond = self.totalSinglestimesA/self.tA[0]
        self.singlestimesBPerSecond   = self.totalSinglestimesB/self.tB[0]
        


"""calibration_range, calibration_binwidth = 1e3,1
coinc_range_ns = 100
timesA = np.loadtxt("timesA.txt")
timesB = np.loadtxt("timesB.txt")
Coin = Coincidences(timesA,timesB,calibration_range, calibration_binwidth)

histo, edges, mx = Coin.calibration(Coin.calibration_range,Coin.calibration_binwidth)
Coin.get_offset(calibration_range,calibration_binwidth)

Coin.CoincidenceAndRates(coinc_range_ns)
print(Coin.totalCoincidences)
histo_plt = plt
histo_plt.plot(edges[1:] , histo)
histo_plt.show()"""
