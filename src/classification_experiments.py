"""Step 7: reproducible classification experiments. Run from repository root.

Requires locally downloaded Zindi files in data/zindi. Does not publish loan-level data.
Uses Joseph's shared features/splits; records aggregate results and safe summaries.
"""
from __future__ import annotations

from pathlib import Path
import joblib
import json
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.metrics import (
    average_precision_score, roc_auc_score, brier_score_loss, log_loss,
    confusion_matrix, f1_score, precision_score, recall_score,
)
from sklearn.calibration import calibration_curve
from lightgbm import LGBMClassifier
from src.features import build, FEATURES, preprocessor, splits

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / 'learnings' / 'tables'
FIGURES = ROOT / 'learnings' / 'figures'
LOCAL = ROOT / 'data' / 'experiments' / 'step7_reproducible'
SEED = 17
NOISE_FLOOR = .0263


def models():
    return {
        'Majority baseline': DummyClassifier(strategy='prior'),
        'Logistic Regression': LogisticRegression(max_iter=2000),
        'Logistic balanced': LogisticRegression(max_iter=2000, class_weight='balanced'),
        'k-NN': KNeighborsClassifier(n_neighbors=31),
        'Pruned Decision Tree': DecisionTreeClassifier(max_depth=5, min_samples_leaf=100, ccp_alpha=0.0001, random_state=SEED),
        'Random Forest': RandomForestClassifier(n_estimators=150, min_samples_leaf=20, n_jobs=-1, random_state=SEED),
        'LightGBM': LGBMClassifier(n_estimators=180, learning_rate=.05, num_leaves=15, min_child_samples=80, verbosity=-1, random_state=SEED, n_jobs=4),
    }


def partition_fit_cal(train, idx, scheme):
    """Keep fitting and calibration disjoint; for time, only past KNOWN labels."""
    pool = train.loc[idx].copy()
    if scheme == 'time_block':
        pool = pool.sort_values('disbursement_date', kind='mergesort')
        dates = np.sort(pool.disbursement_date.unique())
        boundary = pd.Timestamp(dates[int(.75 * (len(dates)-1))])
        fit = pool.index[(pool.disbursement_date < boundary) & (pool.outcome_known_at < boundary)]
        cal = pool.index[pool.disbursement_date >= boundary]
    elif scheme == 'fold_customer':
        split = GroupShuffleSplit(n_splits=1, test_size=.25, random_state=SEED)
        a, b = next(split.split(pool, pool.target, groups=pool.customer_id))
        fit, cal = pool.index[a], pool.index[b]
    else:
        a, b = train_test_split(np.arange(len(pool)), test_size=.25, random_state=SEED, stratify=pool.target)
        fit, cal = pool.index[a], pool.index[b]
    # Avoid fitting calibrators from only one class, with auditable skip instead of silent leakage.
    if len(fit)==0 or len(cal)==0 or train.loc[fit,'target'].nunique()<2 or train.loc[cal,'target'].nunique()<2:
        raise ValueError(f'Insufficient fit/calibration labels in {scheme}: {len(fit)} fit, {len(cal)} cal')
    if scheme == 'time_block':
        assert train.loc[fit, 'outcome_known_at'].max() < train.loc[cal, 'disbursement_date'].min()
    if scheme == 'fold_customer':
        assert not set(train.loc[fit, 'customer_id']) & set(train.loc[cal, 'customer_id'])
    return fit, cal


def logit(p):
    p = np.clip(np.asarray(p), 1e-8, 1-1e-8)
    return np.log(p / (1-p))


def predict_platt(base, xcal, ycal, xtest):
    pc = base.predict_proba(xcal)[:, 1]
    calibrator = LogisticRegression(max_iter=1000, random_state=SEED)
    calibrator.fit(logit(pc).reshape(-1, 1), ycal)
    test_raw = base.predict_proba(xtest)[:, 1]
    return calibrator.predict_proba(logit(test_raw).reshape(-1, 1))[:,1]


