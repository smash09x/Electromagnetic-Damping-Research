"""Recompute derived numbers quoted in /root/paper2/main.tex."""
import sys, json, glob, csv, re, subprocess, numpy as np
sys.path.insert(0,'/root/paper/analysis')
from fit_decay import load
SW='/root/paper/reviews/stats_work/'
st=json.load(open(SW+'final_stats.json')); ck=json.load(open('/root/paper/figs/clock.json'))
rows=list(csv.DictReader(open(SW+'final_table.csv')))
rr=json.load(open(SW+'out/final_rows.json'))
g=lambda sp:[float(r['gamma_true']) for r in rows if r['run'].startswith(sp) and float(r['R_ext'])<1e5]
e=lambda sp:[float(r['eps_rms_init_mV']) for r in rows if r['run'].startswith(sp) and float(r['R_ext'])<1e5]
S=ck['s']; m=0.105; A=0.022; Rc=15.2
print('n S1 runs',len(g('spring1/coil1')),'mean g',np.mean(g('spring1/coil1')),'sd',np.std(g('spring1/coil1'),ddof=1))
print('S2 mean/sd',np.mean(g('spring2/coil1')),np.std(g('spring2/coil1'),ddof=1))
print('s=63.067/50',ck['f_hum_mean']/50,'sd/50',ck['f_hum_sd']/50, 'harm 2x',2*ck['f_hum_mean'])
print('631us',500*S,' 12.6us',10*S,' rate deficit 1-1/s',1-1/S,' interval excess s-1',S-1)
eps1=np.mean(e('spring1/coil1')); print('eps S1 mean mV',eps1)
I=eps1*1e-3/1e6; print('I nA',I*1e9,'P nW',I**2*1e6*1e9)
f1,f2=st['S1']['f_true_mean'],st['S2']['f_true_mean']; print('f',f1,f2,'ratio',f1/f2,'swapped pred',np.sqrt(19.438/16.578))
for k in(19.438,16.578): print('static f k',k,np.sqrt(k/m)/2/np.pi)
fp1=np.sqrt(19.438/m)/2/np.pi; fp2=np.sqrt(16.578/m)/2/np.pi
print('below static (swapped): S1 %.1f%%  S2 %.1f%%'%((1-f1/fp1)*100,(1-f2/fp2)*100))
print('unswapped pred ratio',np.sqrt(16.578/19.438))
# mechanical loss
for lab,gam,w in(('corrected',st['S1']['gamma'][0]*1e-3,2*np.pi*f1),('nominal(old)',0.0178,2*np.pi*f1*S)):
    E=0.5*m*w**2*A**2; print('mech loss',lab,'E mJ',E*1e3,'2gE mW',2*gam*E*1e3)
Pm=2*st['S1']['gamma'][0]*1e-3*0.5*m*(2*np.pi*f1)**2*A**2
print('gem as built 1/s',st['S1_cfit']['c_pred']/1e6, 'frac of gamma',st['S1_cfit']['c_pred']/1e6/(st['S1']['gamma'][0]*1e-3))
print('gamma/omega',st['S1']['gamma'][0]*1e-3/(2*np.pi*f1), st['S2']['gamma'][0]*1e-3/(2*np.pi*f2))
print('Q check',np.pi*f1/(st['S1']['gamma'][0]*1e-3))
print('divider',1e6/3.2e6)
h=[x['h21'] for x in rr if x['sp']=='S1' and x['R']<1e5]; h22=[x['h21'] for x in rr if x['run']=='2.2M'][0]
print('release smaller by',1-h22/np.mean(h))
# early/late
for s in('S1','S2'): print(s,'early/late',st[s]['early'][0]/st[s]['late'][0], 'peak/hilbert',st[s]['g_peak'][0]/st[s]['gamma'][0],'rms/hilb',st[s]['g_rms'][0]/st[s]['gamma'][0],
   'nls',st[s]['g_nls'][0]/st[s]['gamma'][0],'phys',st[s]['g_phys'][0]/st[s]['gamma'][0],
   'halfrange',(max(st[s]['gamma'][0],st[s]['g_nls'][0],st[s]['g_phys'][0])-min(st[s]['gamma'][0],st[s]['g_nls'][0],st[s]['g_phys'][0]))/2,
   'fullrange/gamma',(max(st[s]['gamma'][0],st[s]['g_nls'][0],st[s]['g_phys'][0])-min(st[s]['gamma'][0],st[s]['g_nls'][0],st[s]['g_phys'][0]))/st[s]['gamma'][0])
