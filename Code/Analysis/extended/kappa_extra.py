import numpy as np, glob, os, json, runpy, sys, io, contextlib
from est import REPO, HERE
DR=os.path.join(REPO,'Data','Raw','session_2026-07-23')+'/'; DV=os.path.join(REPO,'Data','Video','session_2026-07-23')+'/'
# release amplitude on 23 July from the displacement reports (first swing)
A=[]
for p in sorted(glob.glob(DV+'track_label_*.csv')):
    d=np.genfromtxt(p,delimiter=',',skip_header=2,usecols=(0,1)); y=d[:,1]; y=y[~np.isnan(y)]; y0=np.median(y[:5]); k=int(np.argmax(np.abs(y-y0)>0.003)); seg=y[k:k+14]; opp=seg.min() if y0>y[k:].mean() else seg.max(); A.append(abs(y0-opp)/2*100)
A=np.array(A); print('23 July first-swing half p2p (cm):',np.round(A,2),'median %.2f'%np.median(A))
ns={}
try: exec(open(os.path.join(HERE,'kappa_recon.py')).read().split("if __name__ != '__main__'")[0], ns)
except SystemExit: pass
recon=ns['recon']; A_rel=float(np.median(A))/100
Ks=[]
for p in sorted(glob.glob(DR+'*.csv')):
    cen,o,h,r0=recon(p,A_rel,g0=0.0495,b=0.0); Ks.append(o['all']*np.sign(np.nanmedian(o['all'])))
Ks=np.array(Ks); mean=np.nanmean(Ks,axis=0); sd=np.nanstd(Ks,axis=0,ddof=1); i0=len(cen)//2; kap=mean/A_rel
shape=Ks/Ks[:,[i0]]
print('23 July: %d runs, kappa at rest %.3f V s/m (run sd %.1f%%), shape sd %.1f%%'%(len(Ks),kap[i0],100*sd[i0]/mean[i0],100*np.nanmedian(np.nanstd(shape,axis=0,ddof=1))))
K=json.load(open('kappa_recon.json')); z1=np.array(K['S1']['z_cm']); k1=np.array(K['S1']['kappa']); g1=~np.isnan(k1)
z3=cen*A_rel*100; g3=~np.isnan(kap)
def mis(d,sc=1.0):
    zz=z3[g3]+d; m=(zz>z1[g1].min())&(zz<z1[g1].max()); return np.sqrt(np.mean((np.interp(zz[m],z1[g1],k1[g1])/(sc*kap[g3][m])-1)**2))
ds=np.linspace(-2,3,501); r=np.array([mis(d) for d in ds]); d0=ds[np.argmin(r)]
print('23 July curve vs 24 July spring-1 curve: best height offset %.2f cm, rms mismatch %.1f%%'%(d0,100*r.min()))
K['Jul23']=dict(A_rel=A_rel,z_cm=z3.tolist(),kappa=kap.tolist(),kappa_sd=(sd/A_rel).tolist(),shift_cm=float(d0),mismatch=float(r.min()),n=len(Ks))
json.dump(K,open('kappa_recon.json','w'),indent=1,default=float)

# --- 23 July session: decay rate, frequency and an independent clock factor (100-read blocks, 1000 us nominal)
from est import load, headline, S_CLOCK
from scipy.optimize import least_squares
G=[];Fn=[]
for p in sorted(glob.glob(DR+'*.csv')):
    t,v=load(p); h=headline(t,v); G.append(h['gamma']*1e3); Fn.append(h['f']*S_CLOCK)
fv=[];gv=[]
for p in sorted(glob.glob(DV+'track_label_*.csv')):
    d=np.genfromtxt(p,delimiter=',',skip_header=2,usecols=(0,1)); d=d[~np.isnan(d).any(axis=1)]; t,y=d[:,0],d[:,1]
    y0=np.median(y[:5]); i0=int(np.argmax(np.abs(y-y0)>0.003)); t=t[i0:]-t[i0]; y=y[i0:]; k=(t>1.0)&(t<t[-1]-1.0); t,y=t[k]-t[k][0],y[k]; n=len(y)
    Fq=np.abs(np.fft.rfft((y-y.mean())*np.hanning(n),16*n)); fr=np.fft.rfftfreq(16*n,np.mean(np.diff(t))); m=(fr>1)&(fr<4); w0=2*np.pi*fr[m][np.argmax(Fq[m])]
    best=None
    for ph in np.linspace(0,2*np.pi,8,endpoint=False):
        s=least_squares(lambda q:q[0]*np.exp(-q[1]*t)*np.cos(q[2]*t+q[3])+q[4]+q[5]*t-y,[np.ptp(y)/2,0.05,w0,ph,y.mean(),0])
        if best is None or s.cost<best.cost: best=s
    fv.append(best.x[2]/2/np.pi); gv.append(best.x[1]*1e3)
sess=dict(n_daq=len(G),gamma_emf_env_mean=float(np.mean(G)),gamma_emf_env_sd=float(np.std(G,ddof=1)),f_nominal_mean=float(np.mean(Fn)),
          n_video=len(fv),f_video_mean=float(np.mean(fv)),f_video_sd=float(np.std(fv,ddof=1)),gamma_video_mean=float(np.mean(gv)),gamma_video_sd=float(np.std(gv,ddof=1)),
          clock_factor=float(np.mean(Fn)/np.mean(fv)),clock_factor_se=float(np.mean(Fn)/np.mean(fv)*np.std(fv,ddof=1)/np.sqrt(len(fv))/np.mean(fv)))
print('23 July session:',json.dumps(sess,indent=1)); json.dump(sess,open('session_0723.json','w'),indent=1)
