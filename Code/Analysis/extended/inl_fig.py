import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d=np.load('inl_est.npy'); g,mean,C,m,m2=d.T; m=m.astype(bool); m2=m2.astype(bool); B,O,INK,MUT,GRID='#2a78d6','#eb6834','#0b0b0b','#52514e','#e4e3df'
plt.rcParams.update({'font.size':9.5,'axes.edgecolor':MUT,'axes.labelcolor':INK,'xtick.color':MUT,'ytick.color':MUT,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#fcfcfb','axes.facecolor':'#fcfcfb'})
fig,a=plt.subplots(figsize=(6.6,3.5)); x=g*23.647/1000
a.plot(x[m],mean[m],color=B,lw=1.8,label='Spring 1 (8 runs)'); a.plot(x[m2],C[m2],color=O,lw=1.2,label='Spring 2 (8 runs)')
for lv in (-456,54,567): a.axvline(lv*23.647/1000,color=MUT,lw=.8,ls=':')
a.set_xlabel('Input level (mV)'); a.set_ylabel('Level-dependent error (μV)'); a.grid(axis='y',color=GRID,lw=.8); a.set_axisbelow(True); a.legend(frameon=False,fontsize=8.5,loc='lower left')
fig.savefig('adc_inl.png',dpi=170,bbox_inches='tight'); fig.savefig('adc_inl.pdf',bbox_inches='tight')
