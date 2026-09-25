import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "results", "tables", "battery_processed.csv")
TABLES = os.path.join(ROOT, "results", "tables")
FIGS = os.path.join(ROOT, "results", "figures")
os.makedirs(TABLES, exist_ok=True); os.makedirs(FIGS, exist_ok=True)

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,
    'axes.spines.right':False,'savefig.dpi':300,'savefig.bbox':'tight','axes.linewidth':0.8})
C={'B0005':'#2166AC','B0006':'#D6604D','B0007':'#4D9221','B0018':'#9970AB'}
d=pd.read_csv(DATA)
s=d.dropna(subset=['Re','Rct'])
F = FIGS

# Figures 1-8. Run src/analysis.py and src/export_tables.py first.

# ---- Fig 1: pipeline schematic ----
fig,ax=plt.subplots(figsize=(11.0,2.0)); ax.axis('off')
w,h,gap=1.95,1.05,0.34
ax.set_xlim(0,0.1+5*w+4*gap+0.1); ax.set_ylim(0,1.5)
for i,(t,col) in enumerate([("NASA PCoE dataset\nB0005–B0007, B0018","#E8EEF7"),
        ("Read $R_e$ and $R_{ct}$\nfrom impedance records","#E8EEF7"),
        ("Capacity from the\nNASA Capacity field","#E8EEF7"),
        ("Mixed-effects\nbetween-cell analysis","#FBEDE9"),
        ("Four-fold LOBO\nforest and ablation","#FBEDE9")]):
    x=0.1+i*(w+gap)
    ax.add_patch(FancyBboxPatch((x,0.22),w,h,boxstyle="round,pad=0.03,rounding_size=0.07",
        linewidth=0.9,edgecolor='#44546A',facecolor=col))
    ax.text(x+w/2,0.745,t,ha='center',va='center',fontsize=8.6,linespacing=1.5)
    if i<4: ax.add_patch(FancyArrowPatch((x+w+0.03,0.745),(x+w+gap-0.03,0.745),
        arrowstyle='-|>',mutation_scale=11,linewidth=0.9,color='#44546A'))
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

# ---- Fig 4: between-cell distributions ----
fig,axes=plt.subplots(1,3,figsize=(9.6,3.2))
specs=[('Re','$R_e$ (mΩ)',1000,'ICC 0.899   η² 0.600'),
       ('Rct','$R_{ct}$ (mΩ)',1000,'ICC 0.854   η² 0.480'),
       ('Capacity_Ah','Discharge capacity (Ah)',1,'ICC 0.646   η² 0.038')]
for ax,(col,lab,sc,note) in zip(axes,specs):
    data=[g[col].dropna().values*sc for _,g in d.groupby('Battery')]
    bats=sorted(d.Battery.unique())
    bp=ax.boxplot(data,widths=.55,patch_artist=True,showfliers=False,
        medianprops=dict(color='black',lw=1.1),whiskerprops=dict(lw=.8),capprops=dict(lw=.8))
    for patch,b in zip(bp['boxes'],bats):
        patch.set_facecolor(C[b]); patch.set_alpha(.45); patch.set_edgecolor(C[b]); patch.set_linewidth(1.0)
    for i,(b,v) in enumerate(zip(bats,data)):
        ax.plot(np.random.normal(i+1,0.055,len(v)),v,'.',ms=1.6,color=C[b],alpha=.35,zorder=0)
    ax.set_xticks(range(1,5),[b.replace('B00','B') for b in bats],fontsize=8.5)
    ax.set_ylabel(lab); ax.set_title(note,fontsize=8.5,pad=6)
fig.tight_layout(); fig.savefig(f'{F}/fig4_between_cell.png'); plt.close()

# ---- Fig 5: pooled coupling and correlation matrix ----
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
fig.tight_layout(); fig.savefig(f'{F}/fig5_coupling.png'); plt.close()

