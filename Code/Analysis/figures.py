"""Final figures (true time axis, s = 1.261 clock correction; fundamental-band Hilbert gamma)."""
import os, sys, glob, csv, json, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, hilbert, sosfiltfilt
from common import D, RES
from fit_decay import load
tab, st = os.path.join(RES, 'final_table.csv'), os.path.join(RES, 'final_stats.json')
out = os.path.join(RES, 'figures'); os.makedirs(out, exist_ok=True)
S = 1.2613; RC = 15.2
plt.rcParams.update({"font.family":"serif","font.size":9,"axes.spines.top":False,"axes.spines.right":False,
  "axes.edgecolor":"#555","axes.labelcolor":"#222","xtick.color":"#555","ytick.color":"#555","axes.grid":True,
  "grid.color":"#e6e6e6","grid.linewidth":0.6,"legend.frameon":False,"savefig.bbox":"tight"})
C1, C2, GR = "#2a78d6", "#eb6834", "#666"
rows = list(csv.DictReader(open(tab))); J = json.load(open(st))
def sel(prefix): return [r for r in rows if r['run'].startswith(prefix)]
s1, s2 = sel('spring1/coil1'), sel('spring2/coil1')

# Fig: gamma vs R
fig, ax = plt.subplots(figsize=(3.5, 2.6))
for rr, col, mk, lab in ((s1, C1, "o", "Spring 1"), (s2, C2, "s", "Spring 2")):
    R = np.array([float(r['R_ext']) for r in rr]) + RC
    g = np.array([float(r['gamma_true']) for r in rr]); e = np.array([float(r['gamma_err']) for r in rr])
    ax.errorbar(R, g, yerr=e, fmt=mk, ms=4.5, color=col, mec="white", mew=0.6, elinewidth=1, capsize=0, label=lab)
cp = J['S1_cfit']['c_pred']; g1 = J['S1']['gamma'][0]
Rg = np.logspace(np.log10(RC), 6.6, 300)
ax.plot(Rg, g1 - 0.0 + 1e3*cp/Rg - 1e3*cp/1e4, "--", color=GR, lw=1.2, label="Spring 1, loop closed via $R_c+R_{\\rm ext}$")
ax.plot(Rg, np.full_like(Rg, g1), ":", color="#222", lw=1.2, label="As built (loop via 1 M$\\Omega$)")
ax.set_xscale("log"); ax.set_ylim(9.5, 16.5)
ax.set_xlabel(r"$R_c+R_{\rm ext}$ ($\Omega$, log scale)"); ax.set_ylabel(r"Decay rate $\gamma$ ($10^{-3}$ s$^{-1}$)")
ax.legend(fontsize=6.8, loc="upper right")
fig.savefig(f"{out}/gamma_vs_R.pdf"); fig.savefig(f"{out}/gamma_vs_R.png", dpi=200)

# Fig: gamma vs initial EMF amplitude
fig, ax = plt.subplots(figsize=(3.5, 2.5))
from scipy.stats import pearsonr
for rr, col, mk, lab in ((s1, C1, "o", "Spring 1"), (s2, C2, "s", "Spring 2")):
    rr = [r for r in rr if float(r['R_ext']) < 1e5]
    v = np.array([float(r['eps_rms_init_mV']) for r in rr]); g = np.array([float(r['gamma_true']) for r in rr])
    rcoef = pearsonr(v, g)[0]; p = np.polyfit(v, g, 1); xs = np.linspace(v.min(), v.max(), 10)
    ax.plot(v, g, mk, ms=4.5, color=col, mec="white", mew=0.6, label=f"{lab} ($r$ = {rcoef:.2f})")
    ax.plot(xs, np.polyval(p, xs), color=col, lw=1, alpha=0.7)
ax.set_xlabel("Initial EMF (rms, first 3 cycles) (mV)"); ax.set_ylabel(r"$\gamma$ ($10^{-3}$ s$^{-1}$)"); ax.legend(fontsize=7)
fig.savefig(f"{out}/gamma_vs_amp.pdf"); fig.savefig(f"{out}/gamma_vs_amp.png", dpi=200)

# Fig: example trace with fundamental-band envelope, true time
p = glob.glob(D + "spring_1/coil_1/Resistance/0.0/Retake 2/*.csv")[0]
t, v = load(p); t = t*S; fs = 1/np.median(np.diff(t)); f0 = 2.0834
b, a = butter(4, 20/(fs/2)); vf = filtfilt(b, a, v)*1e-3; vf -= np.median(vf[:int(0.3*fs)])
sos = butter(4, [0.6*f0, 1.4*f0], 'band', fs=fs, output='sos'); xf = sosfiltfilt(sos, vf); env = np.abs(hilbert(xf))
fig, ax = plt.subplots(2, 1, figsize=(3.5, 3.6), gridspec_kw=dict(height_ratios=[2, 1.3], hspace=0.55))
ax[0].plot(t, vf, color=C1, lw=0.3, label="EMF (20 Hz low-pass)")
m = (t > t[np.argmax(np.abs(vf) > 0.5*np.abs(vf).max())] + 1.3) & (t < t[-1] - 1.5)
ax[0].plot(t[m], env[m], color="#222", lw=1.1, label="fundamental-band envelope")
ax[0].set_xlabel("Time (s, clock-corrected)"); ax[0].set_ylabel("EMF (mV)")
ax[0].legend(fontsize=6.5, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
i0 = np.argmax(t > t[np.argmax(np.abs(vf) > 0.5*np.abs(vf).max())] + 5); z = slice(i0, i0 + int(1.5/f0*fs))
ax[1].plot(t[z]-t[z][0], vf[z], color=C1, lw=1.1, label="EMF")
ax[1].plot(t[z]-t[z][0], xf[z], color=GR, lw=1, ls="--", label="fundamental only")
ax[1].set_xlabel("Time within window (s)"); ax[1].set_ylabel("EMF (mV)"); ax[1].legend(fontsize=6.5, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
fig.savefig(f"{out}/trace.pdf"); fig.savefig(f"{out}/trace.png", dpi=200)

# Fig: hum spectrum (clock calibration)
p = glob.glob(D + "spring_1/coil_1/Resistance/2.2M/*.csv")[0]
t, v = load(p); fs = 1/np.median(np.diff(t))
from scipy.signal import welch
b, a = butter(4, 15/(fs/2), 'high'); h = filtfilt(b, a, v)
f, P = welch(h, fs=fs, nperseg=16384)
fig, ax = plt.subplots(figsize=(3.5, 2.2))
ax.semilogy(f, P, color=C1, lw=0.8); ax.set_xlim(20, 160); mm=(f>20)&(f<160); ax.set_ylim(P[mm].min()*0.5, P[mm].max()*20)
for x, l in ((63.07, "63.1 Hz"), (126.1, "126.1 Hz")): ax.annotate(l, (x, P[np.argmin(abs(f-x))]), xytext=(6, -2), textcoords="offset points", fontsize=7)
ax.axvline(50, color=GR, ls=":", lw=1); ax.text(48.5, P[mm].max()*2, "50 Hz (true mains)", fontsize=6.5, color=GR, ha="right")
ax.set_xlabel("Frequency on the firmware's nominal timebase (Hz)"); ax.set_ylabel(r"PSD ($\mu$V$^2$/Hz)")
fig.savefig(f"{out}/hum.pdf"); fig.savefig(f"{out}/hum.png", dpi=200)
print("ok")
