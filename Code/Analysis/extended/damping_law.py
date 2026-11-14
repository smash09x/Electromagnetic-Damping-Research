"""Which loss law does the motion follow? Fit the video tracks (true frame times) with
dA/dt = -(g0 + beta*A/A0 + delta*A0/A) A : viscous (g0), amplitude-proportional (beta, e.g. quadratic drag), Coulomb-like (delta)."""
import numpy as np, glob, os, json
from scipy.optimize import least_squares
from scipy.integrate import solve_ivp
from est import REPO
R = os.path.join(REPO, 'Data', 'Video') + '/'
S1 = ['WA0011','WA0012','WA0030','WA0031','WA0033','WA0034','WA0042']; S2 = ['WA0035','WA0038','WA0043']
def env(t, g0, beta, delta):
    if delta == 0:
        e = np.exp(-g0*t); return g0*e/(g0+beta*(1-e)) if abs(beta) > 1e-12 else e
    return np.clip((1+delta/g0)*np.exp(-g0*t) - delta/g0, 1e-6, None)      # viscous + Coulomb-like (beta ignored)
def load(v):
    y = np.genfromtxt(R+f'VID-20260725-{v}.csv', delimiter=',', skip_header=1)[:, 1]; t = np.genfromtxt(R+f'frame_times/VID-20260725-{v}.csv', skip_header=1)
    y0 = np.median(y[:15]); i0 = np.where(np.abs(y-y0) > 0.003)[0][0]; t, y = t[i0:]-t[i0], y[i0:]
    k = (t > 0.5) & (t < t[-1]-1.0); return t[k]-t[k][0], y[k]
def fit(t, y, model):
    n = len(y); F = np.abs(np.fft.rfft((y-y.mean())*np.hanning(n), 16*n)); fr = np.fft.rfftfreq(16*n, np.mean(np.diff(t))); m = (fr > 1) & (fr < 4); w0 = 2*np.pi*fr[m][np.argmax(F[m])]
    def r(q):
        A, w, ph, c0, c1, g0 = q[:6]; b = q[6] if model in ('drag', 'both') else 0.0; d = q[-1] if model in ('coulomb', 'both') else 0.0
        return A*env(t, g0, b, d)*np.cos(w*t+ph)+c0+c1*t-y
    best = None
    for ph in np.linspace(0, 2*np.pi, 8, endpoint=False):
        q0 = [np.ptp(y)/2, w0, ph, y.mean(), 0, 0.011] + ([0.002] if model in ('drag', 'both') else []) + ([0.0005] if model in ('coulomb', 'both') else [])
        s = least_squares(r, q0, x_scale=[0.01, 0.01, 1, 0.001, 1e-4, 1e-3] + [1e-3]*(len(q0)-6))
        if best is None or s.cost < best.cost: best = s
    k = len(best.x); rss = 2*best.cost; cov = np.linalg.pinv(best.jac.T@best.jac)*rss/(n-k)
    return best.x, np.sqrt(np.diag(cov)), rss, n, k
out = []
for sp, vids in (('S1', S1), ('S2', S2)):
    for v in vids:
        t, y = load(v); rec = dict(spring=sp, video=v)
        for mdl in ('exp', 'drag', 'coulomb'):
            q, se, rss, n, k = fit(t, y, mdl); aic = n*np.log(rss/n)+2*k
            rec[mdl] = dict(A0=abs(q[0])*100, g0=q[5]*1e3, g0_se=se[5]*1e3, rms_mm=np.sqrt(rss/n)*1e3, aic=aic,
                            beta=(q[6]*1e3 if mdl in ('drag', 'both') else None), beta_se=(se[6]*1e3 if mdl in ('drag', 'both') else None),
                            delta=(q[-1]*1e3 if mdl in ('coulomb', 'both') else None), delta_se=(se[-1]*1e3 if mdl in ('coulomb', 'both') else None))
        out.append(rec); e, d, c = rec['exp'], rec['drag'], rec['coulomb']
        print(f"{sp} {v} A0 {d['A0']:.2f}cm | exp g {e['g0']:.2f} rms {e['rms_mm']:.2f} | drag g0 {d['g0']:.2f} beta {d['beta']:.2f}+-{d['beta_se']:.2f} dAIC {d['aic']-e['aic']:.0f} | coulomb g0 {c['g0']:.2f} delta {c['delta']:.2f}+-{c['delta_se']:.2f} dAIC {c['aic']-e['aic']:.0f}")
json.dump(out, open('damping_law.json', 'w'), indent=1, default=float)
s1 = [r for r in out if r['spring'] == 'S1']; B = np.array([r['drag']['beta'] for r in s1]); G = np.array([r['drag']['g0'] for r in s1]); A = np.array([r['drag']['A0'] for r in s1])
print('S1 drag model: g0 %.2f +- %.2f (sd), beta@A0 %.2f +- %.2f (sd, n=7), amplitude-dependent fraction at release %.0f%%' % (G.mean(), G.std(ddof=1), B.mean(), B.std(ddof=1), 100*np.mean(B/(B+G))))
# air-drag expectation for beta at each track's A0 (disc broadside, Cd 1.17)
kq = 0.5*1.2*1.17*np.pi*0.0205**2; w = 2*np.pi*2.0812; bd = (8/(3*np.pi))*kq*w*(A/100)/(2*0.105)*1e3
print('air-drag beta expected %.2f; measured/expected %.1f' % (bd.mean(), np.mean(B/bd)))