# ---- Fig 6: per-cell coupling on shared axes ----
fig,axes=plt.subplots(1,4,figsize=(10.4,3.1),sharey=True,sharex=True)
for ax,(b,g) in zip(axes,s.groupby('Battery')):
    ax.plot(g.Re*1000,g.Rct*1000,'.',ms=3,color=C[b],alpha=.65)
    sl,ic,r,p,_=stats.linregress(g.Re*1000,g.Rct*1000)
    x=np.array([g.Re.min()*1000,g.Re.max()*1000]); ax.plot(x,sl*x+ic,color='k',lw=1.2)
    span=1000*(g.Re.max()-g.Re.min())
    ax.set_title(f"{b}\nslope {sl:.2f},  R² {r**2:.3f}",fontsize=8.5)
    ax.annotate('',xy=(g.Re.min()*1000,108),xytext=(g.Re.max()*1000,108),
        arrowprops=dict(arrowstyle='<->',lw=.8,color='#555'))
    ax.text((g.Re.min()+g.Re.max())*500,109.5,f"span {span:.1f} mΩ",ha='center',fontsize=7.2,color='#555')
    ax.set_xlabel('$R_e$ (mΩ)')
axes[0].set_ylabel('$R_{ct}$ (mΩ)'); axes[0].set_ylim(55,118)
fig.tight_layout(); fig.savefig(f'{F}/fig6_percell_coupling.png'); plt.close()

# ---- Fig 7: predicted vs actual RUL across folds ----
EOL_T=1.40; FEATS=["Re","Rct","Capacity_Ah","CycleIndex","V_mean","T_mean","Duration_s"]
out=[]
for b,g in d.groupby('Battery'):
    g=g.sort_values('CycleIndex').copy()
    below=g[g.Capacity_Ah<=EOL_T]
    eol=int(below.CycleIndex.min()) if len(below) else 169
    g['RUL']=(eol-g.CycleIndex).clip(lower=0); out.append(g)
df=pd.concat(out,ignore_index=True); clean=df.dropna(subset=FEATS+['RUL'])
fig,axes=plt.subplots(1,4,figsize=(11.0,2.9),sharey=True)
for ax,held in zip(axes,["B0005","B0006","B0007","B0018"]):
    tr=clean[clean.Battery!=held]; te=clean[clean.Battery==held].sort_values('CycleIndex')
    sc=StandardScaler(); m=RandomForestRegressor(n_estimators=200,random_state=42,n_jobs=-1)
    m.fit(sc.fit_transform(tr[FEATS]),tr.RUL); p=m.predict(sc.transform(te[FEATS]))
    rmse=np.sqrt(((te.RUL-p)**2).mean())
    ax.plot(te.CycleIndex,te.RUL,color='#333',lw=1.5,label='Actual')
    ax.plot(te.CycleIndex,p,color=C[held],lw=1.5,ls='--',label='Predicted')
    ax.fill_between(te.CycleIndex,te.RUL,p,color=C[held],alpha=.16)
    ax.set_title(f"Held out: {held}\nRMSE {rmse:.2f} cycles",fontsize=8.5)
    ax.set_xlabel('Discharge cycle index')
axes[0].set_ylabel('Remaining useful life (cycles)'); axes[0].legend(fontsize=7.5,frameon=False)
fig.tight_layout(); fig.savefig(f'{F}/fig7_rul_folds.png'); plt.close()

# ---- Fig 8: ablation and baselines ----
_a = pd.read_csv(os.path.join(TABLES,'ablation_baselines.csv')).sort_values('mean_RMSE', ascending=False)
fig, ax = plt.subplots(figsize=(7.2, 3.4))
_cols = ['#B2182B' if ('Re and Rct' in m or 'ridge' in m) else ('#7F7F7F' if 'no training' in m else '#4393C3')
         for m in _a.Model]
ax.barh(range(len(_a)), _a.mean_RMSE, color=_cols, height=.66)
ax.set_yticks(range(len(_a)), [m.replace(' (RF)', '') for m in _a.Model], fontsize=8)
for i, v in enumerate(_a.mean_RMSE):
    ax.text(v + 0.4, i, f"{v:.2f}", va='center', fontsize=7.6)
ax.set_xlabel('Mean RMSE across the four folds (cycles)'); ax.set_xlim(0, 38)
fig.savefig(os.path.join(FIGS, 'fig8_ablation.png')); plt.close()

print("figures 1-8 written to", FIGS)
