import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import datetime as dt
from datetime import date, timedelta
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'API_XM'))
from pydataxm.pydataxm import ReadDB
import warnings
warnings.filterwarnings("ignore")

# Inicializar la aplicación Dash con tema Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])
app.title = "Dashboard Caudal - XM"

# Inicializar API XM
try:
    objetoAPI = ReadDB()
    print("API XM inicializada correctamente")
except Exception as e:
    print(f"Error al inicializar API XM: {e}")
    objetoAPI = None

# --- Restaurar función para imprimir embalses en la terminal al iniciar la app ---

# --- Restaurar función para imprimir ríos en la terminal al iniciar la app ---
def print_rios_api():
    if objetoAPI is None:
        print("API XM no inicializada")
        return
    try:
        df = objetoAPI.request_data('AporCaudal', 'Rio', '2000-01-01', date.today().strftime('%Y-%m-%d'))
        if 'Name' in df.columns:
            rios = sorted(df['Name'].dropna().unique())
            print("\nRíos únicos encontrados en la API (desde 2000):")
            for r in rios:
                print(f'"{r}": "",')
        else:
            print("No se encontró la columna 'Name' en el DataFrame.")
    except Exception as e:
        print(f"Error obteniendo ríos de la API: {e}")

print_rios_api()
import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import datetime as dt
from datetime import date, timedelta
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'API_XM'))
from pydataxm.pydataxm import ReadDB
import warnings
warnings.filterwarnings("ignore")


# Inicializar la aplicación Dash con tema Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])
app.title = "Dashboard Caudal - XM"

# Inicializar API XM
try:
    objetoAPI = ReadDB()
    print("API XM inicializada correctamente")
except Exception as e:
    print(f"Error al inicializar API XM: {e}")
    objetoAPI = None

import pandas as pd

# Ruta al archivo CSV (ajusta si está en otra carpeta)
csv_path = "data.csv"


# Obtener la relación río-región directamente desde la API XM
def get_rio_region_dict():
    try:
        df = objetoAPI.request_data('ListadoRios', 'Sistema', '2024-01-01', '2024-01-02')
        if 'Values_Name' in df.columns and 'Values_HydroRegion' in df.columns:
            # Normalizar nombres igual que antes
            df['Values_Name'] = df['Values_Name'].str.strip().str.upper()
            df['Values_HydroRegion'] = df['Values_HydroRegion'].str.strip().str.title()
            return dict(sorted(zip(df['Values_Name'], df['Values_HydroRegion'])))
        else:
            return {}
    except Exception as e:
        print(f"Error obteniendo relación río-región desde la API: {e}")
        return {}

RIO_REGION = get_rio_region_dict()

def get_region_options():
    return sorted(set(RIO_REGION.values()))





# --- NUEVO: Función para obtener todos los ríos únicos desde la API ---
def get_all_rios_api():
    if objetoAPI is None:
        return []
    try:
        df = objetoAPI.request_data('AporCaudal', 'Rio', '2000-01-01', date.today().strftime('%Y-%m-%d'))
        if 'Name' in df.columns:
            rios = sorted(df['Name'].dropna().unique())
            return rios
        else:
            return []
    except Exception:
        return []

