import pandas as pd
import streamlit as st
import pickle
import numpy as np

with open('pkl_dis.pkl', 'rb') as pdis:
    model_dis = pickle.load(pdis)

with open('pkl_dur.pkl', 'rb') as pdur:
    model_dur = pickle.load(pdur)

with open('pkl_rate.pkl', 'rb') as prate:
    model_rate = pickle.load(prate)

with open('pkl_tolls.pkl', 'rb') as ptolls:
    model_tolls = pickle.load(ptolls)

with open('pkl_air.pkl', 'rb') as pair:
    model_air = pickle.load(pair)

with open('pkl_lin.pkl', 'rb') as plin:
    model_lin = pickle.load(plin)

df = pd.read_parquet('taxi_trip.parquet', 'pyarrow')
zones_lookup = pd.read_parquet('zones.parquet', 'pyarrow')
data = {zones_lookup.Zone[i] : zones_lookup.LocationID[i] for i in range(len(zones_lookup.LocationID))}

def fare(est_fare):
    return 'Valor: {:.2f} USD'.format(est_fare)

def main():
    st.title('Tarifa Estimada')

    st.sidebar.header('Parametros del viaje')

    option = list(zones_lookup.Zone)
    hour = list(range(0, 24))
    pu_location = st.sidebar.selectbox('Origen', option)
    do_location = st.sidebar.selectbox('Destino', option)
    trip_hour = st.sidebar.selectbox('Hora del viaje', hour)

    val = np.array([data[pu_location], data[do_location], hour[trip_hour]])
    if st.button('Mostrar'):
        try:
            val_def = np.array([
                df[(df['PULocationID'] == val[0]) & (df['DOLocationID'] == val[1])]['Trip_Distance'].mean(),
                df[(df['PULocationID'] == val[0]) & (df['DOLocationID'] == val[1])]['Duration_Secs'].mean(),
                df[(df['PULocationID'] == val[0]) & (df['DOLocationID'] == val[1])]['RatecodeID_ml'].median(),
                df[(df['PULocationID'] == val[0]) & (df['DOLocationID'] == val[1])]['Tolls_Amount'].median(),
                df[(df['PULocationID'] == val[0]) & (df['DOLocationID'] == val[1])]['Airport_Fee_ml'].median()
            ])
            st.success(fare(round(model_lin.predict(val_def.reshape(1,-1))[0], 2)))

        except:
            val_def = np.array([
                model_dis.predict(val.reshape(1,-1))[0],
                model_dur.predict(val.reshape(1,-1))[0],
                model_rate.predict(val.reshape(1,-1))[0],
                model_tolls.predict(val.reshape(1,-1))[0],
                model_air.predict(val.reshape(1,-1))[0]
            ])
            st.success(fare(round(model_lin.predict(val_def.reshape(1,-1))[0], 2)))

    with st.expander('Contexto'):
        st.write('Modelo general')
        st.image('./assets/General.png')
        st.write('Modelos generadores de parámetros')
        st.image('./assets/Condicionales.png')

if __name__ == '__main__':
    main()