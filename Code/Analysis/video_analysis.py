"""Independent clock check and displacement-level damping from the phone-video tracks.

Data/Video/VID-*.csv               time_s, vertical_distance_m, tracked frame by frame. The time column
                                   assumes evenly spaced frames at the file's average frame rate.
Data/Video/frame_times/VID-*.csv   the true presentation time of every frame, read with ffprobe from the
                                   original .mp4 files by check_video_clocks.py.
The videos (WhatsApp copies) have a variable frame rate, so the even-spacing assumption puts five tracks
0.7-2.6 % off in frequency. Every track is therefore fitted against its true frame times.

Model (nonlinear least squares, window = 1.5 s after release to 1.5 s before the end):
    y(t) = A exp(-gamma t) cos(omega t + phi) + c0 + c1 t
Early/late = gamma fitted to the first half of the window / gamma fitted to the second half.
Tracking-quality cut for the decay rate: rms fit residual < 10 % of the initial amplitude
(tracking failures leave residuals of several mm; frequencies are robust and kept for every track).
Writes Data/Results/video_analysis.json
"""
import os, glob, json, numpy as np
from scipy.optimize import least_squares
from common import RES, ROOT, clock

S_HUM = clock()[0]
VID = os.path.join(ROOT, "Data", "Video")
RESID_CUT = 0.10
rng = np.random.default_rng(11)

def damped_fit(t, y, f0):
    def r(q):
        A, g, w, ph, c0, c1 = q; return A * np.exp(-g * t) * np.cos(w * t + ph) + c0 + c1 * t - y
    best = None
    for ph in np.linspace(0, 2 * np.pi, 8, endpoint=False):
        s = least_squares(r, [0.02, 0.011, 2 * np.pi * f0, ph, y.mean(), 0])
        if best is None or s.cost < best.cost: best = s
    if best.x[0] < 0: best.x[0] *= -1; best.x[3] += np.pi
    cov = np.linalg.pinv(best.jac.T @ best.jac) * 2 * best.cost / (len(t) - 6)
    return best.x, np.sqrt(np.diag(cov)), float(np.sqrt(2 * best.cost / len(t)))

def analyse(t, y):
    y0 = np.median(y[:15]); i0 = np.where(np.abs(y - y0) > 0.003)[0][0]
    t, y = t[i0:] - t[i0], y[i0:]
    k = (t > 1.5) & (t < t[-1] - 1.5); t, y = t[k], y[k]
    n = len(y); F = np.abs(np.fft.rfft((y - y.mean()) * np.hanning(n), 16 * n)); fr = np.fft.rfftfreq(16 * n, np.mean(np.diff(t)))
    m = (fr > 1) & (fr < 4); f0 = fr[m][np.argmax(F[m])]
    q, e, res = damped_fit(t - t[0], y, f0)
    h = len(t) // 2
    qe = damped_fit(t[:h] - t[0], y[:h], q[2] / 2 / np.pi)[0]; ql = damped_fit(t[h:] - t[0], y[h:], q[2] / 2 / np.pi)[0]
    return dict(f=q[2] / 2 / np.pi, f_se=e[2] / 2 / np.pi, gamma=q[1] * 1e3, gamma_se=e[1] * 1e3,
                early=qe[1] * 1e3, late=ql[1] * 1e3, A0_cm=q[0] * 100, resid_mm=res * 1e3)

def boot_median(x, B=20000):
    x = np.asarray(x); idx = rng.integers(0, len(x), (B, len(x)))
    return float(np.std(np.median(x[idx], axis=1)))

rows = []
for p in sorted(glob.glob(os.path.join(VID, "VID-*.csv"))):
    name = os.path.basename(p)
    d = np.genfromtxt(p, delimiter=",", skip_header=1); t_even, y = d[:, 0], d[:, 1]
    pts = np.genfromtxt(os.path.join(VID, "frame_times", name), skip_header=1)
    assert len(pts) == len(y), name
    true = analyse(pts, y); naive = analyse(t_even, y)
    rows.append(dict(video=name.replace(".csv", "").replace("VID-20260725-", ""),
                     fps=float((len(pts) - 1) / pts[-1]), frame_dt_sd_ms=float(np.std(np.diff(pts)) * 1e3),
                     f_even_spacing=naive["f"], **true, spring=1 if true["f"] > 1.97 else 2))
for r in rows:
    r["passes_tracking_cut"] = bool(r["resid_mm"] / 10 < RESID_CUT * r["A0_cm"])

