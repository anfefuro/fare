import io
import pandas as pd
from nicegui import app, ui
from fastapi.responses import Response

from ipcp import input_transformacion, actualizacion as calc_actualizacion, actualizacion_y_capitalizacion

MIN_DATE = '1954/08/01'
TIPOS = [
    'Valor Fecha Corte', 'Valor Fecha Riesgo', 'Abono', 'Reintegro',
    'Valor a Pagar', 'Valor Fecha Cobro', 'Valor a Pagar Recursos Propios',
]

_excel_cache = None  # type: bytes | None


def today_str() -> str:
    return pd.Timestamp.today().strftime('%Y/%m/%d')


def to_date(s: str):
    return pd.Timestamp(s.replace('/', '-')).date()


# ── FastAPI download endpoint ─────────────────────────────────────────────────
@app.get('/descargar-resultados')
def descargar_resultados():
    if _excel_cache is None:
        return Response(content='Sin datos', status_code=404)
    return Response(
        content=_excel_cache,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=resultados_ipcp.xlsx'},
    )


# ── Movimiento model ──────────────────────────────────────────────────────────
class Movimiento:
    def __init__(self):
        self.valor: float = 0
        self.fecha: str = today_str()
        self.fecha_check: bool = False
        self.fecha_ipcp: str = MIN_DATE
        self.tipo: str = TIPOS[0]
        self.trr: float = 4
        self.descripcion: str = ''


movimientos: list[Movimiento] = [Movimiento()]


# ── Section 1: IPCP Calculator ────────────────────────────────────────────────
@ui.refreshable
def render_movimientos():
    for idx, mov in enumerate(movimientos):
        with ui.card().classes('w-full mb-2 p-4'):
            with ui.row().classes('w-full items-center justify-between'):
                ui.label(f'Movimiento {idx + 1}').classes('text-xl font-bold')
                def on_delete(m=mov):
                    movimientos.remove(m)
                    render_movimientos.refresh()
                ui.button('🗑️', on_click=on_delete).props('flat dense color=negative')

            ui.number(f'Valor {idx + 1}', value=mov.valor, min=0, format='%.0f').bind_value(mov, 'valor')
            ui.label(f'Fecha {idx + 1}').classes('mt-2 text-sm text-gray-600')
            ui.date(value=mov.fecha).bind_value(mov, 'fecha')
            ui.checkbox('📅 Fecha IPCP', value=mov.fecha_check).bind_value(mov, 'fecha_check')
            with ui.column() as ipcp_col:
                ui.label(f'Fecha IPCP {idx + 1}').classes('text-sm text-gray-600')
                ui.date(value=mov.fecha_ipcp).bind_value(mov, 'fecha_ipcp')
            ipcp_col.bind_visibility_from(mov, 'fecha_check')
            ui.select(TIPOS, value=mov.tipo, label=f'Tipo {idx + 1}').bind_value(mov, 'tipo').classes('w-full')
            ui.number(f'TRR {idx + 1} (%)', value=mov.trr, min=0, max=5, step=1).bind_value(mov, 'trr')
            ui.input(f'Descripción {idx + 1}', value=mov.descripcion,
                     placeholder='Descripción del movimiento').bind_value(mov, 'descripcion').classes('w-full')


ui.label('IPCP Calculadora').classes('text-3xl font-bold my-4')
render_movimientos()

result_ipcp = ui.column().classes('w-full mt-2')


def mostrar_ipcp():
    global _excel_cache
    datos = [
        {
            'valor': int(mov.valor or 0),
            'fecha': to_date(mov.fecha),
            'fecha_check': mov.fecha_check,
            'fecha_ipcp': to_date(mov.fecha_ipcp) if mov.fecha_check else pd.Timestamp('1954-08-01').date(),
            'tipo': mov.tipo,
            'trr': int(mov.trr or 0),
            'descripcion': mov.descripcion,
        }
        for mov in movimientos
    ]
    df = pd.DataFrame(datos)
    resultado = input_transformacion(df)

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        resultado.to_excel(writer, index=False, sheet_name='Resultados')
    buf.seek(0)
    _excel_cache = buf.read()

    result_ipcp.clear()
    with result_ipcp:
        ui.table.from_pandas(resultado).classes('w-full')
        ui.button('💾 Descargar resultados (Excel)',
                  on_click=lambda: ui.navigate.to('/descargar-resultados', new_tab=True)).classes('mt-2')


