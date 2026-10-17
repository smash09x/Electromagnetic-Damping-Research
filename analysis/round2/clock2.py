from common import *
from scipy.signal import butter as bt, sosfiltfilt
import json
cl=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','clock.json')))
for sp,R,s,p in runs():
    t,v,x,fs=prep(p); f0=authors_fit(p)['f']
    xf=sosfiltfilt(bt(4,[0.6*f0,1.4*f0],btype='band',fs=fs,output='sos'),x)
    zc=np.where((xf[:-1]<0)&(xf[1:]>=0))[0]; zc=zc[(t[zc]>3)&(t[zc]<29)]; tz=t[zc]; mid=len(tz)//2
    fa=(mid-1)/(tz[mid-1]-tz[0]); fb=(len(tz)-mid-1)/(tz[-1]-tz[mid])
    print(f"{sp:4s}{R:>9g} {s[:9]:9s} f_osc halves {fa:.4f} {fb:.4f} ratio {fb/fa:.4f}")
