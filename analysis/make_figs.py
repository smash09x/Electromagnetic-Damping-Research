import sys, glob, json, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import butter, filtfilt
sys.path.insert(0, sys.argv[1]); from fit_decay import fit, load
root, out = sys.argv[2], sys.argv[3]
plt.rcParams.update({"font.family":"serif","font.size":9,"axes.spines.top":False,"axes.spines.right":False,
  "axes.edgecolor":"#555","axes.labelcolor":"#222","xtick.color":"#555","ytick.color":"#555","axes.grid":True,
  "grid.color":"#e3e3e3","grid.linewidth":0.6,"legend.frameon":False,"savefig.bbox":"tight"})
C1, C2, GR = "#2a78d6", "#eb6834", "#777"
RC = 15.2
S1 = {0:["0.0/Retake 1","0.0/Retake 2"],33.6:["33.6"],81.4:["81.4"],324:["324"],1051:["1051"],3180:["3.18k"],9610:["9.61k"],2.2e6:["2.2M"]}
S2 = {0:["0.0","0.0/Retake"],33.3:["33.3"],84.1:["84.1"],327:["327"],997:["997"],3190:["3.19k"],9670:["9.67k"]}
def collect(base, d):
    rows=[]
    for R, subs in d.items():
        for s in subs:
            p=glob.glob(f"{root}/data/{base}/{s}/*.csv")[0]; r=fit(p)
            # rms EMF over first 3 cycles
            t,v=load(p); fs=1/np.median(np.diff(t)); b,a=butter(4,20/(fs/2)); v=filtfilt(b,a,v)
            v-=np.median(v[:int(0.3*fs)]); i0=np.argmax(np.abs(v)>0.5*np.abs(v).max())
            vr=np.sqrt(np.mean(v[i0:i0+int(3/r['f']*fs)]**2))*1e-3
            rows.append(dict(R=R, run=s, gamma=r['gamma'], gerr=r['gerr'], f=r['f'], Q=r['Q'], Vrms_mV=vr, r2=r['r2']))
    return rows
s1=collect("spring_1/coil_1/Resistance",S1); s2=collect("spring_2/coil_1",S2)
coils={}
for sp in ("spring_1","spring_2"):
    for c in ("coil_2","coil_3"):
        p=glob.glob(f"{root}/data/{sp}/{c}/*.csv")[0]; r=fit(p)
        t,v=load(p); fs=1/np.median(np.diff(t)); b,a=butter(4,20/(fs/2)); v=filtfilt(b,a,v)
        v-=np.median(v[:int(0.3*fs)]); i0=np.argmax(np.abs(v)>0.5*np.abs(v).max())
        coils[f"{sp}/{c}"]=dict(gamma=r['gamma'],gerr=r['gerr'],Q=r['Q'],f=r['f'],Vrms_mV=np.sqrt(np.mean(v[i0:i0+int(3/r['f']*fs)]**2))*1e-3)
json.dump(dict(s1=s1,s2=s2,coils=coils),open(f"{out}/results.json","w"),indent=1)

m, A = 0.105, 0.022
w1 = 2*np.pi*np.mean([r['f'] for r in s1])
vr0 = np.mean([r['Vrms_mV'] for r in s1 if r['R']<1e5])*1e-3
c_pred = vr0**2/(m*w1**2*A**2)   # gamma_em*R_loop  [ohm/s]
stats={}
for name, rows in (("S1",[r for r in s1 if r['R']<1e5]),("S2",s2)):
    g=np.array([r['gamma'] for r in rows]); e=np.array([r['gerr'] for r in rows]); R=np.array([r['R'] for r in rows])
    f=lambda R,g0,c: g0+c/(RC+R)
    (g0,c),cov=curve_fit(f,R,g,p0=[g.mean(),0],sigma=np.full_like(g,g.std(ddof=1)),absolute_sigma=True)
    stats[name]=dict(mean=g.mean(),sd=g.std(ddof=1),n=len(g),g0=g0,c=c,cerr=np.sqrt(cov[1,1]),
                     b_mean=2*m*g.mean(), b_sd=2*m*g.std(ddof=1), Q=np.mean([r['Q'] for r in rows]), Qsd=np.std([r['Q'] for r in rows],ddof=1))
stats["c_pred"]=c_pred; stats["gem_pred_RC"]=c_pred/RC; stats["gem_actual"]=c_pred/(1e6+RC)
nonopen=[r['Vrms_mV'] for r in s1 if r['R']<1e5]; op=[r['Vrms_mV'] for r in s1 if r['R']>1e5][0]
stats["V_ratio_2M2"]=op/np.mean(nonopen); stats["V_ratio_pred"]=1e6/(1e6+2.2e6+RC); stats["V_ratio_sd"]=np.std(nonopen,ddof=1)/np.mean(nonopen)
json.dump(stats,open(f"{out}/stats.json","w"),indent=1); print(json.dumps(stats,indent=1))

