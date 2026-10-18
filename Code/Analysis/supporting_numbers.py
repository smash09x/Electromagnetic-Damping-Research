"""Smaller numbers quoted in the paper that are not produced elsewhere.

1. ADC step at the amplifier input (from the quantisation of the recorded values) vs the published firmware constants.
2. Input-referred noise before release (raw record, first 0.3 s, magnet at rest).
3. Release-size correction for the 2.2 MOhm divider check.
4. Effective dipole moment from the 11 G Hall reading, and coil-1 turns from the measured EMF;
   independent turns estimate from the coil's 15.2 Ohm resistance and size.
5. Equivalent linear damping from quadratic air drag on the magnet.
6. Time per ADC read implied by the clock factor.
Writes Data/Results/supporting_numbers.json
"""
from common import *
import json
S = clock()[0]
st = json.load(open(os.path.join(RES, "final_stats.json")))
rows = json.load(open(os.path.join(OUT, "final_rows.json")))
out = {}

# 1. ADC step: recorded values sit on a lattice; fit its spacing
steps = []
for sp, R, s, p in runs():
    t, v = load(p); u = np.unique(v); d = np.diff(u); q = np.median(d[d > 1])   # nearest-neighbour spacing
    for _ in range(3):                                   # refine on the full lattice
        k = np.round((u - u[0]) / q).astype(int); q = np.polyfit(k, u, 1)[0]
    steps.append(q)
pub = 3.3 / 4095 / 35 * 1e6                      # main.cpp: sourceVoltage / 4095 / gain, in uV
out["adc_step_uV"] = round(float(np.mean(steps)), 3); out["adc_step_spread_uV"] = float(np.ptp(steps))
out["adc_step_published_uV"] = round(pub, 3); out["adc_step_excess_pct"] = round(100 * (np.mean(steps) / pub - 1), 2)

# 2. pre-release noise (raw, first 0.3 s): coil-1 runs below 10 kOhm, and all 21 runs
nz = {}
for sp, R, s, p in runs():
    t, v = load(p); fs = 1 / np.median(np.diff(t)); nz[(sp, R, s)] = float(np.std(v[:int(0.3 * fs)]))
c1 = [x for (sp, R, s), x in nz.items() if sp in ("S1", "S2") and R < 1e4]
allr = list(nz.values())
out["noise_coil1_lt10k_uV"] = dict(n=len(c1), min=round(min(c1)), max=round(max(c1)), median=round(float(np.median(c1))))
out["noise_all21_uV"] = dict(n=len(allr), min=round(min(allr)), max=round(max(allr)), median=round(float(np.median(allr))))
eps_mean = np.mean([r["eps"] for r in rows if r["sp"] == "S1" and r["R"] < 1e5])
out["noise_over_signal"] = round(float(np.median(c1)) * 1e-3 / eps_mean, 4)

# 3. release-size correction for the 2.2 MOhm run
dv = st["divider_2M2"]
out["release_2M2_smaller_pct"] = round(100 * (1 - dv["eps_expected_mV"] / eps_mean), 1)

# 4. dipole moment and turns
mu0 = 4e-7 * np.pi; B = 11e-4; z0 = 0.06; a_in = 0.028; h = 0.04
m_dip = 2 * np.pi * z0**3 * B / mu0                          # on-axis dipole field B = mu0 m / (2 pi z^3)
f1 = st["S1"]["f_true_mean"]; w = 2 * np.pi * f1
def eps_rms_per_turn(A, wth):
    t = np.linspace(0, 1 / f1, 2000, endpoint=False); z = A * np.cos(w * t); zd = -A * w * np.sin(w * t)
    k = 0
    aa = np.linspace(a_in, a_in + wth, 7); hh = np.linspace(-h / 2, h / 2, 41)
    for a in aa:
        for dz in hh:
            d = z0 + dz + z; k = k - 3 * mu0 * m_dip * a**2 * d / (2 * (d**2 + a**2)**2.5)
    k = k / (len(aa) * len(hh)); return float(np.sqrt(np.mean((k * zd)**2)))
eps1 = eps_mean * 1e-3
N_emf = {f"A={A*100:.1f}cm,w={wd*1000:.0f}mm": round(eps1 / eps_rms_per_turn(A, wd)) for A in (0.020, A_INIT, 0.024) for wd in (0.002, 0.005)}
# turns from resistance: N^2 = R h w * fill / (8 rho r_mean)   (round wire, packing fill 0.6-0.9)
rho = 1.72e-8
N_R = [float(np.sqrt(RC * h * wd * fill / (8 * rho * (a_in + wd / 2)))) for wd in (0.002, 0.005) for fill in (0.6, 0.9)]
out["dipole_moment_Am2"] = round(m_dip, 2); out["turns_from_emf"] = N_emf
out["turns_from_emf_central"] = round(eps1 / eps_rms_per_turn(A_INIT, 0.003))
out["turns_from_resistance_range"] = [round(min(N_R)), round(max(N_R))]

# 5. quadratic air drag on the magnet (disc broadside, Cd ~ 1.17), equivalent linear gamma at amplitude A
rho_air, Cd, Dm = 1.2, 1.17, 0.041
kq = 0.5 * rho_air * Cd * np.pi * (Dm / 2)**2
g_drag = (8 / (3 * np.pi)) * kq * w * A_INIT / (2 * M_OSC)    # energy loss per cycle (8/3) kq w^2 A^3 = pi b w A^2
vid = json.load(open(os.path.join(RES, "video_analysis.json")))
out["drag_gamma_1e3"] = round(g_drag * 1e3, 2)
out["drag_frac_of_gamma_video"] = round(g_drag * 1e3 / vid["spring1"]["gamma_video_mean"], 3)

# 6. time per ADC read: 50-read blocks, nominally 500 us per stored point
out["stored_point_spacing_us"] = round(500 * S, 1); out["time_per_read_us"] = round(500 * S / 50, 2)

json.dump(out, open(os.path.join(RES, "supporting_numbers.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
