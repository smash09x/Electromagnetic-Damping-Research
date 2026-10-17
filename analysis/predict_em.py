"""Predict EM damping rate if coil loop were closed through R (energy method):
gamma_em = <EMF^2>_cycle / (R * m * omega^2 * A^2), using open-circuit EMF measured
by the high-impedance DAQ and oscillation amplitude A at the same epoch."""
import sys, numpy as np
sys.path.insert(0, sys.argv[1]); from fit_decay import load
from scipy.signal import butter, filtfilt
root=sys.argv[2]; m=0.105; A=0.022  # m, kg ; A from Tracker position traces at release
runs={"S1C1 (15.2 ohm)":"spring_1/coil_1/Resistance/0.0/Retake 1","S1C2":"spring_1/coil_2","S1C3":"spring_1/coil_3",
      "S1C1 2.2M":"spring_1/coil_1/Resistance/2.2M"}
for k,d in runs.items():
    import glob; p=glob.glob(f"{root}/data/{d}/*.csv")[0]
    t,v=load(p); fs=1/np.median(np.diff(t)); b,a=butter(4,20/(fs/2)); v=filtfilt(b,a,v)*1e-6
    v-=np.median(v[:int(0.3*fs)]); i0=np.argmax(np.abs(v)>0.5*np.abs(v).max())
    f=2.633; seg=v[i0:i0+int(3/f*fs)]  # first 3 cycles
    ms=np.mean(seg**2); w=2*np.pi*f
    for R in (15.2, 15.2+9610, 1e6+15.2):
        g=ms/(R*m*w**2*A**2)
        print(f"{k:16s} Vrms={np.sqrt(ms)*1e3:6.2f} mV  R={R:>10.1f}  gamma_em={g:.3e} s^-1  b_em={2*m*g:.3e} kg/s  frac_of_0.0177={g/0.0177:.1%}")