st = json.load(open(os.path.join(RES, "final_stats.json")))
daq = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "final_rows.json")))
out = dict(n_videos=len(rows), resid_cut_frac_of_A0=RESID_CUT, videos=rows)
for sp in (1, 2):
    rr = [r for r in rows if r["spring"] == sp]; ok = [r for r in rr if r["passes_tracking_cut"]]
    f = np.array([r["f"] for r in rr]); fn = np.array([r["f_even_spacing"] for r in rr])
    g = np.array([r["gamma"] for r in ok]); el = np.array([r["early"] / r["late"] for r in ok])
    f_daq_nominal = st[f"S{sp}"]["f_true_mean"] * S_HUM          # DAQ frequency on the firmware's timebase
    fmed = float(np.median(f)); fse = boot_median(f)
    fd = np.array([r["f"] for r in daq if r["sp"] == f"S{sp}" and r["R"] < 1e5])   # true-time DAQ frequencies
    daq_rel = float(fd.std(ddof=1) / np.sqrt(len(fd)) / fd.mean())
    out[f"spring{sp}"] = dict(n=len(rr), n_pass=len(ok), passing=[r["video"] for r in ok],
        f_video_median=fmed, f_video_se_boot=fse,
        f_video_mad_hz=float(1.4826 * np.median(np.abs(f - fmed))),
        f_video_spread_pct=float(100 * (f.max() - f.min()) / fmed),
        f_even_spacing_spread_pct=float(100 * (fn.max() - fn.min()) / np.median(fn)),
        f_daq_nominal=f_daq_nominal, s_video=f_daq_nominal / fmed, s_video_se=f_daq_nominal / fmed * float(np.hypot(fse / fmed, daq_rel)),
        daq_f_sd_pct=float(100 * fd.std(ddof=1) / fd.mean()),
        gamma_video_mean=float(g.mean()), gamma_video_sd=float(g.std(ddof=1)), gamma_video_median=float(np.median(g)),
        early_late_ratio_mean=float(el.mean()), early_late_ratio_sd=float(el.std(ddof=1)), n_early_faster=int((el > 1).sum()),
        gamma_emf_envelope=st[f"S{sp}"]["gamma"][0], Q_video=float(np.pi * fmed / (g.mean() * 1e-3)))
w = [1 / out[f"spring{sp}"]["s_video_se"]**2 for sp in (1, 2)]
out["s_video_combined"] = sum(wi * out[f"spring{sp}"]["s_video"] for wi, sp in zip(w, (1, 2))) / sum(w)
out["s_video_combined_se"] = (1 / sum(w))**0.5
out["s_hum"] = S_HUM
json.dump(out, open(os.path.join(RES, "video_analysis.json"), "w"), indent=1)
print(f"{'video':7s} sp   fps  dt_sd(ms) f_even  f_true   gamma(se)     early/late A0(cm) resid(mm) pass")
for r in rows:
    print(f"{r['video']:7s} {r['spring']}  {r['fps']:5.2f}  {r['frame_dt_sd_ms']:5.2f}   {r['f_even_spacing']:.4f} {r['f']:.4f}  {r['gamma']:6.2f}({r['gamma_se']:.2f})  {r['early']/r['late']:6.2f}   {r['A0_cm']:.1f}   {r['resid_mm']:5.2f}   {r['passes_tracking_cut']}")
for sp in (1, 2):
    o = out[f"spring{sp}"]
    print(f"spring {sp}: f_video={o['f_video_median']:.4f}±{o['f_video_se_boot']:.4f} Hz (bootstrap; MAD {o['f_video_mad_hz']:.4f}; spread {o['f_video_spread_pct']:.2f}% vs {o['f_even_spacing_spread_pct']:.2f}% with even spacing)  "
          f"s_video={o['s_video']:.4f}±{o['s_video_se']:.4f} | {o['n_pass']}/{o['n']} pass: gamma={o['gamma_video_mean']:.2f}±{o['gamma_video_sd']:.2f} Q={o['Q_video']:.0f} "
          f"EMF-env {o['gamma_emf_envelope']:.2f} early/late={o['early_late_ratio_mean']:.2f}±{o['early_late_ratio_sd']:.2f} ({o['n_early_faster']}/{o['n_pass']})")
print(f"s (video, combined) = {out['s_video_combined']:.4f} ± {out['s_video_combined_se']:.4f}   vs  s (mains hum) = {S_HUM:.4f}")
