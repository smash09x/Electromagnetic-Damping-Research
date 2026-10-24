"""Per-file frame-clock check of the phone videos with ffprobe.

Usage:  python check_video_clocks.py <folder with the original VID-*.mp4 files>
        (the ~10 MB videos are not in the repository; their frame times are, in Data/Video/frame_times/)

For every video it
  * reads the presentation time of every frame (ffprobe -show_entries frame=pts_time),
  * writes Data/Video/frame_times/<name>.csv (frame times relative to the first frame),
  * checks that the tracking CSV has one row per frame and spans the same duration,
  * reports the spread of frame intervals: the WhatsApp copies have a variable frame rate
    (intervals of ~33 and ~36 ms mixed), which is why the even spacing assumed by the tracking CSVs
    puts some tracks 0.7-2.9 % off in frequency. video_analysis.py uses the true frame times.
Writes Data/Results/video_clock_check.json. Needs ffprobe (FFmpeg) on the PATH.
"""
import os, sys, glob, json, subprocess, numpy as np
from common import ROOT, RES

src = sys.argv[1] if len(sys.argv) > 1 else None
VID = os.path.join(ROOT, "Data", "Video"); FT = os.path.join(VID, "frame_times"); os.makedirs(FT, exist_ok=True)
if not src or not os.path.isdir(src):
    sys.exit("give the folder holding the original VID-*.mp4 files; frame times already in Data/Video/frame_times/ are used otherwise")
rows = []
for csvp in sorted(glob.glob(os.path.join(VID, "VID-*.csv"))):
    name = os.path.basename(csvp)[:-4]; mp4 = os.path.join(src, name + ".mp4")
    if not os.path.exists(mp4): print("missing", mp4); continue
    meta = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
        "stream=avg_frame_rate,r_frame_rate,nb_frames,duration", "-of", "json", mp4], capture_output=True, text=True, check=True).stdout)["streams"][0]
    pts = np.array([float(x) for x in subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
        "frame=pts_time", "-of", "csv=p=0", mp4], capture_output=True, text=True, check=True).stdout.split() if x not in ("", "N/A")])
    pts = np.sort(pts) - pts.min()
    with open(os.path.join(FT, name + ".csv"), "w") as fh:
        fh.write("pts_time_s\n" + "\n".join(f"{x:.6f}" for x in pts) + "\n")
    trk = np.genfromtxt(csvp, delimiter=",", skip_header=1); dt = np.diff(pts)
    num, den = (int(x) for x in meta["avg_frame_rate"].split("/"))
    rows.append(dict(video=name, frames=len(pts), csv_rows=len(trk), rows_match=len(pts) == len(trk),
        avg_fps_metadata=num / den, fps_from_pts=(len(pts) - 1) / pts[-1], duration_csv_s=float(trk[-1, 0]), duration_pts_s=float(pts[-1]),
        duration_agree_pct=float(100 * (trk[-1, 0] / pts[-1] - 1)), frame_dt_min_ms=float(dt.min() * 1e3),
        frame_dt_max_ms=float(dt.max() * 1e3), frame_dt_sd_ms=float(dt.std() * 1e3)))
    r = rows[-1]
    print(f"{name}: {r['frames']} frames (csv {r['csv_rows']}), {r['avg_fps_metadata']:.2f} fps, duration agree {r['duration_agree_pct']:+.2f}%, "
          f"frame interval {r['frame_dt_min_ms']:.1f}-{r['frame_dt_max_ms']:.1f} ms (sd {r['frame_dt_sd_ms']:.2f})")
json.dump(rows, open(os.path.join(RES, "video_clock_check.json"), "w"), indent=1)
