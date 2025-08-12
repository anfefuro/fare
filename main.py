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
    # Este valor es un entero, sin embargo el usuario puede verlo en formato moneda con dos decimales
    st.number_input(f"Valor {i+1}", key=f"valor_{i}", min_value=0, help="Ingrese el valor del evento, por ejemplo, 1000000 para 1000000.00")
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

import locale

# Configurar formato local (cambia 'es_CO.UTF-8' según tu región)
locale.setlocale(locale.LC_ALL, 'es_CO.UTF-8')

st.title("Entrada con formato moneda")

# Recuperar valor anterior (para que persista)
if "monto_str" not in st.session_state:
    st.session_state.monto_str = ""

# Input de texto para simular number_input con formato
monto_str = st.text_input(
    "Monto",
    value=st.session_state.monto_str,
    key="monto_str"
)

# Quitar caracteres no numéricos para convertir
valor_numerico = monto_str.replace("$", "").replace(".", "").replace(",", ".").replace("'", "").strip()

try:
    monto_float = float(valor_numerico) if valor_numerico else 0.0
except ValueError:
    monto_float = 0.0

# Formatear en estilo moneda
if monto_str:
    monto_formateado = locale.currency(monto_float, grouping=True)
    st.session_state.monto_str = monto_formateado

st.write(f"💾 Valor como float: {monto_float}")



