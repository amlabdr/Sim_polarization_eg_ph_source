import numpy as np
import yaml
class Coincidences():
    def __init__(self, yamlfn, Alice, Bob):
        
        self.yamlfn = yamlfn
        yfn   = open(self.yamlfn,'r')
        self.dicty = yaml.load(yfn, Loader=yaml.SafeLoader)
        yfn.close()
        
        self.trange     = float(self.dicty["trange"]) # in ns
        self.binwidth   = float(self.dicty["binwidth"]) # in ns
        self.offset     = float(self.dicty["offset"]) # in ps
        self.resolution = float(self.dicty["resolution"]) # in ps
        self.range      = float(self.dicty["range"]) # in ps
        self.syncrate    = float(self.dicty["sync_rate"])
        
        self.Alice = Alice - self.offset
        self.Bob   = Bob
        
        
    def getHistogram(self, range_ns, width_ns):
        
        radius: 4 # coincidence window radius in ns
        accidental_offset: 20 # offset from peak to find accidentals in ns
        peak: 6
        Afloor   = np.int64(np.floor(self.Alice/(range_ns*1000/2)))
        Bfloor   = np.int64(np.floor(self.Bob/(range_ns*1000/2)))
        # this only returns values and indices of the first elements
        coinc0    = np.intersect1d(Afloor,Bfloor, return_indices = True)
        coinc1    = np.intersect1d(Afloor,Bfloor-1, return_indices = True)
        coinc2    = np.intersect1d(Afloor,Bfloor+1, return_indices = True)
        self.coinc     = np.hstack((coinc0, coinc1, coinc2))
        # now find multiple ones: find diff == 0 and where it intersects with A and B: this will give the doubles
        # this should be done when detetcor deadtime is small
        # print(len(np.intersect1d((np.where(np.diff(Afloor)==0)[0]),coinc[0],return_indices = True)[0]))
        # print(len(np.intersect1d((np.where(np.diff(Bfloor)==0)[0]),coinc[0],return_indices = True)[0]))

        Atime    = self.Alice[self.coinc[1]]
        Btime    = self.Bob[self.coinc[2]]
        dtime    = Atime-Btime
        
        bins     = np.arange(-range_ns/2,range_ns/2+width_ns/2,width_ns)*1000
        
        [histo, edges]  = np.histogram(dtime, bins)
        mx = bins[np.where(histo == max(histo))[0][0]]
        
        return [histo, edges, mx]
        
    def findPeak(self): # this should be run once at the beginning and will find a rough peak value        
        self.H_rough, self.edge_rough, self.mxp = self.getHistogram(self.trange, self.binwidth)
        self.offset = self.mxp
                
        
    def CoincidenceAndRates(self):
        
        
        yfn   = open(self.yamlfn,'r')
        self.dicty = yaml.load(yfn, Loader=yaml.SafeLoader)
        yfn.close()
        
        
        self.Alice = self.Alice-self.offset
        self.H, self.edge, self.mx = self.getHistogram(self.range, self.resolution/1000)
        
        # find values for singles and coincidences
        
        self.mxtim = self.edge[np.int32(np.mean(np.where(max(self.H)==self.H)[0]))]/1000
        
        #self.mxtim = self.dicty["coin_window"]["peak"]
    
        self.coin_edge_lo = float(self.mxtim - self.dicty["coin_window"]["radius"])# in ns
        if self.coin_edge_lo < -self.range/2:
            self.coin_edge_lo = self.coin_edge_lo + self.range
        if self.coin_edge_lo > self.range/2:
            self.coin_edge_lo = self.coin_edge_lo - self.range
        
                    
        self.coin_edge_hi = float(self.mxtim + self.dicty["coin_window"]["radius"]) # in ns
        if self.coin_edge_hi > self.range/2:
            self.coin_edge_hi = self.coin_edge_hi - self.range
        if self.coin_edge_hi < -self.range/2:
            self.coin_edge_hi = self.coin_edge_hi + self.range
        
        self.acc_edge_lo  = float(self.coin_edge_lo + self.dicty["coin_window"]["accidental_offset"])
        if self.acc_edge_lo < -self.range/2:
            self.acc_edge_lo = self.acc_edge_lo + self.range
        if self.acc_edge_lo > self.range/2:
            self.acc_edge_lo = self.acc_edge_lo - self.range
        
        self.acc_edge_hi  = float(self.coin_edge_hi + self.dicty["coin_window"]["accidental_offset"])
        if self.acc_edge_hi > self.range/2:
            self.acc_edge_hi = self.acc_edge_hi - self.range
        if self.acc_edge_hi < -self.range/2:
            self.acc_edge_hi = self.acc_edge_hi + self.range

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
        self.totalSinglesAlice = len(self.Alice)
        self.totalSinglesBob   = len(self.Bob)

        # per second        
        self.tA = (self.Alice[-1:]-self.Alice[0])/1e12
        self.tB = (self.Bob[-1:]-self.Bob[0])/1e12
        
        '''print('Alice collection time: %.8f'%self.tA)
        print('Bob collection time: %.8f'%self.tB)'''
        
        
        self.coincidencesPerSecond = self.totalCoincidences/np.mean([self.tA, self.tB])
        self.accidentalsPerSecond  = self.totalAccidentals/np.mean([self.tA, self.tB])
        self.singlesAlicePerSecond = self.totalSinglesAlice/self.tA[0]
        self.singlesBobPerSecond   = self.totalSinglesBob/self.tB[0]
        