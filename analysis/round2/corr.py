import json,numpy as np
from scipy import stats
d=json.load(open('out/refit.json')); a=json.load(open('out/results.json'))
V={('S1',r['R'],r['run']):r['Vrms_mV'] for r in a['s1']}; V.update({('S2',r['R'],r['run']):r['Vrms_mV'] for r in a['s2']})
for sp in ('S1','S2'):
    rows=[r for r in d if r['sp']==sp and r['R']<1e5]
    v=np.array([V[(sp,r['R'],r['run'])] for r in rows]); A1=np.array([r['A1'] for r in rows]); h=np.array([r['A2']/r['A1'] for r in rows])
    for m in ('g_auth','g_hilb','g_rms','g_nls1','g_nls2','g_early','g_late','curv'):
        g=np.array([r[m] for r in rows]); pr=stats.pearsonr(v,g); sr=stats.spearmanr(v,g)
        loo=[stats.pearsonr(np.delete(v,i),np.delete(g,i))[0] for i in range(len(g))]
        print(sp,m.ljust(8),'pearson r=%.2f p=%.1e  spearman=%.2f p=%.3f  LOO r in [%.2f,%.2f]'%(pr[0],pr[1],sr[0],sr[1],min(loo),max(loo)),
              ' | vs NLS A1: r=%.2f'%stats.pearsonr(A1,g)[0], ' vs A2/A1: r=%.2f'%stats.pearsonr(h,g)[0])
    print(sp,'sd/mean g_auth %.3f g_nls1 %.3f g_hilb %.3f'%tuple(np.std([r[m] for r in rows],ddof=1)/np.mean([r[m] for r in rows]) for m in ('g_auth','g_nls1','g_hilb')))
    for m in ('g_auth','g_hilb','g_rms','g_nls1'):
        g=np.array([r[m] for r in rows]); print('   ',m,'mean %.2f sd %.2f'%(g.mean()*1e3,g.std(ddof=1)*1e3))
    print('   ratio nls2/nls1', np.round(np.array([r['g_nls2']/r['g_nls1'] for r in rows]),2))
    print('   early-late (auth) mean %.2f, n with early>late %d/%d'%(np.mean([r['g_early']-r['g_late'] for r in rows])*1e3,sum(r['g_early']>r['g_late'] for r in rows),len(rows)))
