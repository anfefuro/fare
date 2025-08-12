import streamlit as st
import pandas as pd
import os

from ipcp import input_transformacion

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
    # La TRR tendran un valor por defecto de 4
    st.number_input(f"TRR {i+1}", key=f"trr_{i}", min_value=0, max_value=5, step=1, help="Ingrese el porcentaje de TRR, por ejemplo, 3 para 3%", value=4)

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
    
    # Convertir la lista de diccionarios en un DataFrame
    df = pd.DataFrame(datos)

    user_input = input_transformacion(df)

    st.write(user_input)

