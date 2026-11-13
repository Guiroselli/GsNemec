import pandas as pd, glob, numpy as np
from scipy import stats
from statsmodels.stats.proportion import proportion_confint
from statsmodels.stats.multitest import multipletests
D='../dados/dados'
df=pd.concat([pd.read_csv(f) for f in sorted(glob.glob(D+'/*.csv'))],ignore_index=True)
for c in ['co2e_total_g','agua_total_l','desmatamento_atribuido_m2','indice_efluentes_toxicos']:
    df[c+'_pg']=df[c]/df.massa_cafe_g
M=['Aurora','Bravura','Cerrado','Delta','Estacao','Flora','Granito','Horizonte']
pd.set_option('display.width',250); pd.set_option('display.max_columns',50)
def ci(s):
    m=s.mean(); se=s.sem(); h=stats.t.ppf(.975,len(s)-1)*se; return m,m-h,m+h
for c in ['co2e_total_g_pg','agua_total_l_pg','desmatamento_atribuido_m2_pg','indice_efluentes_toxicos_pg','co2e_total_g','remuneracao_relativa_referencia','massa_cafe_g']:
    g=[df[df.marca==m][c] for m in M]
    F=stats.f_oneway(*g); K=stats.kruskal(*g); L=stats.levene(*g)
    print(c,'ANOVA p=%.2g Kruskal p=%.2g Levene p=%.2g'%(F.pvalue,K.pvalue,L.pvalue))
    print({m:tuple(round(x,3) for x in ci(df[df.marca==m][c])) for m in M})
# rates
def rate(m,col,sub=None):
    d=df[df.marca==m]
    if sub is not None: d=d[sub(d)]
    x=d[col].dropna(); k=int(x.sum()); n=len(x); lo,hi=proportion_confint(k,n,method='wilson'); return k,n,round(k/n,3),round(lo,3),round(hi,3)
for col in ['reciclagem_efetiva','coleta_pos_consumo','auditoria_fornecedor_realizada','trabalho_infantil_constatado','nao_conformidade_trabalhista']:
    print(col); [print(' ',m,rate(m,col)) for m in M]
    t=pd.crosstab(df.marca,df[col]); print(' chi2 p=%.2g'%stats.chi2_contingency(t)[1])
print('reciclagem|coletada')
for m in M: print(' ',m,rate(m,'reciclagem_efetiva',lambda d:d.coleta_pos_consumo==1))
print('desm>1m2 etc skip')
# audited: chi2 for child labor
a=df[df.auditoria_fornecedor_realizada==1]
print(stats.chi2_contingency(pd.crosstab(a.marca,a.trabalho_infantil_constatado))[1], stats.chi2_contingency(pd.crosstab(a.marca,a.nao_conformidade_trabalhista))[1])
# audit rate Estacao vs others
print(stats.chi2_contingency(pd.crosstab(df.marca=='Estacao',df.auditoria_fornecedor_realizada))[1])
# pairwise Holm for key indicators vs Bravura
def pw(c,ref):
    r=[]
    for m in M:
        if m==ref: continue
        x=df[df.marca==ref][c]; y=df[df.marca==m][c]
        t=stats.ttest_ind(x,y,equal_var=False); d=x.mean()-y.mean()
        se=np.sqrt(x.var()/len(x)+y.var()/len(y)); dfw=se**4/((x.var()/len(x))**2/(len(x)-1)+(y.var()/len(y))**2/(len(y)-1))
        h=stats.t.ppf(.975,dfw)*se; r.append((m,d,d-h,d+h,t.pvalue))
    p=multipletests([x[4] for x in r],method='holm')[1]
    return pd.DataFrame([(a,round(b,2),round(c_,2),round(d_,2),pp) for (a,b,c_,d_,e),pp in zip(r,p)],columns=['vs','diff','lo','hi','holm'])
print(pw('co2e_total_g_pg','Bravura')); print(pw('co2e_total_g','Bravura'))
