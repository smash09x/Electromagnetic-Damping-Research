"""Coupling function straight from the recordings: emf = kappa(z) * zdot, so kappa(z) = emf / zdot.
Turning points of the motion are the zero crossings of the EMF; amplitude scale and envelope come from the videos."""
import numpy as np, json, sys
from est import *
from sim import envelope
import common
P = json.load(open('params.json')); G0, B_PER_M = P['g0'], P['b_per_m']
M_OSC, RC = 0.105, 15.2
def recon(p, A_rel, nb=41, g0=None, b=None):
    g0 = G0 if g0 is None else g0; b = B_PER_M if b is None else b
    t, v = load(p); h = headline(t, v); tt, x = h['t'], h['x']*1e-6           # true time, volts
    n0 = int(0.3*h['fsT']); thr = max(8*np.std(x[:n0]), 0.03*np.abs(x).max()); i0 = int(np.argmax(np.abs(x) > thr))
    # release instant: extrapolate the initial linear rise of |emf| back to zero
    j = np.arange(i0, i0+max(4, int(0.01*h['fsT']))); pf = np.polyfit(tt[j], np.abs(x[j]), 1); t_rel = min(tt[i0], -pf[1]/pf[0]) if pf[0] > 0 else tt[i0]
    zc = np.where(np.sign(x[:-1]) != np.sign(x[1:]))[0]; zc = zc[tt[zc] > t_rel + 0.12]
    tz = tt[zc] - x[zc]*(tt[zc+1]-tt[zc])/(x[zc+1]-x[zc]); tz = tz[np.r_[True, np.diff(tz) > 0.15]]
    tz = np.r_[t_rel, tz]
    k = np.arange(len(tz)); m = (tt > tz[0]) & (tt < tz[-1]); th = np.interp(tt[m], tz, k*np.pi); thd = np.gradient(th, tt[m])
    a = envelope(tt[m]-tz[0], g0, b*A_rel); ad = -(g0 + b*A_rel*a)*a
    u = a*np.cos(th); ud = ad*np.cos(th) - a*thd*np.sin(th); e = x[m]
    ok = np.abs(np.sin(th)) > 0.35; K = e[ok]/ud[ok]; uu = u[ok]; down = (np.sin(th[ok]) > 0)
    edges = np.linspace(-1, 1, nb+1); cen = 0.5*(edges[1:]+edges[:-1]); out = {}
    for name, sel in (('all', np.ones(len(uu), bool)), ('down', down), ('up', ~down)):
        idx = np.digitize(uu[sel], edges)-1; out[name] = np.array([np.median(K[sel][idx == i]) if np.sum(idx == i) > 30 else np.nan for i in range(nb)])
    return cen, out, h, (tz[1]-tz[0])/np.median(np.diff(tz[2:40]))
if __name__ != '__main__': raise SystemExit
res = {}
for sp, A_rel in (('S1', 0.0220), ('S2', 0.0265)):          # release amplitudes: video first-swing values (see text)
    Ks = []; hp = []
    for s_, R, s, p in common.runs():
        if s_ != sp or R > 1e5: continue
        cen, o, h, r0 = recon(p, A_rel); Ks.append(o); hp.append(r0)
    Kall = np.array([o['all'] for o in Ks]); Kd = np.array([o['down'] for o in Ks]); Ku = np.array([o['up'] for o in Ks])
    sg = np.sign(np.nanmedian(Kall, axis=1))[:, None]; Kall, Kd, Ku = sg*Kall, sg*Kd, sg*Ku
    print('   first half-period / median half-period per run:', np.round(hp, 2))
    mean = np.nanmean(Kall, axis=0); sd = np.nanstd(Kall, axis=0, ddof=1)
    # normalise each run by its own K(0) to separate shape from release-amplitude scatter
    i0 = len(cen)//2; shape = Kall/Kall[:, [i0]]; shsd = np.nanstd(shape, axis=0, ddof=1)
    kap = mean/A_rel                                           # V s / m
    print(sp, 'runs', len(Ks), '| kappa at rest %.3f V s/m (run sd %.1f%%) | kappa(+A)/kappa(0) %.2f  kappa(-A)/kappa(0) %.2f | shape sd across runs (median over z) %.1f%% | up/down stroke difference (median |d|/K) %.1f%%' % (
        kap[i0], 100*sd[i0]/mean[i0], np.nanmean(mean[-2:])/mean[i0], np.nanmean(mean[:2])/mean[i0], 100*np.nanmedian(shsd), 100*np.nanmedian(np.abs(np.nanmean(Kd, 0)-np.nanmean(Ku, 0))/mean)))
    good = ~np.isnan(mean); pc = np.polyfit(cen[good], mean[good], 5)
    def c_of(a):
        thq = np.linspace(0, 2*np.pi, 2000, endpoint=False); return float(np.mean(np.polyval(pc, a*np.cos(thq))**2*np.sin(thq)**2)/(M_OSC*A_rel**2))
    cs = {a: c_of(a) for a in (1.0, 0.8, 0.6, 0.4, 0.2, 0.05)}
    print('   c(a) Ohm/s:', {k: round(v, 4) for k, v in cs.items()}, '-> shorted-coil gamma_em (1e-3/s):', {k: round(v/RC*1e3, 2) for k, v in cs.items()})
    res[sp] = dict(A_rel=A_rel, z_cm=(cen*A_rel*100).tolist(), kappa=kap.tolist(), kappa_sd=(sd/A_rel).tolist(), poly=pc.tolist(), c=cs, shape_sd=shsd.tolist())
json.dump(res, open('kappa_recon.json', 'w'), indent=1, default=float)
