import pandas as pd
import os
import numpy as np

def base_transformacion(dataFrame):

    ipcp_base = dataFrame.copy()

    ipcp_base = ipcp_base[['PERIODO(DD-MM-AAAA)','VALOR IPC','VALOR IPCP','FECHA INICIO','FECHA FINAL','VALOR IPCP.1','VALOR IPCP-1']]
    ipcp_base.rename(columns={
        'PERIODO(DD-MM-AAAA)':'periodo',
        'VALOR IPC':'ipc',
        'VALOR IPCP':'ipcp',
        'FECHA INICIO':'fecha_inicio',
        'FECHA FINAL':'fecha_final',
        'VALOR IPCP.1':'ipcp.1',
        'VALOR IPCP-1':'ipcp-1'
    }, inplace=True)

    # ------ CAMBIOS BASE --------
    # Transformar la columna Periodo a fecha con formato date %Y-%m-%d
    ipcp_base['periodo'] = pd.to_datetime(ipcp_base['periodo'], format='%d/%m/%Y')
    ipcp_base['fecha_inicio'] = pd.to_datetime(ipcp_base['fecha_inicio'], format='%d/%m/%Y')
    ipcp_base['fecha_final'] = pd.to_datetime(ipcp_base['fecha_final'], format='%d/%m/%Y')
    # Formato de las columnas VALOR IPCP, VALOR IPCP.1, VALOR IPCP-1
    ipcp_base['ipcp'] = ipcp_base['ipcp'].str.replace(',', '').astype(float)
    ipcp_base['ipcp.1'] = ipcp_base['ipcp.1'].str.replace(',', '.').astype(float)
    ipcp_base['ipcp-1'] = ipcp_base['ipcp-1'].str.replace(',', '.').astype(float)

    # Calculo de IPCP 12 meses
    ipcp_base['ipc'] = pd.to_numeric(ipcp_base['ipc'].str.replace(',', '.'), errors='coerce')
    ipcp_base['ipc_calc'] = 1 + (ipcp_base['ipc'] / 100)

    ipcp_12m_values = []
    ipcp_values = ipcp_base['ipc_calc'].values

    for i in range(len(ipcp_values)):
      value = math.prod(ipcp_values[i:i+12])
      ipcp_12m_values.append(value)

    ipcp_base['ipc_calc'] = ipcp_12m_values

    return ipcp_base

file_dir = f'{os.getcwd()}/'

ipcp_base = pd.read_csv(f'{file_dir}IPCP.csv')

ipcp_base = base_transformacion(ipcp_base)

