import numpy as np, json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from est import *; from model import *; from sim import kappa_table
import common
P = json.load(open('params.json')); V = json.load(open('validate.json')); rows = json.load(open('real_rows.json'))
B, O, INK, MUT, GRID = '#2a78d6', '#eb6834', '#0b0b0b', '#52514e', '#e4e3df'
plt.rcParams.update({'font.size': 9.5, 'axes.edgecolor': MUT, 'axes.labelcolor': INK, 'xtick.color': MUT, 'ytick.color': MUT, 'axes.spines.top': False, 'axes.spines.right': False,
                     'figure.facecolor': '#fcfcfb', 'axes.facecolor': '#fcfcfb', 'font.family': 'DejaVu Sans'})
fig, ax = plt.subplots(1, 2, figsize=(10.2, 4.1), gridspec_kw=dict(wspace=0.28))
# (a) one cycle: measured vs models, normalised to the fundamental
p = [r for r in common.runs() if r[0] == 'S1' and r[2] == '0.0/Retake 2'][0][3]
t, v = load(p); h = headline(t, v); f = h['f']; tt, x = h['t'], h['x']
H = harmonics(tt, x, f, h['t_release']); ph = np.angle(H[0]); m = (tt >= h['t_release']) & (tt < h['t_release'] + 6/f)
th = (2*np.pi*f*(tt[m]-h['t_release']) + ph) % (2*np.pi); o = np.argsort(th)
a = ax[0]; a.plot(th[o]/(2*np.pi), x[m][o]/abs(H[0]), '.', ms=2.2, color=B, alpha=.55, label='Measured (spring 1, 6 cycles)', rasterized=True)
def cyc(kap, A):
    thm, e = emf_cycle(kap, A, f); Hm = 2*np.mean(e*np.exp(-1j*thm)); thp = (thm + np.angle(Hm)) % (2*np.pi); o = np.argsort(thp); return thp[o]/(2*np.pi), e[o]/abs(Hm)
xs, ys = cyc(kappa_factory(0.06), 0.0211); xs2, ys2 = cyc(kappa_factory(P['Z0']), 0.0211/P['LAM'])
# sign: model sign convention is arbitrary -> pick the sign that matches the data's 2nd-harmonic phase
def best(xs, ys):
    yi = np.interp(th[o]/(2*np.pi), xs, ys); yj = np.interp(th[o]/(2*np.pi), (xs+.5) % 1, -ys, period=1)
    d = x[m][o]/abs(H[0]); return (xs, ys) if np.sum((yi-d)**2) < np.sum((yj-d)**2) else (np.sort((xs+.5) % 1), -ys[np.argsort((xs+.5) % 1)])
xs, ys = best(xs, ys); xs2, ys2 = best(xs2, ys2)
a.plot(xs, ys, color=O, lw=2, label='Point dipole, stated geometry (no fit)'); a.plot(xs2, ys2, color=INK, lw=1.6, label='Effective coupling (2 fitted numbers)')
a.set_xlabel('Phase of the fundamental (cycles)'); a.set_ylabel('EMF / fundamental amplitude'); a.set_title('(a) Waveform over one cycle', loc='left', fontsize=10.5, color=INK)
a.grid(axis='y', color=GRID, lw=.8); a.set_axisbelow(True); a.legend(frameon=False, fontsize=8.3, loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=1); a.set_xlim(0, 1)
# (b) EMF-envelope decay rate vs second-harmonic fraction (amplitude proxy)
a = ax[1]
S1 = [r for r in rows if r['sp'] == 'S1' and r['R'] < 1e5]; S2 = [r for r in rows if r['sp'] == 'S2']
sw = V['sweep']['S2']; a.plot([s['h21'] for s in sw], [s['gamma_env'] for s in sw], color=INK, lw=1.6, label='Simulation (motion decay from the videos)', zorder=2)
a.plot([r['h21'] for r in S1], [r['gamma'] for r in S1], 'o', ms=6.5, color=B, mec='#fcfcfb', mew=1.2, label='Spring 1 runs', zorder=3)
a.plot([r['h21'] for r in S2], [r['gamma'] for r in S2], 's', ms=6.5, color=O, mec='#fcfcfb', mew=1.2, label='Spring 2 runs', zorder=3)
a.set_xlim(0.28, 0.5); a.set_ylim(10, 15.6); a.set_xlabel('Second-harmonic fraction of the EMF (grows with release amplitude)'); a.set_ylabel('EMF-envelope decay rate (10$^{-3}$ s$^{-1}$)')
a.set_title('(b) Apparent damping tracks release amplitude', loc='left', fontsize=10.5, color=INK); a.grid(axis='y', color=GRID, lw=.8); a.set_axisbelow(True)
a.legend(frameon=False, fontsize=8.3, loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=1)
fig.savefig('sim_validation.png', dpi=170, bbox_inches='tight'); fig.savefig('sim_validation.pdf', bbox_inches='tight')
# regression numbers for (b)
x2 = np.array([r['h21'] for r in S2]); y2 = np.array([r['gamma'] for r in S2]); sl, ic = np.polyfit(x2, y2, 1)
xm = np.array([s['h21'] for s in sw]); ym = np.array([s['gamma_env'] for s in sw]); k = (xm > 0.33) & (xm < 0.49); slm = np.polyfit(xm[k], ym[k], 1)[0]
resid = y2 - np.interp(x2, xm, ym); r1 = np.array([r['gamma'] for r in S1]) - np.interp([r['h21'] for r in S1], xm, ym)
print('S2 slope meas %.1f, model %.1f per unit h21; S2 resid vs model mean %.2f sd %.2f (raw sd %.2f); S1 resid mean %.2f sd %.2f (raw sd %.2f)' % (sl, slm, resid.mean(), resid.std(ddof=1), y2.std(ddof=1), r1.mean(), r1.std(ddof=1), np.std([r['gamma'] for r in S1], ddof=1)))