with ui.row().classes('gap-2 my-2'):
    ui.button('➕ Agregar movimiento',
              on_click=lambda: (movimientos.append(Movimiento()), render_movimientos.refresh()))
    ui.button('📋 Mostrar datos ingresados', on_click=mostrar_ipcp)
    ui.button('🖨️ Imprimir página', on_click=lambda: ui.run_javascript('window.print()'))


# ── Section 2: Calculadora de Actualización ───────────────────────────────────
ui.separator().classes('my-6')
ui.label('Calculadora de Actualización').classes('text-3xl font-bold my-4')


class EstadoAct:
    def __init__(self):
        self.valor: float = 0
        self.fecha_inicial: str = today_str()
        self.fecha_check: bool = False
        self.fecha_ipcp: str = MIN_DATE
        self.fecha_final: str = today_str()


act = EstadoAct()
result_act = ui.label('').classes('text-xl my-2')

with ui.card().classes('w-full p-4'):
    ui.number('Valor', value=act.valor, min=0, format='%.0f').bind_value(act, 'valor')
    ui.label('Fecha Inicial').classes('mt-2 text-sm text-gray-600')
    ui.date(value=act.fecha_inicial).bind_value(act, 'fecha_inicial')
    ui.checkbox('📅 Fecha IPCP', value=act.fecha_check).bind_value(act, 'fecha_check')
    with ui.column() as act_ipcp_col:
        ui.label('Fecha IPCP').classes('text-sm text-gray-600')
        ui.date(value=act.fecha_ipcp).bind_value(act, 'fecha_ipcp')
    act_ipcp_col.bind_visibility_from(act, 'fecha_check')
    ui.label('Fecha Final').classes('mt-2 text-sm text-gray-600')
    ui.date(value=act.fecha_final).bind_value(act, 'fecha_final')


def mostrar_actualizacion():
    fecha_ipcp = to_date(act.fecha_ipcp) if act.fecha_check else pd.Timestamp('1954-08-01').date()
    valor = calc_actualizacion(
        int(act.valor or 0),
        to_date(act.fecha_inicial),
        to_date(act.fecha_final),
        act.fecha_check,
        fecha_ipcp,
    )
    result_act.set_text(f'El valor actualizado es: {valor:,.2f}')


ui.button('📋 Mostrar resultados de actualización', on_click=mostrar_actualizacion).classes('my-2')


# ── Section 3: Calculadora de Actualización y Capitalización ──────────────────
ui.separator().classes('my-6')
ui.label('Calculadora de Actualización y Capitalización').classes('text-3xl font-bold my-4')


class EstadoAyC:
    def __init__(self):
        self.valor: float = 0
        self.fecha_inicial: str = today_str()
        self.fecha_check: bool = False
        self.fecha_ipcp: str = MIN_DATE
        self.fecha_final: str = today_str()
        self.trr: float = 4


ayc = EstadoAyC()
result_ayc = ui.label('').classes('text-xl my-2')

with ui.card().classes('w-full p-4'):
    ui.number('Valor', value=ayc.valor, min=0, format='%.0f').bind_value(ayc, 'valor')
    ui.label('Fecha Inicial').classes('mt-2 text-sm text-gray-600')
    ui.date(value=ayc.fecha_inicial).bind_value(ayc, 'fecha_inicial')
    ui.checkbox('📅 Fecha IPCP', value=ayc.fecha_check).bind_value(ayc, 'fecha_check')
    with ui.column() as ayc_ipcp_col:
        ui.label('Fecha IPCP').classes('text-sm text-gray-600')
        ui.date(value=ayc.fecha_ipcp).bind_value(ayc, 'fecha_ipcp')
    ayc_ipcp_col.bind_visibility_from(ayc, 'fecha_check')
    ui.label('Fecha Final').classes('mt-2 text-sm text-gray-600')
    ui.date(value=ayc.fecha_final).bind_value(ayc, 'fecha_final')
    ui.number('TRR (%)', value=ayc.trr, min=0, max=5, step=1).bind_value(ayc, 'trr')


def mostrar_ayc():
    fecha_ipcp = to_date(ayc.fecha_ipcp) if ayc.fecha_check else pd.Timestamp('1954-08-01').date()
    valor = actualizacion_y_capitalizacion(
        int(ayc.valor or 0),
        to_date(ayc.fecha_inicial),
        to_date(ayc.fecha_final),
        ayc.fecha_check,
        fecha_ipcp,
        int(ayc.trr or 0),
    )
    result_ayc.set_text(f'El valor actualizado y capitalizado es: {valor:,.2f}')


ui.button('📋 Mostrar resultados de actualización y capitalización',
          on_click=mostrar_ayc).classes('my-2')


ui.run(title='IPCP Calculadora', port=8080)
