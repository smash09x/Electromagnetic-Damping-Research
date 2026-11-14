"""Injection-recovery: known motion -> as-built DAQ -> repo pipeline. What does each DAQ flaw do to the result?"""
import numpy as np, json, time
from est import headline
from sim import *
P = json.load(open('params.json')); kap = kappa_table(P['Z0'])
A0, F = 0.0211, 2.0820; g0 = P['g0']; bet = P['b_per_m']*A0; TR = 12.613e-6; S_TRUE = 50*TR/500e-6
def emf(t):
    z, zd = motion(t, A0/P['LAM'], F, g0, bet, t_rel=1.0); return P['SCALE']*kap(z)*zd
# truth: decay of the motion over the estimator's window (release+1 s .. end-1 s), and of the ideal EMF envelope
T_END = 60000*50*TR; tw = np.linspace(2.0, T_END-1.0, 4000)
G_MOTION = -np.polyfit(tw, np.log(envelope(tw-1.0, g0, bet)), 1)[0]
conds = [
 ('ideal sampling, true timestamps',            dict(sigma_lsb=0, hum=0, quantise=False, int_div=False, true_time=True),  1),
 ('+ 12-bit quantisation, float average',       dict(sigma_lsb=0, hum=0, quantise=True,  int_div=False, true_time=True),  1),
 ('+ integer-division average (no noise)',      dict(sigma_lsb=0, hum=0, quantise=True,  int_div=True,  true_time=True),  1),
 ('+ read noise 5 LSB and 7 uV hum',            dict(sigma_lsb=5, hum=7e-6, quantise=True, int_div=True, true_time=True), 12),
 ('+ nominal timestamps, uncorrected',          dict(sigma_lsb=5, hum=7e-6, quantise=True, int_div=True, true_time=False), 12),
 ('+ nominal timestamps, hum-corrected',        dict(sigma_lsb=5, hum=7e-6, quantise=True, int_div=True, true_time=False), 12),
]
out = []; t0 = time.time()
for name, kw, n in conds:
    G, Fq, Sx, EP = [], [], [], []
    for seed in range(n):
        rng = np.random.default_rng(100+seed); t, v = daq(emf, rng, T_reads=TR, **kw)
        if 'hum-corrected' in name: s = hum_clock(t, v)
        else: s = 1.0
        h = headline(t, v, S=s); G.append(h['gamma']); Fq.append(h['f']); Sx.append(s); EP.append(h['eps_mV'])
    G = np.array(G); rec = dict(cond=name, n=n, gamma=G.mean()*1e3, gamma_sd=(G.std(ddof=1)*1e3 if n > 1 else 0.0), f=np.mean(Fq), s=np.mean(Sx), s_sd=(np.std(Sx, ddof=1) if n > 1 else 0.0), eps=np.mean(EP),
                             gamma_over_motion=G.mean()/G_MOTION, f_over_true=np.mean(Fq)/F)
    out.append(rec); print(f"{name:42s} n={n:2d} gamma {rec['gamma']:6.3f} +- {rec['gamma_sd']:.3f}  (x{rec['gamma_over_motion']:.4f} of motion)  f {rec['f']:.4f} (x{rec['f_over_true']:.4f})  s {rec['s']:.5f} +- {rec['s_sd']:.5f}  eps {rec['eps']:.2f}  [{time.time()-t0:.0f}s]", flush=True)
json.dump(dict(gamma_motion=G_MOTION*1e3, f_true=F, s_true=S_TRUE, rows=out), open('inject.json', 'w'), indent=1, default=float)
print('truth: gamma_motion %.3f, f %.4f, s %.5f' % (G_MOTION*1e3, F, S_TRUE))
