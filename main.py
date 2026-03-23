import streamlit as st
import pandas as pd
import os
import io

from ipcp import input_transformacion, actualizacion, actualizacion_y_capitalizacion

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
    st.date_input(f"Fecha {idx+1}", key=f"fecha_{i}", min_value=pd.Timestamp('1954-08-01').date())
    # Agregar un checkbox para habilitar fecha IPCP
    fecha_ipcp = st.checkbox("📅 Fecha IPCP", key=f"fecha_check_{i}")
    
    # Si la fecha IPCP está habilitada, agregar un input para la fecha IPCP
    if fecha_ipcp:
        st.date_input(f"Fecha IPCP {idx+1}", key=f"fecha_ipcp_{i}", min_value=pd.Timestamp('1954-08-01').date())
    
    st.selectbox(f"Tipo {idx+1}", key=f"tipo_{i}", options=['Valor Fecha Corte', 'Valor Fecha Riesgo', 'Abono', 'Reintegro', 'Valor a Pagar', 'Valor Fecha Cobro', 'Valor a Pagar Recursos Propios', 'Abono Despues de Fecha Cobro'])
    # La TRR tendran un valor por defecto de 4
    st.number_input(f"TRR {idx+1}", key=f"trr_{i}", min_value=0, max_value=5, step=1, help="Ingrese el porcentaje de TRR, por ejemplo, 3 para 3%", value=4)

    # Al final de cada bloque, agregar un cuadro de texto donde el usuario pueda ingresar una descripción
    st.text_input(f"Descripción {idx+1}", key=f"descripcion_{i}", help="Descripción del movimiento")

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
            "fecha_check": st.session_state[f"fecha_check_{i}"],
            "fecha_ipcp": st.session_state[f"fecha_ipcp_{i}"] if st.session_state[f"fecha_check_{i}"] else pd.Timestamp('1954-08-01').date(),
            "tipo": st.session_state[f"tipo_{i}"],
            "trr": st.session_state[f"trr_{i}"],
            "descripcion": st.session_state[f"descripcion_{i}"]
        })
    
    # Convertir la lista de diccionarios en un DataFrame
    df = pd.DataFrame(datos)

    # Procesar los datos con la función input_transformacion
    resultado = input_transformacion(df)

    # Mostrar el resultado en la interfaz
    st.write(resultado)
    
    # Crear un buffer en memoria para el archivo Excel
    buffer = io.BytesIO()
    
    # Guardar el DataFrame en formato Excel
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        resultado.to_excel(writer, index=False, sheet_name='Resultados')
    
    # Establecer el puntero al inicio del buffer
    buffer.seek(0)
    
    # Agregar botón de descarga para el DataFrame de resultados en formato Excel
    st.download_button(
        label="💾 Descargar resultados (Excel)",
        data=buffer,
        file_name="resultados_ipcp.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# Botón para imprimir la página
if st.button("🖨️ Imprimir página"):
    st.write("Imprimiendo página...")
    # Aquí puedes agregar la lógica para imprimir la página, por ejemplo, usando JavaScript
    st.markdown("""
        <script>
            window.print();
        </script>
    """, unsafe_allow_html=True)


st.title("Calculadora de Actualización")

# Creamos un bloque más, pero aislado del resto
with st.container():
    # Este valor es un entero, sin embargo el usuario puede verlo en formato moneda con dos decimales
    st.number_input(f"Valor", key=f"valor", min_value=0, help="Ingrese el valor del evento, por ejemplo, 1000000 para 1000000.00")
    st.date_input(f"Fecha Inicial", key=f"fecha_inicial", min_value=pd.Timestamp('1954-08-01').date())
    # Agregar un checkbox para habilitar fecha IPCP
    fecha_ipcp = st.checkbox("📅 Fecha IPCP", key=f"fecha_check")
    
    # Si la fecha IPCP está habilitada, agregar un input para la fecha IPCP
    if fecha_ipcp:
        st.date_input(f"Fecha IPCP", key=f"fecha_ipcp", min_value=pd.Timestamp('1954-08-01').date())
    st.date_input(f"Fecha Final", key=f"fecha_final", min_value=pd.Timestamp('1954-08-01').date())

# Botón para mostrar resultados de actualización
if st.button("📋 Mostrar resultados de actualización"):
    # Obtener los valores de entrada
    valor = st.session_state["valor"]
    fecha_inicial = st.session_state["fecha_inicial"]
    fecha_check = st.session_state["fecha_check"]
    fecha_ipcp = st.session_state["fecha_ipcp"] if fecha_check else pd.Timestamp('1954-08-01').date()
    fecha_final = st.session_state["fecha_final"]

    # Llamar a la función de actualización
    actualizacion = actualizacion(valor, fecha_inicial, fecha_final, fecha_check, fecha_ipcp)

    # Mostrar el resultado de la actualización con un formato de texto grande y como moneda
    st.write(f"El valor actualizado es: **{actualizacion:,.2f}**")


st.title("Calculadora de Actualización y Capitalización")

with st.container():
    st.number_input("Valor", key="valor_ayc", min_value=0, help="Ingrese el valor del evento, por ejemplo, 1000000 para 1000000.00")
    st.date_input("Fecha Inicial", key="fecha_inicial_ayc", min_value=pd.Timestamp('1954-08-01').date())
    fecha_ipcp_ayc = st.checkbox("📅 Fecha IPCP", key="fecha_check_ayc")

    if fecha_ipcp_ayc:
        st.date_input("Fecha IPCP", key="fecha_ipcp_ayc", min_value=pd.Timestamp('1954-08-01').date())
    st.date_input("Fecha Final", key="fecha_final_ayc", min_value=pd.Timestamp('1954-08-01').date())
    st.number_input("TRR", key="trr_ayc", min_value=0, max_value=5, step=1, help="Ingrese el porcentaje de TRR, por ejemplo, 3 para 3%", value=4)

if st.button("📋 Mostrar resultados de actualización y capitalización"):
    valor_ayc = st.session_state["valor_ayc"]
    fecha_inicial_ayc = st.session_state["fecha_inicial_ayc"]
    fecha_check_ayc = st.session_state["fecha_check_ayc"]
    fecha_ipcp_ayc = st.session_state["fecha_ipcp_ayc"] if fecha_check_ayc else pd.Timestamp('1954-08-01').date()
    fecha_final_ayc = st.session_state["fecha_final_ayc"]
    trr_ayc = st.session_state["trr_ayc"]

    resultado_ayc = actualizacion_y_capitalizacion(valor_ayc, fecha_inicial_ayc, fecha_final_ayc, fecha_check_ayc, fecha_ipcp_ayc, trr_ayc)

    st.write(f"El valor actualizado y capitalizado es: **{resultado_ayc:,.2f}**")