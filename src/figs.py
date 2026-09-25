import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from scipy import stats
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,
    'axes.spines.right':False,'savefig.dpi':300,'savefig.bbox':'tight','axes.linewidth':0.8})
C={'B0005':'#2166AC','B0006':'#D6604D','B0007':'#4D9221','B0018':'#9970AB'}
d=pd.read_csv('/home/claude/repo/results/tables/battery_processed.csv')
s=d.dropna(subset=['Re','Rct'])
F='/home/claude/rev/figs'

# ---- Fig 1: pipeline schematic (vector) ----
fig,ax=plt.subplots(figsize=(10,2.6)); ax.axis('off'); ax.set_xlim(0,10); ax.set_ylim(0,2.6)
boxes=[("NASA PCoE\nB0005–B0007, B0018","#E8EEF7"),
       ("Read Re and Rct\nfrom impedance records","#E8EEF7"),
       ("Capacity from\nNASA Capacity field","#E8EEF7"),
       ("Mixed-effects\nbetween-cell analysis","#FBEDE9"),
       ("Four-fold LOBO\nrandom forest + ablation","#FBEDE9")]
w,h,gap=1.72,1.0,0.35
for i,(t,col) in enumerate(boxes):
    x=0.15+i*(w+gap)
    ax.add_patch(FancyBboxPatch((x,0.8),w,h,boxstyle="round,pad=0.04,rounding_size=0.08",
        linewidth=0.9,edgecolor='#44546A',facecolor=col))
    ax.text(x+w/2,1.3,t,ha='center',va='center',fontsize=8.2,linespacing=1.45)
    if i<len(boxes)-1:
        ax.add_patch(FancyArrowPatch((x+w+0.04,1.3),(x+w+gap-0.04,1.3),
            arrowstyle='-|>',mutation_scale=11,linewidth=0.9,color='#44546A'))
ax.text(0.15+w/2,0.55,"Data",ha='center',fontsize=7.5,color='#7F7F7F')
ax.text(0.15+2*(w+gap)+w/2,0.55,"Feature layer",ha='center',fontsize=7.5,color='#7F7F7F')
ax.text(0.15+4*(w+gap)+w/2,0.55,"Evaluation",ha='center',fontsize=7.5,color='#7F7F7F')
fig.savefig(f'{F}/fig1_pipeline.png'); plt.close()

# ---- Fig 2: capacity fade ----
fig,ax=plt.subplots(figsize=(6.2,3.6))
for b,g in d.groupby('Battery'):
    g=g.sort_values('CycleIndex')
    ax.plot(g.CycleIndex,g.Capacity_Ah,'.',ms=2.4,color=C[b],alpha=.55)
    sl,ic,r,p,_=stats.linregress(g.CycleIndex,g.Capacity_Ah)
    x=np.array([g.CycleIndex.min(),g.CycleIndex.max()])
    ax.plot(x,sl*x+ic,color=C[b],lw=1.4,label=f"{b}  R²={r**2:.3f}")
ax.axhline(1.40,ls='--',lw=0.9,color='#666')
ax.text(5,1.415,'EOL threshold 1.40 Ah',fontsize=7.5,color='#666')
ax.set_xlabel('Discharge cycle index'); ax.set_ylabel('Discharge capacity (Ah)')
ax.legend(fontsize=7.5,frameon=False,loc='upper right')
fig.savefig(f'{F}/fig2_capacity_fade.png'); plt.close()

# ---- Fig 3: Re trend ----
fig,ax=plt.subplots(figsize=(6.2,3.6))
for b,g in s.groupby('Battery'):
    g=g.sort_values('CycleIndex')
    ax.plot(g.CycleIndex,g.Re*1000,'.',ms=2.4,color=C[b],alpha=.55)
    sl,ic,r,p,_=stats.linregress(g.CycleIndex,g.Re*1000)
    x=np.array([g.CycleIndex.min(),g.CycleIndex.max()])
    ax.plot(x,sl*x+ic,color=C[b],lw=1.4,label=f"{b}  R²={r**2:.3f}")
ax.set_xlabel('Discharge cycle index'); ax.set_ylabel('Electrolyte resistance $R_e$ (mΩ)')
ax.legend(fontsize=7.5,frameon=False,loc='upper left')
fig.savefig(f'{F}/fig3_Re_trend.png'); plt.close()

