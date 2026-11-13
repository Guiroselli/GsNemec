import pandas as pd, glob, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from statsmodels.stats.proportion import proportion_confint
plt.rcParams.update({'font.size':9,'font.family':'DejaVu Sans','axes.titlesize':9,'axes.labelsize':9,'xtick.labelsize':9,'ytick.labelsize':9,'legend.fontsize':9,'axes.spines.top':False,'axes.spines.right':False})
df=pd.concat([pd.read_csv(f) for f in sorted(glob.glob('../dados/dados/*.csv'))],ignore_index=True)
for c in ['co2e_total_g','agua_total_l','desmatamento_atribuido_m2','indice_efluentes_toxicos']: df[c+'_pg']=df[c]/df.massa_cafe_g
M=['Aurora','Bravura','Cerrado','Delta','Estacao','Flora','Granito','Horizonte']
NM={'Estacao':'Estação'}
lab=lambda m:NM.get(m,m)
lower={'co2':1,'agua':1,'desm':1,'efl':1,'rec':0,'ti':1,'nc':1,'rem':0}
def ind(d):
    a=d[d.auditoria_fornecedor_realizada==1]
    return pd.Series({'co2':d.co2e_total_g_pg.mean(),'agua':d.agua_total_l_pg.mean(),'desm':d.desmatamento_atribuido_m2_pg.mean(),'efl':d.indice_efluentes_toxicos_pg.mean(),'rec':d.reciclagem_efetiva.mean(),'ti':a.trabalho_infantil_constatado.mean(),'nc':a.nao_conformidade_trabalhista.mean(),'rem':d.remuneracao_relativa_referencia.mean()})
W={'Base (social 40%)':dict(co2=15,agua=10,desm=10,efl=10,rec=15,ti=20,nc=10,rem=10),'Pesos iguais':{k:12.5 for k in lower},'Ambiental (social 10%)':dict(co2=25,agua=15,desm=15,efl=15,rec=20,ti=4,nc=3,rem=3),'Social (social 72%)':dict(co2=8,agua=4,desm=4,efl=4,rec=8,ti=40,nc=20,rem=12)}
def score(I,w):
    Z=(I-I.mean())/I.std(ddof=0)
    for k in lower:
        if lower[k]: Z[k]=-Z[k]
    return sum(Z[k]*w[k] for k in lower)/sum(w.values())
I=df.groupby('marca').apply(ind); I.to_csv('ind.csv')
S=pd.DataFrame({n:score(I,w) for n,w in W.items()}); order=S.iloc[:,0].sort_values().index
fig,ax=plt.subplots(1,3,figsize=(7.08,1.95),gridspec_kw={'width_ratios':[1.25,1,1],'wspace':0.12})
a=ax[0]; mk=['o','s','^','D']; cols=['#1b4f72','#7f8c8d','#c0392b','#27ae60']
for i,m in enumerate(order):
    for j,n in enumerate(W): a.scatter(S.loc[m,n],i,marker=mk[j],color=cols[j],s=22,zorder=3,label=n if i==0 else None)
a.axvline(0,color='#999',lw=.7); a.set_yticks(range(8)); a.set_yticklabels([lab(m) for m in order]); a.set_xlabel('Escore (z médio pond.)'); a.set_title('A. Escore por esquema de pesos',loc='left',fontsize=9)
a.legend(loc='lower right',frameon=True,fontsize=7.5,borderpad=.3,labelspacing=.25,handletextpad=.2,bbox_to_anchor=(1.45,-0.02)) if False else None
a.grid(axis='x',lw=.3)
b=ax[1]; au=df[df.auditoria_fornecedor_realizada==1]
ord2=list(order)
for i,m in enumerate(ord2):
    x=au[au.marca==m].trabalho_infantil_constatado; k,n=int(x.sum()),len(x); lo,hi=proportion_confint(k,n,method='wilson'); p=k/n
    b.errorbar(p*100,i,xerr=[[ (p-lo)*100],[(hi-p)*100]],fmt='o',color='#c0392b' if m=='Estacao' else '#1b4f72',ms=4,capsize=2,lw=1)
    b.text(29,i,f'n={n}',va='center',fontsize=9)
b.set_yticks(range(8)); b.set_yticklabels([]); b.set_xlim(0,39); b.set_xlabel('% c/ trab. infantil\n(auditados; IC95%)'); b.set_title('B. Trabalho infantil',loc='left',fontsize=9); b.grid(axis='x',lw=.3)
c=ax[2]
y=np.arange(8); col=df.groupby('marca').coleta_pos_consumo.mean()*100; rec=df.groupby('marca').reciclagem_efetiva.mean()*100
c.barh(y+.2,[col[m] for m in ord2],height=.38,color='#bdc3c7',label='coletada'); c.barh(y-.2,[rec[m] for m in ord2],height=.38,color='#1b4f72',label='reciclada')
c.set_yticks(y); c.set_yticklabels([]); c.set_xlabel('% das cápsulas\n(n=640 cada)'); c.set_title('C. Coleta ≠ reciclagem',loc='left',fontsize=9); c.set_xlim(0,80)
fig.subplots_adjust(left=.115,right=.985,top=.91,bottom=.3)
fig.savefig('fig.png',dpi=300)
print(S.round(2)); print(order.tolist())
