"""Round-2 final numbers. Headline estimator: Hilbert envelope of the fundamental band (0.6-1.4 f),
fit window = first peak above 50% max + 1 s  ->  end - 1 s, one point per cycle, OLS on ln(env).
Errors: moving-block bootstrap (6-cycle blocks). Clock correction t_true = S * t_nominal."""
from common import *
from scipy.signal import butter as bt, sosfiltfilt
from scipy import stats
import json, csv
S, S_SD, S_GRID = clock()         # from clock_calibration.json (mains-hum line, n=11 runs)
rng = np.random.default_rng(7)
def lin(tt, y):
    p, c = np.polyfit(tt, y, 1, cov=True); return -p[0], np.sqrt(c[0, 0]), p
def bboot(tt, y, L=6, B=4000):
    p = np.polyfit(tt, y, 1); fit = np.polyval(p, tt); r = y - fit; n = len(y); g = []
    for _ in range(B):
        idx = np.concatenate([np.arange(s, s+L) for s in rng.integers(0, n-L+1, n//L+1)])[:n]
        g.append(-np.polyfit(tt, fit + r[idx], 1)[0])
    return np.std(g)
rows = []; alt = json.load(open(os.path.join(OUT,'refit.json'))); ph = json.load(open(os.path.join(OUT,'phys.json')))
key = lambda r: (r['sp'], r['R'], r['run'])
ALT = {key(r): r for r in alt}; PH = {key(r): r for r in ph}
for sp, R, s, p in runs():
    t, v, x, fs = prep(p); t = t * S                      # TRUE time
    fsT = fs / S
    f0 = authors_fit(p)['f'] / S
    sos = bt(4, [0.6*f0, 1.4*f0], btype='band', fs=fsT, output='sos'); xf = sosfiltfilt(sos, x)
    zc = np.where((xf[:-1] < 0) & (xf[1:] >= 0))[0]
    pk, _ = find_peaks(np.abs(x), distance=int(0.35*fs/(f0*S))); amp = np.abs(x[pk]); i0 = np.argmax(amp > 0.5*amp.max())
    ta, te = t[pk[i0]] + 1*S, t[-1] - 1*S
    zc = zc[(t[zc] > ta) & (t[zc] < te)]; f_true = (len(zc)-1) / (t[zc[-1]] - t[zc[0]])
    env = np.abs(hilbert(xf)); ds = int(round(fs / (f0*S))); m = (t > ta) & (t < te)
    th, eh = t[m][::ds], np.log(env[m][::ds])
    g, gse, pp = lin(th, eh); gb = bboot(th, eh)
    # local gamma vs fundamental amplitude (4-cycle windows) -> gamma at reference amplitude
    W = 8; loc = [(np.exp(eh[i:i+W].mean()), lin(th[i:i+W], eh[i:i+W])[0]) for i in range(0, len(th)-W, 2)]
    loc = np.array(loc)
    # eps_rms over first 3 cycles (authors' definition, sample-count based -> clock independent)
    i0s = np.argmax(np.abs(x) > 0.5*np.abs(x).max()); eps = np.sqrt(np.mean(x[i0s:i0s+int(3/(f0*S)*fs)]**2))*1e-3
    a = ALT[(sp, R, s)]; q = PH[(sp, R, s)]
    rows.append(dict(sp=sp, R=R, run=s, gamma=g, gse=gse, gboot=gb, f=f_true, Q=np.pi*f_true/g, eps=eps,
                     g_peak=a['g_auth']/S, g_rms=a['g_rms']/S, g_nls=a['g_nls1']/S, g_phys=q['g_phys']/S,
                     A1=a['A1'], h21=a['A2']/a['A1'], loc=loc.tolist(), early=a['g_early']/S, late=a['g_late']/S))
# reference-amplitude gamma: local slope regression gamma_loc = a + b*envamp, evaluated at a common amplitude
def gref(r, Aref):
    L = np.array(r['loc']); b = np.polyfit(L[:, 0], L[:, 1], 1); return np.polyval(b, Aref)
c1 = [r for r in rows if r['sp'] in ('S1', 'S2')]
names = {'S1': 'spring1/coil1', 'S2': 'spring2/coil1', 'S12c': 'spring1/coil2', 'S13c': 'spring1/coil3', 'S22c': 'spring2/coil2', 'S23c': 'spring2/coil3'}
with open(os.path.join(RES, 'final_table.csv'), 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['run', 'R_ext', 'gamma_true', 'gamma_err', 'Q', 'f_true', 'eps_rms_init_mV'])
    for r in rows:
        w.writerow([f"{names[r['sp']]}/{r['run']}", r['R'], f"{r['gamma']*1e3:.2f}", f"{r['gboot']*1e3:.2f}", f"{r['Q']:.0f}", f"{r['f']:.4f}", f"{r['eps']:.2f}"])
out = {'units': 'gamma in 1e-3 s^-1 (true time), c in Ohm/s', 'clock_s': S, 'clock_s_sd_runs': S_SD, 'clock_s_grid_tol': S_GRID,
       'estimator': 'Hilbert envelope of fundamental band 0.6-1.4f, window t0+1s..end-1s, 1 pt/cycle, 6-cycle block bootstrap'}
for sp in ('S1', 'S2'):
    rr = [r for r in rows if r['sp'] == sp and r['R'] < 1e5]
    d = {}
    for k in ('gamma', 'g_peak', 'g_rms', 'g_nls', 'g_phys', 'early', 'late'):
        g = np.array([r[k] for r in rr])*1e3; d[k] = [round(g.mean(), 3), round(g.std(ddof=1), 3)]
    Aref = 0.75*min(np.exp(np.mean(np.log(np.array(r['loc'])[:2, 0]))) for r in rr)   # an amplitude every run passes
    gr = np.array([gref(r, Aref) for r in rr])*1e3
    d['gamma_at_ref_amp'] = dict(A_ref_uV=round(Aref), mean=round(gr.mean(), 3), sd=round(gr.std(ddof=1), 3),
                                 corr_with_eps=round(stats.pearsonr([r['eps'] for r in rr], gr)[0], 2))
    d['corr_gamma_eps_pearson'] = round(stats.pearsonr([r['eps'] for r in rr], [r['gamma'] for r in rr])[0], 3)
    d['corr_gamma_eps_spearman'] = round(stats.spearmanr([r['eps'] for r in rr], [r['gamma'] for r in rr])[0], 3)
    d['corr_lategamma_eps'] = round(stats.pearsonr([r['eps'] for r in rr], [r['late'] for r in rr])[0], 3)
    d['f_true_mean'] = round(np.mean([r['f'] for r in rr]), 4); d['Q_mean'] = round(np.mean([r['Q'] for r in rr]), 1); d['Q_sd'] = round(np.std([r['Q'] for r in rr], ddof=1), 1)
    d['bootstrap_over_fitSE'] = round(np.median([r['gboot']/r['gse'] for r in rr]), 2)
    out[sp] = d
    print(sp, json.dumps(d))
json.dump(out, open(os.path.join(OUT,'_tmp.json'),'w'))
json.dump(rows, open(os.path.join(OUT,'final_rows.json'),'w'), default=float)
