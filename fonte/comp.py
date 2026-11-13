import pandas as pd, glob, numpy as np
from scipy import stats
D='../dados'
df=pd.concat([pd.read_csv(f) for f in sorted(glob.glob(D+'/*.csv'))],ignore_index=True)
pd.set_option('display.width',250); pd.set_option('display.max_columns',50)
print(df.groupby(['marca','destinacao_final']).co2e_fim_vida_g.agg(['mean','count']).round(1).unstack())
print(df.groupby(['coleta_pos_consumo']).co2e_fim_vida_g.mean())
for c in ['co2e_total_g','agua_total_l','desmatamento_atribuido_m2','indice_efluentes_toxicos']: df[c+'_pg']=df[c]/df.massa_cafe_g
M=['Aurora','Bravura','Cerrado','Delta','Estacao','Flora','Granito','Horizonte']
# indicators: (name, func(group)->value, lower_is_better)
def ind(d):
    a=d[d.auditoria_fornecedor_realizada==1]
    return pd.Series({'co2':d.co2e_total_g_pg.mean(),'agua':d.agua_total_l_pg.mean(),'desm':d.desmatamento_atribuido_m2_pg.mean(),'efl':d.indice_efluentes_toxicos_pg.mean(),
     'rec':d.reciclagem_efetiva.mean(),'ti':a.trabalho_infantil_constatado.mean(),'nc':a.nao_conformidade_trabalhista.mean(),'rem':d.remuneracao_relativa_referencia.mean()})
lower={'co2':1,'agua':1,'desm':1,'efl':1,'rec':0,'ti':1,'nc':1,'rem':0}
W={'base':dict(co2=15,agua=10,desm=10,efl=10,rec=15,ti=20,nc=10,rem=10),
   'igual':{k:12.5 for k in lower},
   'ambiental':dict(co2=25,agua=15,desm=15,efl=15,rec=20,ti=4,nc=3,rem=3),
   'social':dict(co2=8,agua=4,desm=4,efl=4,rec=8,ti=40,nc=20,rem=12)}
def score(I,w):
    Z=(I-I.mean())/I.std(ddof=0)
    for k in lower:
        if lower[k]: Z[k]=-Z[k]
    return sum(Z[k]*w[k] for k in lower)/sum(w.values())
I=df.groupby('marca').apply(ind); print(I.round(3))
for n,w in W.items():
    s=score(I,w); print(n,s.sort_values(ascending=False).round(2).to_dict())
# bootstrap
rng=np.random.default_rng(1); groups={m:df[df.marca==m] for m in M}
B=1000; wins={n:{m:0 for m in M} for n in W}; wins['dirichlet']={m:0 for m in M}; ranks={m:[] for m in M}
for b in range(B):
    Ib=pd.DataFrame({m:ind(groups[m].sample(len(groups[m]),replace=True,random_state=int(rng.integers(1e9)))) for m in M}).T
    for n,w in W.items():
        s=score(Ib,w); wins[n][s.idxmax()]+=1
        if n=='base':
            r=s.rank(ascending=False)
            for m in M: ranks[m].append(r[m])
    wd=dict(zip(lower,rng.dirichlet(np.ones(8)))); s=score(Ib,wd); wins['dirichlet'][s.idxmax()]+=1
print(pd.DataFrame(wins)/B)
print({m:(np.percentile(ranks[m],2.5),np.median(ranks[m]),np.percentile(ranks[m],97.5)) for m in M})
# Dirichlet on point estimates
rng=np.random.default_rng(2); c={m:0 for m in M}; top2={m:0 for m in M}
for _ in range(20000):
    s=score(I,dict(zip(lower,rng.dirichlet(np.ones(8)))));c[s.idxmax()]+=1
    for m in s.nlargest(2).index: top2[m]+=1
print({k:v/20000 for k,v in c.items()}); print({k:v/20000 for k,v in top2.items()})
# excluding Estacao
I2=I.drop('Estacao')
for n,w in W.items(): print(n,score(I2,w).sort_values(ascending=False).round(2).to_dict())
