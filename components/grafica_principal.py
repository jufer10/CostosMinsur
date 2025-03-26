import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from reading import DF_PV, DF_AC, DF_EV, BARRAS, MESES

#FASES

FASES =  DF_PV.dropna(subset=[1])['FASE'].tolist()
fase = st.sidebar.selectbox("Fase", ['Todas'] + FASES)


#FIGURA

fig = make_subplots(
    rows=2, cols=2,
    shared_yaxes=True,
    row_heights=[0.7, 0.3],
    column_widths=[0.06, 0.94],
    vertical_spacing=0.01,
    horizontal_spacing=0,
    specs=[
        [None, {"type": "xy", "secondary_y": True}],
        [{"type": "table"}, {"type": "table"}]
    ]
)

fig.update_layout(
    title= '📊 ANÁLISIS DE VALOR GANADO',
    height=800,
    legend_title="Leyenda",
    xaxis=dict(tickmode="linear", dtick=1)
)

# fig.update_layout(
#     title= '📊 ANÁLISIS DE VALOR GANADO',
#     xaxis_title="MES",
#     yaxis_title="ACUMULADO",
#     height=750,
#     legend_title="Leyenda",
#     xaxis=dict(tickmode="linear", dtick=1),
#     yaxis=dict(tickmode="linear", dtick=25000)
# )


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

fig.add_trace(go.Scatter(x=df_pv['MES'], y=df_pv['ACUMULADO'], mode='lines', name='PV', line=dict(color='blue')), secondary_y=True, row=1, col=2)
fig.add_trace(go.Scatter(x=df_ac['MES'], y=df_ac['ACUMULADO'], mode='lines', name='AC', line=dict(color='red')), secondary_y=True, row=1, col=2)
fig.add_trace(go.Scatter(x=df_ev['MES'], y=df_ev['ACUMULADO'], mode='lines', name='EV', line=dict(color='green')), secondary_y=True, row=1, col=2)


#BARRAS

df = BARRAS.melt(id_vars=['MODELO'], value_vars=[i for i in range(1, 32)], var_name='MES', value_name='VALOR')

df_plan = df.query('MODELO == "PLAN"')
df_actual = df.query('MODELO == "ACTUAL"')
df_earned = df.query('MODELO == "EARNED"')

if fase == 'Todas':
    fig.add_trace(go.Bar(x=df_plan['MES'], y=df_plan['VALOR'], name='PLANNED', marker_color='yellow'), row=1, col=2)
    fig.add_trace(go.Bar(x=df_actual['MES'], y=df_actual['VALOR'], name='EARNED', marker_color='grey'), row=1, col=2)
    fig.add_trace(go.Bar(x=df_earned['MES'], y=df_earned['VALOR'], name='ACTUAL', marker_color='orange'), row=1, col=2)


#TABLA

orden = ['ACUM PV', 'ACUM AC', 'ACUM EV', 'PLAN', 'EARNED', 'ACTUAL']

fig.add_trace(
    go.Table(
        header=dict(values=[""], align='center', fill_color='lightblue', height=50),
        cells=dict(
            values=[orden], align='center', fill_color='lightblue',
            font=dict(color=[["blue", "red", "green","yellow", "grey", "orange"]], weight="bold")
            )
    ),
    row=2, col=1
)


def format_thousands(x):
    return f"{round(x / 1000)}k" if pd.notnull(x) else x


df1 = df_pv.set_index("MES").T.drop(index='COSTO').map(format_thousands)
df2 = df_ac.set_index("MES").T.drop(index='COSTO').map(format_thousands)
df3 = df_ev.set_index("MES").T.drop(index='COSTO').map(format_thousands)

df = pd.concat([df1, df2, df3, BARRAS.drop(columns=['MODELO']).round(1)]).reset_index(drop=True).fillna("")

def obtener_str_mes(l1):
    f2 = MESES.loc[1,l1]
    return f2.strftime("%b").capitalize() + " " + f2.strftime("%Y")

fig.add_trace(
    go.Table(
        header=dict(
            values=[obtener_str_mes(l) for l in df.columns], 
            align='center', fill_color='lightblue', height=50,
            font=dict(color="black", weight="bold")
            ),
        cells=dict(values=[df[col] for col in df.columns], align='center'),
    ),
    row=2, col=2
)


#SHOW
st.plotly_chart(fig)