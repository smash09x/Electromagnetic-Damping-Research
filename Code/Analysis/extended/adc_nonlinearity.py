"""The 52-55 Hz 'feature' is the 20th-21st harmonic of the oscillation. It is one line of a comb produced by a
level-dependent error of the RP2040 ADC (erratum RP2040-E11: wide codes at 512, 1536, 2560, 3584).
1. Harmonic comb of the motion in every run.  2. Level-dependent error estimated from the recordings, split into
independent halves.  3. The same steps injected into the simulated DAQ reproduce the comb and leave the decay rate alone."""
import numpy as np, json
from est import *
import common
from scipy.signal import butter, sosfiltfilt
from sim import *
STEP = 23.647; S = S_CLOCK
def band_peak(v, fs, lo, hi):
    n = len(v); x = (v-v.mean())*np.hanning(n); F = np.abs(np.fft.rfft(x, 4*n))*2/np.sum(np.hanning(n)); fr = np.fft.rfftfreq(4*n, 1/fs); m = (fr > lo) & (fr < hi); i = np.argmax(F[m]); return fr[m][i], F[m][i]
rows = []
for sp, R, s, p in common.runs():
    t, v = load(p); fs = 1/np.median(np.diff(t)); h = headline(t, v); f1, a1 = band_peak(v, fs, 50, 58); f2, a2 = band_peak(v, fs, 60, 66)
    rows.append(dict(sp=sp, R=R, run=s, feature_true_hz=f1/S, feature_uV=a1, harmonic_order=f1/S/h['f'], mains_true_hz=f2/S, mains_uV=a2, eps_mV=h['eps_mV']))
    print(f"{sp:5s}{R:>9g} {s[:10]:10s} feature {f1/S:6.2f} Hz = {f1/S/h['f']:5.2f} x f, {a1:5.1f} uV | mains {f2/S:6.2f} Hz {a2:7.1f} uV | emf {h['eps_mV']:5.1f} mV")
def inl_est(paths, bw=6):
    K = []; Rr = []
    for p in paths:
        t, v = load(p); fs = 1/np.median(np.diff(t)); lp = sosfiltfilt(butter(6, 18/(fs/2), output='sos'), v)
        r = sosfiltfilt(butter(4, [58/(fs/2), 68/(fs/2)], btype='bandstop', output='sos'), v-lp); i0 = int(2*fs); K.append(np.round(lp[i0:-i0]/STEP).astype(int)); Rr.append(r[i0:-i0])
    k = np.concatenate(K); r = np.concatenate(Rr); b = np.floor(k/bw).astype(int); lo = b.min(); n = np.bincount(b-lo); s = np.bincount(b-lo, weights=r)
    return (np.arange(lo, lo+len(n))*bw+bw/2), s/np.maximum(n, 1), n
r1 = [p for sp, R, s, p in common.runs() if sp == 'S1' and R < 1e5]; r2 = [p for sp, R, s, p in common.runs() if sp == 'S2']
xa, ia, na = inl_est(r1[:4]); xb, ib, nb = inl_est(r1[4:]); xc, ic, nc = inl_est(r2)
g = np.arange(max(xa.min(), xb.min()), min(xa.max(), xb.max())+1, 6)
A = np.interp(g, xa, ia); B = np.interp(g, xb, ib); C = np.interp(g, xc, ic); m = (np.interp(g, xa, na) > 200) & (np.interp(g, xb, nb) > 200); m2 = m & (np.interp(g, xc, nc) > 200); mean = (A+B)/2
d = np.diff(mean[m]); gg = g[m]
from scipy.signal import find_peaks
s5 = np.convolve(d, np.ones(5), mode='same')                      # total jump across five adjacent 6-code bins
pk, _ = find_peaks(np.abs(s5), height=30, distance=25); levels = [float(gg[i]) for i in pk]; sizes = [float(s5[i]) for i in pk]
inl = dict(corr_independent_halves=float(np.corrcoef(A[m], B[m])[0, 1]), corr_spring1_vs_spring2=float(np.corrcoef(mean[m2], C[m2])[0, 1]), p2p_uV=float(np.ptp(mean[m])),
           step_levels_lattice=levels, step_levels_mV=[l*STEP/1000 for l in levels], step_sizes_uV=sizes, step_sizes_lsb=[x/STEP for x in sizes], step_spacing_codes=np.diff(levels).tolist())
print(json.dumps(inl, indent=1)); np.save('inl_est.npy', np.c_[g, mean, C, m, m2])
P = json.load(open('params.json')); kap = kappa_table(P['Z0']); A0, F = 0.0211, 2.0820; g0 = P['g0']; bet = P['b_per_m']*A0; TR = 12.613e-6
def emf(t):
    z, zd = motion(t, A0/P['LAM'], F, g0, bet, t_rel=1.0); return P['SCALE']*kap(z)*zd
def comb(t, v, ks=(10, 14, 18, 20, 21, 22, 26, 30)):
    h = headline(t, v, S=1.0); tt = h['t']; f = h['f']; mm = (tt > h['t_release']+1) & (tt < h['t_release']+12); y = v[mm]-v[mm].mean(); w = np.hanning(mm.sum()); w /= w.mean()
    return h, {int(k): float(abs(2*np.mean(w*y*np.exp(-2j*np.pi*k*f*tt[mm])))) for k in ks}
sim_out = {}
for name, st in (('no_step_error', None), ('rp2040_e11_steps', [(1536+55, 7.0), (2048+55, 1.6), (2560+55, 7.2)])):
    Gm = []; Cm = []
    for seed in range(4):
        t, v = daq(emf, np.random.default_rng(40+seed), T_reads=TR, true_time=True, inl_steps=st); h, c = comb(t, v); Gm.append(h['gamma']*1e3); Cm.append(list(c.values()))
    sim_out[name] = dict(gamma=float(np.mean(Gm)), comb_uV=dict(zip(c.keys(), np.mean(Cm, axis=0).tolist())))
# measured comb in one spring-1 run for comparison
t, v = load(r1[3]); h = headline(t, v); tt = h['t']; mm = (tt > h['t_release']+1) & (tt < h['t_release']+12); y = v[mm]-v[mm].mean(); w = np.hanning(mm.sum()); w /= w.mean()
meas = {int(k): float(abs(2*np.mean(w*y*np.exp(-2j*np.pi*k*h['f']*tt[mm])))) for k in (10, 14, 18, 20, 21, 22, 26, 30)}
print('simulated:', json.dumps(sim_out)); print('measured comb (spring 1, 81.4 ohm):', meas)
json.dump(dict(feature=rows, inl=inl, simulation=sim_out, measured_comb_uV=meas), open('adc_nonlinearity.json', 'w'), indent=1, default=float)
