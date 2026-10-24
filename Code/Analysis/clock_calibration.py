"""Calibrate the DAQ timebase from the 50 Hz mains-hum line (Pakistan grid, nominal 50.0 Hz).
Firmware timestamps assume 500 us per stored sample; the true spacing is s*500 us.

Step 1: the strongest narrow line in 50-75 Hz (nominal timebase) is found in every run.
Step 2: in three low-resistance spring-1 runs a different feature (52.5-55 Hz) is stronger, so the
        mains line itself is located as the strongest peak in 60-66 Hz, where step 1 finds it in the
        other 18 runs. It is present in all 21 (peak/median >= 8.7).
Step 3: s = f_line/50 is averaged over the runs where the line is clearest (peak/median > 50).
The quoted uncertainty is the +/-1 % tolerance of the grid frequency, which dominates the run scatter."""
import os, glob, json, numpy as np
from scipy.signal import butter, filtfilt
from common import D, RES
from fit_decay import load
SNR_MIN = 50
out=[]
for p in sorted(glob.glob(D+"**/*.csv", recursive=True)):
    t,v=load(p); fs=1/np.median(np.diff(t))
    b,a=butter(4,[45/(fs/2),80/(fs/2)],'band'); h=filtfilt(b,a,v)
    n=len(h); w=np.hanning(n); F=np.abs(np.fft.rfft(h*w,8*n)); f=np.fft.rfftfreq(8*n,1/fs)
    wide=(f>50)&(f<75); noise=np.median(F[wide])
    kb=np.argmax(F[wide]); f_broad=f[wide][kb]
    m=(f>60)&(f<66); k=np.argmax(F[m])
    out.append(dict(run=os.path.dirname(os.path.relpath(p,D)).replace(os.sep,'/'), f_hum=float(f[m][k]), snr=float(F[m][k]/noise),
                    f_strongest_50_75=float(f_broad)))
fh=np.array([o['f_hum'] for o in out]); snr=np.array([o['snr'] for o in out]); good=snr>SNR_MIN
s=fh[good]/50.0
res=dict(n_runs=len(out), n_line_present=int((snr>5).sum()), n=int(good.sum()), snr_min=SNR_MIN,
         f_hum_mean=float(fh[good].mean()), f_hum_sd=float(fh[good].std(ddof=1)),
         f_hum_mean_all=float(fh.mean()), f_hum_sd_all=float(fh.std(ddof=1)),
         s=float(s.mean()), s_sd=float(s.std(ddof=1)), s_grid_tol=float(0.01*s.mean()),
         n_strongest_not_mains=int(sum(abs(o['f_strongest_50_75']-o['f_hum'])>0.5 for o in out)), runs=out)
json.dump(res,open(os.path.join(RES,'clock_calibration.json'),'w'),indent=1)
print(f"line present in {res['n_line_present']}/{res['n_runs']} runs; strongest 50-75 Hz feature is something else in {res['n_strongest_not_mains']}")
print(f"n={res['n']} (peak/median>{SNR_MIN})  f_hum = {res['f_hum_mean']:.3f} +/- {res['f_hum_sd']:.3f} Hz  ->  s = {res['s']:.4f} +/- {res['s_sd']:.4f} (runs), +/- {res['s_grid_tol']:.4f} (grid)")
print(f"all {res['n_runs']} runs: f_hum = {res['f_hum_mean_all']:.3f} +/- {res['f_hum_sd_all']:.3f} Hz")
for o in out: print(f"  {o['run'][:40]:40s} {o['f_hum']:.3f} Hz  peak/median={o['snr']:.0f}  (strongest 50-75 Hz: {o['f_strongest_50_75']:.2f})")
