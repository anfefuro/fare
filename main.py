import streamlit as st
import pandas as pd
import os

from ipcp import base_transformacion, actualizacion, capitalizacion, actualizacion_y_capitalizacion, input_transformacion

file_dir = f'{os.getcwd()}/'

ipcp_base = pd.read_csv(f'{file_dir}IPCP.csv')

ipcp_base = base_transformacion(ipcp_base)

st.title("IPCP Calculadora")

# Inicializar el contador de bloques en session_state
if "num_bloques" not in st.session_state:
    st.session_state.num_bloques = 1

# Botón para agregar otro bloque
if st.button("➕ Agregar evento"):
    st.session_state.num_bloques += 1

# Mostrar cada bloque de 3 inputs
for i in range(st.session_state.num_bloques):
    st.subheader(f"Evento {i+1}")
    st.text_input(f"Valor {i+1}", key=f"valor_{i}")
    # Permitir fechas desde 1950
    st.date_input(f"Fecha {i+1}", key=f"fecha_{i}", min_value=pd.Timestamp('1950-01-01'))
    st.selectbox(f"Tipo {i+1}", key=f"tipo_{i}", options=['Inicial', 'Pension', 'Abono', 'Reintegro', 'Pago'])
    st.number_input(f"TRR {i+1}", key=f"trr_{i}", min_value=0, max_value=5, step=1, help="Ingrese el porcentaje de TRR, por ejemplo, 3 para 3%")


# Botón para mostrar resultados
if st.button("📋 Mostrar datos ingresados"):
    datos = []
    for i in range(st.session_state.num_bloques):
        datos.append({
            "valor": st.session_state[f"valor_{i}"],
            "fecha": st.session_state[f"fecha_{i}"],
            "tipo": st.session_state[f"tipo_{i}"],
            "trr": st.session_state[f"trr_{i}"],
        })
    st.write(datos)



