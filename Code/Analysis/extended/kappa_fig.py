import numpy as np, json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from model import kappa_factory
K = json.load(open('kappa_recon.json')); B, O, INK, MUT, GRID = '#2a78d6', '#eb6834', '#0b0b0b', '#52514e', '#e4e3df'
plt.rcParams.update({'font.size': 9.5, 'axes.edgecolor': MUT, 'axes.labelcolor': INK, 'xtick.color': MUT, 'ytick.color': MUT, 'axes.spines.top': False, 'axes.spines.right': False, 'figure.facecolor': '#fcfcfb', 'axes.facecolor': '#fcfcfb'})
z1, k1, s1 = [np.array(K['S1'][k]) for k in ('z_cm', 'kappa', 'kappa_sd')]; z2, k2, s2 = [np.array(K['S2'][k]) for k in ('z_cm', 'kappa', 'kappa_sd')]
g1 = ~np.isnan(k1); g2 = ~np.isnan(k2)
# one free number: the height offset of spring 2's rest position relative to spring 1's
def mis(d):
    zz = z2[g2] + d; m = (zz > z1[g1].min()) & (zz < z1[g1].max()); return np.sqrt(np.mean((np.interp(zz[m], z1[g1], k1[g1])/k2[g2][m]-1)**2)), m.sum()
ds = np.linspace(-0.5, 2.5, 301); r = np.array([mis(d)[0] for d in ds]); d0 = ds[np.argmin(r)]
print('spring-2 rest position is %.2f cm above spring-1 rest; rms mismatch of the two kappa(z) curves over the overlap %.1f%% (%d bins)' % (d0, 100*r.min(), mis(d0)[1]))
fig, ax = plt.subplots(1, 2, figsize=(10.2, 4.0), gridspec_kw=dict(wspace=0.28)); a = ax[0]
a.fill_between(z1[g1], (k1-s1)[g1], (k1+s1)[g1], color=B, alpha=.18, lw=0); a.plot(z1[g1], k1[g1], color=B, lw=2, label='Spring 1, 24 July (8 runs)')
a.plot(z2[g2]+d0, k2[g2], 's', ms=4.5, color=O, mec='#fcfcfb', mew=.8, label=f'Spring 2, 24 July (8 runs), shifted {d0:.1f} cm')
J = K.get('Jul23')
if J:
    z3, k3 = np.array(J['z_cm']), np.array(J['kappa']); g3 = ~np.isnan(k3); a.plot(z3[g3]+J['shift_cm'], k3[g3], '^', ms=4.5, color='#1baf7a', mec='#fcfcfb', mew=.8, label=f"23 July session (12 runs), shifted {J['shift_cm']:.1f} cm")
zz = np.linspace(min(z1[g1].min(), -2.4), (z2[g2]+d0).max(), 200)/100; kd = kappa_factory(0.06)(zz); i0 = np.argmin(np.abs(zz)); kd = kd/kd[i0]*np.interp(0, z1[g1], k1[g1])
a.plot(zz*100, kd, '--', color=MUT, lw=1.3, label='Point dipole 6 cm above coil centre\n(scaled to match at rest)')
a.set_xlabel('Magnet height relative to spring-1 rest position (cm)'); a.set_ylabel('Coupling κ = EMF / velocity (V s m$^{-1}$)'); a.set_title('(a) Coupling function measured from the recordings', loc='left', fontsize=10.5, color=INK)
a.grid(axis='y', color=GRID, lw=.8); a.set_axisbelow(True); a.legend(frameon=False, fontsize=8.3, loc='upper right'); a.set_ylim(0, None)
a = ax[1]; aa = np.linspace(0.05, 1, 40); th = np.linspace(0, 2*np.pi, 2000, endpoint=False)
for nm, col, lab in (('S1', B, 'Spring 1'), ('S2', O, 'Spring 2')):
    pc = K[nm]['poly']; A = K[nm]['A_rel']; g = np.array([np.mean(np.polyval(pc, x*np.cos(th))**2*np.sin(th)**2)/(0.105*A*A)/15.2*1e3 for x in aa])
    a.fill_between(aa*A*100, g*0.84, g*1.16, color=col, alpha=.15, lw=0); a.plot(aa*A*100, g, color=col, lw=2, label=lab)
a.set_xlabel('Oscillation amplitude (cm)'); a.set_ylabel('Predicted added decay rate, coil shorted (10$^{-3}$ s$^{-1}$)'); a.set_title('(b) Prediction for the control that was not run', loc='left', fontsize=10.5, color=INK)
a.grid(axis='y', color=GRID, lw=.8); a.set_axisbelow(True); a.set_ylim(0, None); a.set_xlim(0, None); a.legend(frameon=False, fontsize=8.3, loc='lower right')
fig.savefig('kappa_measured.png', dpi=170, bbox_inches='tight'); fig.savefig('kappa_measured.pdf', bbox_inches='tight')