def get_rio_options(region=None):
    if objetoAPI is None:
        print("API XM no inicializada")
        return []
    try:
        df = objetoAPI.request_data('AporCaudal', 'Rio', (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'), date.today().strftime('%Y-%m-%d'))
        if 'Name' in df.columns:
            rios = sorted(df['Name'].dropna().unique())
            if region:
                rios = [r for r in rios if RIO_REGION.get(r) == region]
            return rios
        else:
            return []
    except Exception as e:
        print(f"Error obteniendo opciones de Río: {e}")
        return []

regiones = get_region_options()
rios = get_rio_options()



# Layout minimalista tipo pizarra para caudal
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2("Aportes en GWh por Río", className="text-center text-dark mb-2 fw-bold", style={"letterSpacing": "-1px"}),
            html.Hr(style={"marginTop": "0.5rem", "marginBottom": "1.5rem"})
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Región", className="fw-bold mb-1"),
                            dcc.Dropdown(
                                id="region-dropdown",
                                options=[{"label": r, "value": r} for r in regiones],
                                placeholder="Selecciona una región...",
                                className="mb-0"
                            )
                        ], md=3, xs=12),
                        dbc.Col([
                            html.Label("Nombre del Río", className="fw-bold mb-1"),
                            dcc.Dropdown(
                                id="rio-dropdown",
                                options=[{"label": r, "value": r} for r in rios],
                                placeholder="Selecciona un río...",
                                className="mb-0"
                            )
                        ], md=3, xs=12),
                        dbc.Col([
                            html.Label("Fecha Inicio", className="fw-bold mb-1"),
                            dcc.DatePickerSingle(
                                id="start-date",
                                date=date.today() - timedelta(days=30),
                                display_format="YYYY-MM-DD",
                                className="mb-0"
                            )
                        ], md=2, xs=12),
                        dbc.Col([
                            html.Label("Fecha Fin", className="fw-bold mb-1"),
                            dcc.DatePickerSingle(
                                id="end-date",
                                date=date.today(),
                                display_format="YYYY-MM-DD",
                                className="mb-0"
                            )
                        ], md=2, xs=12),
                        dbc.Col([
                            html.Label("\u00A0"),  # Espacio
                            dbc.Button(
                                [html.I(className="bi bi-search me-2"), "Consultar"],
                                id="query-button",
                                color="primary",
                                className="w-100",
                                style={"marginTop": "0.5rem"}
                            )
                        ], md=2, xs=12)
                    ], className="g-2 align-items-end justify-content-center")
                ])
            ], className="shadow-sm border-0", style={"background": "#fff", "borderRadius": "1rem", "padding": "0.5rem 1rem"})
        ], width=11, className="mx-auto mb-4")
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id="loading-indicator",
                children=[html.Div(id="tab-content")],
                type="default"
            )
        ], width=12)
    ]),
    # Sección para mostrar ríos únicos
    dbc.Row([
        dbc.Col([
            html.Hr(),
            dbc.Button(
                [html.I(className="bi bi-list-ul me-2"), "Mostrar todos los ríos de la API"],
                id="show-rios-btn",
                color="secondary",
                className="mb-2"
            ),
            html.Div(id="rios-list-output")
        ], width=12)
    ])
], fluid=True, className="px-2 px-md-5", style={"background": "#f6f6f6", "minHeight": "100vh"})


