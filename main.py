import streamlit as st
from components.grafica_principal import grafica_principal
from components.tabla_principal import tabla_principal

st.set_page_config(layout="wide")

st.header("📊 ANÁLISIS DE VALOR GANADO")
grafica_principal()
tabla_principal()
