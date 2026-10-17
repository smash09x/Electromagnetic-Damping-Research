from common import *
import json
from scipy import stats
S=1.2613; RC=15.2; m=0.105; A=0.022
rows=json.load(open(os.path.join(OUT,'final_rows.json'))); out=json.load(open(os.path.join(OUT,'_tmp.json')))
def gref(r,Aref):
    L=np.array(r['loc']); b=np.polyfit(L[:,0],L[:,1],1); return np.polyval(b,Aref)
for Aref in (11000,13000):
    for sp in ('S1','S2'):
        rr=[r for r in rows if r['sp']==sp and r['R']<1e5]; g=np.array([gref(r,Aref) for r in rr])*1e3
        print('common Aref',Aref,sp,'%.2f +- %.2f'%(g.mean(),g.std(ddof=1)))
# --- c fit, clock corrected
s1=[r for r in rows if r['sp']=='S1']
R=np.array([r['R'] for r in s1]); g=np.array([r['gamma'] for r in s1]); sub=R<1e5
eps0=np.mean([r['eps'] for r in s1 if r['R']<1e5])*1e-3; w=2*np.pi*np.mean([r['f'] for r in s1 if r['R']<1e5])
c_pred=eps0**2/(m*w**2*A**2)
def ols(R,g):
    X=np.c_[np.ones_like(R),1/(RC+R)]; b,*_=np.linalg.lstsq(X,g,rcond=None); r=g-X@b; cov=r@r/(len(g)-2)*np.linalg.inv(X.T@X); return b[1],np.sqrt(cov[1,1]),len(g)-2
res={}
for lab,(RR,gg) in {'n8_lt10k':(R[sub],g[sub]),'n9_incl_2M2':(R,g),
    'n7_0ohm_avg':(np.r_[0,R[sub&(R>0)]],np.r_[g[sub&(R==0)].mean(),g[sub&(R>0)]])}.items():
    c,ce,dof=ols(RR,gg)
    d=dict(c=round(c,5),c_err=round(ce,5),dof=dof)
    for fa in (0.0,0.1,0.2):
        sig=np.hypot(ce,2*fa*c_pred); z=(c_pred-c)/sig; p=stats.t.sf(z,dof); d[f'sigmaA_{int(fa*100)}pct']=dict(z=round(z,2),p_one_sided=round(p,4),gauss_equiv=round(stats.norm.isf(p),2))
    # permutation
    gs=gg-c_pred/(RC+RR); cobs=ols(RR,gs)[0]; perm=np.array([ols(RR,np.random.default_rng(k).permutation(gs))[0] for k in range(5000)])
    d['perm_p']=round(np.mean(perm<=cobs),4); d['perm_gauss_equiv']=round(stats.norm.isf(np.mean(perm<=cobs)),2)
    res[lab]=d
for k in ('n8_lt10k',):
    # leave-one-out range
    zs=[]
    for i in range(sub.sum()):
        RR=np.delete(R[sub],i); gg=np.delete(g[sub],i); c,ce,dof=ols(RR,gg); zs.append(stats.norm.isf(stats.t.sf((c_pred-c)/ce,dof)))
    res[k]['loo_gauss_equiv_range']=[round(min(zs),2),round(max(zs),2)]
out['S1_cfit']=dict(model='gamma = gamma0 + c/(Rc+Rext), OLS (equal weights = run-to-run scatter, residual-scaled), Student t',
    c_pred=round(c_pred,5), c_pred_note='energy method, eps_rms first 3 cycles, true omega, A=2.2 cm (no sigma_A)',
    gamma_em_pred_at_Rc_1e3=round(c_pred/RC*1e3,3), gamma_em_frac_of_gamma=round(c_pred/RC/np.mean(g[sub]),3),
    gamma_em_as_built_1e3=c_pred/(1e6+RC)*1e3, **res)
print(json.dumps(out['S1_cfit'],indent=1))
# --- divider
from scipy.signal import butter,filtfilt
r2=[r for r in s1 if r['R']>1e5][0]; lo=[r for r in s1 if r['R']<1e5]
V=np.array([r['eps'] for r in lo]); H=np.array([r['h21'] for r in lo])
# filtered pre-release noise (same filter as eps_rms) for each run
def prenoise(p):
    t,v,x,fs=prep(p); return np.std(x[:int(0.3*fs)])*1e-3
