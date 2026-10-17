import json,numpy as np, itertools
from scipy.optimize import curve_fit
from scipy import stats
d=json.load(open('out/refit.json')); RC=15.2
c_pred=0.01895
def fitc(R,g,sig=None,abs_sig=False):
    X=np.c_[np.ones_like(R),1/(RC+R)]
    if sig is None:
        beta,res,_,_=np.linalg.lstsq(X,g,rcond=None); r=g-X@beta; s2=r@r/(len(g)-2)
        cov=s2*np.linalg.inv(X.T@X); return beta[1],np.sqrt(cov[1,1]),len(g)-2
    W=np.diag(1/sig**2); cov=np.linalg.inv(X.T@W@X); beta=cov@X.T@W@g
    if not abs_sig:
        r=g-X@beta; cov*= (r@W@r)/(len(g)-2)
    return beta[1],np.sqrt(cov[1,1]),len(g)-2
def report(name,R,g,e=None):
    out=[]
    c,ce,dof=fitc(R,g); z=(c_pred-c)/ce; p1=stats.t.sf(z,dof); out.append(('unweighted,resid-scaled',c,ce,z,p1))
    c2,ce2,_=fitc(R,g,np.full_like(g,g.std(ddof=1)),True); z2=(c_pred-c2)/ce2; out.append(('paper: sigma=sd(g),absolute',c2,ce2,z2,stats.t.sf(z2,dof)))
    if e is not None:
        c3,ce3,_=fitc(R,g,e,True); z3=(c_pred-c3)/ce3; out.append(('fit SE weights, absolute',c3,ce3,z3,stats.norm.sf(z3)))
        c4,ce4,_=fitc(R,g,e,False); out.append(('fit SE weights, scaled',c4,ce4,(c_pred-c4)/ce4,stats.t.sf((c_pred-c4)/ce4,dof)))
    # pairs bootstrap
    rng=np.random.default_rng(0); cs=[]
    n=len(g)
    for _ in range(20000):
        i=rng.integers(0,n,n)
        if len(set(R[i]))<3 or (1/(RC+R[i])).std()<1e-4: continue
        cs.append(fitc(R[i],g[i])[0])
    cs=np.array(cs); out.append(('pairs bootstrap',np.median(cs),cs.std(),(c_pred-np.median(cs))/cs.std(),np.mean(cs>=c_pred)))
    # permutation test of slope vs predicted: shift model g - c_pred/(RC+R) has zero slope?
    gs=g-c_pred/(RC+R); cobs=fitc(R,gs)[0]
    perm=[fitc(R,np.random.default_rng(k).permutation(gs))[0] for k in range(5000)]
    out.append(('permutation (H0: c=c_pred)',cobs+c_pred,np.nan,np.nan,np.mean(np.array(perm)<=cobs)))
    print('==',name,'n=',len(g))
    for o in out: print('  %-30s c=%+.4f +/- %.4f  z=%.2f  p(one-sided)=%.4f  [gauss-eq %.2f sig]'%(o[0],o[1],o[2],o[3],o[4],stats.norm.isf(max(o[4],1e-12))))
for meth,ek in (('g_auth','e_auth'),('g_hilb','eb_hilb'),('g_rms','eb_rms'),('g_nls1','e_nls1')):
    s1=[r for r in d if r['sp']=='S1']
    R=np.array([r['R'] for r in s1]); g=np.array([r[meth] for r in s1]); e=np.array([r[ek] for r in s1])
    sub=R<1e5
    print('\n######## method',meth)
    report('S1 <10k (paper)',R[sub],g[sub],e[sub])
    report('S1 incl 2.2M',R,g,e)
    # mean of 0 ohm retakes
    m0=(R==0)&sub; Rm=np.r_[0,R[sub&~m0]]; gm=np.r_[g[m0].mean(),g[sub&~m0]]
    report('S1 0-ohm averaged (n=7)',Rm,gm)
    # drop each 0 ohm
    for k in np.where(m0)[0]:
        keep=sub.copy(); keep[k]=False; report('S1 drop %s'%s1[k]['run'],R[keep],g[keep],e[keep])
