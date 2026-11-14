import numpy as np, json
from est import headline, harmonics
from model import kappa_factory, harm
from sim import *
from scipy.optimize import least_squares
rows = json.load(open('real_rows.json'))
S1 = [r for r in rows if r['sp']=='S1' and r['R']<1e5]; S2 = [r for r in rows if r['sp']=='S2']
m = lambda rr,k: float(np.mean([r[k] for r in rr])); sd = lambda rr,k: float(np.std([r[k] for r in rr], ddof=1))
A_VID1, A_VID2 = 0.0211, 0.0265         # mean video A0 (Table S2): spring 1 (7 tracks), spring 2 (10 tracks)
F1, F2 = 2.0820, 1.8622
res = {}
# ---- 1. geometry-only prediction (stated geometry, point dipole, video amplitude)
H = np.abs(harm(kappa_factory(0.06), A_VID1, F1))
res['geometry_only'] = dict(h21_pred=H[1]/H[0], h31_pred=H[2]/H[0], h21_meas=m(S1,'h21'), h31_meas=m(S1,'h31'), h21_sd=sd(S1,'h21'), h31_sd=sd(S1,'h31'))
# ---- 2. effective model: fit z0 and one length scale lam (A_eff = A_video/lam) to spring-1 mean h21,h31
def r(q):
    H = np.abs(harm(kappa_factory(q[0]), A_VID1/q[1], F1)); return [H[1]/H[0]-m(S1,'h21'), H[2]/H[0]-m(S1,'h31')]
q = least_squares(r, [0.056, 1.5]).x; Z0, LAM = q
res['effective'] = dict(z0_cm=Z0*100, length_scale=LAM, A_eff_cm=A_VID1/LAM*100)
kap = kappa_table(Z0)
# ---- 3. unfitted: spring 2 harmonics at its video amplitudes, same z0 and lam
pred2 = {A: (np.abs(harm(kap, A/LAM, F2))) for A in (0.022, A_VID2, 0.031)}
res['spring2_harmonics'] = dict(pred={f'A={A*100:.2f}cm': dict(h21=H[1]/H[0], h31=H[2]/H[0], h41=H[3]/H[0]) for A,H in pred2.items()},
                                meas=dict(h21=[min(r['h21'] for r in S2), m(S2,'h21'), max(r['h21'] for r in S2)], h31=[min(r['h31'] for r in S2), m(S2,'h31'), max(r['h31'] for r in S2)], h41=m(S2,'h41')),
                                h41_S1=dict(pred=float(np.abs(harm(kap, A_VID1/LAM, F1))[3]/np.abs(harm(kap, A_VID1/LAM, F1))[0]), meas=m(S1,'h41')))
# ---- 4. truth for the motion from the spring-1 videos: gamma 11.31e-3, early/late 1.08
g0, beta = solve_truth(11.31e-3, 1.08); b_per_m = beta/A_VID1
res['truth'] = dict(g0=g0*1e3, beta_at_A0=beta*1e3, frac_amp_dep=beta/(g0+beta))
# ---- 5. simulate, ideal sampling, run repo estimators -> estimator biases (unfitted)
def run(A0, f, scale, rng=None, **kw):
    bet = b_per_m*A0
    def emf(t):
        z, zd = motion(t, A0/LAM, f, g0, bet, t_rel=1.0); return scale*kap(z)*zd
    return daq(emf, rng or np.random.default_rng(0), **kw), bet
def motion_gamma(A0, f, bet, t0, t1):
    t = np.linspace(t0, t1, 4000); y = np.log(envelope(t, g0, bet)); return -np.polyfit(t, y, 1)[0]
# scale so spring-1 fundamental = measured A1
(t, v), bet = run(A_VID1, F1, 1.0, sigma_lsb=0, hum=0, quantise=False, int_div=False, true_time=True)
h = headline(t, v, S=1.0); Hh = harmonics(h['t'], h['x'], h['f'], h['t_release']); SCALE = m(S1,'A1')*1e3/np.abs(Hh[0])
res['scale_N_times_m'] = SCALE*1e-6
out = []
for name, A0, f, meas in (('S1', A_VID1, F1, S1), ('S2', A_VID2, F2, S2)):
    (t, v), bet = run(A0, f, SCALE, sigma_lsb=0, hum=0, quantise=False, int_div=False, true_time=True)
    h = headline(t, v, S=1.0); gm = motion_gamma(A0, f, bet, h['t_release']-1.0+1.0, t[-1]-1.0-1.0)
    Hh = np.abs(harmonics(h['t'], h['x'], h['f'], h['t_release']))
    out.append(dict(spring=name, A0_cm=A0*100, gamma_motion=gm*1e3, gamma_env_pred=h['gamma']*1e3, gamma_env_meas=m(meas,'gamma'), gamma_env_sd=sd(meas,'gamma'),
                    env_bias_pred=h['gamma']/gm-1, g_peak_pred=h['g_peak']*1e3, g_peak_meas=m(meas,'g_peak'), peak_over_env_pred=h['g_peak']/h['gamma'], peak_over_env_meas=m(meas,'g_peak')/m(meas,'gamma'),
                    early_late_pred=h['early_late'], early_late_meas=m(meas,'el'), eps_pred=h['eps_mV'], eps_meas=m(meas,'eps'), A1_pred=Hh[0]*1e-3, A1_meas=m(meas,'A1'), h21_sim=Hh[1]/Hh[0]))
res['estimators'] = out
# ---- 6. gamma_env vs release amplitude (curve for figure): sweep A0 for both springs
sweep = {}
for name, f in (('S1', F1), ('S2', F2)):
    L = []
    for A0 in np.linspace(0.014, 0.034, 9):
        (t, v), bet = run(A0, f, SCALE, sigma_lsb=0, hum=0, quantise=False, int_div=False, true_time=True)
        h = headline(t, v, S=1.0); Hh = np.abs(harmonics(h['t'], h['x'], h['f'], h['t_release']))
        L.append(dict(A0_cm=A0*100, h21=Hh[1]/Hh[0], gamma_env=h['gamma']*1e3, g_peak=h['g_peak']*1e3, eps=h['eps_mV'], A1=Hh[0]*1e-3))
    sweep[name] = L
res['sweep'] = sweep
json.dump(dict(Z0=Z0, LAM=LAM, g0=g0, b_per_m=b_per_m, SCALE=SCALE), open('params.json','w'))
json.dump(res, open('validate.json','w'), indent=1, default=float)
print(json.dumps({k:v for k,v in res.items() if k!='sweep'}, indent=1, default=float))
for n in sweep: print(n, [(round(x['A0_cm'],2), round(x['h21'],3), round(x['gamma_env'],2), round(x['eps'],1)) for x in sweep[n]])