def actualizacion(valor_actualizar, fecha_inicial, fecha_final, fecha_check, fecha_ipcp):

  # Valores usuario
  valor_actualizar = float(valor_actualizar)
  # Variable instanciada como fecha
  fecha_inicial = pd.to_datetime(fecha_inicial) # '1995-04-28 00:00:00'
  fecha_final = pd.to_datetime(fecha_final) # '2024-01-30 00:00:00'
  # fecha_ipc_actualizar = pd.to_datetime('2023-12-31 00:00:00')
  # Valores de fecha truncados a mes
  fecha_inicial_mes = fecha_inicial.to_period('M').to_timestamp()
  fecha_final_mes = fecha_final.to_period('M').to_timestamp()
  # fecha_ipc_actualizar_mes = fecha_ipc_actualizar.to_period('M').to_timestamp()

  if fecha_check:
    fecha_ipcp = pd.to_datetime(fecha_ipcp)
    fecha_ipcp_mes = fecha_ipcp.to_period('M').to_timestamp()
  else:
    fecha_ipcp_mes = fecha_final_mes

  # Definición de variables
  # Valor a actualizar (En este ejemplo son $100.000)
  b1 = valor_actualizar

  # IPCP del mes anterior a la Fecha Final (En este ejemplo es el IPCP de diciembre de 2023)
  fecha_final_menos_un_mes = fecha_ipcp_mes - pd.DateOffset(months=1)
  IPCPf = ipcp_base[ipcp_base['fecha_inicio'] == fecha_final_menos_un_mes]['ipcp'].values[0]

  # IPCP del mes Fecha Final (En este caso el IPCP de enero de 2024)
  IPCPaltf = ipcp_base[ipcp_base['fecha_inicio'] == fecha_ipcp_mes]['ipcp'].values[0]

  # Es el # de dias Calendario que tiene el mes de Fecha Final (En este caso son 31 dias (Enero 2024), en la formula se obtiene de la Hoja DiasMes)
  inicio_mes_final = ipcp_base[ipcp_base['fecha_inicio'] == fecha_final_mes]['fecha_inicio'].values[0]
  fin_mes_final = ipcp_base[ipcp_base['fecha_inicio'] == fecha_final_mes]['fecha_final'].values[0]
  Dmf = int((fin_mes_final - inicio_mes_final) / np.timedelta64(1, 'D')) + 1

  # Son los dias del mes final posterior al primer dia (En este caso, al ser 30 de enero; se calculan esos 30 dias adicionales de IPCP)
  df = int((fecha_final - inicio_mes_final) / np.timedelta64(1, 'D')) + 1

  # IPCP del mes anterior a la Inicial (En este ejemplo es el IPCP de marzo de 1995)
  fecha_inicial_menos_un_mes = fecha_inicial_mes - pd.DateOffset(months=1)
  IPCPi = ipcp_base[ipcp_base['fecha_inicio'] == fecha_inicial_menos_un_mes]['ipcp'].values[0]

  # IPCP del mes Fecha Inicial (En este caso el IPCP de abril de 1995)
  IPCPalti = ipcp_base[ipcp_base['fecha_inicio'] == fecha_inicial_mes]['ipcp'].values[0]

  # Es el # de dias Calendario que tiene el mes de Fecha Inicial (En este caso son 30 dias (Abril 1995), en la formula se obtiene de la Hoja DiasMes)
  inicio_mes_inicial = ipcp_base[ipcp_base['fecha_inicio'] == fecha_inicial_mes]['fecha_inicio'].values[0]
  fin_mes_inicial = ipcp_base[ipcp_base['fecha_inicio'] == fecha_inicial_mes]['fecha_final'].values[0]
  Dmi = int((fin_mes_inicial - inicio_mes_inicial) / np.timedelta64(1, 'D')) + 1

  # Son los dias del mes inicial posterior al primer dia (En este caso, al ser 28 de abril; se calculan esos 28 dias adicionales de IPCP)
  di = int((fecha_inicial - inicio_mes_inicial) / np.timedelta64(1, 'D')) + 1

  VIPCm = ipcp_base[ipcp_base['fecha_inicio'] == fecha_ipcp_mes]['ipc_calc'].values[0]

  # print(
  #     f'IPCPf: {IPCPf}\n',
  #     f'IPCPaltf: {IPCPaltf}\n',
  #     f'Dmf: {Dmf}\n',
  #     f'df: {df}\n',
  #     f'IPCPi: {IPCPi}\n',
  #     f'IPCPalti: {IPCPalti}\n',
  #     f'Dmi: {Dmi}\n',
  #     f'di: {di}'
  # )

  if fecha_check:
    
    IPCPaltf = IPCPf * (((1 + (VIPCm / 100)) * (1 / 12)) - 1)

    num = IPCPf + (((IPCPaltf - IPCPf) / Dmf) * df)
    den = IPCPi + (((IPCPalti - IPCPi) / Dmi) * di)

    valor_actualizado = b1 * (num / den)
    valor_actualizado = round(valor_actualizado, 2)

    return valor_actualizado
  else:
    num = IPCPf + (((IPCPaltf - IPCPf) / Dmf) * df)
    den = IPCPi + (((IPCPalti - IPCPi) / Dmi) * di)

    valor_actualizado = b1 * (num / den)
    valor_actualizado = round(valor_actualizado, 2)

    return valor_actualizado

def capitalizacion(valor_capitalizar, TRR, fecha_inicial, fecha_final, fecha_check, fecha_ipcp):

  # Valores Usuario
  valor_capitalizar = float(valor_capitalizar)
  fecha_inicial = pd.to_datetime(fecha_inicial)
  fecha_final = pd.to_datetime(fecha_final)
  TRR = TRR

  # Variables
  # Valor a Actualizar (En este ejemplo son $100.000)
  B1 = valor_capitalizar
  # Tasa de Rendimiento (Puede ser 3% o 4%) (Se expresa como entero pues en la formula se convierte en porcentaje al dividir en 100)
  B4 = TRR
  # Fecha Final ("En este caso excel no cuenta el primer dia, por tanto si se resta (31/12/2025-01/01/2025) es igual a 364 y no 365, y así lo calcula el MinHacienda")
  B3 = fecha_final
  # Fecha Inicial
  B2 = fecha_inicial
  # Calculo del exponente
  exp = int((B3 - B2) / np.timedelta64(1, 'D'))

  print(
      f'B1: {B1}\n'
      f'B2: {B2}\n'
      f'B3: {B3}\n'
      f'B4: {B4}\n'
      f'exp: {exp}'
  )

  exp_cal = exp / 365.25
  valor_capitalizado = B1 * ((1 + (B4 / 100)) ** exp_cal)
  valor_capitalizado = round(valor_capitalizado, 2)

  return valor_capitalizado