print('clock err in gamma: 1.03% of 11.887 =',0.013/S*st['S1']['gamma'][0], ' with sd runs',np.hypot(0.013,0.0047)/S*st['S1']['gamma'][0])
# peak-overestimate per run
pk=[x['g_peak']/x['gamma'] for x in rr if x['sp'] in('S1','S2') and x['R']<1e5]; print('per-run peak/hilb range',min(pk),max(pk),np.mean(pk))
# coil ratios
c1={'S1':np.mean(e('spring1/coil1')),'S2':np.mean(e('spring2/coil1'))}
c1z={'S1':np.mean([float(r['eps_rms_init_mV']) for r in rows if r['run'].startswith('spring1/coil1/0.0')]),'S2':np.mean([float(r['eps_rms_init_mV']) for r in rows if r['run'].startswith('spring2/coil1/0.0')])}
ep={r['run']:float(r['eps_rms_init_mV']) for r in rows}
for nm,sp,c in(('coil2 S1','S1','spring1/coil2/coil_2'),('coil2 S2','S2','spring2/coil2/coil_2'),('coil3 S1','S1','spring1/coil3/coil_3'),('coil3 S2','S2','spring2/coil3/coil_3')):
    print(nm,'vs all-lowR mean %.3f  vs 0-ohm mean %.3f'%(ep[c]/c1[sp],ep[c]/c1z[sp]))
# data checks
D='/root/electromagnetic-damping-daq/data/'
lens=[];noise=[];steps=[]
for p in sorted(glob.glob(D+'**/*.csv',recursive=True)):
    t,v=load(p); lens.append(len(t))
    if 'coil_1' in p:
        fs=1/np.median(np.diff(t)); n=int(0.3*fs); noise.append(np.std(v[:n]))
    d=np.diff(np.unique(np.round(v,3))); steps.append(np.median(d))
print('lens',set(lens),'dur true s',60000*500e-6*S)
print('coil1 prerelease noise n=%d min %.1f max %.1f median %.1f uV'%(len(noise),min(noise),max(noise),np.median(noise)))
print('step median',np.median(steps),'repo',3.3/4095/35*1e6,'ratio',np.median(steps)/(3.3/4095/35*1e6))
print('cycles in 37.8 s: S1 %.1f S2 %.1f'%(60000*500e-6*S*f1,60000*500e-6*S*f2))
print('noise/signal',48e-6/16e-3)
print('BOM total',2.21+3.64+12.69+7.25+2.63+2.96+3.36+0.23+1.64+3.36+0.45+0.44+0.74+0.99*4)
# hum 2nd harmonic in 2.2M run
p=glob.glob(D+'spring_1/coil_1/Resistance/2.2M/*.csv')[0]; t,v=load(p); fs=1/np.median(np.diff(t))
F=np.abs(np.fft.rfft((v-v.mean())*np.hanning(len(v)),8*len(v))); f=np.fft.rfftfreq(8*len(v),1/fs)
mk=(f>120)&(f<132); print('2.2M 2nd harmonic at',f[mk][np.argmax(F[mk])]); mk=(f>55)&(f<70); print('fund',f[mk][np.argmax(F[mk])])
# word count
txt=subprocess.run(['detex','-n','/root/paper2/main.tex'],capture_output=True,text=True).stdout
print('detex words total',len(txt.split()))
src=open('/root/paper2/main.tex').read()
body=src[src.index(r'\abstract{'):src.index(r'\printbibliography')]
body=re.sub(r'\\todo\{[^}]*\}','',body); b2=subprocess.run(['detex','-n'],input=body,capture_output=True,text=True).stdout
print('abstract..data availability detex words',len(b2.split()))
i=src.index(r'\section{Introduction}'); j=src.index(r'\section{Author Contributions}')
b3=re.sub(r'\\todo\{[^}]*\}','',src[i:j]); print('intro..conclusion words',len(subprocess.run(['detex','-n'],input=b3,capture_output=True,text=True).stdout.split()))
# noise excluding the 2.2M run
nz=[]
for p in sorted(glob.glob(D+'**/*.csv',recursive=True)):
    if 'coil_1' in p and '2.2M' not in p:
        t,v=load(p); n=int(0.3/np.median(np.diff(t))); nz.append(np.std(v[:n]))
print('noise excl 2.2M: n=%d min %.1f max %.1f median %.1f'%(len(nz),min(nz),max(nz),np.median(nz)))
# pre-release rms using window up to release (first |x - median| > 0.2*max)
nz=[]
for p in sorted(glob.glob(D+'**/*.csv',recursive=True)):
    if 'coil_1' in p and '2.2M' not in p:
        t,v=load(p); x=v-np.median(v[:300]); r=np.argmax(np.abs(x)>0.2*np.abs(x).max()); nz.append((np.std(v[:max(r-200,100)]),r))
a=[z[0] for z in nz]; print('prerelease(to release) n=%d min %.1f max %.1f median %.1f'%(len(a),min(a),max(a),np.median(a)),[z[1] for z in nz])