# Mostrar ríos en el dashboard al hacer clic en el botón
from dash.exceptions import PreventUpdate
@app.callback(
    Output("rios-list-output", "children"),
    [Input("show-rios-btn", "n_clicks")]
)
def show_rios_list(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    rios = get_all_rios_api()
    if not rios:
        return dbc.Alert("No se pudieron obtener ríos desde la API.", color="danger")
    return html.Div([
        html.H6("Ríos únicos encontrados en la API (desde 2000):", className="fw-bold mt-2"),
        html.Pre("\n".join(rios), style={"maxHeight": "300px", "overflowY": "auto", "background": "#f8f9fa", "padding": "1em", "fontSize": "1em"})
    ])







# Callback para actualizar ríos según región seleccionada
@app.callback(
    Output("rio-dropdown", "options"),
    [Input("region-dropdown", "value")]
)
def update_rio_options(region):
    rios_region = get_rio_options(region)
    options = [{"label": "Todos los ríos", "value": "__ALL__"}]
    options += [{"label": r, "value": r} for r in rios_region]
    return options


# Callback principal para consultar y mostrar datos filtrando por río y fechas
@app.callback(
    Output("tab-content", "children"),
    [Input("query-button", "n_clicks")],
    [State("rio-dropdown", "value"),
     State("start-date", "date"),
     State("end-date", "date"),
     State("region-dropdown", "value")]
)
def update_content(n_clicks, rio, start_date, end_date, region):
    if not n_clicks or not start_date or not end_date:
        return dbc.Alert("Selecciona una región, fechas y/o río, luego haz clic en Consultar.", color="info", className="text-center")
    try:
        data = objetoAPI.request_data('AporCaudal', 'Rio', start_date, end_date)
        if data is None or data.empty:
            return dbc.Alert("No se encontraron datos para los parámetros seleccionados.", color="warning")

        # Si hay un río específico seleccionado (y no es 'Todos los ríos'), mostrar la serie temporal diaria de ese río
        if rio and rio != "__ALL__":
            data_rio = data[data['Name'] == rio]
            if data_rio.empty:
                return dbc.Alert("No se encontraron datos para el río seleccionado.", color="warning")
            plot_df = data_rio.copy()
            if 'Date' in plot_df.columns and 'Value' in plot_df.columns:
                plot_df = plot_df[['Date', 'Value']].rename(columns={'Date': 'Fecha', 'Value': 'GWh'})
            return html.Div([
                html.H5(f"Aportes de Caudal en GWh - {rio}", className="text-center mb-3"),
                dbc.Row([
                    dbc.Col(create_line_chart(plot_df), md=7),
                    dbc.Col(create_data_table(plot_df), md=5)
                ])
            ])

        # Si no hay río seleccionado o es 'Todos los ríos', mostrar barra de contribución total por río en la región
        if region:
            data['Region'] = data['Name'].map(RIO_REGION)
            data_region = data[data['Region'] == region]
            if data_region.empty:
                return dbc.Alert("No se encontraron datos para la región seleccionada.", color="warning")
            if 'Name' in data_region.columns and 'Value' in data_region.columns:
                bar_df = data_region.groupby('Name')['Value'].sum().reset_index()
                bar_df = bar_df.rename(columns={'Name': 'Río', 'Value': 'GWh'})
                embalses_df = get_embalses_capacidad(region)
                # Obtener embalses de la región usando ListadoEmbalses
                try:
                    embalses_info = objetoAPI.request_data('ListadoEmbalses','Sistema','2024-01-01','2024-01-02')
                    embalses_info['Values_Name'] = embalses_info['Values_Name'].str.strip().str.upper()
                    embalses_info['Values_HydroRegion'] = embalses_info['Values_HydroRegion'].str.strip().str.title()
                    embalses_region = embalses_info[embalses_info['Values_HydroRegion'] == region]['Values_Name'].sort_values().unique()
                except Exception as e:
                    print(f"Error obteniendo embalses para el filtro: {e}")
                    embalses_region = []
                layout = [
                    html.H5(f"Contribución de cada río en la región {region}", className="text-center mb-3"),
                    dbc.Row([
                        dbc.Col(create_bar_chart(bar_df, f"Aportes por río en {region}"), md=12)
                    ]),
                    dcc.Store(id="region-data-store", data=data_region.to_dict('records')),
                    dbc.Modal([
                        dbc.ModalHeader(dbc.ModalTitle("Detalle diario del río seleccionado"), close_button=True),
                        dbc.ModalBody([
                            html.Div(id="modal-table-content")
                        ]),
                    ], id="modal-rio-table", is_open=False, size="xl", backdrop=True, centered=True, style={"zIndex": 2000}),
                    html.Hr(),
                    html.H5("Capacidad útil diaria de energía por embalse", className="text-center mt-4 mb-2"),
                    dbc.Row([
                        dbc.Col([
                            dcc.Dropdown(
                                id="embalse-cap-dropdown",
                                options=[{"label": e.title(), "value": e} for e in embalses_region],
                                placeholder="Filtrar por embalse...",
                                className="mb-2"
                            ),
                            dash_table.DataTable(
                                id="tabla-capacidad-embalse",
                                data=embalses_df.to_dict('records'),
                                columns=[
                                    {"name": "Embalse", "id": "Embalse"},
                                    {"name": "Capacidad Útil Diaria (GWh)", "id": "Capacidad Útil Diaria (GWh)"}
                                ],
                                style_cell={'textAlign': 'left', 'padding': '6px', 'fontFamily': 'Arial', 'fontSize': 14},
                                style_header={'backgroundColor': '#e3e3e3', 'fontWeight': 'bold'},
                                style_data={'backgroundColor': '#f8f8f8'},
                                page_action="native",
                                page_current=0,
                                page_size=10
                            )
                        ], md=8, className="mx-auto")
                    ]),
                    dcc.Store(id="embalse-cap-data", data=embalses_df.to_dict('records'))
                ]
                return html.Div(layout)
            else:
                return dbc.Alert("No se pueden graficar los datos de la región.", color="warning")
        return dbc.Alert("Selecciona una región para ver la contribución de los ríos.", color="info")
    except Exception as e:
        return dbc.Alert(f"Error al consultar los datos: {str(e)}", color="danger")

# --- Mover fuera: Callback para actualizar la tabla de capacidad útil de embalse de forma interactiva ---
@app.callback(
    Output("tabla-capacidad-embalse", "data"),
    [Input("embalse-cap-dropdown", "value")],
    [State("embalse-cap-data", "data")]
)
def update_tabla_capacidad_embalse(embalse, data):
    import pandas as pd
    df = pd.DataFrame(data)
    if embalse:
        # El dropdown usa embalses en mayúsculas, igual que la columna 'Embalse'
        df = df[df['Embalse'].str.upper() == embalse.upper()]
    return df.to_dict('records')

# --- Mover fuera: Función para obtener la capacidad útil de energía por embalse ---
def get_embalses_capacidad(region=None):
    """
    Obtiene la capacidad útil diaria de energía por embalse desde la API XM (CapaUtilDiarEner).
    Si se pasa una región, filtra los embalses de esa región.
    """
    try:
        df = objetoAPI.request_data('CapaUtilDiarEner','Embalse','2024-01-01','2024-01-02')
        if 'Name' in df.columns and 'Value' in df.columns:
            embalses_info = objetoAPI.request_data('ListadoEmbalses','Sistema','2024-01-01','2024-01-02')
            embalses_info['Values_Name'] = embalses_info['Values_Name'].str.strip().str.upper()
            embalses_info['Values_HydroRegion'] = embalses_info['Values_HydroRegion'].str.strip().str.title()
            embalse_region_dict = dict(zip(embalses_info['Values_Name'], embalses_info['Values_HydroRegion']))
            df['Region'] = df['Name'].map(embalse_region_dict)
            if region:
                df = df[df['Region'] == region]
            df_grouped = df.groupby('Name')['Value'].sum().reset_index()
            df_grouped = df_grouped.rename(columns={'Name': 'Embalse', 'Value': 'Capacidad Útil Diaria (GWh)'})
            df_grouped['Capacidad Útil Diaria (GWh)'] = df_grouped['Capacidad Útil Diaria (GWh)'].round(2)
            return df_grouped.sort_values('Embalse')
        else:
            return pd.DataFrame(columns=['Embalse', 'Capacidad Útil Diaria (GWh)'])
    except Exception as e:
        print(f"Error obteniendo capacidad útil diaria de energía por embalse: {e}")
        return pd.DataFrame(columns=['Embalse', 'Capacidad Útil Diaria (GWh)'])
    
def create_data_table(data):
    """Tabla simple de datos de caudal"""
    if data is None or data.empty:
        return dbc.Alert("No hay datos para mostrar en la tabla.", color="warning")
    return dash_table.DataTable(
        data=data.head(1000).to_dict('records'),
        columns=[{"name": i, "id": i} for i in data.columns],
        style_cell={'textAlign': 'left', 'padding': '6px', 'fontFamily': 'Arial', 'fontSize': 14},
        style_header={'backgroundColor': '#e3e3e3', 'fontWeight': 'bold'},
        style_data={'backgroundColor': '#f8f8f8'},
        page_action="native",
        page_current=0,
        page_size=10,
        export_format="xlsx",
        export_headers="display"
    )

def create_line_chart(data):
    """Gráfico de líneas de caudal"""
    if data is None or data.empty:
        return dbc.Alert("No se pueden crear gráficos con estos datos.", color="warning")
    # Esperar columnas 'Fecha' y 'GWh' tras el renombrado
    if 'Fecha' in data.columns and 'GWh' in data.columns:
        fig = px.line(data, x='Fecha', y='GWh', labels={'GWh': "GWh", 'Fecha': "Fecha"}, markers=True)
        fig.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10), template="simple_white")
        return dcc.Graph(figure=fig)
    else:
        return dbc.Alert("No se pueden crear gráficos con estos datos.", color="warning")

