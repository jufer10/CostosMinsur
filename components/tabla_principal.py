import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, JsCode

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from reading import DF_PV, DF_AC, DF_EV, FASES, MESES


# def obtener_df_tabla(DF: pd.DataFrame, modelo: str):
#     df= DF.dropna(subset=[1])
    
#     if DF is DF_PV: cols = [i for i in range(1, 32)]
#     else: cols = [i for i in range(1, 23)]
    
#     df = df.melt(id_vars=['FASE', 'DESCRIPCION'], value_vars=cols, var_name='MES', value_name='COSTO')
#     df['MES'] = df['MES'].astype(int)
#     df['ACUMULADO'] = df['COSTO'].cumsum()
#     df['MODELO'] = modelo
#     df=df.replace(0, pd.NA)
    
#     return df

# df_pv = obtener_df_tabla(DF_PV, 'PV')
# df_ac = obtener_df_tabla(DF_AC, 'AC')
# df_ev = obtener_df_tabla(DF_EV, 'EV')


# df = pd.concat([df_ev, df_ac, df_pv])

# st.dataframe(df)

# df = df.pivot(index=['FASE', 'DESCRIPCION'], columns=['MES', 'MODELO'], values='COSTO')
# df = df.sort_index(axis=1, level=[0, 1])

# def obtener_str_mes(l1):
#     f1 = MESES.loc[0,l1]; f2 = MESES.loc[1,l1]
#     str1 = f1.strftime("%b").capitalize() + " " + f1.strftime("%d")
#     str2 = f2.strftime("%b").capitalize() + " " + f2.strftime("%d") + ", " + f2.strftime("%Y")
#     return "MES "+ str(l1) + ", " + str1 + " - " + str2

# df.columns = pd.MultiIndex.from_tuples([(obtener_str_mes(l1), l2) for l1, l2 in df.columns])


# def format(x):
#     return f"{x:,.2f}".replace(",", " ") if pd.notna(x) else x
# df = df.applymap(format)


# st.dataframe(df, height=700, column_config={
#         "PV": st.column_config.Column(width=100),
#         "AC": st.column_config.Column(width=100),
#         "EV": st.column_config.Column(width=100)
#     })

#DF FASES
















#DF VALORES

def obtener_df_tabla(DF: pd.DataFrame, modelo: str):
    df= DF.dropna(subset=[1])
    
    if DF is DF_PV: cols = [i for i in range(1, 32)]
    else: cols = [i for i in range(1, 23)]
    
    df = df.melt(id_vars=['FASE'], value_vars=cols, var_name='MES', value_name='COSTO')
    df['MES'] = df['MES'].astype(int)
    df['ACUMULADO'] = df['COSTO'].cumsum()
    df['MODELO'] = modelo
    df=df.replace(0, pd.NA)
    
    return df

df_pv = obtener_df_tabla(DF_PV, 'PV')
df_ac = obtener_df_tabla(DF_AC, 'AC')
df_ev = obtener_df_tabla(DF_EV, 'EV')


df = pd.concat([df_ev, df_ac, df_pv]).reset_index(drop=True)
df['MES'] = df['MES'].astype(str).str.zfill(2) + "_" + df['MODELO']
df = df.pivot(index=["FASE"], columns=['MES'], values='COSTO').reset_index()



#######################################################
#Añadir fases padre

df1 = pd.merge(df, FASES[["FASE", 'PADRE']], on='FASE').drop(columns=['FASE'])
df1 = df1.groupby(['PADRE']).sum().reset_index().rename(columns={"PADRE": "FASE"})
df = pd.concat([df, df1])

for i in range(2):
    df1 = pd.merge(df1, FASES[["FASE", 'PADRE']], on='FASE').drop(columns=['FASE'])
    df1 = df1.groupby(['PADRE']).sum().reset_index().rename(columns={"PADRE": "FASE"})
    df = pd.concat([df, df1])



#################################################
#Crear columna String

df2 = FASES[['FASE','PADRE','DESCRIPCION']].astype(str).replace("nan", None)

parent_map = dict(zip(df2["FASE"], df2["PADRE"]))

def get_hierarchy(code):
    hierarchy = []
    while code:
        hierarchy.insert(0, code)
        code = parent_map.get(code)
    return "/".join(hierarchy)

df2["HERARQUIA"] = df2["FASE"].apply(get_hierarchy)
df = pd.merge(df, df2, on='FASE').drop(columns=['FASE', 'PADRE'])



#####################################################
# Aggrid
df = df.map(lambda x: round(x) if isinstance(x, (int, float)) else x)

gb = GridOptionsBuilder.from_dataframe(df)

gridOptions = gb.build()

gridOptions["defaultColDef"] = {"sortable": False}
gridOptions["animateRows"] = True
gridOptions["treeData"]=True
gridOptions["autoGroupColumnDef"]= {
    "headerName": 'FASE', "minWidth": 300,
    "cellRendererParams": {"suppressCount": True}
  }
gridOptions["getDataPath"]=JsCode("""function(data){ return data.HERARQUIA.split("/"); }""").js_code


def obtener_str_mes(l1):
    f1 = MESES.loc[0,l1]; f2 = MESES.loc[1,l1]
    str1 = f1.strftime("%b").capitalize() + " " + f1.strftime("%d")
    str2 = f2.strftime("%b").capitalize() + " " + f2.strftime("%d") + ", " + f2.strftime("%Y")
    return "MES "+ str(l1) + ", " + str1 + " - " + str2

columns = [f"{i}_{letter}" for i in range(1, 32) for letter in ["EV", "AC", "PV"]]
column_groups = {}
for col in df.columns:
    if col == 'DESCRIPCION' or col == 'HERARQUIA': continue
    group, sub_col = col.split("_")
    group = obtener_str_mes(int(group))
    if group not in column_groups:
        column_groups[group] = []
    column_groups[group].append({"headerName": sub_col, "field": col})

# Crear la estructura de columnas en AgGrid
column_defs = [{"headerName": "DESCRIPCION", "field": "DESCRIPCION"}]+[
    {"headerName": group, "children": children} for group, children in column_groups.items()
]

gb.configure_grid_options(columnDefs = column_defs)
gb.configure_grid_options(domLayout='autoHeight')


# gb.configure_grid_options(
#     columnDefs=[
#         {"headerName": "DESCRIPCION", "field": "DESCRIPCION"},
#         {
#             "headerName": "1",
#             "children": [
#                 {"headerName": "PV", "field": "1_PV"},
#                 {"headerName": "AC", "field": "1_PV"}
#             ]
#         }
#     ]
# )

r = AgGrid(
    df,
    gridOptions=gridOptions,
    allow_unsafe_jscode=True,
    enable_enterprise_modules=True,
    filter=True,
    tree_data=True
)



























# df=pd.DataFrame([
#     {"orgHierarchy": 'A', "jobTitle": "CEO", "employmentType": "Permanent" },
#     { "orgHierarchy": 'A/B', "jobTitle": "VP", "employmentType": "Permanent" },
#     { "orgHierarchy": 'A/B/C', "jobTitle": "VP", "employmentType": "Permanent" }
#     ])
# st.dataframe(df)

# gb = GridOptionsBuilder.from_dataframe(df)
# gridOptions = gb.build()

# gridOptions["treeData"]=True
# gridOptions["getDataPath"]=JsCode("""function(data){ return data.orgHierarchy.split("/"); }""").js_code

# r = AgGrid(
#     df,
#     gridOptions=gridOptions,
#     allow_unsafe_jscode=True,
#     enable_enterprise_modules=True,
#     filter=True,
#     tree_data=True
# )



