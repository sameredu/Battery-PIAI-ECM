import pandas as pd, numpy as np, json, os
from scipy import stats
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

OUT="/home/claude/rev"
d = pd.read_csv('/home/claude/repo/results/tables/battery_processed.csv')
EOL_T=1.40
FEATS=["Re","Rct","Capacity_Ah","CycleIndex","V_mean","T_mean","Duration_s"]
R={}

def add_rul(df, b7_eol):
    out=[]
    for b,g in df.groupby('Battery'):
        g=g.sort_values('CycleIndex').copy()
        below=g[g['Capacity_Ah']<=EOL_T]
        if len(below): eol=int(below['CycleIndex'].min())
        else: eol=b7_eol
        g['RUL']=(eol-g['CycleIndex']).clip(lower=0); g['EOL_cycle']=eol
        out.append(g)
    return pd.concat(out,ignore_index=True)

def lobo(clean, featset, model_fn):
    rows=[]
    for held in ["B0005","B0006","B0007","B0018"]:
        tr=clean[clean.Battery!=held]; te=clean[clean.Battery==held].sort_values('CycleIndex')
        sc=StandardScaler(); Xtr=sc.fit_transform(tr[featset]); Xte=sc.transform(te[featset])
        m=model_fn(); m.fit(Xtr,tr['RUL']); p=m.predict(Xte)
        rows.append(dict(held=held,RMSE=float(np.sqrt(mean_squared_error(te['RUL'],p))),
                         MAE=float(mean_absolute_error(te['RUL'],p)),R2=float(r2_score(te['RUL'],p))))
    return pd.DataFrame(rows)

rf=lambda: RandomForestRegressor(n_estimators=200,random_state=42,n_jobs=-1)

# ---- B0007 EOL sensitivity ----
print("### B0007 EOL SENSITIVITY ###")
sens=[]
for label,eol in [("166 (cycle of minimum capacity)",166),("169 (last observed + 1)",169),("178 (linear extrapolation)",178)]:
    df=add_rul(d,eol); clean=df.dropna(subset=FEATS+['RUL'])
    r=lobo(clean,FEATS,rf)
    sens.append(dict(label=label,eol=eol,mean_RMSE=round(r.RMSE.mean(),2),mean_R2=round(r.R2.mean(),3),
                     B0007_RMSE=round(float(r[r.held=='B0007'].RMSE.iloc[0]),2),
                     B0007_R2=round(float(r[r.held=='B0007'].R2.iloc[0]),3)))
    print(f"  EOL={label:34s} mean RMSE={r.RMSE.mean():6.2f}  mean R2={r.R2.mean():.3f}  | B0007 fold RMSE={float(r[r.held=='B0007'].RMSE.iloc[0]):6.2f}")
R['b0007_sensitivity']=sens
pd.DataFrame(sens).to_csv(f"{OUT}/tables/b0007_eol_sensitivity.csv",index=False)

# ---- main tables at EOL=169 ----
df=add_rul(d,169); clean=df.dropna(subset=FEATS+['RUL'])
main=lobo(clean,FEATS,rf)
ci=stats.t.interval(0.95,3,loc=main.RMSE.mean(),scale=stats.sem(main.RMSE))
R['lobo']=dict(folds=main.round(3).to_dict('records'),mean_RMSE=round(main.RMSE.mean(),2),
   median_RMSE=round(main.RMSE.median(),2),min_RMSE=round(main.RMSE.min(),2),max_RMSE=round(main.RMSE.max(),2),
   ci_low=round(ci[0],2),ci_high=round(ci[1],2),mean_R2=round(main.R2.mean(),3))
main.round(3).to_csv(f"{OUT}/tables/lobo_folds.csv",index=False)

abl=[("Full feature set (RF)",FEATS,rf),
     ("Capacity + cycle index (RF)",["Capacity_Ah","CycleIndex"],rf),
     ("Capacity only (RF)",["Capacity_Ah"],rf),
     ("Full feature set (gradient boosting)",FEATS,lambda:GradientBoostingRegressor(random_state=42)),
     ("No capacity (RF)",["Re","Rct","CycleIndex","V_mean","T_mean","Duration_s"],rf),
     ("No capacity, no cycle index (RF)",["Re","Rct","V_mean","T_mean","Duration_s"],rf),
     ("Full feature set (ridge)",FEATS,lambda:Ridge(alpha=1.0)),
     ("Re and Rct only (RF)",["Re","Rct"],rf)]
rows=[]
for name,fs,fn in abl:
    r=lobo(clean,fs,fn); rows.append(dict(Model=name,mean_RMSE=round(r.RMSE.mean(),2),mean_R2=round(r.R2.mean(),3)))
# training-free baseline
bl=[]
for held in ["B0005","B0006","B0007","B0018"]:
    te=clean[clean.Battery==held].sort_values('CycleIndex'); preds=[]
    for i,(_,row) in enumerate(te.iterrows()):
        h=te.iloc[:i+1]
        if len(h)<10: preds.append(np.nan); continue
        sl,ic,_,_,_=stats.linregress(h.CycleIndex,h.Capacity_Ah)
        e=(EOL_T-ic)/sl if sl<0 else np.nan
        preds.append(max(e-row.CycleIndex,0) if np.isfinite(e) else np.nan)
    t=te.assign(pred=preds).dropna(subset=['pred'])
    bl.append(dict(RMSE=np.sqrt(mean_squared_error(t.RUL,t.pred)),R2=r2_score(t.RUL,t.pred)))
blf=pd.DataFrame(bl)
rows.append(dict(Model="Linear capacity extrapolation (no training)",mean_RMSE=round(blf.RMSE.mean(),2),mean_R2=round(blf.R2.mean(),3)))
ablt=pd.DataFrame(rows).sort_values('mean_RMSE')
ablt.to_csv(f"{OUT}/tables/ablation_baselines.csv",index=False)
R['ablation']=ablt.to_dict('records')
print("\n### ABLATION ###"); print(ablt.to_string(index=False))

json.dump(R,open(f"{OUT}/results_summary.json","w"),indent=2)
print("\nsaved")
