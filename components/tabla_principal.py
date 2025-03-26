import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from reading import DF_PV, DF_AC, DF_EV, BARRAS, MESES


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

def obtener_str_mes(l1):
    f1 = MESES.loc[0,l1]; f2 = MESES.loc[1,l1]
    str1 = f1.strftime("%b").capitalize() + " " + f1.strftime("%d")
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
