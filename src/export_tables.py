import pandas as pd, numpy as np
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.stattools import durbin_watson
from itertools import combinations
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "results", "tables", "battery_processed.csv")
TABLES = os.path.join(ROOT, "results", "tables")
FIGS = os.path.join(ROOT, "results", "figures")
os.makedirs(TABLES, exist_ok=True); os.makedirs(FIGS, exist_ok=True)

O = TABLES
d=pd.read_csv(DATA)

# 1. between-cell summary
rows=[]
def eta2(g):
    a=np.concatenate(g); m=a.mean()
    return sum(len(x)*(x.mean()-m)**2 for x in g)/((a-m)**2).sum()
for col in ['Re','Rct','Capacity_Ah']:
    g=[x[col].dropna().values for _,x in d.groupby('Battery')]
    F,pF=stats.f_oneway(*g); H,pH=stats.kruskal(*g)
    N=sum(len(x) for x in g); k=len(g)
    sub=d.dropna(subset=[col]).copy(); sub['y']=sub[col]; sub['cyc']=sub['CycleIndex']
    m=smf.mixedlm("y ~ cyc",sub,groups=sub['Battery']).fit(reml=True)
    vc=float(m.cov_re.iloc[0,0]); rv=float(m.scale); ci=m.conf_int().loc['cyc']
    rows.append(dict(Parameter=col,n=N,ANOVA_F=round(F,2),ANOVA_p=f"{pF:.2e}",Kruskal_H=round(H,2),
        Kruskal_p=f"{pH:.2e}",eta2=round(eta2(g),3),eps2=round((H-k+1)/(N-k),3),
        ICC=round(vc/(vc+rv),3),slope_per_cycle=f"{m.params['cyc']:.4e}",
        slope_CI_low=f"{ci[0]:.4e}",slope_CI_high=f"{ci[1]:.4e}"))
pd.DataFrame(rows).to_csv(f"{O}/between_cell_summary.csv",index=False)

# 2. autocorrelation diagnostics
rows=[]
for col in ['Re','Rct','Capacity_Ah']:
    for b,g in d.dropna(subset=[col]).groupby('Battery'):
        g=g.sort_values('CycleIndex')
        sl,ic,_,_,_=stats.linregress(g.CycleIndex,g[col]); res=(g[col]-(sl*g.CycleIndex+ic)).values
        rows.append(dict(Parameter=col,Battery=b,n=len(g),durbin_watson=round(durbin_watson(res),3),
                         lag1_acf=round(pd.Series(res).autocorr(1),3)))
pd.DataFrame(rows).to_csv(f"{O}/autocorrelation_diagnostics.csv",index=False)

# 3. pairwise Holm + Cliff's delta
rows=[]
for col in ['Re','Rct','Capacity_Ah']:
    bats=sorted(d.Battery.unique()); pv=[]; meta=[]
    for a,b in combinations(bats,2):
        x=d[d.Battery==a][col].dropna(); y=d[d.Battery==b][col].dropna()
        u,p=stats.mannwhitneyu(x,y); pv.append(p); meta.append((a,b,2*u/(len(x)*len(y))-1))
    order=np.argsort(pv); adj=np.empty(len(pv)); prev=0; M=len(pv)
    for rank,idx in enumerate(order):
        v=min(1,(M-rank)*pv[idx]); prev=max(prev,v); adj[idx]=prev
    for (a,b,dl),p,pa in zip(meta,pv,adj):
        rows.append(dict(Parameter=col,Cell_A=a,Cell_B=b,cliffs_delta=round(dl,3),
                         p_raw=f"{p:.2e}",p_holm=f"{pa:.2e}"))
pd.DataFrame(rows).to_csv(f"{O}/pairwise_holm_cliffs.csv",index=False)

# 4. per-cell coupling
s=d.dropna(subset=['Re','Rct'])
rows=[]
for b,g in s.groupby('Battery'):
    sl,ic,r,p,_=stats.linregress(g.Re,g.Rct)
    rx=g.Re-np.poly1d(np.polyfit(g.CycleIndex,g.Re,1))(g.CycleIndex)
    ry=g.Rct-np.poly1d(np.polyfit(g.CycleIndex,g.Rct,1))(g.CycleIndex)
    pr,pp=stats.pearsonr(rx,ry)
    ded=g.sort_values('CycleIndex'); ded=ded[ded.Re.ne(ded.Re.shift())]
    sl2,_,r2,_,_=stats.linregress(ded.Re,ded.Rct)
    rows.append(dict(Battery=b,n=len(g),n_unique_Re=g.Re.nunique(),slope=round(sl,4),R2=round(r**2,4),
        partial_r_given_cycle=round(pr,3),R2_deduplicated=round(r2**2,4),n_deduplicated=len(ded)))
sl,ic,r,p,_=stats.linregress(s.Re,s.Rct)
sc=s.copy(); sc['Re_c']=sc.Re-sc.groupby('Battery').Re.transform('mean')
sc['Rct_c']=sc.Rct-sc.groupby('Battery').Rct.transform('mean')
slw,_,rw,_,_=stats.linregress(sc.Re_c,sc.Rct_c)
rows.append(dict(Battery="POOLED",n=len(s),n_unique_Re=s.Re.nunique(),slope=round(sl,4),R2=round(r**2,4),
    partial_r_given_cycle="",R2_deduplicated="",n_deduplicated=""))
rows.append(dict(Battery="WITHIN-CELL CENTRED",n=len(s),n_unique_Re="",slope=round(slw,4),
    R2=round(rw**2,4),partial_r_given_cycle="",R2_deduplicated="",n_deduplicated=""))
pd.DataFrame(rows).to_csv(f"{O}/coupling_per_cell.csv",index=False)
print("tables exported")