# Fig: gamma vs R
fig,ax=plt.subplots(figsize=(3.4,2.5))
for rows,col,mk,lab in ((s1,C1,"o","Spring 1"),(s2,C2,"s","Spring 2")):
    R=np.array([r['R'] for r in rows])+RC; g=np.array([r['gamma'] for r in rows])*1e3; e=np.array([r['gerr'] for r in rows])*1e3
    ax.errorbar(R,g,yerr=e,fmt=mk,ms=4.5,color=col,mec="white",mew=0.6,elinewidth=1,capsize=0,label=lab)
Rg=np.logspace(np.log10(RC),6.6,200)
g0=stats["S1"]["mean"]-0
ax.plot(Rg,(stats["S1"]["g0"]+c_pred/Rg)*1e3,"--",color=GR,lw=1.2,label="Spring 1 prediction,\nloop closed via $R_c+R_{ext}$")
ax.set_xscale("log"); ax.set_xlabel(r"Coil-side series resistance $R_c+R_{\rm ext}$ ($\Omega$)"); ax.set_ylabel(r"Decay rate $\gamma$ ($10^{-3}$ s$^{-1}$)")
ax.legend(fontsize=7,loc="upper right"); ax.set_ylim(14,27)
fig.savefig(f"{out}/gamma_vs_R.pdf"); fig.savefig(f"{out}/gamma_vs_R.png",dpi=200)

# Fig: example trace
p=glob.glob(f"{root}/data/spring_1/coil_1/Resistance/0.0/Retake 1/*.csv")[0]
t,v=load(p); fs=1/np.median(np.diff(t)); b,a=butter(4,20/(fs/2)); vf=filtfilt(b,a,v); vf-=np.median(vf[:int(0.3*fs)])
r=fit(p); i0=np.argmax(np.abs(vf)>0.5*np.abs(vf).max()); t0=t[i0]
fig,ax=plt.subplots(2,1,figsize=(3.4,3.4),gridspec_kw=dict(height_ratios=[2,1.2]))
ax[0].plot(t,vf*1e-3,color=C1,lw=0.35); env=np.abs(vf[i0:i0+int(2*fs)]).max()*1e-3
tt=np.linspace(t0,t[-1],200); ax[0].plot(tt,env*np.exp(-r['gamma']*(tt-t0)),color="#222",lw=1); ax[0].plot(tt,-env*np.exp(-r['gamma']*(tt-t0)),color="#222",lw=1,label=rf"$V_0e^{{-\gamma t}}$, $\gamma$={r['gamma']*1e3:.1f}$\times10^{{-3}}$ s$^{{-1}}$")
ax[0].set_ylabel("Coil EMF (mV)"); ax[0].set_xlabel("Time (s)"); ax[0].legend(fontsize=7,loc="upper right")
z=(t>t0+5)&(t<t0+6.2); ax[1].plot(t[z]-t0-5,v[z]*1e-3,color="#999",lw=1.6,label="raw (decimated 2 kS/s)"); ax[1].plot(t[z]-t0-5,vf[z]*1e-3+np.median(v[:600])*1e-3,color=C1,lw=1,label="Butterworth, 20 Hz")
ax[1].set_xlabel("Time within window (s)"); ax[1].set_ylabel("EMF (mV)"); ax[1].legend(fontsize=6.5,loc="lower center",bbox_to_anchor=(0.5,1.0),ncol=2)
fig.tight_layout(); fig.savefig(f"{out}/trace.pdf"); fig.savefig(f"{out}/trace.png",dpi=200)

# Fig: gamma vs initial EMF amplitude (amplitude-dependent damping)
from scipy.stats import pearsonr
fig,ax=plt.subplots(figsize=(3.4,2.4))
for rows,col,mk,lab in ((s1,C1,"o","Spring 1"),(s2,C2,"s","Spring 2")):
    rows=[r for r in rows if r['R']<1e5]
    v=np.array([r['Vrms_mV'] for r in rows]); g=np.array([r['gamma'] for r in rows])*1e3
    rr,pp=pearsonr(v,g); p=np.polyfit(v,g,1); xs=np.linspace(v.min(),v.max(),10)
    ax.plot(v,g,mk,ms=4.5,color=col,mec="white",mew=0.6,label=f"{lab} ($r$ = {rr:.2f})")
    ax.plot(xs,np.polyval(p,xs),color=col,lw=1,alpha=0.7)
ax.set_xlabel("Initial EMF amplitude, rms of first 3 cycles (mV)"); ax.set_ylabel(r"$\gamma$ ($10^{-3}$ s$^{-1}$)"); ax.legend(fontsize=7)
fig.savefig(f"{out}/gamma_vs_amp.pdf"); fig.savefig(f"{out}/gamma_vs_amp.png",dpi=200)
