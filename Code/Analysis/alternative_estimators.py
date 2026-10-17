from common import *
from scipy.optimize import least_squares
from scipy.signal import sosfiltfilt, butter as bt
import json
rng=np.random.default_rng(1)
def linfit(tt,y):
    p,cov=np.polyfit(tt,y,1,cov=True); return -p[0],np.sqrt(cov[0,0]),y-np.polyval(p,tt)
def blockboot(tt,y,L,B=2000):
    p=np.polyfit(tt,y,1); fit=np.polyval(p,tt); res=y-fit; n=len(y); gs=[]
    for _ in range(B):
        idx=np.concatenate([np.arange(s,s+L) for s in rng.integers(0,n-L+1,size=n//L+1)])[:n]
        gs.append(-np.polyfit(tt,fit+res[idx],1)[0])
    return np.std(gs)
def acf1(r): r=r-r.mean(); return np.sum(r[1:]*r[:-1])/np.sum(r*r)
out=[]
for sp,R,s,p in runs():
    t,v,x,fs=prep(p); r=authors_fit(p); f=r['f']
    # replicate author's peaks
    pk,_=find_peaks(np.abs(x),distance=int(0.35*fs/f)); amp=np.abs(x[pk]); keep=amp>0.25*amp.max()
    i0=np.argmax(amp>0.5*amp.max()); sel=(np.arange(len(pk))>=i0)&keep
    tp,ap,sg=t[pk][sel],amp[sel],np.sign(x[pk][sel])
    g0,e0,res=linfit(tp,np.log(ap))
    rho=acf1(res); L=max(2,int(round(2*fs/f/ (np.median(np.diff(pk[sel])) ) * 3)))  # ~3 cycles
    eb=blockboot(tp,np.log(ap),L)
    # pos / neg peaks separately
    gpos=linfit(tp[sg>0],np.log(ap[sg>0]))[0] if (sg>0).sum()>5 else np.nan
    gneg=linfit(tp[sg<0],np.log(ap[sg<0]))[0] if (sg<0).sum()>5 else np.nan
    # curvature: quadratic in log env
    pq,covq=np.polyfit(tp-tp.mean(),np.log(ap),2,cov=True); curv=pq[0]; curve=np.sqrt(covq[0,0])
    # early vs late halves
    mid=(tp[0]+tp[-1])/2; ge,gee,_=linfit(tp[tp<mid],np.log(ap[tp<mid])); gl,gle,_=linfit(tp[tp>=mid],np.log(ap[tp>=mid]))
    ta,te=tp[0],tp[-1]
    # Hilbert of fundamental band
    sos=bt(4,[0.6*f,1.4*f],btype='band',fs=fs,output='sos'); xf=sosfiltfilt(sos,x)
    env=np.abs(hilbert(xf)); m=(t>ta+1)&(t<te-1); ds=int(fs/f)  # one point per cycle for errors
    th,eh=t[m][::ds],np.log(env[m][::ds]); gh,ghe,resh=linfit(th,eh); ebh=blockboot(th,eh,3)
    # full-band hilbert (whole waveform)
    # per-cycle rms
    N=int(round(fs/f)); idx=np.where(m)[0]; starts=np.arange(idx[0],idx[-1]-N,N)
    tr=np.array([t[i+N//2] for i in starts]); rr=np.array([np.sqrt(np.mean(x[i:i+N]**2)) for i in starts])
    grms,grmse,resr=linfit(tr,np.log(rr)); ebr=blockboot(tr,np.log(rr),3)
    # NLS harmonic series with per-harmonic decay
    mm=(t>ta)&(t<te); tt=t[mm][::4]-ta; yy=x[mm][::4]
    def model(q):
        w=2*np.pi*q[0]; y=np.full_like(tt,q[1])
        for k in range(3):
            A,g,ph=q[2+3*k:5+3*k]; y+=A*np.exp(-g*tt)*np.cos((k+1)*w*tt+ph+ (k+1)*q[-1]*tt**2)
        return y
    # init amplitudes from fft
    q0=[f,0]
    for k in range(3):
        c=np.exp(-1j*2*np.pi*(k+1)*f*tt); z=2*np.mean(yy[:int(5/f*fs/4)]*c[:int(5/f*fs/4)])
        q0+= [abs(z),0.018*(k+1),np.angle(z)]
    q0+=[0.0]
    sol=least_squares(lambda q:model(q)-yy,q0,x_scale='jac')
    J=sol.jac; resn=sol.fun; dof=len(yy)-len(q0); s2=np.sum(resn**2)/dof
    cov=np.linalg.pinv(J.T@J)*s2; gn,gne=sol.x[3],np.sqrt(cov[3,3]); g2n=sol.x[6]
    racf=acf1(resn)
    rec=dict(sp=sp,R=R,run=s,f=f,n=len(tp),g_auth=g0,e_auth=e0,rho1=rho,e_boot=eb,gpos=gpos,gneg=gneg,curv=curv,curve=curve,
        g_early=ge,e_early=gee,g_late=gl,e_late=gle,g_hilb=gh,e_hilb=ghe,eb_hilb=ebh,rho_hilb=acf1(resh),g_rms=grms,eb_rms=ebr,
        g_nls1=gn,e_nls1=gne,g_nls2=g2n,nls_rho=racf,A1=abs(sol.x[2]),A2=abs(sol.x[5]),chirp=sol.x[-1])
    out.append(rec)
    print(f"{sp:4s}{R:>9g} {s[:9]:9s} n={len(tp):3d} auth {g0*1e3:6.2f}({e0*1e5:3.0f}) rho1={rho:5.2f} boot={eb*1e5:3.0f} | pos {gpos*1e3:6.2f} neg {gneg*1e3:6.2f} | early {ge*1e3:6.2f}({gee*1e5:.0f}) late {gl*1e3:6.2f}({gle*1e5:.0f}) curv {curv*1e5:6.2f}({curve*1e5:.2f}) | hilb1 {gh*1e3:6.2f}({ebh*1e5:.0f}) rms {grms*1e3:6.2f}({ebr*1e5:.0f}) nls1 {gn*1e3:6.2f}({gne*1e5:.1f}) nls2 {g2n*1e3:6.2f} A2/A1 {abs(sol.x[5])/abs(sol.x[2]):.2f}")
json.dump(out,open(os.path.join(OUT,'refit.json'),'w'),indent=1,default=float)
