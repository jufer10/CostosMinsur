import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
#import locale

from reading import DF_PV, DF_AC, DF_EV, BARRAS, MESES

#FASES

FASES =  DF_PV.dropna(subset=[1])['FASE'].tolist()
fase = st.sidebar.selectbox("Fase", ['Todas'] + FASES)


#FIGURA

# fig = make_subplots(
#     rows=2, cols=1,
#     shared_xaxes=True,
#     row_heights=[0.7, 0.3],
#     vertical_spacing=0.05,
#     specs=[[{"type": "bar"}], [{"type": "table"}]]
# )

fig = make_subplots(
    rows=2, cols=2,
    shared_xaxes=True,
    row_heights=[0.7, 0.3],
    column_widths=[0.05, 0.95],
    vertical_spacing=0.01,
    horizontal_spacing=0,
    specs=[
        [None, {"type": "xy"}],
        [{"type": "table"}, {"type": "table"}]
    ]
)


fig.update_layout(
    title= '📊 ANÁLISIS DE VALOR GANADO',
    xaxis_title="MES",
    yaxis_title="ACUMULADO",
    legend_title="Leyenda",
    xaxis=dict(tickmode="linear", dtick=1),
    yaxis=dict(tickmode="linear", dtick=25000)
)


#CURVAS

def obtener_df_curva(DF, fase='Todas'):
    df=DF.dropna(subset=[1])
    
    if DF is DF_PV: cols = [i for i in range(1, 32)]
    else: cols = [i for i in range(1, 23)]
    
    df = df.melt(id_vars=['FASE'], value_vars=cols, var_name='MES', value_name='COSTO')
    df['MES'] = df['MES'].astype(int)
    
    if fase == 'Todas': pass
    else: df = df[df['FASE'] == fase]
    
    df = df[['MES', 'COSTO']].groupby('MES', as_index=False)['COSTO'].sum()
    df['ACUMULADO'] = df['COSTO'].cumsum()
    
    return df
    
df_pv = obtener_df_curva(DF_PV, fase)
df_ac = obtener_df_curva(DF_AC, fase)
df_ev = obtener_df_curva(DF_EV, fase)

fig.add_trace(go.Scatter(x=df_pv['MES'], y=df_pv['ACUMULADO'], mode='lines', name='PV', line=dict(color='blue')), row=1, col=2)
fig.add_trace(go.Scatter(x=df_ac['MES'], y=df_ac['ACUMULADO'], mode='lines', name='AC', line=dict(color='red')), row=1, col=2)
fig.add_trace(go.Scatter(x=df_ev['MES'], y=df_ev['ACUMULADO'], mode='lines', name='EV', line=dict(color='green')), row=1, col=2)


#BARRAS

df = BARRAS.melt(id_vars=['MODELO'], value_vars=[i for i in range(1, 32)], var_name='MES', value_name='VALOR')
df['VALOR'] = df['VALOR'] * 10000

df_plan = df.query('MODELO == "PLAN"')
df_actual = df.query('MODELO == "ACTUAL"')
df_earned = df.query('MODELO == "EARNED"')

if fase == 'Todas':
    fig.add_trace(go.Bar(x=df_plan['MES'], y=df_plan['VALOR'], name='PLANNED', marker_color='yellow'), row=1, col=2)
    fig.add_trace(go.Bar(x=df_actual['MES'], y=df_actual['VALOR'], name='EARNED', marker_color='grey'), row=1, col=2)
    fig.add_trace(go.Bar(x=df_earned['MES'], y=df_earned['VALOR'], name='ACTUAL', marker_color='orange'), row=1, col=2)


#TABLA

# df1 = df_pv.set_index("MES").T; df1['MODELO'] = ['PV', 'ACUM PV']

# df2 = df_ac.set_index("MES").T; df2['MODELO'] = ['AC', 'ACUM AC']

# df3 = df_ev.set_index("MES").T; df3['MODELO'] = ['EV', 'ACUM EV']

# df = pd.concat([df1, df2, df3, BARRAS]).reset_index(drop=True)

# order = ['PV', 'AC', 'EV', 'ACUM PV', 'ACUM AC', 'ACUM EV', 'PLAN', 'EARNED', 'ACTUAL',]

df1 = df_pv.set_index("MES").T.drop(index='COSTO')
df2 = df_ac.set_index("MES").T.drop(index='COSTO')
df3 = df_ev.set_index("MES").T.drop(index='COSTO')

df = pd.concat([df1, df2, df3, BARRAS.drop(columns=['MODELO'])]).reset_index(drop=True)

orden = ['ACUM PV', 'ACUM AC', 'ACUM EV', 'PLAN', 'EARNED', 'ACTUAL']

fig.add_trace(
    go.Table(
        header=dict(values=[''], align='center', fill_color='lightblue'),
        cells=dict(values=[orden], align='center')
    ),
    row=2, col=1
)

def format(x):
    return f"{x:.2f}" if pd.notna(x) else x
#df = df.applymap(format)

fig.add_trace(
    go.Table(
        header=dict(values=list(range(1, 32)), align='center', fill_color='lightblue'),
        cells=dict(values=[df[col] for col in df.columns], align='center')
    ),
    row=2, col=2
)



#SHOW
fig.update_layout(height=750)
st.plotly_chart(fig)


###########################################################################################

def obtener_df_tabla(DF: pd.DataFrame, modelo: str):
    df= DF.dropna(subset=[1])
    
    if DF is DF_PV: cols = [i for i in range(1, 32)]
    else: cols = [i for i in range(1, 23)]
    
    df = df.melt(id_vars=['FASE', 'DESCRIPCION'], value_vars=cols, var_name='MES', value_name='COSTO')
    df['MES'] = df['MES'].astype(int)
    df['ACUMULADO'] = df['COSTO'].cumsum()
    df['MODELO'] = modelo
    df=df.replace(0, pd.NA)
    
    return df

df_pv = obtener_df_tabla(DF_PV, 'PV')
df_ac = obtener_df_tabla(DF_AC, 'AC')
df_ev = obtener_df_tabla(DF_EV, 'EV')


df = pd.concat([df_ev, df_ac, df_pv])

df = df.pivot(index=['FASE', 'DESCRIPCION'], columns=['MES', 'MODELO'], values='COSTO')
df = df.sort_index(axis=1, level=[0, 1])

#locale.setlocale(locale.LC_TIME, "Spanish_Spain.1252")

def obtener_str_mes(l1):
    f1 = MESES.loc[0,l1]; f2 = MESES.loc[1,l1]
    str1 = f1.strftime("%b").capitalize() + " " + f1.strftime("%d") + ", " + f1.strftime("%Y")
    str2 = f2.strftime("%b").capitalize() + " " + f2.strftime("%d") + ", " + f2.strftime("%Y")
    return "MES "+ str(l1) + ", " + str1 + " - " + str2

df.columns = pd.MultiIndex.from_tuples([(obtener_str_mes(l1), l2) for l1, l2 in df.columns])


def format(x):
    return f"{x:,.2f}".replace(",", " ") if pd.notna(x) else x
df = df.applymap(format)


st.dataframe(df, height=700, column_config={
        "PV": st.column_config.Column(width=100),
        "AC": st.column_config.Column(width=100),
        "EV": st.column_config.Column(width=100)
    })

