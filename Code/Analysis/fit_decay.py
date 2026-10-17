"""Refit exponential decay of coil EMF envelope from raw DAQ dumps.
Envelope: V0 e^{-gamma t}. Peaks of |V-baseline| per half-cycle, then log-linear fit.
Outputs gamma (s^-1), f (Hz), Q = omega/(2 gamma)."""
import sys, glob, os, numpy as np
from scipy.signal import find_peaks, butter, filtfilt

def load(path):
    caps, cur = [], []
    for line in open(path, errors="ignore"):
        if "," in line:
            try:
                t, v = line.strip().split(","); cur.append((float(t)*1e-6, float(v)))
            except ValueError: pass
        elif "STARTING" in line and cur:
            caps.append(cur); cur = []
    if cur: caps.append(cur)
    a = np.array(max(caps, key=len)); return a[:,0], a[:,1]

def fit(path):
    t, v = load(path)
    fs = 1/np.median(np.diff(t))
    b, a = butter(4, 20/(fs/2)); vf = filtfilt(b, a, v)
    # baseline: median of first 0.3 s (magnet at rest before release)
    base = np.median(vf[: int(0.3*fs)]); x = vf - base
    # crude frequency via FFT
    X = np.abs(np.fft.rfft(x - x.mean())); fr = np.fft.rfftfreq(len(x), 1/fs)
    f = fr[np.argmax(X[fr > 0.3]) + np.sum(fr <= 0.3)]
    pk, _ = find_peaks(np.abs(x), distance=int(0.35*fs/f))
    amp = np.abs(x[pk]); keep = amp > 0.25*amp.max()
    # start after release: first peak above 50% max
    i0 = np.argmax(amp > 0.5*amp.max()); sel = np.arange(len(pk)) >= i0
    tt, aa = t[pk][keep & sel], amp[keep & sel]
    p, cov = np.polyfit(tt, np.log(aa), 1, cov=True)
    g, ge = -p[0], np.sqrt(cov[0,0])
    resid = np.log(aa) - np.polyval(p, tt); r2 = 1 - resid.var()/np.log(aa).var()
    return dict(fs=fs, f=f, gamma=g, gerr=ge, Q=2*np.pi*f/(2*g), Vpk=aa.max(), n=len(aa), dur=tt[-1]-tt[0], r2=r2)

if __name__ == "__main__":
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Data", "Raw")
    for p in sorted(glob.glob(os.path.join(root, "**/*.csv"), recursive=True)):
        try:
            r = fit(p)
            print(f"{os.path.relpath(p, root):70s} fs={r['fs']:.0f} f={r['f']:.3f}Hz gamma={r['gamma']*1e3:.2f}±{r['gerr']*1e3:.2f} ms^-1 Q={r['Q']:.0f} Vpk={r['Vpk']:.0f}uV n={r['n']} T={r['dur']:.1f}s R2={r['r2']:.3f}")
        except Exception as e:
            print(p, "ERR", e)
