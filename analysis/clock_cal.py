"""Calibrate the DAQ timebase from the 50 Hz mains-hum line (Pakistan grid, nominal 50.0 Hz).
Firmware timestamps assume 500 us per stored sample; the true period is s*500 us."""
import sys, glob, json, numpy as np
from scipy.signal import butter, filtfilt
sys.path.insert(0, sys.argv[1]); from fit_decay import load
out=[]
for p in sorted(glob.glob(sys.argv[2]+"/data/**/*.csv", recursive=True)):
    t,v=load(p); fs=1/np.median(np.diff(t))
    b,a=butter(4,[45/(fs/2),80/(fs/2)],'band'); h=filtfilt(b,a,v)
    n=len(h); w=np.hanning(n); F=np.abs(np.fft.rfft(h*w,8*n)); f=np.fft.rfftfreq(8*n,1/fs)
    m=(f>50)&(f<75); k=np.argmax(F[m]); fh=f[m][k]
    snr=F[m][k]/np.median(F[m])
    out.append(dict(run=p.split('data/')[1].rsplit('/',1)[0], f_hum=fh, snr=snr))
fh=np.array([o['f_hum'] for o in out]); good=np.array([o['snr'] for o in out])>50
s=fh[good]/50.0
res=dict(n=int(good.sum()), f_hum_mean=fh[good].mean(), f_hum_sd=fh[good].std(ddof=1), s=s.mean(), s_sd=s.std(ddof=1), runs=out)
json.dump(res,open(sys.argv[3],'w'),indent=1)
print(f"n={res['n']}  f_hum = {res['f_hum_mean']:.3f} +/- {res['f_hum_sd']:.3f} Hz  ->  s = {res['s']:.4f} +/- {res['s_sd']:.4f}")
for o in out: print(f"  {o['run'][:40]:40s} {o['f_hum']:.3f} Hz  snr={o['snr']:.0f}")
