"""Forward model: dipole magnet on the axis of a finite multi-turn coil.
kappa(d) = -dPhi/dd per turn, averaged over the winding; emf = N * kappa(z0+z) * zdot (sign convention irrelevant here)."""
import numpy as np
MU0 = 4e-7*np.pi
def kappa_factory(z0, a_in=0.028, h=0.04, w=0.003, na=5, nh=41):
    aa = np.linspace(a_in, a_in+w, na); hh = np.linspace(-h/2, h/2, nh)
    A, H = np.meshgrid(aa, hh, indexing='ij'); A = A.ravel(); H = H.ravel()
    def kappa(z):                       # z = displacement from rest (toward coil negative => d smaller)
        d = (z0 + np.asarray(z))[..., None] + H
        return np.mean(3*MU0*A**2*d/(2*(d*d + A*A)**2.5), axis=-1)   # per turn, per unit dipole moment
    return kappa
def emf_cycle(kappa, A, f, n=4096):
    th = 2*np.pi*np.arange(n)/n; z = A*np.cos(th); zd = -A*2*np.pi*f*np.sin(th)
    return th, kappa(z)*zd
def harm(kappa, A, f, nh=4):
    th, e = emf_cycle(kappa, A, f); return np.array([2*np.mean(e*np.exp(-1j*k*th)) for k in range(1, nh+1)])