import glob
pM=glob.glob(D+'spring_1/coil_1/Resistance/2.2M/*.csv')[0]; nM=prenoise(pM)
eps_c=np.sqrt(r2['eps']**2-nM**2)
pp=np.polyfit(H,V,1); rH=stats.pearsonr(H,V)[0]; Vexp=np.polyval(pp,r2['h21'])
# residual sd of amplitude prediction
resid=V-np.polyval(pp,H); sdV=resid.std(ddof=2)
ratio_raw=r2['eps']/V.mean(); ratio_amp=r2['eps']/Vexp; ratio_amp_noise=eps_c/Vexp
# also A1 (fundamental) based: ratio of NLS fundamental amplitudes? (not amp-corrected) 
pred=1e6/(1e6+2.2e6+RC)
# error: 6% scatter -> raw; amplitude-corrected: resid sd/Vexp plus extrapolation; resistor tolerances 5% each -> pred +-
pred_lo=0.95e6/(0.95e6+2.31e6); pred_hi=1.05e6/(1.05e6+2.09e6)
e_amp=ratio_amp*np.hypot(sdV/Vexp,0.02)
out['divider_2M2']=dict(predicted=round(pred,4),predicted_range_5pct_resistors=[round(pred_lo,3),round(pred_hi,3)],
   observed_raw=round(ratio_raw,3),observed_raw_err=round(ratio_raw*V.std(ddof=1)/V.mean(),3),
   h21_2M2=round(r2['h21'],3),h21_lowR_range=[round(H.min(),3),round(H.max(),3)],r_eps_vs_h21=round(rH,3),
   eps_expected_mV=round(Vexp,2),ratio_amp_corrected=round(ratio_amp,3),ratio_amp_corrected_err=round(e_amp,3),
   filtered_prerelease_noise_mV=round(nM,3),raw_prerelease_noise_mV=1.433,
   ratio_amp_and_noise_corrected=round(ratio_amp_noise,3),
   note='hum at 63 Hz nominal is removed by the 20 Hz Butterworth used for eps_rms, so the 1.4 mV raw noise contributes only the filtered residual in quadrature; H2/H1 extrapolation outside the low-R range (0.32-0.35)')
print(json.dumps(out['divider_2M2'],indent=1))
json.dump(out,open(os.path.join(RES,'final_stats.json'),'w'),indent=1,default=float)
# --- (c) video
vid={'S1':{0:11.7,33.6:17.3,81.4:16.1,324:13.3,3180:11.6,9610:11.8},'S2':{0:11.6,33.3:15.7,84.1:13.6,327:14.7,3190:10.5,9670:12.1}}
allr=[]
for sp in ('S1','S2'):
    rr=[]
    for R0,gv in vid[sp].items():
        cand=[r for r in rows if r['sp']==sp and r['R']==R0]
        # 0-ohm: which retake? report first (a) and mean
        ge=cand[0]['gamma']*1e3; gmean=np.mean([c['gamma'] for c in cand])*1e3
        rr.append((R0,gv,ge,gmean,gv/ge,cand[0]['g_peak']*S*1e3))
    a=np.array([x[4] for x in rr]); allr+=list(a)
    print(sp,[(x[0],x[1],round(x[2],2),round(x[4],2)) for x in rr])
    print(sp,'ratio video/EMF_true mean %.3f sd %.3f sem %.3f; vs nominal peak %.3f; corr %.2f'%(a.mean(),a.std(ddof=1),a.std(ddof=1)/np.sqrt(len(a)),np.mean([x[1]/x[5] for x in rr]),stats.pearsonr([x[1] for x in rr],[x[2] for x in rr])[0]))
a=np.array(allr); print('ALL mean %.3f sd %.3f sem %.3f n=%d; t vs 1: p=%.3f'%(a.mean(),a.std(ddof=1),a.std(ddof=1)/np.sqrt(len(a)),len(a),stats.ttest_1samp(a,1).pvalue))
print('median',np.median(a))