def actualizacion_y_capitalizacion(valor_actualizar_capitalizar, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, TRR):

  # Valores usuario
  valor_actualizar_capitalizar = float(valor_actualizar_capitalizar)
  fecha_inicial = pd.to_datetime(fecha_inicial)
  fecha_final = pd.to_datetime(fecha_final)
  TRR = float(TRR)
  # Valores de fecha truncados a mes
  fecha_inicial_mes = fecha_inicial.to_period('M').to_timestamp()
  fecha_final_mes = fecha_final.to_period('M').to_timestamp()

  if fecha_check:
    fecha_ipcp = pd.to_datetime(fecha_ipcp)
    fecha_ipcp_mes = fecha_ipcp.to_period('M').to_timestamp()
  else:
    fecha_ipcp_mes = fecha_inicial_mes

  # Valor a Actualizar (En este ejemplo son $4.000.000)
  B1 = valor_actualizar_capitalizar

  # IPCP del mes anterior a la Fecha Final (En este ejemplo es el IPCP de mayo de 2024)
  fecha_final_menos_un_mes = fecha_final_mes - pd.DateOffset(months=1)
  IPCP_yf_mf = ipcp_base[ipcp_base['fecha_inicio'] == fecha_final_menos_un_mes]['ipcp'].values[0]

  # IPCP del mes Fecha Final (En este caso el IPCP de junio de 2024)
  IPCPsig_yf_mf = ipcp_base[ipcp_base['fecha_inicio'] == fecha_final_mes]['ipcp'].values[0]

  # Es el # de dias Calendario que tiene el mes de Fecha Final ("En este caso son 30 dias (junio 2024), en la formula se obtiene de la Hoja DiasMes")
  inicio_mes_final = ipcp_base[ipcp_base['fecha_inicio'] == fecha_final_mes]['fecha_inicio'].values[0]
  fin_mes_final = ipcp_base[ipcp_base['fecha_inicio'] == fecha_final_mes]['fecha_final'].values[0]
  Dmf = int((fin_mes_final - inicio_mes_final) / np.timedelta64(1, 'D')) + 1

  # Son los dias del mes Fecha Final posterior al primer dia ("En este caso, al ser 07 de junio; se calculan esos 07 dias adicionales de IPCP")
  df = int((fecha_final - inicio_mes_final) / np.timedelta64(1, 'D')) + 1

  # IPCP del mes anterior a la Inicial (En este ejemplo es el IPCP de marzo de 1995)
  fecha_inicial_menos_un_mes = fecha_inicial_mes - pd.DateOffset(months=1)
  IPCP_yi_mi = ipcp_base[ipcp_base['fecha_inicio'] == fecha_inicial_menos_un_mes]['ipcp'].values[0]

  # IPCP del mes Fecha Inicial (En este caso el IPCP de abril de 1995)
  IPCPsig_yi_mi = ipcp_base[ipcp_base['fecha_inicio'] == fecha_inicial_mes]['ipcp'].values[0]

  # Es el # de dias Calendario que tiene el mes de Fecha Inicial ("En este caso son 30 dias (Abril 1995), en la formula se obtiene de la Hoja DiasMes")
  inicio_mes_inicial = ipcp_base[ipcp_base['fecha_inicio'] == fecha_inicial_mes]['fecha_inicio'].values[0]
  fin_mes_inicial = ipcp_base[ipcp_base['fecha_inicio'] == fecha_inicial_mes]['fecha_final'].values[0]
  Dmi = int((fin_mes_inicial - inicio_mes_inicial) / np.timedelta64(1, 'D')) + 1

  # Son los dias del mes Fecha Inicial posterior al primer dia ("En este caso, al ser 28 de abril; se calculan esos 28 dias adicionales de IPCP")
  di = int((fecha_inicial - inicio_mes_inicial) / np.timedelta64(1, 'D')) + 1

  # Tasa de Rendimiento (Puede ser 3% o 4%) (Se expresa como entero pues en la formula se convierte en porcentaje al dividir en 100)
  B4 = TRR
  # Fecha Final ("En este caso excel no cuenta el primer dia, por tanto si se resta (31/12/2025-01/01/2025) es igual a 364 y no 365, y así lo calcula el MinHacienda")
  B3 = fecha_final
  # Fecha Inicial
  B2 = fecha_inicial
  # Calculo del exponente
  exp = float((B3 - B2) / np.timedelta64(1, 'D'))

  # print(
  #     f'B1: {B1}\n',
  #     f'IPCP_yf_mf: {IPCP_yf_mf}\n',
  #     f'IPCPsig_yf_mf: {IPCPsig_yf_mf}\n',
  #     f'Dmf: {Dmf}\n',
  #     f'df: {df}\n',
  #     f'IPCP_yi_mi: {IPCP_yi_mi}\n',
  #     f'IPCPsig_yi_mi: {IPCPsig_yi_mi}\n',
  #     f'Dmi: {Dmi}\n',
  #     f'di: {di}\n',
  #     f'B4: {B4}\n',
  #     f'B3: {B3}\n',
  #     f'B2: {B2}\n',
  #     f'exp: {exp}'
  # )

  num = IPCP_yf_mf + (((IPCPsig_yf_mf - IPCP_yf_mf) / Dmf) * df)
  dem = IPCP_yi_mi + (((IPCPsig_yi_mi - IPCP_yi_mi) / Dmi) * di)
  mulp = (1 + (B4 / 100)) ** (exp / 365.25)

  valor_actualizado_capitalizado = (B1 * (num / dem)) * mulp
  valor_actualizado_capitalizado = round(valor_actualizado_capitalizado, 2)

  return valor_actualizado_capitalizado