def create_bar_chart(data, metric_name):
    """Crear gráfico de barras"""
    # Detectar columnas categóricas y numéricas
    cat_cols = [col for col in data.columns if data[col].dtype == 'object']
    num_cols = [col for col in data.columns if data[col].dtype in ['float64', 'int64']]
    
    if not cat_cols or not num_cols:
        return dbc.Alert("No se pueden crear gráficos de barras con estos datos.", color="warning")
    
    cat_col = cat_cols[0]
    num_col = num_cols[0]
    
    # Agrupar datos si hay muchas categorías
    grouped_data = data.groupby(cat_col)[num_col].sum().reset_index()
    
    fig = px.bar(
        grouped_data.head(20),  # Top 20 para mejor visualización
        x=cat_col,
        y=num_col,
        title=f"Aportes de Caudal (GWh) por Río",
        labels={num_col: "Caudal (GWh)", cat_col: "Río"}
    )
    fig.update_layout(
        height=500,
        xaxis_tickangle=-45
    )
    return dbc.Card([
        dbc.CardHeader([
            html.H6([
                html.I(className="bi bi-bar-chart me-2"),
                "Aportes de Caudal (GWh) por Río"
            ], className="mb-0")
        ]),
        dbc.CardBody([
            dcc.Graph(id="bar-rio-graph", figure=fig, clear_on_unhover=True)
        ])
    ])
