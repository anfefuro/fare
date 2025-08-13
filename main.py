import streamlit as st
import pandas as pd
import os

from ipcp import input_transformacion

st.title("IPCP Calculadora")

# Inicializar el contador de bloques en session_state
if "num_bloques" not in st.session_state:
    st.session_state.num_bloques = 1

# Inicializar la lista de índices de eventos si no existe
if "indices_eventos" not in st.session_state:
    st.session_state.indices_eventos = list(range(st.session_state.num_bloques))

# Función para eliminar un evento
def eliminar_evento(indice_a_eliminar):
    # Obtener la lista actual de índices
    indices_actuales = st.session_state.indices_eventos.copy()
    # Eliminar el índice del evento a eliminar
    indices_actuales.remove(indice_a_eliminar)
    # Actualizar la lista de índices
    st.session_state.indices_eventos = indices_actuales
    # Reducir el contador de bloques
    st.session_state.num_bloques -= 1

# Mostrar cada bloque de inputs
for idx, i in enumerate(st.session_state.indices_eventos):
    col1, col2 = st.columns([0.95, 0.05])
    
    with col1:
        st.subheader(f"Movimiento {idx+1}")
    
    with col2:
        # Botón de eliminar con icono de bote de basura
        if st.button("🗑️", key=f"eliminar_{i}"):
            eliminar_evento(i)
            st.rerun()
    
    # Este valor es un entero, sin embargo el usuario puede verlo en formato moneda con dos decimales
    st.number_input(f"Valor {idx+1}", key=f"valor_{i}", min_value=0, help="Ingrese el valor del evento, por ejemplo, 1000000 para 1000000.00")
    st.date_input(f"Fecha {idx+1}", key=f"fecha_{i}", min_value=pd.Timestamp('1950-01-01'))
    st.selectbox(f"Tipo {idx+1}", key=f"tipo_{i}", options=['Inicial', 'Pension', 'Abono', 'Reintegro', 'Pago'])
    # La TRR tendran un valor por defecto de 4
    st.number_input(f"TRR {idx+1}", key=f"trr_{i}", min_value=0, max_value=5, step=1, help="Ingrese el porcentaje de TRR, por ejemplo, 3 para 3%", value=4)

# Botón para agregar otro bloque
if st.button("➕ Agregar movimiento"):
    # Agregar un nuevo índice (mayor que los existentes)
    nuevo_indice = max(st.session_state.indices_eventos + [-1]) + 1
    st.session_state.indices_eventos.append(nuevo_indice)
    st.session_state.num_bloques += 1

# Botón para mostrar resultados
if st.button("📋 Mostrar datos ingresados"):
    datos = []
    for i in st.session_state.indices_eventos:
        datos.append({
            "valor": st.session_state[f"valor_{i}"],
            "fecha": st.session_state[f"fecha_{i}"],
            "tipo": st.session_state[f"tipo_{i}"],
            "trr": st.session_state[f"trr_{i}"],
        })
    
    # Convertir la lista de diccionarios en un DataFrame
    df = pd.DataFrame(datos)

    # Procesar los datos con la función input_transformacion
    resultado = input_transformacion(df)

    # Mostrar el resultado en la interfaz
    st.write(resultado)
    
    # Agregar botón de descarga para el DataFrame de resultados
    csv = resultado.to_csv(index=False)
    st.download_button(
        label="💾 Descargar resultados",
        data=csv,
        file_name="resultados_ipcp.csv",
        mime="text/csv",
    )