# ---- Fig 4: pooled coupling + correlation matrix ----
fig,axes=plt.subplots(1,2,figsize=(9.2,3.5))
ax=axes[0]
for b,g in s.groupby('Battery'):
    ax.plot(g.Re*1000,g.Rct*1000,'.',ms=3,color=C[b],alpha=.6,label=b)
sl,ic,r,p,_=stats.linregress(s.Re*1000,s.Rct*1000)
x=np.array([s.Re.min()*1000,s.Re.max()*1000])
ax.plot(x,sl*x+ic,'k-',lw=1.3)
ax.text(.04,.94,f"pooled R² = {r**2:.3f}  (n = {len(s)})",transform=ax.transAxes,fontsize=8)
ax.set_xlabel('$R_e$ (mΩ)'); ax.set_ylabel('$R_{ct}$ (mΩ)'); ax.legend(fontsize=7.5,frameon=False,loc='lower right')
ax=axes[1]
cols=['Re','Rct','Capacity_Ah','CycleIndex']; lab=['$R_e$','$R_{ct}$','Capacity','Cycle']
M=s[cols].corr().values
im=ax.imshow(M,cmap='RdBu_r',vmin=-1,vmax=1)
ax.set_xticks(range(4),lab,fontsize=8); ax.set_yticks(range(4),lab,fontsize=8)
for i in range(4):
    for j in range(4):
        ax.text(j,i,f"{M[i,j]:.2f}",ha='center',va='center',fontsize=8,
                color='white' if abs(M[i,j])>0.6 else 'black')
for sp in ax.spines.values(): sp.set_visible(False)
fig.colorbar(im,ax=ax,fraction=0.045,pad=0.03)
fig.tight_layout(); fig.savefig(f'{F}/fig4_coupling.png'); plt.close()

# ---- Fig 5: per-cell coupling heterogeneity ----
fig,axes=plt.subplots(1,4,figsize=(10.4,2.9),sharey=True)
for ax,(b,g) in zip(axes,s.groupby('Battery')):
    ax.plot(g.Re*1000,g.Rct*1000,'.',ms=3,color=C[b],alpha=.6)
    sl,ic,r,p,_=stats.linregress(g.Re*1000,g.Rct*1000)
    x=np.array([g.Re.min()*1000,g.Re.max()*1000]); ax.plot(x,sl*x+ic,color='k',lw=1.2)
    ax.set_title(f"{b}\nslope {sl:.2f},  R² {r**2:.3f}",fontsize=8.5)
    ax.set_xlabel('$R_e$ (mΩ)')
axes[0].set_ylabel('$R_{ct}$ (mΩ)')
fig.tight_layout(); fig.savefig(f'{F}/fig5_percell_coupling.png'); plt.close()

# ---- Fig 6: LOBO folds + ablation ----
folds=pd.read_csv('/home/claude/rev/tables/lobo_folds.csv')
abl=pd.read_csv('/home/claude/rev/tables/ablation_baselines.csv')
fig,axes=plt.subplots(1,2,figsize=(10.4,3.7),gridspec_kw={'width_ratios':[1,1.5]})
ax=axes[0]
bars=ax.bar(folds.held,folds.RMSE,color=[C[b] for b in folds.held],width=.62)
ax.axhline(folds.RMSE.mean(),ls='--',lw=1,color='#444')
ax.text(3.45,folds.RMSE.mean()+0.8,f"mean {folds.RMSE.mean():.2f}",fontsize=7.5,ha='right',color='#444')
for bar,v,r2 in zip(bars,folds.RMSE,folds.R2):
    ax.text(bar.get_x()+bar.get_width()/2,v+0.6,f"{v:.1f}\nR²={r2:.2f}",ha='center',fontsize=7.3)
ax.set_ylabel('RMSE (cycles)'); ax.set_xlabel('Held-out cell'); ax.set_ylim(0,40)
ax=axes[1]
a=abl.sort_values('mean_RMSE',ascending=False)
cols=['#B2182B' if 'Re and Rct' in m or 'ridge' in m else '#4393C3' for m in a.Model]
ax.barh(range(len(a)),a.mean_RMSE,color=cols,height=.66)
ax.set_yticks(range(len(a)),[m.replace(' (RF)','') for m in a.Model],fontsize=7.6)
for i,v in enumerate(a.mean_RMSE): ax.text(v+0.4,i,f"{v:.2f}",va='center',fontsize=7.3)
ax.set_xlabel('Mean RMSE across four folds (cycles)'); ax.set_xlim(0,38)
fig.tight_layout(); fig.savefig(f'{F}/fig6_lobo_ablation.png'); plt.close()
print("figures written")
