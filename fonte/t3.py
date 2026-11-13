import pandas as pd, glob, numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests
df=pd.concat([pd.read_csv(f) for f in sorted(glob.glob('../dados/*.csv'))],ignore_index=True)
M=['Aurora','Bravura','Cerrado','Delta','Estacao','Flora','Granito','Horizonte']
a=df[df.auditoria_fornecedor_realizada==1]
def two(d,col,m1,m2):
    x=d[d.marca==m1][col]; y=d[d.marca==m2][col]
    p1,p2=x.mean(),y.mean(); n1,n2=len(x),len(y)
    se=np.sqrt(p1*(1-p1)/n1+p2*(1-p2)/n2); z=(p1-p2)
    pp=(x.sum()+y.sum())/(n1+n2); zs=z/np.sqrt(pp*(1-pp)*(1/n1+1/n2))
    return round(z*100,1),round((z-1.96*se)*100,1),round((z+1.96*se)*100,1),2*(1-stats.norm.cdf(abs(zs)))
for col,d in [('trabalho_infantil_constatado',a),('nao_conformidade_trabalhista',a),('reciclagem_efetiva',df)]:
    r=[(m,)+two(d,col,'Aurora',m) for m in M if m!='Aurora']
    p=multipletests([x[4] for x in r],method='holm')[1]
    print(col); [print(' ',x[:4],'holm=%.2g'%pp) for x,pp in zip(r,p)]
# Welch other indicators Aurora vs others per g
for c in ['agua_total_l','desmatamento_atribuido_m2','indice_efluentes_toxicos']:
    df[c+'_pg']=df[c]/df.massa_cafe_g
for c in ['agua_total_l_pg','desmatamento_atribuido_m2_pg','indice_efluentes_toxicos_pg','remuneracao_relativa_referencia']:
    r=[]
    for m in M:
        if m=='Aurora':continue
        x=df[df.marca=='Aurora'][c];y=df[df.marca==m][c];t=stats.ttest_ind(x,y,equal_var=False);r.append((m,round(x.mean()-y.mean(),3),t.pvalue))
    p=multipletests([z[2] for z in r],method='holm')[1]
    print(c,[(z[0],z[1],'%.1g'%pp) for z,pp in zip(r,p)])
# Estacao bounds & audit
print('Estacao TI bounds per capsule',36/640,(36+469)/640)
# sub-ref share
print((df.remuneracao_relativa_referencia<1).mean(), df.groupby('marca').apply(lambda g:(g.remuneracao_relativa_referencia<1).mean()).round(3).to_dict())
# pooled recycle|collect
c=df[df.coleta_pos_consumo==1]; print(c.reciclagem_efetiva.mean(), df[df.coleta_pos_consumo==0].reciclagem_efetiva.sum())
# Aurora vs Delta: CO2 per capsule & per g
print(df.groupby('marca').massa_embalagem_g.mean().round(2).to_dict())
# Aurora CO2 by component diff vs Bravura
print(df.groupby('marca')[['co2e_producao_g','co2e_logistica_g','co2e_fim_vida_g']].mean().round(1))
print(df.groupby('marca').apply(lambda g:(g.co2e_total_g/g.massa_cafe_g).std()).round(2).to_dict())
