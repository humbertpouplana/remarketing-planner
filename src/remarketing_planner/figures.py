"""Regenerate every figure of the paper from results/results.json.

Run:  python -m remarketing_planner.figures
"""
import json
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'paper' / 'fig'
D = json.load(open(ROOT / 'results' / 'results.json'))
B,G,A,Rd,Gy,Pu='#2f6fe0','#12905a','#c47d0c','#c8372f','#6d7690','#7c5ce0'
plt.rcParams.update({'font.size':8.5,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.25,'grid.linewidth':.5,'figure.dpi':150,'savefig.bbox':'tight','font.family':'DejaVu Sans','legend.frameon':False})
OUT.mkdir(parents=True, exist_ok=True)
def sv(n): plt.savefig(OUT / f'{n}.pdf'); plt.close()
# ================= P3
T=D['p3']['types']; ap=T['applied']['rows']
def xp(t):
    for a,b,x0,x1 in [(0,1,0,.35),(1,7,.35,.6),(7,30,.6,.8),(30,180,.8,1)]:
        if t<=b: return x0+(x1-x0)*(max(t,a)-a)/(b-a)
    return 1
fig,ax=plt.subplots(figsize=(6.6,2.4))
for r in ap: ax.scatter(xp(r['t']),1 if r['ch']=='e' else 0,s=22,color=B if r['ch']=='e' else G,zorder=3)
ax.axvspan(0,.35,color=A,alpha=.12); ax.set_yticks([0,1]); ax.set_yticklabels(['SMS','Email']); tk=[0,.25,1,3,7,14,30,60,90,180]; ax.set_xticks([xp(t) for t in tk]); ax.set_xticklabels(['0','6h','24h','3d','7d','14d','30d','60d','90d','180d']); ax.set_ylim(-.6,1.6); ax.grid(axis='x',alpha=.25); ax.grid(axis='y',alpha=0); ax.set_xlabel('Time since entering the flow (piecewise-linear axis)'); sv('p3_timeline')
edges=[(.25,'0-6h'),(1,'6-24h'),(3,'1-3d'),(7,'3-7d'),(14,'7-14d'),(30,'14-30d'),(60,'30-60d'),(90,'60-90d'),(180,'90-180d')]
def bk(t):
    for i,(e,_) in enumerate(edges):
        if t<=e: return i
    return len(edges)-1
ce=[0]*9; cs=[0]*9
for r in ap:
    (ce if r['ch']=='e' else cs)[bk(r['t'])]+=1
fig,ax=plt.subplots(figsize=(6.4,2.8)); ax.bar([l for _,l in edges],ce,color=B,label='Email'); ax.bar([l for _,l in edges],cs,bottom=ce,color=G,label='SMS'); ax.set_ylabel('Touches per lead'); ax.legend(); plt.xticks(rotation=30); sv('p3_buckets')
ts=[0]+[r['t'] for r in ap]; al=[1]+[r['alive'] for r in ap]; cv=np.cumsum([0]+[r['conv'] for r in ap]); un=np.cumsum([0]+[r['un'] for r in ap])
fig,ax=plt.subplots(figsize=(6.4,2.8)); ax.step([xp(t) for t in ts],np.array(al)*100,where='post',color=B,label='Active'); ax.step([xp(t) for t in ts],cv*100,where='post',color=G,label='Converted'); ax.step([xp(t) for t in ts],un*100,where='post',color=Rd,label='Unsubscribed'); ax.set_xticks([xp(t) for t in tk]); ax.set_xticklabels(['0','6h','24h','3d','7d','14d','30d','60d','90d','180d']); ax.set_ylabel('% of cohort'); ax.legend(ncol=3); sv('p3_alive')
cr=np.cumsum([r['rev'] for r in ap]); cc=np.cumsum([r['cost'] for r in ap]); fig,ax=plt.subplots(figsize=(6.4,2.8)); ax.plot([xp(r['t']) for r in ap],cr,color=G,label='Incremental revenue'); ax.plot([xp(r['t']) for r in ap],cc,color=Rd,label='Sending cost'); ax.set_xticks([xp(t) for t in tk]); ax.set_xticklabels(['0','6h','24h','3d','7d','14d','30d','60d','90d','180d']); ax.set_ylabel('EUR (cohort of 10,000)'); ax.legend(); sv('p3_cum')
ks=list(T); nm=['Applied','First step','All declined','ASNEF','High quality','Cold base']; x=np.arange(len(ks)); fig,ax=plt.subplots(figsize=(6.4,3)); w=.27
ax.bar(x-w,[T[q]['net'] for q in ks],w,color=B,label='Front-loaded (proposed)'); ax.bar(x,[T[q]['flat']['net'] for q in ks],w,color=Gy,label='Weekly email'); ax.bar(x+w,[T[q]['agg']['net'] for q in ks],w,color=A,label='Aggressive daily'); ax.set_xticks(x); ax.set_xticklabels(nm,rotation=20); ax.set_ylabel('Net profit (EUR, cohort of 10,000)'); ax.axhline(0,color='k',lw=.6); ax.legend(fontsize=7); sv('p3_strat')
sn=sorted(D['p3']['sens'],key=lambda a:a[1]); fig,ax=plt.subplots(figsize=(6.4,2.7)); ax.barh([a for a,_ in sn],[v-D['p3']['base'] for _,v in sn],color=[G if v>=D['p3']['base'] else Rd for _,v in sn]); ax.set_xlabel('Change in net profit (EUR)'); sv('p3_sens')

def main(): print('figures written to', OUT)
if __name__=='__main__': main()
