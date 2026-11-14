"""Simulated experiment: motion -> coil EMF -> DAQ (as built) -> repo estimators."""
import numpy as np
from model import kappa_factory, harm
from scipy.optimize import brentq, least_squares

def envelope(t, g0, beta):
    """Normalised amplitude with dA/dt = -(g0 + beta*A) A, A(0)=1."""
    e = np.exp(-g0*t)
    return g0*e/(g0 + beta*(1-e)) if abs(beta) > 1e-12 else e

def solve_truth(gamma_mean, early_late, T=40.0):
    """(g0, beta) whose log-envelope fit over a T-second window gives the video mean gamma and early/late ratio."""
    t = np.linspace(0, T, 2000)
    def stats(q):
        y = np.log(envelope(t, q[0], q[1])); h = len(t)//2
        g = -np.polyfit(t, y, 1)[0]; ge = -np.polyfit(t[:h], y[:h], 1)[0]; gl = -np.polyfit(t[h:], y[h:], 1)[0]
        return [g/gamma_mean - 1, ge/gl/early_late - 1]
    return least_squares(stats, [gamma_mean*0.8, gamma_mean*0.3], x_scale=[1e-3, 1e-3]).x

def motion(t, A0, f, g0, beta, t_rel):
    """Held at +A0 until t_rel, then released from rest. Quasi-harmonic (gamma/omega ~ 1e-3)."""
    tt = np.clip(t - t_rel, 0, None); A = A0*envelope(tt, g0, beta); w = 2*np.pi*f
    dA = -(g0 + beta*A/A0)*A
    z = A*np.cos(w*tt); zd = np.where(t > t_rel, dA*np.cos(w*tt) - A*w*np.sin(w*tt), 0.0)
    return z, zd

def daq(emf_fn, rng, T_reads=12.613e-6, n_store=60000, osf=50, gain=35.0, vref=1.65, vs=3.3,
        offset=700e-6, sigma_lsb=5.0, hum=7e-6, f_mains=50.0, quantise=True, int_div=True, true_time=False, inl_steps=None):
    """As-built firmware: one read per T_reads, blocks of osf summed, integer-divided, stamped i*500 us."""
    n = n_store*osf; out = np.empty(n_store); lsb = vs/4096
    if sigma_lsb == 0 and not quantise and not int_div:      # ideal path: block mean of a smooth signal = value at block centre
        tc = (np.arange(n_store)*osf + (osf-1)/2)*T_reads
        out = (vref + gain*(emf_fn(tc) + offset + hum*np.sin(2*np.pi*f_mains*tc)))/lsb
        volts = (out/4095.0*vs - vref)/gain*1e6
        return (np.arange(n_store)*osf*T_reads if true_time else np.arange(n_store)*500e-6), volts
    chunk = 2000*osf
    for i0 in range(0, n, chunk):
        t = (i0 + np.arange(min(chunk, n - i0)))*T_reads
        v = vref + gain*(emf_fn(t) + offset + hum*np.sin(2*np.pi*f_mains*t)) + sigma_lsb*lsb*rng.standard_normal(len(t))
        code = np.clip(np.floor(v/lsb), 0, 4095) if quantise else v/lsb
        if inl_steps:                                  # RP2040-E11-like wide codes: readings above each level come out low
            for lev, st in inl_steps: code = code - st*(code > lev)
        s = code.reshape(-1, osf).sum(axis=1)
        out[i0//osf:i0//osf + len(s)] = np.floor(s/osf) if int_div else s/osf
    volts = (out/4095.0*vs - vref)/gain*1e6            # firmware's conversion, uV
    idx = np.arange(n_store)
    t_out = idx*osf*T_reads if true_time else idx*500e-6
    return t_out, volts

def hum_clock(t_nom, v, lo=60, hi=66):
    """Clock factor from the mains line, as in clock_calibration.py: peak of the spectrum in 60-66 Hz nominal."""
    fs = 1/np.median(np.diff(t_nom)); x = (v - v.mean())*np.hanning(len(v))
    F = np.abs(np.fft.rfft(x, 8*len(x))); fr = np.fft.rfftfreq(8*len(x), 1/fs); m = (fr > lo) & (fr < hi)
    return fr[m][np.argmax(F[m])]/50.0

def kappa_table(z0, zmax=0.045, n=4001):
    """Interpolated coupling (fast): tabulate kappa on [-zmax, zmax]."""
    k = kappa_factory(z0); zz = np.linspace(-zmax, zmax, n); kk = k(zz)
    return lambda z: np.interp(z, zz, kk)