def actualizacion_y_capitalizacion_inversa(valor_actualizar_capitalizar, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, TRR):

  # Valores usuario
  valor_actualizar_capitalizar = float(valor_actualizar_capitalizar)
  fecha_inicial = pd.to_datetime(fecha_inicial)
  fecha_final = pd.to_datetime(fecha_final)
  TRR = float(TRR)
  # Valores de fecha truncados a mes
  fecha_inicial_mes = fecha_inicial.to_period('M').to_timestamp()
  fecha_final_mes = fecha_final.to_period('M').to_timestamp()

  if fecha_check:
    fecha_ipcp = pd.to_datetime(fecha_ipcp)
    fecha_ipcp_mes = fecha_ipcp.to_period('M').to_timestamp()
  else:
    fecha_ipcp_mes = fecha_inicial_mes

  # Valor a Actualizar (En este ejemplo son $4.000.000)
  B1 = valor_actualizar_capitalizar

  # IPCP del mes anterior a la Fecha Final (En este ejemplo es el IPCP de mayo de 2024)
  fecha_final_menos_un_mes = fecha_final_mes - pd.DateOffset(months=1)
  IPCP_yf_mf = ipcp_base[ipcp_base['fecha_inicio'] == fecha_final_menos_un_mes]['ipcp'].values[0]

  # IPCP del mes Fecha Final (En este caso el IPCP de junio de 2024)
  IPCPsig_yf_mf = ipcp_base[ipcp_base['fecha_inicio'] == fecha_final_mes]['ipcp'].values[0]

  # Es el # de dias Calendario que tiene el mes de Fecha Final ("En este caso son 30 dias (junio 2024), en la formula se obtiene de la Hoja DiasMes")
  inicio_mes_final = ipcp_base[ipcp_base['fecha_inicio'] == fecha_final_mes]['fecha_inicio'].values[0]
  fin_mes_final = ipcp_base[ipcp_base['fecha_inicio'] == fecha_final_mes]['fecha_final'].values[0]
  Dmf = int((fin_mes_final - inicio_mes_final) / np.timedelta64(1, 'D')) + 1

  # Son los dias del mes Fecha Final posterior al primer dia ("En este caso, al ser 07 de junio; se calculan esos 07 dias adicionales de IPCP")
  df = int((fecha_final - inicio_mes_final) / np.timedelta64(1, 'D')) + 1

  # IPCP del mes anterior a la Inicial (En este ejemplo es el IPCP de marzo de 1995)
  fecha_inicial_menos_un_mes = fecha_inicial_mes - pd.DateOffset(months=1)
  IPCP_yi_mi = ipcp_base[ipcp_base['fecha_inicio'] == fecha_inicial_menos_un_mes]['ipcp'].values[0]

  # IPCP del mes Fecha Inicial (En este caso el IPCP de abril de 1995)
  IPCPsig_yi_mi = ipcp_base[ipcp_base['fecha_inicio'] == fecha_inicial_mes]['ipcp'].values[0]

  # Es el # de dias Calendario que tiene el mes de Fecha Inicial ("En este caso son 30 dias (Abril 1995), en la formula se obtiene de la Hoja DiasMes")
  inicio_mes_inicial = ipcp_base[ipcp_base['fecha_inicio'] == fecha_inicial_mes]['fecha_inicio'].values[0]
  fin_mes_inicial = ipcp_base[ipcp_base['fecha_inicio'] == fecha_inicial_mes]['fecha_final'].values[0]
  Dmi = int((fin_mes_inicial - inicio_mes_inicial) / np.timedelta64(1, 'D')) + 1

  # Son los dias del mes Fecha Inicial posterior al primer dia ("En este caso, al ser 28 de abril; se calculan esos 28 dias adicionales de IPCP")
  di = int((fecha_inicial - inicio_mes_inicial) / np.timedelta64(1, 'D')) + 1

  # Tasa de Rendimiento (Puede ser 3% o 4%) (Se expresa como entero pues en la formula se convierte en porcentaje al dividir en 100)
  B4 = TRR
  # Fecha Final ("En este caso excel no cuenta el primer dia, por tanto si se resta (31/12/2025-01/01/2025) es igual a 364 y no 365, y así lo calcula el MinHacienda")
  B3 = fecha_final
  # Fecha Inicial
  B2 = fecha_inicial
  # Calculo del exponente
  exp = float((B3 - B2) / np.timedelta64(1, 'D'))

  # print(
  #     f'B1: {B1}\n',
  #     f'IPCP_yf_mf: {IPCP_yf_mf}\n',
  #     f'IPCPsig_yf_mf: {IPCPsig_yf_mf}\n',
  #     f'Dmf: {Dmf}\n',
  #     f'df: {df}\n',
  #     f'IPCP_yi_mi: {IPCP_yi_mi}\n',
  #     f'IPCPsig_yi_mi: {IPCPsig_yi_mi}\n',
  #     f'Dmi: {Dmi}\n',
  #     f'di: {di}\n',
  #     f'B4: {B4}\n',
  #     f'B3: {B3}\n',
  #     f'B2: {B2}\n',
  #     f'exp: {exp}'
  # )

  num = IPCP_yi_mi + (((IPCPsig_yi_mi - IPCP_yi_mi) / Dmi) * di)
  dem = IPCP_yf_mf + (((IPCPsig_yf_mf - IPCP_yf_mf) / Dmf) * df)
  mulp = (1 + (B4 / 100)) ** ((exp / 365.25) * -1)

  valor_actualizado_capitalizado = (B1 * (num / dem)) * mulp
  valor_actualizado_capitalizado = round(valor_actualizado_capitalizado, 2)

  return valor_actualizado_capitalizado

