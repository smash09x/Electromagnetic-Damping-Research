from common import *
from scipy.signal import butter as bt, sosfiltfilt
for sp,R,s,p in runs():
    t,v=load(p); fs=1/np.median(np.diff(t)); n=len(v)
    def peak(seg,lo,hi):
        m=len(seg); F=np.abs(np.fft.rfft((seg-seg.mean())*np.hanning(m),16*m)); f=np.fft.rfftfreq(16*m,1/fs); k=(f>lo)&(f<hi)
        i=np.argmax(F[k]); return f[k][i], F[k][i]/np.median(F[k])
    f1,s1=peak(v,55,70); f2,s2=peak(v,120,132); f3,s3=peak(v,180,198)
    fa,_=peak(v[:n//2],55,70); fb,_=peak(v[n//2:],55,70)
    # raw pre-release noise and offset
    pre=v[:600]
    print(f"{sp:4s}{R:>9g} {s[:9]:9s} f1 {f1:.2f}(snr {s1:.0f}) f2 {f2:.2f}({s2:.0f}) f3 {f3:.2f}({s3:.0f}) | halves {fa:.2f} {fb:.2f} | raw pre rms {pre.std():.0f}uV mean {pre.mean():.0f}")
