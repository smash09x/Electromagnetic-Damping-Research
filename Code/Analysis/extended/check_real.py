import csv, json, numpy as np, sys
from est import *
sys.path.insert(0, REPO+'/Code/Analysis')
import common
ref = {r['run']: r for r in csv.DictReader(open(REPO+'/Data/Results/final_table.csv'))}
names = {'S1': 'spring1/coil1', 'S2': 'spring2/coil1', 'S12c': 'spring1/coil2', 'S13c': 'spring1/coil3', 'S22c': 'spring2/coil2', 'S23c': 'spring2/coil3'}
rows = []
for sp, R, s, p in common.runs():
    t, v = load(p); h = headline(t, v)
    H = harmonics(h['t'], h['x'], h['f'], h['t_release'])
    a = np.abs(H); ph = np.angle(H)
    # harmonic phase relative to fundamental: phi_k - k*phi_1
    rel = [np.degrees(np.angle(np.exp(1j*(ph[k]-(k+1)*ph[0])))) for k in range(1, 4)]
    rr = ref[f"{names[sp]}/{s}"]
    rows.append(dict(sp=sp, R=R, run=s, gamma=h['gamma']*1e3, f=h['f'], eps=h['eps_mV'], g_peak=h['g_peak']*1e3, el=h['early_late'],
                     A1=a[0]*1e-3, h21=a[1]/a[0], h31=a[2]/a[0], h41=a[3]/a[0], rel=rel, dur=h['t'][-1]))
    print(f"{sp:4s} {R:>9g} {s[:9]:9s} g {h['gamma']*1e3:6.2f} (ref {rr['gamma_true']}) f {h['f']:.4f} ({rr['f_true']}) eps {h['eps_mV']:5.2f} ({rr['eps_rms_init_mV']}) "
          f"gpk {h['g_peak']*1e3:6.2f} A1 {a[0]*1e-3:5.2f}mV h21 {a[1]/a[0]:.3f} h31 {a[2]/a[0]:.3f} h41 {a[3]/a[0]:.3f} rel {rel[0]:6.1f} {rel[1]:6.1f} dur {h['t'][-1]:.1f}")
json.dump(rows, open('real_rows.json', 'w'), indent=1)