# Callback para mostrar el modal con la tabla diaria al hacer click en una barra
@app.callback(
    [Output("modal-rio-table", "is_open"), Output("modal-table-content", "children")],
    [Input("bar-rio-graph", "clickData"), Input("modal-rio-table", "is_open")],
    [State("region-data-store", "data")]
)
def show_modal_table(clickData, is_open, region_data):
    ctx = dash.callback_context
    # Si se hace click en una barra, mostrar el modal con la tabla de ese río
    if ctx.triggered and ctx.triggered[0]["prop_id"].startswith("bar-rio-graph") and clickData:
        rio = clickData["points"][0]["x"]
        df = pd.DataFrame(region_data)
        df_rio = df[df["Name"] == rio]
        if not df_rio.empty:
            df_rio = df_rio.sort_values("Date")
            df_rio = df_rio[["Date", "Value"]].rename(columns={"Date": "Fecha", "Value": "Caudal (GWh)"})
            total = df_rio["Caudal (GWh)"].sum()
            total_row = {"Fecha": "TOTAL", "Caudal (GWh)": round(total, 2)}
            data_with_total = df_rio.to_dict('records') + [total_row]
            table = dash_table.DataTable(
                data=data_with_total,
                columns=[{"name": i, "id": i} for i in df_rio.columns],
                style_cell={'textAlign': 'left', 'padding': '6px', 'fontFamily': 'Arial', 'fontSize': 14},
                style_header={'backgroundColor': '#e3e3e3', 'fontWeight': 'bold'},
                style_data={'backgroundColor': '#f8f8f8'},
                page_action="native",
                page_current=0,
                page_size=15,
                export_format="xlsx",
                export_headers="display"
            )
            return True, table
        else:
            return False, None
    # Si se cierra el modal
    elif ctx.triggered and ctx.triggered[0]["prop_id"].startswith("modal-rio-table"):
        return False, None
    # Por defecto, modal cerrado
    return False, None

def create_stats_summary(data):
    """Crear resumen estadístico"""
    numeric_data = data.select_dtypes(include=['float64', 'int64'])
    
    if numeric_data.empty:
        return dbc.Alert("No hay datos numéricos para análisis estadístico.", color="warning")
    
    stats = numeric_data.describe()
    
    return dbc.Card([
        dbc.CardHeader([
            html.H6([
                html.I(className="bi bi-calculator me-2"),
                "Resumen Estadístico"
            ], className="mb-0")
        ]),
        dbc.CardBody([
            dash_table.DataTable(
                data=stats.round(2).reset_index().to_dict('records'),
                columns=[{"name": i, "id": i} for i in stats.reset_index().columns],
                style_cell={
                    'textAlign': 'center',
                    'padding': '10px',
                    'fontFamily': 'Arial'
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                style_data={
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            )
        ])
    ])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
