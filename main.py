import streamlit as st
import pandas as pd
import os

from ipcp import base_transformacion, actualizacion, capitalizacion, actualizacion_y_capitalizacion, input_transformacion

file_dir = f'{os.getcwd()}/'

ipcp_base = pd.read_csv(f'{file_dir}ipcp.csv')

ipcp_base = base_transformacion(ipcp_base)

st.write("""
# My first app
Hello *world!*
""")
