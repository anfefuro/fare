import streamlit as st
import pandas as pd
import os

from ipcp import base_transformacion, actualizacion, capitalizacion, actualizacion_y_capitalizacion, input_transformacion

file_dir = f'{os.getcwd()}/'

ipcp_base = pd.read_csv(f'{file_dir}IPCP.csv')

ipcp_base = base_transformacion(ipcp_base)

st.write("""
# IPCP Calculadora
Hello *world!*
""")

# Mostrar las primeras 5 filas del documento base con streamlit
st.write("""Documento Base""")
st.write(ipcp_base.head(5))

st.title("Formulario dinámico")

# Inicializar el contador de bloques en session_state
if "num_bloques" not in st.session_state:
    st.session_state.num_bloques = 1

# Botón para agregar otro bloque
if st.button("➕ Agregar otro bloque"):
    st.session_state.num_bloques += 1

# Mostrar cada bloque de 3 inputs
for i in range(st.session_state.num_bloques):
    st.subheader(f"Bloque {i+1}")
    st.text_input(f"Nombre {i+1}", key=f"nombre_{i}")
    st.number_input(f"Edad {i+1}", key=f"edad_{i}", min_value=0, max_value=120)
    st.text_input(f"Ciudad {i+1}", key=f"ciudad_{i}")

# Botón para mostrar resultados
if st.button("📋 Mostrar datos ingresados"):
    datos = []
    for i in range(st.session_state.num_bloques):
        datos.append({
            "nombre": st.session_state[f"nombre_{i}"],
            "edad": st.session_state[f"edad_{i}"],
            "ciudad": st.session_state[f"ciudad_{i}"]
        })
    st.write(datos)