def determinador_accion(tipo, fecha_inicial, fecha_pension, fecha_cobro):

  if tipo == 'Valor Fecha Riesgo':
    return 'actualizacion_capitalizacion'
  if tipo == 'Abono' and fecha_inicial < fecha_pension:
    return 'actualizacion_capitalizacion'
  if tipo == 'Abono' and fecha_inicial >= fecha_pension:
    return 'actualizacion'
  if tipo == 'Reintegro' and fecha_inicial < fecha_pension:
    return 'actualizacion_capitalizacion'
  if tipo == 'Reintegro' and fecha_inicial >= fecha_pension:
    return 'actualizacion'
  if tipo == 'Valor a Pagar' and fecha_inicial <= fecha_pension:
    return 'actualizacion_capitalizacion'
  if tipo == 'Valor a Pagar' and fecha_inicial > fecha_pension:
    return 'actualizacion'
  if tipo == 'Valor Fecha Cobro':
    return 'actualizacion'
  if tipo == 'Valor a Pagar Recursos Propios' and fecha_inicial <= fecha_cobro:
    return 'actualizacion'
  if tipo == 'Valor a Pagar Recursos Propios' and fecha_inicial > fecha_cobro:
    return 'actualizacion_capitalizacion'
  else:
    return None

def input_transformacion(dataFrame):

    user_input = dataFrame.copy()

     # Transoformar la fecha de referencia como datetime año/mes/dia
    fecha_inicio = ipcp_base['fecha_inicio'].min().date()
    fecha_final = ipcp_base['fecha_final'].max().date()

    # Si la fecha que ingresa el usuario es mas antigua que la primera fecha de la base, se toma la primera fecha de la base
    if user_input['fecha'].min() < fecha_inicio:
        user_input['fecha'] = fecha_inicio
    if user_input['fecha'].max() > fecha_final:
        user_input['fecha'] = fecha_final

    # Se genera la columna fecha final y valor anterior
    user_input = user_input.sort_values('fecha').reset_index(drop=True)
    user_input['fecha_inicial'] = user_input['fecha'].shift(1)
    user_input['valor'] = user_input['valor'].fillna(0)
    user_input['valor_anterior'] = user_input['valor'].shift(1)
    user_input['valor_anterior'] = user_input['valor_anterior'].fillna(0)
    user_input['tipo_anterior'] = user_input['tipo'].shift(1)

    user_input['fecha_check'] = user_input['fecha_check']
    user_input['fecha_ipcp'] = user_input['fecha_ipcp']

    try:
        user_input['fecha_pension'] = user_input[user_input['tipo'] == 'Valor Fecha Riesgo']['fecha'].values[0]
    except:
        user_input['fecha_pension'] = user_input[user_input['tipo'] == 'Valor a Pagar']['fecha'].values[0]

    try:
        user_input['fecha_cobro'] = user_input[user_input['tipo'] == 'Valor Fecha Cobro']['fecha'].values[0]
    except:
        user_input['fecha_cobro'] = user_input[user_input['tipo'] == 'Valor a Pagar']['fecha'].values[0]
        
    user_input['accion'] = user_input.apply(lambda x: determinador_accion(x['tipo'], x['fecha_inicial'], x['fecha_pension'], x['fecha_cobro']), axis=1)

    nuevo_valor = []
    valor_referencia = 0
    for i in range(len(user_input)):


      valor = round(user_input['valor'][i], 2)
      fecha_inicial = user_input['fecha_inicial'][i]
      fecha_final = user_input['fecha'][i]
      trr = user_input['trr'][i]
      tipo = user_input['tipo'][i]
      accion = user_input['accion'][i]
      valor_anterior = user_input['valor_anterior'][i]
      tipo_anterior = user_input['tipo_anterior'][i]
      fecha_check = user_input['fecha_check'][i]
      fecha_ipcp = user_input['fecha_ipcp'][i]


      if accion == None:
        valor_referencia = valor
      if accion == 'actualizacion_capitalizacion' and tipo == 'Valor Fecha Riesgo':
        valor_referencia = actualizacion_y_capitalizacion(valor_referencia, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)

      #### ABONO #####
      #### ACT / CAP ####
      if accion == 'actualizacion_capitalizacion' and tipo == 'Abono' and tipo_anterior == 'Reintegro':
        valor_mas_reintegro = valor_referencia + valor_anterior
        valor_referencia = actualizacion_y_capitalizacion(valor_mas_reintegro, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      if accion == 'actualizacion_capitalizacion' and tipo == 'Abono' and tipo_anterior == 'Abono':
        valo_menos_abono = valor_referencia - valor_anterior
        valor_referencia = actualizacion_y_capitalizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      if accion == 'actualizacion_capitalizacion' and tipo == 'Abono' and tipo_anterior == 'Valor Fecha Riesgo':
        valor_referencia = actualizacion_y_capitalizacion(valor_referencia, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      if accion == 'actualizacion_capitalizacion' and tipo == 'Abono' and tipo_anterior == 'Valor Fecha Corte':
        valo_menos_abono = valor_referencia - valor
        valor_referencia = actualizacion_y_capitalizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      if accion == 'actualizacion_capitalizacion' and tipo == 'Abono' and tipo_anterior == 'Valor Fecha Cobro':
        valo_menos_abono = valor_referencia + valor
        valor_referencia = actualizacion_y_capitalizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      if accion == 'actualizacion_capitalizacion' and tipo == 'Abono' and tipo_anterior == 'Valor a Pagar Recursos Propios':
        valo_menos_abono = valor_referencia + valor
        valor_referencia = actualizacion_y_capitalizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      #### ACT ####
      if accion == 'actualizacion' and tipo == 'Abono' and tipo_anterior == 'Reintegro':
        valor_mas_reintegro = valor_referencia + valor_anterior
        valor_referencia = actualizacion(valor_mas_reintegro, fecha_inicial, fecha_final, fecha_check, fecha_ipcp)
      if accion == 'actualizacion' and tipo == 'Abono' and tipo_anterior == 'Abono':
        valo_menos_abono = valor_referencia - valor_anterior
        valor_referencia = actualizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp)
      if accion == 'actualizacion' and tipo == 'Abono' and tipo_anterior == 'Valor Fecha Riesgo':
        valor_referencia = actualizacion(valor_referencia, fecha_inicial, fecha_final, fecha_check, fecha_ipcp)
      if accion == 'actualizacion' and tipo == 'Abono' and tipo_anterior == 'Valor Fecha Cobro':
        valo_menos_abono = valor_referencia + valor
        valor_referencia = actualizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp)
      if accion == 'actualizacion' and tipo == 'Abono' and tipo_anterior == 'Valor a Pagar Recursos Propios':
        valo_menos_abono = valor_referencia + valor
        valor_referencia = actualizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp)


      #### REINTEGRO ####
      #### ACT / CAP ####
      if accion == 'actualizacion_capitalizacion' and tipo == 'Reintegro' and tipo_anterior == 'Reintegro':
        valor_mas_reintegro = valor_referencia + valor_anterior
        valor_referencia = actualizacion_y_capitalizacion(valor_mas_reintegro, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      if accion == 'actualizacion_capitalizacion' and tipo == 'Reintegro' and tipo_anterior == 'Abono':
        valo_menos_abono = valor_referencia - valor_anterior
        valor_referencia = actualizacion_y_capitalizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      if accion == 'actualizacion_capitalizacion' and tipo == 'Reintegro' and tipo_anterior == 'Valor Fecha Riesgo':
        valo_menos_abono = valor_referencia + valor
        valor_referencia = actualizacion_y_capitalizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      if accion == 'actualizacion_capitalizacion' and tipo == 'Reintegro' and tipo_anterior == 'Valor Fecha Corte':
        pass
      if accion == 'actualizacion_capitalizacion' and tipo == 'Reintegro' and tipo_anterior == 'Valor Fecha Cobro':
        valo_menos_abono = valor_referencia + valor
        valor_referencia = actualizacion_y_capitalizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      if accion == 'actualizacion_capitalizacion' and tipo == 'Reintegro' and tipo_anterior == 'Valor a Pagar Recursos Propios':
        valo_menos_abono = valor_referencia + valor
        valor_referencia = actualizacion_y_capitalizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
        ########### ROMPER GENERAR ALERTA #############
      #### ACT ####
      if accion == 'actualizacion' and tipo == 'Reintegro' and tipo_anterior == 'Reintegro':
        valor_mas_reintegro = valor_referencia + valor_anterior
        valor_referencia = actualizacion(valor_mas_reintegro, fecha_inicial, fecha_final, fecha_check, fecha_ipcp)
      if accion == 'actualizacion' and tipo == 'Reintegro' and tipo_anterior == 'Abono':
        valo_menos_abono = valor_referencia - valor_anterior
        valor_referencia = actualizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp)
      if accion == 'actualizacion' and tipo == 'Reintegro' and tipo_anterior == 'Valor Fecha Riesgo':
        valo_menos_abono = valor_referencia + valor
        valor_referencia = actualizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp)
      if accion == 'actualizacion' and tipo == 'Reintegro' and tipo_anterior == 'Valor Fecha Cobro':
        valo_menos_abono = valor_referencia + valor
        valor_referencia = actualizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp)
      if accion == 'actualizacion' and tipo == 'Reintegro' and tipo_anterior == 'Valor a Pagar Recursos Propios':
        valo_menos_abono = valor_referencia + valor
        valor_referencia = actualizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp)

      #### PAGO ####
      #### ACT / CAP ####
      if accion == 'actualizacion_capitalizacion' and tipo == 'Valor a Pagar' and tipo_anterior == 'Reintegro':
        valor_mas_reintegro = valor_referencia + valor_anterior
        valor_referencia = actualizacion_y_capitalizacion(valor_mas_reintegro, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      if accion == 'actualizacion_capitalizacion' and tipo == 'Valor a Pagar' and tipo_anterior == 'Abono':
        valo_menos_abono = valor_referencia - valor_anterior
        valor_referencia = actualizacion_y_capitalizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      if accion == 'actualizacion_capitalizacion' and tipo == 'Valor a Pagar' and tipo_anterior == 'Valor Fecha Riesgo':
        valo_menos_abono = valor_referencia + valor
        valor_referencia = actualizacion_y_capitalizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      if accion == 'actualizacion_capitalizacion' and tipo == 'Valor a Pagar' and tipo_anterior == 'Valor Fecha Corte':
        valor_referencia = actualizacion_y_capitalizacion(valor_referencia, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      if accion == 'actualizacion_capitalizacion' and tipo == 'Valor a Pagar' and tipo_anterior == 'Valor Fecha Cobro':
        valo_menos_abono = valor_referencia + valor
        valor_referencia = actualizacion_y_capitalizacion(valor_referencia, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      if accion == 'actualizacion_capitalizacion' and tipo == 'Valor a Pagar' and tipo_anterior == 'Valor a Pagar Recursos Propios':
        valo_menos_abono = valor_referencia + valor
        valor_referencia = actualizacion_y_capitalizacion(valor_referencia, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      #### ACT ####
      if accion == 'actualizacion' and tipo == 'Valor a Pagar' and tipo_anterior == 'Reintegro':
        valor_mas_reintegro = valor_referencia + valor_anterior
        valor_referencia = actualizacion(valor_mas_reintegro, fecha_inicial, fecha_final, fecha_check, fecha_ipcp)
      if accion == 'actualizacion' and tipo == 'Valor a Pagar' and tipo_anterior == 'Abono':
        valo_menos_abono = valor_referencia - valor_anterior
        valor_referencia = actualizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp)
      if accion == 'actualizacion' and tipo == 'Valor a Pagar' and tipo_anterior == 'Valor Fecha Riesgo':
        valo_menos_abono = valor_referencia + valor
        valor_referencia = actualizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp)
      if accion == 'actualizacion' and tipo == 'Valor a Pagar' and tipo_anterior == 'Valor Fecha Cobro':
        valo_menos_abono = valor_referencia + valor
        valor_referencia = actualizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp)
      if accion == 'actualizacion' and tipo == 'Valor a Pagar' and tipo_anterior == 'Valor a Pagar Recursos Propios':
        valo_menos_abono = valor_referencia + valor
        valor_referencia = actualizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp)

      #### VALOR A FECHA DE COBRO ####
      #### ACT / CAP ####
      if accion == 'actualizacion_capitalizacion' and tipo == 'Valor Fecha Cobro' and tipo_anterior == 'Reintegro':
        valor_mas_reintegro = valor_referencia + valor_anterior
        valor_referencia = actualizacion_y_capitalizacion(valor_mas_reintegro, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      if accion == 'actualizacion_capitalizacion' and tipo == 'Valor Fecha Cobro' and tipo_anterior == 'Abono':
        valo_menos_abono = valor_referencia - valor_anterior
        valor_referencia = actualizacion_y_capitalizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      if accion == 'actualizacion_capitalizacion' and tipo == 'Valor Fecha Cobro' and tipo_anterior == 'Valor Fecha Riesgo':
        valo_menos_abono = valor_referencia + valor
        valor_referencia = actualizacion_y_capitalizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      if accion == 'actualizacion_capitalizacion' and tipo == 'Valor Fecha Cobro' and tipo_anterior == 'Valor Fecha Corte':
        valor_referencia = actualizacion_y_capitalizacion(valor_referencia, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      if accion == 'actualizacion_capitalizacion' and tipo == 'Valor Fecha Cobro' and tipo_anterior == 'Valor a Pagar Recursos Propios':
        valor_referencia = actualizacion_y_capitalizacion(valor_referencia, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      #### ACT ####
      if accion == 'actualizacion' and tipo == 'Valor Fecha Cobro' and tipo_anterior == 'Reintegro':
        valor_mas_reintegro = valor_referencia + valor_anterior
        valor_referencia = actualizacion(valor_mas_reintegro, fecha_inicial, fecha_final, fecha_check, fecha_ipcp)
      if accion == 'actualizacion' and tipo == 'Valor Fecha Cobro' and tipo_anterior == 'Abono':
        valo_menos_abono = valor_referencia - valor_anterior
        valor_referencia = actualizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp)
      if accion == 'actualizacion' and tipo == 'Valor Fecha Cobro' and tipo_anterior == 'Valor Fecha Riesgo':
        valo_menos_abono = valor_referencia + valor
        valor_referencia = actualizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp)
      if accion == 'actualizacion' and tipo == 'Valor Fecha Cobro' and tipo_anterior == 'Valor a Pagar Recursos Propios':
        valor_referencia = actualizacion(valor_referencia, fecha_inicial, fecha_final, fecha_check, fecha_ipcp)

      #### PAGO CON RECURSOS PROPIOS ####
      #### ACT / CAP ####
      if accion == 'actualizacion_capitalizacion' and tipo == 'Valor a Pagar Recursos Propios' and tipo_anterior == 'Valor Fecha Cobro':
        valor_referencia = actualizacion_y_capitalizacion(valor_referencia, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      if accion == 'actualizacion_capitalizacion' and tipo == 'Valor a Pagar Recursos Propios' and tipo_anterior == 'Reintegro':
        valor_mas_reintegro = valor_referencia + valor_anterior
        valor_referencia = actualizacion_y_capitalizacion(valor_mas_reintegro, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      if accion == 'actualizacion_capitalizacion' and tipo == 'Valor a Pagar Recursos Propios' and tipo_anterior == 'Abono':
        valo_menos_abono = valor_referencia - valor_anterior
        valor_referencia = actualizacion_y_capitalizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      if accion == 'actualizacion_capitalizacion' and tipo == 'Valor a Pagar Recursos Propios' and tipo_anterior == 'Valor Fecha Riesgo':
        valo_menos_abono = valor_referencia + valor
        valor_referencia = actualizacion_y_capitalizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      if accion == 'actualizacion_capitalizacion' and tipo == 'Valor a Pagar Recursos Propios' and tipo_anterior == 'Valor Fecha Corte':
        valor_referencia = actualizacion_y_capitalizacion(valor_referencia, fecha_inicial, fecha_final, fecha_check, fecha_ipcp, trr)
      #### ACT ####
      if accion == 'actualizacion' and tipo == 'Valor a Pagar Recursos Propios' and tipo_anterior == 'Valor Fecha Cobro':
        valor_referencia = actualizacion(valor_referencia, fecha_inicial, fecha_final, fecha_check, fecha_ipcp)
      if accion == 'actualizacion' and tipo == 'Valor a Pagar Recursos Propios' and tipo_anterior == 'Reintegro':
        valor_mas_reintegro = valor_referencia + valor_anterior
        valor_referencia = actualizacion(valor_mas_reintegro, fecha_inicial, fecha_final, fecha_check, fecha_ipcp)
      if accion == 'actualizacion' and tipo == 'Valor a Pagar Recursos Propios' and tipo_anterior == 'Abono':
        valo_menos_abono = valor_referencia - valor_anterior
        valor_referencia = actualizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp)
      if accion == 'actualizacion' and tipo == 'Valor a Pagar Recursos Propios' and tipo_anterior == 'Valor Fecha Riesgo':
        valo_menos_abono = valor_referencia + valor
        valor_referencia = actualizacion(valo_menos_abono, fecha_inicial, fecha_final, fecha_check, fecha_ipcp)

      nuevo_valor.append(valor_referencia)

    user_input['nuevo_valor'] = nuevo_valor
    user_input = user_input[['fecha', 'tipo', 'valor', 'accion', 'nuevo_valor', 'descripcion']]
    user_input['nuevo_valor'] = user_input['nuevo_valor'].apply(lambda x: round(x, 2))

    # Vamos a dar formato de moneda ($ 7'000.000,00) a las columnas 'valor' y 'nuevo_valor'
    user_input['valor'] = user_input['valor'].apply(lambda x: f"${x:,.2f}")
    user_input['nuevo_valor'] = user_input['nuevo_valor'].apply(lambda x: f"${x:,.2f}")

    return user_input
