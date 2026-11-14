"""Estimators mirroring the repo pipeline (final_table.py / fit_decay.py), as functions, plus harmonic lock-in."""
import sys, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, 'Code', 'Analysis'))
from fit_decay import load, fit as peak_fit
from scipy.signal import butter, filtfilt, find_peaks, hilbert, sosfiltfilt
S_CLOCK = 1.2613409090916081

def prep_arrays(t, v):
    fs = 1/np.median(np.diff(t)); b, a = butter(4, 20/(fs/2)); vf = filtfilt(b, a, v)
    x = vf - np.median(vf[:int(0.3*fs)]); return x, fs

def crude_f(x, fs):
    X = np.abs(np.fft.rfft(x - x.mean())); fr = np.fft.rfftfreq(len(x), 1/fs)
    return fr[np.argmax(X[fr > 0.3]) + np.sum(fr <= 0.3)]

def peak_gamma(t, x, fs, f):
    """fit_decay.fit logic on nominal time."""
    pk, _ = find_peaks(np.abs(x), distance=int(0.35*fs/f))
    amp = np.abs(x[pk]); keep = amp > 0.25*amp.max()
    i0 = np.argmax(amp > 0.5*amp.max()); sel = np.arange(len(pk)) >= i0
    tt, aa = t[pk][keep & sel], amp[keep & sel]
    return -np.polyfit(tt, np.log(aa), 1)[0]

def headline(t_nom, v, S=S_CLOCK):
    """final_table.py headline estimator. Returns dict in TRUE time using clock factor S."""
    x, fs = prep_arrays(t_nom, v); t = t_nom*S; fsT = fs/S
    f_nom = crude_f(x, fs); f0 = f_nom/S
    sos = butter(4, [0.6*f0, 1.4*f0], btype='band', fs=fsT, output='sos'); xf = sosfiltfilt(sos, x)
    zc = np.where((xf[:-1] < 0) & (xf[1:] >= 0))[0]
    pk, _ = find_peaks(np.abs(x), distance=int(0.35*fs/(f0*S))); amp = np.abs(x[pk]); i0 = np.argmax(amp > 0.5*amp.max())
    ta, te = t[pk[i0]] + 1*S, t[-1] - 1*S
    zc = zc[(t[zc] > ta) & (t[zc] < te)]; f_true = (len(zc)-1)/(t[zc[-1]] - t[zc[0]])
    env = np.abs(hilbert(xf)); ds = int(round(fs/(f0*S))); m = (t > ta) & (t < te)
    th, eh = t[m][::ds], np.log(env[m][::ds]); g = -np.polyfit(th, eh, 1)[0]
    i0s = np.argmax(np.abs(x) > 0.5*np.abs(x).max()); eps = np.sqrt(np.mean(x[i0s:i0s+int(3/(f0*S)*fs)]**2))*1e-3
    g_peak = peak_gamma(t_nom, x, fs, f_nom)/S
    mid = (th[0]+th[-1])/2
    ge = -np.polyfit(th[th < mid], eh[th < mid], 1)[0]; gl = -np.polyfit(th[th >= mid], eh[th >= mid], 1)[0]
    return dict(gamma=g, f=f_true, eps_mV=eps, g_peak=g_peak, early_late=ge/gl, t_release=t[pk[i0]], x=x, t=t, fsT=fsT)

def harmonics(t, x, f, t0, ncyc=6, nh=4):
    """Hann-windowed lock-in amplitudes/phases of harmonics 1..nh over ncyc cycles starting at t0 (true time)."""
    m = (t >= t0) & (t < t0 + ncyc/f); tt = t[m] - t0; y = x[m] - x[m].mean(); w = np.hanning(len(tt)); w /= w.mean()
    out = []
    for k in range(1, nh+1):
        z = 2*np.mean(w*y*np.exp(-2j*np.pi*k*f*tt)); out.append(z)
    return np.array(out)
