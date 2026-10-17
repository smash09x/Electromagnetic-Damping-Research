"""Early vs late half decay rates with the headline estimator (fundamental-band Hilbert envelope, true time)."""
from common import *
from scipy.signal import butter as bt, sosfiltfilt
import json
S=1.2613; out={}
for sp,R,s,p in runs():
    if sp not in ('S1','S2') or R>1e5: continue
    t,v,x,fs=prep(p); t=t*S; f0=authors_fit(p)['f']/S; fsT=fs/S
    xf=sosfiltfilt(bt(4,[0.6*f0,1.4*f0],btype='band',fs=fsT,output='sos'),x); env=np.abs(hilbert(xf))
    pk,_=find_peaks(np.abs(x),distance=int(0.35*fs/(f0*S))); amp=np.abs(x[pk]); i0=np.argmax(amp>0.5*amp.max())
    ta,te=t[pk[i0]]+S,t[-1]-S; ds=int(round(fs/(f0*S))); m=(t>ta)&(t<te); th,eh=t[m][::ds],np.log(env[m][::ds])
    h=len(th)//2; g=lambda a,b:-np.polyfit(a,b,1)[0]*1e3
    out.setdefault(sp,[]).append((g(th,eh),g(th[:h],eh[:h]),g(th[h:],eh[h:])))
res={}
for sp,v in out.items():
    v=np.array(v); r=v[:,1]/v[:,2]
    res[sp]=dict(full=v[:,0].mean(),early=v[:,1].mean(),late=v[:,2].mean(),ratio_mean=r.mean(),ratio_sd=r.std(ddof=1),n_early_faster=int((r>1).sum()),n=len(r))
    print(sp,{k:round(x,3) for k,x in res[sp].items()})
json.dump(res,open(os.path.join(RES,'decay_halves.json'),'w'),indent=1)
