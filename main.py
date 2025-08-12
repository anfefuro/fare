import streamlit as st
import pandas as pd

from ipcp import base_transformacion, actualizacion, capitalizacion, actualizacion_y_capitalizacion, input_transformacion

ipcp_base = pd.read_csv('ipcp.csv')

ipcp_base = base_transformacion(ipcp_base)

st.write("""
# My first app
Hello *world!*
""")
