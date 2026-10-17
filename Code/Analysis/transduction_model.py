# Physical model: z = A(t) cos(theta(t)), emf = (k0+k1 z+k2 z^2+k3 z^3) * zdot + offset
# A(t): linear damping (beta=0) or amplitude-dependent dA/dt = -(g0 + beta*A) A  (A normalised to 1 at t=0)
from common import *
from scipy.optimize import least_squares
import json
def basis(q,tt,amp_dep):
    g0,w,ph,dw=q[0],q[1],q[2],q[3]; beta=q[4] if amp_dep else 0.0
    if amp_dep and abs(beta)>1e-9:
        e=np.exp(-g0*tt); A=g0*e/(g0+beta*(1-e)); dA=-(g0+beta*A)*A
    else:
        A=np.exp(-g0*tt); dA=-g0*A
    th=w*tt+0.5*dw*tt**2+ph; z=A*np.cos(th); zd=dA*np.cos(th)-A*(w+dw*tt)*np.sin(th)
    return np.c_[zd, z*zd, z*z*zd, z**3*zd, np.ones_like(tt)]
def resid(q,tt,yy,amp_dep):
    B=basis(q,tt,amp_dep); c,*_=np.linalg.lstsq(B,yy,rcond=None); return B@c-yy
out=[]
for sp,R,s,p in runs():
    t,v,x,fs=prep(p); r=authors_fit(p); f=r['f']
    pk,_=find_peaks(np.abs(x),distance=int(0.35*fs/f)); amp=np.abs(x[pk]); i0=np.argmax(amp>0.5*amp.max())
    ta=t[pk[i0]]; mm=(t>ta)&(t<t[-1]-0.2); tt=t[mm][::4]-ta; yy=x[mm][::4]
    best=None
    for ph0 in np.linspace(0,2*np.pi,8,endpoint=False):
        sol=least_squares(resid,[0.016,2*np.pi*f,ph0,0.0],args=(tt,yy,False),x_scale=[0.01,0.1,1,0.001])
        if best is None or sol.cost<best.cost: best=sol
    q=best.x; dof=len(yy)-9; s2=2*best.cost/dof; J=best.jac; cov=np.linalg.pinv(J.T@J)*s2
    sol2=least_squares(resid,list(q)+[0.0],args=(tt,yy,True),x_scale=[0.01,0.1,1,0.001,0.01])
    J2=sol2.jac; cov2=np.linalg.pinv(J2.T@J2)*(2*sol2.cost/(dof-1))
    res=best.fun; r1=np.corrcoef(res[1:],res[:-1])[0,1]
    # effective SE inflation for AR(1) residuals at this sampling (Bartlett-ish on 1-cycle blocks)
    # block bootstrap over cycles of residuals (refit only gamma linear-model quickly: use wild-block on residual)
    rng=np.random.default_rng(0); N=int(round(fs/4/f))*3; gs=[]
    fitv=yy+res
    for b in range(60):
        nb=len(yy)//N+1; idx=np.concatenate([np.arange(st,st+N) for st in rng.integers(0,len(yy)-N,nb)])[:len(yy)]
        sb=least_squares(resid,q,args=(tt,fitv-res[idx],False),x_scale=[0.01,0.1,1,0.001]); gs.append(sb.x[0])
    rec=dict(sp=sp,R=R,run=s,g_phys=q[0],e_phys=np.sqrt(cov[0,0]),eb_phys=np.std(gs),rho_res=r1,
             g0_ad=sol2.x[0],beta=sol2.x[4],ebeta=np.sqrt(cov2[4,4]),rms_res=np.sqrt(s2),dchi=(best.cost-sol2.cost)/(sol2.cost/(dof-1)))
    out.append(rec)
    print(f"{sp:4s}{R:>9g} {s[:9]:9s} g_phys {q[0]*1e3:6.2f} (SE {rec['e_phys']*1e5:.1f}, blockboot {rec['eb_phys']*1e5:.1f}, rho1 {r1:.2f}) | ampdep: g0 {sol2.x[0]*1e3:6.2f} beta {sol2.x[4]*1e3:6.2f}+-{rec['ebeta']*1e3:.2f}  dchi2/s2={rec['dchi']:.0f}  resid rms {np.sqrt(s2):.0f}uV")
json.dump(out,open(os.path.join(OUT,'phys.json'),'w'),indent=1,default=float)
