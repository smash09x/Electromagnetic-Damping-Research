import os,sys,glob,numpy as np
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
from fit_decay import load, fit as authors_fit
from scipy.signal import butter,filtfilt,find_peaks,hilbert
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','data')+'/'
S1={0.0:["0.0/Retake 1","0.0/Retake 2"],33.6:["33.6"],81.4:["81.4"],324:["324"],1051:["1051"],3180:["3.18k"],9610:["9.61k"],2.2e6:["2.2M"]}
S2={0.0:["0.0","0.0/Retake"],33.3:["33.3"],84.1:["84.1"],327:["327"],997:["997"],3190:["3.19k"],9670:["9.67k"]}
def runs():
    out=[]
    for R,ss in S1.items():
        for s in ss: out.append(('S1',R,s,glob.glob(D+'spring_1/coil_1/Resistance/'+s+'/*.csv')[0]))
    for R,ss in S2.items():
        for s in ss: out.append(('S2',R,s,glob.glob(D+'spring_2/coil_1/'+s+'/*.csv')[0]))
    for sp in ('spring_1','spring_2'):
        for c in ('coil_2','coil_3'): out.append(('S'+sp[-1]+c[-1:]+'c',0.0,c,glob.glob(D+sp+'/'+c+'/*.csv')[0]))
    return out
def prep(p):
    t,v=load(p); fs=1/np.median(np.diff(t)); b,a=butter(4,20/(fs/2)); vf=filtfilt(b,a,v)
    x=vf-np.median(vf[:int(0.3*fs)]); return t,v,x,fs
