"""Independent clock check and displacement-level damping from the phone-video tracks.

Data/Video/VID-*.csv : time_s, vertical_distance_m (tracked from phone video; time from the
video's own frame clock, verified against ffprobe packet timestamps to <0.1%).
Writes Data/Results/video_analysis.json
"""
import os, glob, json, numpy as np
from scipy.signal import butter, sosfiltfilt, hilbert
from common import RES, ROOT

S_HUM = 1.2613
rows = []
for p in sorted(glob.glob(os.path.join(ROOT, "Data", "Video", "VID-*.csv"))):
    d = np.genfromtxt(p, delimiter=",", skip_header=1); t, y = d[:, 0], d[:, 1]
    dt = np.median(np.diff(t)); fs = 1 / dt
    y0 = np.median(y[:15]); mv = np.where(np.abs(y - y0) > 0.003)[0]; i0 = mv[0] if len(mv) else 0
    tt, yy = t[i0:], y[i0:] - np.mean(y[i0:])
    n = len(yy); F = np.abs(np.fft.rfft(yy * np.hanning(n), 16 * n)); fr = np.fft.rfftfreq(16 * n, dt)
    m = (fr > 1) & (fr < 4); f = fr[m][np.argmax(F[m])]
    sos = butter(2, [0.6 * f, 1.4 * f], "band", fs=fs, output="sos")
    env = np.abs(hilbert(sosfiltfilt(sos, yy)))
    k = (tt > tt[0] + 1.5) & (tt < tt[-1] - 1.5); tk, lk = tt[k], np.log(env[k])
    g = -np.polyfit(tk, lk, 1)[0]
    h = len(tk) // 2
    ge, gl = -np.polyfit(tk[:h], lk[:h], 1)[0], -np.polyfit(tk[h:], lk[h:], 1)[0]
    A0 = float(np.exp(np.polyval(np.polyfit(tk, lk, 1), tk[0])))
    rows.append(dict(video=os.path.basename(p), fps=fs, f=f, gamma=g * 1e3, early=ge * 1e3, late=gl * 1e3, A0_cm=A0 * 100,
                     spring=1 if f > 1.97 else 2))

st = json.load(open(os.path.join(RES, "final_stats.json")))
out = dict(n_videos=len(rows), videos=rows)
for sp in (1, 2):
    rr = [r for r in rows if r["spring"] == sp]
    f = np.array([r["f"] for r in rr]); g = np.array([r["gamma"] for r in rr])
    f_daq_nominal = st[f"S{sp}"]["f_true_mean"] * S_HUM          # frequency on the firmware's timebase
    fmed = float(np.median(f)); fse = float(1.2533 * f.std(ddof=1) / np.sqrt(len(f)))
    out[f"spring{sp}"] = dict(n=len(rr), f_video_median=fmed, f_video_se=fse,
        f_daq_nominal=f_daq_nominal, s_video=f_daq_nominal / fmed, s_video_se=f_daq_nominal * fse / fmed**2,
        gamma_video_mean=float(g.mean()), gamma_video_sd=float(g.std(ddof=1)),
        gamma_video_median=float(np.median(g)),
        early_late_ratio_mean=float(np.mean([r["early"] / r["late"] for r in rr])),
        early_late_ratio_sd=float(np.std([r["early"] / r["late"] for r in rr], ddof=1)),
        gamma_emf_envelope=st[f"S{sp}"]["gamma"][0])
w = [1 / out[f"spring{sp}"]["s_video_se"]**2 for sp in (1, 2)]
out["s_video_combined"] = sum(wi * out[f"spring{sp}"]["s_video"] for wi, sp in zip(w, (1, 2))) / sum(w)
out["s_video_combined_se"] = (1 / sum(w))**0.5
out["s_hum"] = S_HUM
json.dump(out, open(os.path.join(RES, "video_analysis.json"), "w"), indent=1)
for sp in (1, 2):
    o = out[f"spring{sp}"]
    print(f"spring {sp}: n={o['n']} f_video={o['f_video_median']:.4f}±{o['f_video_se']:.4f} Hz  s_video={o['s_video']:.4f}±{o['s_video_se']:.4f}  "
          f"gamma_video={o['gamma_video_mean']:.2f}±{o['gamma_video_sd']:.2f} (median {o['gamma_video_median']:.2f})  EMF-env {o['gamma_emf_envelope']:.2f}  early/late={o['early_late_ratio_mean']:.2f}±{o['early_late_ratio_sd']:.2f}")
print(f"s (video, combined) = {out['s_video_combined']:.4f} ± {out['s_video_combined_se']:.4f}   vs  s (mains hum) = {S_HUM}")
