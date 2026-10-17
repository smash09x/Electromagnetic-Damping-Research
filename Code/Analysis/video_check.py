import os
from common import OUT
import json,numpy as np
from scipy import stats
S=1.2613; RC=15.2
rows=json.load(open(os.path.join(OUT,'final_rows.json')))
vid={'S1':{0:11.7,33.6:17.3,81.4:16.1,324:13.3,3180:11.6,9610:11.8},'S2':{0:11.6,33.3:15.7,84.1:13.6,327:14.7,3190:10.5,9670:12.1}}
sv=[];gv=[];ge=[]
for sp in vid:
    for R0,g in vid[sp].items():
        r=[x for x in rows if x['sp']==sp and x['R']==R0][0]; sv.append(r['gamma']*S*1e3/g); gv.append(g); ge.append(r['gamma']*1e3)
sv=np.array(sv); print('implied s from video: mean %.3f sd %.3f sem %.3f; ratio-of-means %.3f'%(sv.mean(),sv.std(ddof=1),sv.std(ddof=1)/np.sqrt(12),np.mean(np.array(ge)*S)/np.mean(gv)))
print('z vs s=1: %.1f ; vs s=1.051 (60Hz): %.1f; vs 1.261: %.1f'%((sv.mean()-1)/(sv.std(ddof=1)/np.sqrt(12)),(sv.mean()-1.051)/(sv.std(ddof=1)/np.sqrt(12)),(sv.mean()-1.261)/(sv.std(ddof=1)/np.sqrt(12))))
print('video mean S1 %.2f S2 %.2f'%(np.mean(list(vid['S1'].values())),np.mean(list(vid['S2'].values()))))
# per-spring video mean / EMF true mean
for sp in vid:
    em=np.mean([x['gamma'] for x in rows if x['sp']==sp and x['R']<1e5])*1e3; print(sp,'video mean/EMF mean all-8 %.3f'%(np.mean(list(vid[sp].values()))/em))
# c sensitivity to A, clock-corrected
s1=[r for r in rows if r['sp']=='S1' and r['R']<1e5]; R=np.array([r['R'] for r in s1]); g=np.array([r['gamma'] for r in s1])
X=np.c_[np.ones(8),1/(RC+R)]; b,*_=np.linalg.lstsq(X,g,rcond=None); res=g-X@b; ce=np.sqrt(res@res/6*np.linalg.inv(X.T@X)[1,1]); c=b[1]
for A in (1.8,2.2,3.0):
    cp=0.03032*(2.2/A)**2; z=(cp-c)/ce; print('A=%.1f cm c_pred=%.4f z=%.2f gauss-eq(t6) %.2f  gem/g=%.2f'%(A,cp,z,stats.norm.isf(stats.t.sf(z,6)),cp/RC/g.mean()))
# pairs bootstrap
rng=np.random.default_rng(0); cs=[]
for _ in range(20000):
    i=rng.integers(0,8,8)
    if len(set(R[i]))<3: continue
    Xi=X[i]; cs.append(np.linalg.lstsq(Xi,g[i],rcond=None)[0][1])
cs=np.array(cs); p=np.mean(cs>=0.03032); print('pairs bootstrap p=%.4f gauss %.2f'%(p,stats.norm.isf(max(p,1e-6))))
# drop each 0 ohm
for k in np.where(R==0)[0]:
    m=np.arange(8)!=k; Xm=X[m]; bm,*_=np.linalg.lstsq(Xm,g[m],rcond=None); rm=g[m]-Xm@bm; cem=np.sqrt(rm@rm/5*np.linalg.inv(Xm.T@Xm)[1,1])
    print('drop',k,'c=%.4f+-%.4f gauss(t5) %.2f'%(bm[1],cem,stats.norm.isf(stats.t.sf((0.03032-bm[1])/cem,5))))
print('c=%.4f+-%.4f'%(c,ce))
