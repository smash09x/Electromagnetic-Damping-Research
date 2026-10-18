import os,sys,glob,json,numpy as np
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
ROOT=os.path.abspath(os.path.join(HERE,'..','..'))
D=os.path.join(ROOT,'Data','Raw')+'/'          # raw DAQ dumps
RES=os.path.join(ROOT,'Data','Results')         # outputs
OUT=os.path.join(HERE,'out')                    # intermediate files
os.makedirs(RES,exist_ok=True); os.makedirs(OUT,exist_ok=True)
from fit_decay import load, fit as authors_fit
from scipy.signal import butter,filtfilt,find_peaks,hilbert
S1={0.0:["0.0/Retake 1","0.0/Retake 2"],33.6:["33.6"],81.4:["81.4"],324:["324"],1051:["1051"],3180:["3.18k"],9610:["9.61k"],2.2e6:["2.2M"]}
S2={0.0:["0.0","0.0/Retake"],33.3:["33.3"],84.1:["84.1"],327:["327"],997:["997"],3190:["3.19k"],9670:["9.67k"]}
# Apparatus constants used by several scripts
RC=15.2        # coil-1 DC resistance (Ohm)
M_OSC=0.105    # oscillating mass (kg)
A_INIT=0.022   # initial amplitude of the motion from video (m); video A0 range 1.8-2.3 cm, c ~ 1/A^2
def clock():
    """Clock factor s (true sample spacing / firmware's assumed 500 us), from clock_calibration.py.
    Returns (s, sd over the high-SNR runs, uncertainty from the +/-1 % grid-frequency tolerance)."""
    j=json.load(open(os.path.join(RES,'clock_calibration.json')))
    return j['s'], j['s_sd'], j['s_grid_tol']
def runs():
    out=[]
    for R,ss in S1.items():
        for s in ss: out.append(('S1',R,s,glob.glob(D+'spring_1/coil_1/Resistance/'+s+'/*.csv')[0]))
    for R,ss in S2.items():
        for s in ss: out.append(('S2',R,s,glob.glob(D+'spring_2/coil_1/Resistance/'+s+'/*.csv')[0]))
    for sp in ('spring_1','spring_2'):
        for c in ('coil_2','coil_3'): out.append(('S'+sp[-1]+c[-1:]+'c',0.0,c,glob.glob(D+sp+'/'+c+'/*.csv')[0]))
    return out
def prep(p):
    t,v=load(p); fs=1/np.median(np.diff(t)); b,a=butter(4,20/(fs/2)); vf=filtfilt(b,a,v)
    x=vf-np.median(vf[:int(0.3*fs)]); return t,v,x,fs