def metric_row(y, p, threshold):
    y=np.asarray(y, dtype=int); p=np.asarray(p, dtype=float)
    pred=(p > threshold).astype(int)  # positive means decline as risky
    tn, fp, fn, tp = confusion_matrix(y,pred,labels=[0,1]).ravel()
    approve=(pred==0)
    return dict(n=len(y), defaults=int(y.sum()), pr_auc=float(average_precision_score(y,p)),
        roc_auc=float(roc_auc_score(y,p)) if np.unique(y).size==2 else np.nan,
        brier=float(brier_score_loss(y,p)), log_loss=float(log_loss(y,p,labels=[0,1])),
        precision=float(precision_score(y,pred,zero_division=0)),
        recall=float(recall_score(y,pred,zero_division=0)),
        f1=float(f1_score(y,pred,zero_division=0)),
        tn=int(tn), fp=int(fp), fn=int(fn), tp=int(tp),
        approval_rate=float(approve.mean()),
        approved_default_rate=float(y[approve].mean()) if approve.any() else np.nan,
        cost_per_loan_KES=float((fn*4700+fp*100)/len(y)))



class PlattCalibratedModel:
    """Serializable sklearn-like scorer trained without calibration/evaluation overlap."""
    def __init__(self, base, calibrator):
        self.base = base
        self.calibrator = calibrator
    def predict_proba(self, X):
        raw=self.base.predict_proba(X)[:,1]
        p=self.calibrator.predict_proba(logit(raw).reshape(-1,1))[:,1]
        return np.column_stack([1-p,p])

def fit_integration_model(train, test):
    """Fit LR then Platt on later labels; no final-data performance claim."""
    ordered=train.sort_values('disbursement_date',kind='mergesort')
    dates=np.sort(ordered.disbursement_date.unique())
    boundary=pd.Timestamp(dates[int(.8*(len(dates)-1))])
    fit=ordered.index[(ordered.disbursement_date < boundary)&(ordered.outcome_known_at < boundary)]
    cal=ordered.index[ordered.disbursement_date >= boundary]
    assert len(fit)>0 and len(cal)>0
    assert train.loc[fit,'target'].nunique()==2 and train.loc[cal,'target'].nunique()==2
    assert train.loc[fit,'outcome_known_at'].max() < train.loc[cal,'disbursement_date'].min()
    base=make_pipeline(preprocessor(FEATURES),LogisticRegression(max_iter=2000))
    base.fit(train.loc[fit,FEATURES],train.loc[fit,'target'])
    cal_scores=logit(base.predict_proba(train.loc[cal,FEATURES])[:,1])
    calibrator=LogisticRegression(max_iter=1000,random_state=SEED)
    calibrator.fit(cal_scores.reshape(-1,1),train.loc[cal,'target'])
    chosen=PlattCalibratedModel(base,calibrator)
    joblib.dump(chosen, LOCAL/'lr_platt_integration.joblib')
    prob=chosen.predict_proba(test[FEATURES])[:,1]
    # Unlabelled test predictions stay on local laptop, never in public repo.
    pd.DataFrame({'ID':test.ID,'probability':prob}).to_csv(LOCAL/'unlabelled_predictions.csv',index=False)
    (TABLES/'07_model_handover.md').write_text(
        'Integration candidate: standard Logistic Regression + Platt. '
        f'Historical fit rows: {len(fit)}; later calibration rows: {len(cal)}. '
        'Serialized locally to ignored data/experiments/step7_reproducible/lr_platt_integration.joblib. '
        'The frozen training/calibration split must be externally validated before deployment. '
        'Ghana test probabilities have no observed Ghanaian default labels.\n',encoding='utf-8')
    print('SAVED: local integration scorer and unlabelled predictions',flush=True)

def operating_points(chosen):
    """Compare cut-off policies per future-loan block. Approval targets use only the block's own
    scores (no labels), which NkwaPay could do on the day; costs from learnings/04 (KES)."""
    rows=[]
    for fold,g in chosen.groupby('fold'):
        y=g.target.to_numpy(); p=g.probability.to_numpy()
        policies={'Approve everyone (no model)':np.inf,'Cost cut-off 2.1%':.021,'Repeat-business cut-off 9.6%':.096}
        for share in (.7,.8,.9): policies[f'Approve {share:.0%} (lowest risk)']=np.quantile(p,share)
        for name,t in policies.items():
            a=p<=t
            rows.append(dict(fold=fold,period=f'{g.date.min():%d %b %Y} – {g.date.max():%d %b %Y}',n=len(y),
                default_rate=float(y.mean()),policy=name,threshold=float(t),approval_rate=float(a.mean()),
                approved_default_rate=float(y[a].mean()) if a.any() else np.nan,
                defaulters_caught=float((~a & (y==1)).sum()/max(y.sum(),1)),
                cost_main_KES=float(((a&(y==1)).sum()*4700+((~a)&(y==0)).sum()*100)/len(y)),
                cost_repeat_KES=float(((a&(y==1)).sum()*4700+((~a)&(y==0)).sum()*500)/len(y))))
    pd.DataFrame(rows).to_csv(TABLES/'07_operating_points.csv',index=False)


def run():
    for p in (TABLES,FIGURES,LOCAL): p.mkdir(parents=True,exist_ok=True)
    train, unlabelled_test = build(str(ROOT/'data'/'zindi'))
    assert len(FEATURES) == 13
    assert train.target.isin([0,1]).all()
    print('Loaded training rows:',len(train),'features:',len(FEATURES),flush=True)
    all_rows=[]; oof=[]
    for scheme in ('fold_shuffled','fold_customer','time_block'):
        for fold, (learn, test) in enumerate(splits(train,scheme)):
            if not len(learn) or not len(test): continue
            fit, cal = partition_fit_cal(train,learn,scheme)
            if scheme=='time_block':
                assert train.loc[learn,'outcome_known_at'].max() < train.loc[test,'disbursement_date'].min()
            yfit=train.loc[fit,'target'].astype(int)
            ycal=train.loc[cal,'target'].astype(int)
            ytest=train.loc[test,'target'].astype(int).to_numpy()
            for name, estimator in models().items():
                print(scheme,fold,name,flush=True)
                model=make_pipeline(preprocessor(FEATURES),clone(estimator))
                model.fit(train.loc[fit,FEATURES],yfit)
                probs=predict_platt(model,train.loc[cal,FEATURES],ycal,train.loc[test,FEATURES])
                metrics=metric_row(ytest,probs,.021)
                all_rows.append(dict(scheme=scheme,fold=fold,model=name,**metrics))
                # Loan-level outputs ONLY in ignored local data; never commit.
                oof.append(pd.DataFrame({'scheme':scheme,'fold':fold,'model':name,
                    'ID':train.loc[test,'ID'].to_numpy(), 'customer_id':train.loc[test,'customer_id'].to_numpy(),
                    'date':train.loc[test,'disbursement_date'].to_numpy(),'target':ytest,'probability':probs}))
    metrics=pd.DataFrame(all_rows)
    predictions=pd.concat(oof,ignore_index=True)
    metrics.to_csv(TABLES/'07_model_fold_metrics.csv',index=False)
    predictions.to_csv(LOCAL/'oof_predictions.csv',index=False)
    grouped=metrics.groupby(['scheme','model'],as_index=False).agg(
        mean_pr_auc=('pr_auc','mean'),mean_roc_auc=('roc_auc','mean'),
        mean_f1=('f1','mean'),mean_brier=('brier','mean'),mean_cost_KES=('cost_per_loan_KES','mean'))
    grouped.to_csv(TABLES/'07_validation_comparison.csv',index=False)

    chosen=predictions[(predictions.scheme=='time_block') & (predictions.model=='Logistic Regression')].copy()
    assert chosen.ID.is_unique, 'Chronological loan predictions not unique'
    chosen['date']=pd.to_datetime(chosen.date)
    chosen['period']=chosen.date.dt.to_period('Q').astype(str)
    periods=[]
    for (period,fold),g in chosen.groupby(['period','fold']):
        y=g.target.to_numpy(); p=g.probability.to_numpy()
        for label,t,bad,good in [('Kenya 2.1%',.021,4700,100),('Kenyan loans at Ghana 3.2%',.032,2716,90)]:
            a=p<=t
            periods.append(dict(period=period,fold=fold,scenario=label,n=len(g),defaults=int(y.sum()),
                approval_rate=float(a.mean()),approved_default_rate=float(y[a].mean()) if a.any() else np.nan,
                cost_per_loan=float(((a & (y==1)).sum()*bad + ((~a)&(y==0)).sum()*good)/len(y))))
    pd.DataFrame(periods).to_csv(TABLES/'07_approval_by_period.csv',index=False)
    operating_points(chosen)
    plt.figure(figsize=(9,5))
    y=chosen.target.to_numpy(); p=chosen.probability.to_numpy()
    frac,mean=calibration_curve(y,p,n_bins=10,strategy='quantile')
    plt.plot(mean,frac,'o-',label='LR + Platt (chronological OOF)')
    plt.plot([0,1],[0,1],'--',label='Perfect calibration')
    plt.xlim(0,max(.12,1.2*max(mean))); plt.ylim(0,max(.12,1.2*max(frac)))
    plt.xlabel('Mean predicted default probability');plt.ylabel('Observed default frequency');plt.legend();plt.tight_layout()
    plt.savefig(FIGURES/'07_reliability_curve.png',dpi=140);plt.close()
    # Paired comparison at the same temporal OOF loan IDs. Difference is descriptive without a fresh CI.
    rf=predictions[(predictions.scheme=='time_block') & (predictions.model=='Random Forest')]
    lr=chosen.set_index('ID'); rf=rf.set_index('ID')
    common=lr.index.intersection(rf.index)
    assert len(common)==len(lr)==len(rf)
    assert np.array_equal(lr.loc[common,'target'].to_numpy(),rf.loc[common,'target'].to_numpy())
    delta=average_precision_score(lr.loc[common,'target'],lr.loc[common,'probability'])-average_precision_score(rf.loc[common,'target'],rf.loc[common,'probability'])
    # Customer-cluster paired bootstrap to avoid treating repeat loans as independent.
    joint=lr.loc[common,['customer_id','target','probability']].copy()
    joint=joint.rename(columns={'probability':'p_lr'}).join(rf.loc[common,['probability']].rename(columns={'probability':'p_rf'}))
    grouped_indices=list(joint.groupby('customer_id',sort=False).indices.values())
    rng=np.random.default_rng(SEED)
    diffs=[]
    for repeat in range(300):
        samples=rng.integers(0,len(grouped_indices),size=len(grouped_indices))
        idx=np.concatenate([grouped_indices[i] for i in samples])
        sample=joint.iloc[idx]
        if sample.target.nunique()<2: continue
        diffs.append(float(average_precision_score(sample.target,sample.p_lr)-average_precision_score(sample.target,sample.p_rf)))
    assert len(diffs)>=250
    ci=np.quantile(diffs,[.025,.975])
    # Pooling mixes blocks with different default rates (2022 dominates), so also compare block by block.
    tb=metrics[metrics.scheme=='time_block'].pivot(index='fold',columns='model',values='pr_auc')
    fold_delta=(tb['Logistic Regression']-tb['Random Forest']).to_numpy()
    pd.DataFrame({'bootstrap_pr_auc_lr_minus_rf':diffs}).to_csv(TABLES/'07_bootstrap_differences.csv',index=False)
    (TABLES/'07_noise_floor_comparison.md').write_text(
        f'LR minus RF pooled chronological PR-AUC = {delta:+.5f}. '
        f'Paired customer-bootstrap 95% interval [{ci[0]:+.5f}, {ci[1]:+.5f}], '
        f'{len(diffs)} valid replicates. Noise floor ±{NOISE_FLOOR:.4f}. '
        f'Point estimate exceeds noise floor: {abs(delta)>NOISE_FLOOR}. '
        f'Interval wholly above positive floor: {ci[0]>NOISE_FLOOR}. '
        f'Per time block (each scored on its own), LR minus RF = {", ".join(f"{d:+.4f}" for d in fold_delta)}; '
        f'mean {fold_delta.mean():+.4f}, LR ahead in {(fold_delta>0).sum()}/{len(fold_delta)} blocks. '
        'The bootstrap describes uncertainty for this validation procedure, not Ghana performance.\n',encoding='utf-8')
    # Fixed policy and F1 sweep; sweeps on evaluated rows are diagnostic, not unbiased policy selection.
    yy=chosen.target.to_numpy(); pp=chosen.probability.to_numpy()
    sweep=[]
    for t in np.unique(np.concatenate((np.geomspace(.001,.30,70),[.021,.032,.096,.142]))):
        row=metric_row(yy,pp,float(t));sweep.append({'threshold':t,**row})
    pd.DataFrame(sweep).to_csv(TABLES/'07_lr_threshold_sweep.csv',index=False)
    cm=confusion_matrix(yy,(pp>.021).astype(int),labels=[0,1]); fig,ax=plt.subplots(figsize=(5,4))
    ax.imshow(cm,cmap='Blues');ax.set_xticks([0,1],['Approve','Decline']);ax.set_yticks([0,1],['Actually repaid','Actually defaulted'])
    for (i,j),v in np.ndenumerate(cm):ax.text(j,i,str(v),ha='center',va='center')
    ax.set_title('LR + Platt: Kenya 2.1% threshold'); fig.tight_layout();fig.savefig(FIGURES/'07_confusion_matrix.png',dpi=140);plt.close(fig)
    fit_integration_model(train,unlabelled_test)
    print('COMPLETED: aggregate metrics, temporal decisions, reliability curve, noise-floor note')
    print('Local loan-level predictions:',LOCAL/'oof_predictions.csv')
    print('DO NOT COMMIT local loan-level predictions.')

if __name__=='__main__':
    run()
