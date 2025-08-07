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
import importlib.util
pydataxm_path = os.path.join(os.path.dirname(__file__), 'API_XM', 'pydataxm', 'pydataxm.py')
spec = importlib.util.spec_from_file_location('pydataxm', pydataxm_path)
pydataxm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pydataxm)
ReadDB = pydataxm.ReadDB
import warnings
warnings.filterwarnings("ignore")

# Inicializar la aplicación Dash con tema Bootstrap

# --- NUEVO: Fecha/hora de última actualización del código ---
import time
LAST_UPDATE = time.strftime('%Y-%m-%d %H:%M:%S')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])
app.title = " Caudal y capacidad util - XM"

# Inicializar API XM
import traceback
try:
    objetoAPI = ReadDB()
    print("API XM inicializada correctamente")
except Exception as e:
    print(f"Error al inicializar API XM: {e}")
    traceback.print_exc()
    objetoAPI = None



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
            html.Div([
                html.Span(
                    [
                        html.I(className="bi bi-lightning-charge-fill", style={"color": "#007bff", "fontSize": "2.2rem", "verticalAlign": "middle", "marginRight": "0.5rem"}),
                        html.Span("Tablero Hidrológico del MME", style={"fontWeight": "bold", "fontSize": "2.1rem", "color": "#1565c0", "verticalAlign": "middle", "letterSpacing": "-1px"})
                    ],
                    style={"display": "inline-flex", "alignItems": "center"}
                ),
                html.Br(),
                html.Span(
                    "Datos aportados por XM - Sistema de Información Hidrológica de Colombia",
                    style={"fontSize": "1.1rem", "color": "#555", "fontWeight": 400}
                ),
                html.Br(),
                # --- NUEVO: Mostrar fecha/hora de última actualización ---
                html.Span(
                    f"Última actualización: {LAST_UPDATE}",
                    style={"fontSize": "0.95rem", "color": "#888", "fontStyle": "italic"}
                )
            ], className="text-center mb-2 mt-2"),
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
        # Mostrar datos por defecto de todas las regiones al cargar la página
        if start_date and end_date and not n_clicks:
            try:
                data = objetoAPI.request_data('AporCaudal', 'Rio', start_date, end_date)
                if data is None or data.empty:
                    return dbc.Alert("No se encontraron datos para mostrar.", color="warning")
                
                # Agregar información de región
                data['Region'] = data['Name'].map(RIO_REGION)
                
                # Mostrar contribución total por región (todas las regiones)
                if 'Name' in data.columns and 'Value' in data.columns:
                    # Agrupar por región y fecha para crear series temporales
                    region_df = data.groupby(['Region', 'Date'])['Value'].sum().reset_index()
                    region_df = region_df[region_df['Region'].notna()]  # Filtrar regiones válidas
                    
                    # Obtener datos de embalses para todas las regiones con estructura jerárquica
                    regiones_totales, df_completo_embalses = get_tabla_regiones_embalses()
                    
                    return html.Div([
                        html.H5("🇨🇴 Contribución Energética por Región Hidrológica de Colombia", className="text-center mb-2"),
                        html.P("Vista panorámica nacional: Series temporales comparativas de aportes de caudal por región hidrológica. Haga clic en cualquier punto para ver el detalle agregado diario de la región. Los datos incluyen todos los ríos monitoreados en el período seleccionado, agrupados por región para análisis comparativo nacional.", className="text-center text-muted mb-3", style={"fontSize": "0.9rem"}),
                        dbc.Row([
                            dbc.Col(create_bar_chart(region_df, "Aportes por región - Todas las regiones"), md=12)
                        ]),
                        dcc.Store(id="region-data-store", data=data.to_dict('records')),
                        dcc.Store(id="embalses-completo-data", data=df_completo_embalses.to_dict('records')),
                        dbc.Modal([
                            dbc.ModalHeader(dbc.ModalTitle(id="modal-title-dynamic", children="Detalle de datos hidrológicos"), close_button=True),
                            dbc.ModalBody([
                                html.Div(id="modal-description", className="mb-3", style={"fontSize": "0.9rem", "color": "#666"}),
                                html.Div(id="modal-table-content")
                            ]),
                        ], id="modal-rio-table", is_open=False, size="xl", backdrop=True, centered=True, style={"zIndex": 2000}),
                        html.Hr(),
                        html.H5("⚡ Capacidad Útil Diaria de Energía por Región Hidrológica", className="text-center mt-4 mb-2"),
                        html.P("📋 Tabla interactiva jerárquica: Haz clic en cualquier región para expandir y ver el detalle de sus embalses constituyentes. Los totales incluyen la suma de todos los embalses por región con participación porcentual del sistema nacional.", className="text-center text-muted mb-3", style={"fontSize": "0.9rem"}),
                        dbc.Row([
                            dbc.Col([
                                dash_table.DataTable(
                                    id="tabla-regiones-embalses",
                                    data=regiones_totales.to_dict('records'),
                                    columns=[
                                        {"name": "Región", "id": "Región"},
                                        {"name": "Total (GWh)", "id": "Total (GWh)"},
                                        {"name": "Participación (%)", "id": "Participación (%)"}
                                    ],
                                    style_cell={'textAlign': 'left', 'padding': '6px', 'fontFamily': 'Arial', 'fontSize': 14},
                                    style_header={'backgroundColor': '#e3e3e3', 'fontWeight': 'bold'},
                                    style_data={'backgroundColor': '#f8f8f8'},
                                    style_data_conditional=[
                                        {
                                            'if': {'filter_query': '{Tipo} = "region"'},
                                            'backgroundColor': '#e8f4fd',
                                            'fontWeight': 'bold',
                                            'cursor': 'pointer'
                                        },
                                        {
                                            'if': {'filter_query': '{Tipo} = "embalse"'},
                                            'backgroundColor': '#f8f8f8',
                                            'fontStyle': 'italic'
                                        }
                                    ],
                                    page_action="none",
                                    row_selectable="single"
                                ),
                            ], md=12)
                        ])
                    ])
                else:
                    return dbc.Alert("No se pueden procesar los datos obtenidos.", color="warning")
            except Exception as e:
                return dbc.Alert(f"Error al obtener datos por defecto: {str(e)}", color="danger")
        else:
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
                html.H5(f"🌊 Río {rio} - Serie Temporal Completa de Aportes de Caudal", className="text-center mb-2"),
                html.P(f"Análisis detallado del río {rio} incluyendo gráfico de tendencias temporales y tabla de datos diarios con participación porcentual. Los valores están expresados en Gigavatios-hora (GWh) y representan la energía potencial aprovechable del caudal.", className="text-center text-muted mb-3", style={"fontSize": "0.9rem"}),
                dbc.Row([
                    dbc.Col([
                        html.H6("📈 Evolución Temporal", className="text-center mb-2"),
                        create_line_chart(plot_df)
                    ], md=7),
                    dbc.Col([
                        html.H6("📊 Datos Detallados", className="text-center mb-2"),
                        create_data_table(plot_df)
                    ], md=5)
                ])
            ])

        # Si no hay río seleccionado o es 'Todos los ríos', mostrar barra de contribución total por río
        # Si hay región seleccionada, filtrar por región, si no, mostrar todas las regiones
        data['Region'] = data['Name'].map(RIO_REGION)
        
        if region:
            data_filtered = data[data['Region'] == region]
            title_suffix = f"en la región {region}"
            embalses_df = get_embalses_capacidad(region)
            # Obtener embalses de la región específica
            try:
                embalses_info = objetoAPI.request_data('ListadoEmbalses','Sistema','2024-01-01','2024-01-02')
                embalses_info['Values_Name'] = embalses_info['Values_Name'].str.strip().str.upper()
                embalses_info['Values_HydroRegion'] = embalses_info['Values_HydroRegion'].str.strip().str.title()
                embalses_region = embalses_info[embalses_info['Values_HydroRegion'] == region]['Values_Name'].sort_values().unique()
            except Exception as e:
                print(f"Error obteniendo embalses para el filtro: {e}")
                embalses_region = []
        else:
            data_filtered = data
            title_suffix = "- Todas las regiones"
            embalses_df = get_embalses_capacidad()
            embalses_region = embalses_df['Embalse'].unique() if not embalses_df.empty else []

        if data_filtered.empty:
            return dbc.Alert("No se encontraron datos para la región seleccionada." if region else "No se encontraron datos.", color="warning")
            
        if 'Name' in data_filtered.columns and 'Value' in data_filtered.columns:
            bar_df = data_filtered.groupby('Name')['Value'].sum().reset_index()
            bar_df = bar_df.rename(columns={'Name': 'Río', 'Value': 'GWh'})
            
            return html.Div([
                html.H5(f"🏞️ Contribución Energética por Río {title_suffix.title()}", className="text-center mb-2"),
                html.P(f"Análisis comparativo de aportes de caudal entre ríos {'de la región seleccionada' if region else 'de todas las regiones de Colombia'}. Haga clic en cualquier punto del gráfico para ver el detalle diario completo del río correspondiente. Los datos están agregados por el período de tiempo seleccionado.", className="text-center text-muted mb-3", style={"fontSize": "0.9rem"}),
                dbc.Row([
                    dbc.Col(create_bar_chart(bar_df, f"Aportes por río {title_suffix}"), md=12)
                ]),
                dcc.Store(id="region-data-store", data=data_filtered.to_dict('records')),
                dbc.Modal([
                    dbc.ModalHeader(dbc.ModalTitle(id="modal-title-dynamic", children="Detalle de datos hidrológicos"), close_button=True),
                    dbc.ModalBody([
                        html.Div(id="modal-description", className="mb-3", style={"fontSize": "0.9rem", "color": "#666"}),
                        html.Div(id="modal-table-content")
                    ]),
                ], id="modal-rio-table", is_open=False, size="xl", backdrop=True, centered=True, style={"zIndex": 2000}),
                html.Hr(),
                html.H5(f"⚡ Capacidad Útil Diaria de Energía - Embalses {title_suffix}", className="text-center mt-4 mb-2"),
                html.P(f"Análisis detallado de la capacidad energética por embalse. Los datos muestran la energía disponible en GWh que puede ser generada diariamente por cada embalse. Incluye participación porcentual y filtros interactivos.", className="text-center text-muted mb-3", style={"fontSize": "0.9rem"}),
                dbc.Row([
                    dbc.Col([
                        html.H6("📊 Participación Porcentual por Embalse", className="text-center mb-2"),
                        html.P("Distribución porcentual de la capacidad energética entre embalses. La tabla incluye una fila TOTAL que suma exactamente 100%.", className="text-muted mb-2", style={"fontSize": "0.8rem"}),
                        dash_table.DataTable(
                            id="tabla-participacion-embalse",
                            data=get_participacion_embalses(embalses_df).to_dict('records'),
                            columns=[
                                {"name": "Embalse", "id": "Embalse"},
                                {"name": "Participación (%)", "id": "Participación (%)"}
                            ],
                            style_cell={'textAlign': 'left', 'padding': '6px', 'fontFamily': 'Arial', 'fontSize': 14},
                            style_header={'backgroundColor': '#e3e3e3', 'fontWeight': 'bold'},
                            style_data={'backgroundColor': '#f8f8f8'},
                            style_data_conditional=[
                                {
                                    'if': {'filter_query': '{Embalse} = "TOTAL"'},
                                    'backgroundColor': '#007bff',
                                    'color': 'white',
                                    'fontWeight': 'bold'
                                }
                            ],
                            page_action="none"
                        ),
                    ], md=4),
                    dbc.Col([
                        html.H6("🏭 Capacidad Detallada por Embalse", className="text-center mb-2"),
                        html.P("Valores específicos de capacidad útil diaria en GWh. Use el filtro para buscar embalses específicos.", className="text-muted mb-2", style={"fontSize": "0.8rem"}),
                        dcc.Dropdown(
                            id="embalse-cap-dropdown",
                            options=[{"label": e.title(), "value": e} for e in embalses_region],
                            placeholder="🔍 Buscar embalse específico...",
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
                            style_data_conditional=[
                                {
                                    'if': {'filter_query': '{Embalse} = "TOTAL"'},
                                    'backgroundColor': '#007bff',
                                    'color': 'white',
                                    'fontWeight': 'bold'
                                }
                            ],
                            page_action="none"
                        ),
                    ], md=8)
                ]),
                dcc.Store(id="embalse-cap-data", data=embalses_df.to_dict('records')),
                dcc.Store(id="participacion-data", data=get_participacion_embalses(embalses_df).to_dict('records'))
            ])
        else:
            return dbc.Alert("No se pueden graficar los datos de la región." if region else "No se pueden graficar los datos.", color="warning")
    except Exception as e:
        return dbc.Alert(f"Error al consultar los datos: {str(e)}", color="danger")

# Callback adicional para cargar datos por defecto al iniciar la página
@app.callback(
    Output("tab-content", "children", allow_duplicate=True),
    [Input("start-date", "date"), Input("end-date", "date")],
    prevent_initial_call='initial_duplicate'
)
def load_default_data(start_date, end_date):
    # Solo ejecutar si no hay interacción del usuario y las fechas están disponibles
    if start_date and end_date:
        try:
            data = objetoAPI.request_data('AporCaudal', 'Rio', start_date, end_date)
            if data is None or data.empty:
                return dbc.Alert("No se encontraron datos para mostrar.", color="warning", className="text-center")
            
            # Agregar información de región
            data['Region'] = data['Name'].map(RIO_REGION)
            
            # Mostrar contribución total por región (todas las regiones)
            if 'Name' in data.columns and 'Value' in data.columns:
                # Agrupar por región y fecha para crear series temporales
                region_df = data.groupby(['Region', 'Date'])['Value'].sum().reset_index()
                region_df = region_df[region_df['Region'].notna()]  # Filtrar regiones válidas
                
                # Obtener datos de embalses para todas las regiones con estructura jerárquica
                regiones_totales, df_completo_embalses = get_tabla_regiones_embalses()
                
                return html.Div([
                    html.H5("Contribución de caudal por región - Todas las regiones", className="text-center mb-3"),
                    dbc.Row([
                        dbc.Col(create_bar_chart(region_df, "Aportes por región - Todas las regiones"), md=12)
                    ]),
                    dcc.Store(id="region-data-store", data=data.to_dict('records')),
                    dcc.Store(id="embalses-completo-data", data=df_completo_embalses.to_dict('records')),
                    dbc.Modal([
                        dbc.ModalHeader(dbc.ModalTitle(id="modal-title-dynamic", children="Detalle de datos hidrológicos"), close_button=True),
                        dbc.ModalBody([
                            html.Div(id="modal-description", className="mb-3", style={"fontSize": "0.9rem", "color": "#666"}),
                            html.Div(id="modal-table-content")
                        ]),
                    ], id="modal-rio-table", is_open=False, size="xl", backdrop=True, centered=True, style={"zIndex": 2000}),
                    html.Hr(),
                    html.H5("Capacidad útil diaria de energía por región", className="text-center mt-4 mb-2"),
                    html.P("Haz clic en una región para ver sus embalses", className="text-center text-muted mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dash_table.DataTable(
                                id="tabla-regiones-embalses",
                                data=regiones_totales.to_dict('records'),
                                columns=[
                                    {"name": "Región", "id": "Región"},
                                    {"name": "Total (GWh)", "id": "Total (GWh)"},
                                    {"name": "Participación (%)", "id": "Participación (%)"}
                                ],
                                style_cell={'textAlign': 'left', 'padding': '6px', 'fontFamily': 'Arial', 'fontSize': 14},
                                style_header={'backgroundColor': '#e3e3e3', 'fontWeight': 'bold'},
                                style_data={'backgroundColor': '#f8f8f8'},
                                style_data_conditional=[
                                    {
                                        'if': {'filter_query': '{Tipo} = "region"'},
                                        'backgroundColor': '#e8f4fd',
                                        'fontWeight': 'bold',
                                        'cursor': 'pointer'
                                    },
                                    {
                                        'if': {'filter_query': '{Tipo} = "embalse"'},
                                        'backgroundColor': '#f8f8f8',
                                        'fontStyle': 'italic'
                                    }
                                ],
                                page_action="none",
                                row_selectable="single"
                            ),
                        ], md=12)
                    ])
                ])
            else:
                return dbc.Alert("No se pueden procesar los datos obtenidos.", color="warning", className="text-center")
        except Exception as e:
            return dbc.Alert(f"Error al cargar datos iniciales: {str(e)}", color="danger", className="text-center")
    
    return dbc.Alert("Cargando datos iniciales...", color="info", className="text-center")

# --- Mover fuera: Callback para actualizar la tabla de capacidad útil de embalse de forma interactiva ---
@app.callback(
    [Output("tabla-capacidad-embalse", "data"), Output("tabla-participacion-embalse", "data")],
    [Input("embalse-cap-dropdown", "value")],
    [State("embalse-cap-data", "data"), State("participacion-data", "data")]
)
def update_tabla_capacidad_embalse(embalse, data_capacidad, data_participacion):
    import pandas as pd
    df_cap = pd.DataFrame(data_capacidad)
    df_part = pd.DataFrame(data_participacion)
    
    if embalse:
        # El dropdown usa embalses en mayúsculas, igual que la columna 'Embalse'
        df_cap = df_cap[df_cap['Embalse'].str.upper() == embalse.upper()]
        df_part = df_part[df_part['Embalse'].str.upper() == embalse.upper()]
    
    # Tabla de capacidad
    records_cap = df_cap.to_dict('records')
    if not df_cap.empty:
        total = df_cap['Capacidad Útil Diaria (GWh)'].sum()
        total_row = {col: '' for col in df_cap.columns}
        total_row['Embalse'] = 'TOTAL'
        total_row['Capacidad Útil Diaria (GWh)'] = round(total, 2)
        records_cap.append(total_row)
    
    # Tabla de participación
    records_part = df_part.to_dict('records')
    if not df_part.empty:
        # Para la tabla de participación, el total debe ser exactamente 100%
        total_row_part = {col: '' for col in df_part.columns}
        total_row_part['Embalse'] = 'TOTAL'
        total_row_part['Participación (%)'] = 100.0
        records_part.append(total_row_part)
    
    return records_cap, records_part

# --- Callback para manejar expansión/contracción de regiones en la tabla ---
@app.callback(
    Output("tabla-regiones-embalses", "data"),
    [Input("tabla-regiones-embalses", "selected_rows")],
    [State("tabla-regiones-embalses", "data"), State("embalses-completo-data", "data")]
)
def expand_region_table(selected_rows, current_data, embalses_data):
    if not selected_rows or not current_data:
        # Si no hay selección, mostrar solo regiones
        regiones_totales, _ = get_tabla_regiones_embalses()
        return regiones_totales.to_dict('records')
    
    import pandas as pd
    df_current = pd.DataFrame(current_data)
    df_embalses_completo = pd.DataFrame(embalses_data)
    
    selected_row_idx = selected_rows[0]
    if selected_row_idx >= len(df_current):
        return current_data
        
    selected_row = df_current.iloc[selected_row_idx]
    
    # Si se seleccionó una región, expandir o contraer
    if selected_row.get('Tipo') == 'region':
        region_name = selected_row['Región']
        
        # Verificar si ya está expandida (buscar embalses de esta región en la tabla actual)
        is_expanded = any(
            row.get('Tipo') == 'embalse' and region_name in str(row.get('Región', ''))
            for row in current_data[selected_row_idx+1:]
        )
        
        if is_expanded:
            # Contraer: remover embalses de esta región
            new_data = []
            skip_embalses = False
            for i, row in enumerate(current_data):
                if i == selected_row_idx:
                    new_data.append(row)
                    skip_embalses = True
                elif skip_embalses and row.get('Tipo') == 'embalse':
                    # Saltar embalses hasta encontrar otra región
                    continue
                else:
                    skip_embalses = False
                    new_data.append(row)
            return new_data
        else:
            # Expandir: agregar embalses de esta región
            embalses_region = get_embalses_by_region(region_name, df_embalses_completo)
            
            new_data = current_data.copy()
            # Insertar embalses después de la región seleccionada
            insert_idx = selected_row_idx + 1
            for _, embalse_row in embalses_region.iterrows():
                new_data.insert(insert_idx, embalse_row.to_dict())
                insert_idx += 1
            
            return new_data
    
    return current_data

# --- Función para calcular participación porcentual de embalses ---
def get_participacion_embalses(df_embalses):
    """
    Calcula la participación porcentual de cada embalse respecto al total.
    """
    if df_embalses.empty or 'Capacidad Útil Diaria (GWh)' not in df_embalses.columns:
        return pd.DataFrame(columns=['Embalse', 'Participación (%)'])
    
    df_participacion = df_embalses.copy()
    total = df_participacion['Capacidad Útil Diaria (GWh)'].sum()
    
    if total > 0:
        # Calcular porcentajes sin redondear primero
        porcentajes = (df_participacion['Capacidad Útil Diaria (GWh)'] / total * 100)
        
        # Ajustar el último valor para que la suma sea exactamente 100%
        porcentajes_redondeados = porcentajes.round(2)
        diferencia = 100 - porcentajes_redondeados.sum()
        
        # Si hay diferencia por redondeo, ajustar el valor más grande
        if abs(diferencia) > 0.001:
            idx_max = porcentajes_redondeados.idxmax()
            porcentajes_redondeados.loc[idx_max] += diferencia
            
        df_participacion['Participación (%)'] = porcentajes_redondeados.round(2)
    else:
        df_participacion['Participación (%)'] = 0
    
    # Ordenar de mayor a menor por participación
    df_participacion = df_participacion.sort_values('Participación (%)', ascending=False)
    
    # Solo devolver las columnas necesarias
    return df_participacion[['Embalse', 'Participación (%)']].reset_index(drop=True)

# --- Función para crear tabla con capacidad y participación combinadas ---
def get_tabla_con_participacion(df_embalses):
    """
    Crea una tabla que combina la capacidad útil con la participación porcentual.
    """
    if df_embalses.empty or 'Capacidad Útil Diaria (GWh)' not in df_embalses.columns:
        return pd.DataFrame(columns=['Embalse', 'Capacidad Útil Diaria (GWh)', 'Participación (%)'])
    
    df_resultado = df_embalses.copy()
    total = df_resultado['Capacidad Útil Diaria (GWh)'].sum()
    
    if total > 0:
        # Calcular porcentajes sin redondear primero
        porcentajes = (df_resultado['Capacidad Útil Diaria (GWh)'] / total * 100)
        
        # Ajustar el último valor para que la suma sea exactamente 100%
        porcentajes_redondeados = porcentajes.round(2)
        diferencia = 100 - porcentajes_redondeados.sum()
        
        # Si hay diferencia por redondeo, ajustar el valor más grande
        if abs(diferencia) > 0.001:
            idx_max = porcentajes_redondeados.idxmax()
            porcentajes_redondeados.loc[idx_max] += diferencia
            
        df_resultado['Participación (%)'] = porcentajes_redondeados.round(2)
    else:
        df_resultado['Participación (%)'] = 0
    
    # Ordenar de mayor a menor por participación
    df_resultado = df_resultado.sort_values('Participación (%)', ascending=False)
    
    return df_resultado[['Embalse', 'Capacidad Útil Diaria (GWh)', 'Participación (%)']].reset_index(drop=True)

# --- Función para crear tabla jerárquica de regiones con embalses ---
def get_tabla_regiones_embalses():
    """
    Crea una tabla jerárquica que muestra primero las regiones y permite expandir para ver embalses.
    """
    try:
        # Obtener todos los embalses con su información de región
        embalses_info = objetoAPI.request_data('ListadoEmbalses','Sistema','2024-01-01','2024-01-02')
        embalses_info['Values_Name'] = embalses_info['Values_Name'].str.strip().str.upper()
        embalses_info['Values_HydroRegion'] = embalses_info['Values_HydroRegion'].str.strip().str.title()
        
        # Obtener capacidades por embalse
        embalses_capacidad = get_embalses_capacidad()
        
        # Combinar información de región con capacidades
        df_completo = embalses_capacidad.merge(
            embalses_info[['Values_Name', 'Values_HydroRegion']], 
            left_on='Embalse', 
            right_on='Values_Name', 
            how='left'
        )
        
        # Agrupar por región
        regiones_totales = df_completo.groupby('Values_HydroRegion')['Capacidad Útil Diaria (GWh)'].sum().reset_index()
        regiones_totales = regiones_totales.rename(columns={'Values_HydroRegion': 'Región', 'Capacidad Útil Diaria (GWh)': 'Total (GWh)'})
        regiones_totales = regiones_totales.sort_values('Total (GWh)', ascending=False)
        
        # Calcular participación porcentual de regiones
        total_general = regiones_totales['Total (GWh)'].sum()
        if total_general > 0:
            regiones_totales['Participación (%)'] = (regiones_totales['Total (GWh)'] / total_general * 100).round(2)
            # Ajustar para que sume exactamente 100%
            diferencia = 100 - regiones_totales['Participación (%)'].sum()
            if abs(diferencia) > 0.001:
                idx_max = regiones_totales['Participación (%)'].idxmax()
                regiones_totales.loc[idx_max, 'Participación (%)'] += diferencia
                regiones_totales['Participación (%)'] = regiones_totales['Participación (%)'].round(2)
        else:
            regiones_totales['Participación (%)'] = 0
        
        # Agregar identificador de tipo
        regiones_totales['Tipo'] = 'region'
        regiones_totales['ID'] = range(len(regiones_totales))
        
        return regiones_totales, df_completo
        
    except Exception as e:
        print(f"Error creando tabla de regiones: {e}")
        return pd.DataFrame(), pd.DataFrame()

def get_embalses_by_region(region, df_completo):
    """
    Obtiene los embalses de una región específica con participación dentro de esa región.
    """
    embalses_region = df_completo[df_completo['Values_HydroRegion'] == region].copy()
    if embalses_region.empty:
        return pd.DataFrame()
    
    total_region = embalses_region['Capacidad Útil Diaria (GWh)'].sum()
    if total_region > 0:
        embalses_region['Participación (%)'] = (embalses_region['Capacidad Útil Diaria (GWh)'] / total_region * 100).round(2)
        # Ajustar para que sume exactamente 100%
        diferencia = 100 - embalses_region['Participación (%)'].sum()
        if abs(diferencia) > 0.001:
            idx_max = embalses_region['Participación (%)'].idxmax()
            embalses_region.loc[idx_max, 'Participación (%)'] += diferencia
            embalses_region['Participación (%)'] = embalses_region['Participación (%)'].round(2)
    else:
        embalses_region['Participación (%)'] = 0
    
    # Formatear para mostrar como sub-elementos
    resultado = embalses_region[['Embalse', 'Capacidad Útil Diaria (GWh)', 'Participación (%)']].copy()
    resultado = resultado.rename(columns={'Embalse': 'Región', 'Capacidad Útil Diaria (GWh)': 'Total (GWh)'})
    resultado['Región'] = '    └─ ' + resultado['Región'].astype(str)  # Identar embalses
    resultado['Tipo'] = 'embalse'
    
    return resultado
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
    """Tabla simple de datos de caudal con participación porcentual"""
    if data is None or data.empty:
        return dbc.Alert("No hay datos para mostrar en la tabla.", color="warning")
    
    # Crear una copia del dataframe para modificar
    df_with_participation = data.copy()
    
    # Si tiene columna 'GWh', calcular participación
    if 'GWh' in df_with_participation.columns:
        # Filtrar filas que no sean TOTAL para calcular el porcentaje
        df_no_total = df_with_participation[df_with_participation['GWh'] != 'TOTAL'].copy()
        if not df_no_total.empty:
            # Asegurar que los valores son numéricos
            df_no_total['GWh'] = pd.to_numeric(df_no_total['GWh'], errors='coerce')
            total = df_no_total['GWh'].sum()
            
            if total > 0:
                # Calcular porcentajes
                porcentajes = (df_no_total['GWh'] / total * 100).round(2)
                
                # Ajustar para que sume exactamente 100%
                diferencia = 100 - porcentajes.sum()
                if abs(diferencia) > 0.001 and len(porcentajes) > 0:
                    idx_max = porcentajes.idxmax()
                    porcentajes.loc[idx_max] += diferencia
                
                # Agregar la columna de participación
                df_with_participation.loc[df_no_total.index, 'Participación (%)'] = porcentajes.round(2)
                
                # Agregar fila TOTAL si no existe
                has_total_row = any(df_with_participation.iloc[:, 0] == 'TOTAL')
                if not has_total_row:
                    # Crear fila total
                    total_row = {}
                    for col in df_with_participation.columns:
                        if col == df_with_participation.columns[0]:  # Primera columna (normalmente 'Fecha')
                            total_row[col] = 'TOTAL'
                        elif col == 'GWh':
                            total_row[col] = round(total, 2)
                        elif col == 'Participación (%)':
                            total_row[col] = 100.0
                        else:
                            total_row[col] = ''
                    
                    # Agregar la fila total al dataframe
                    df_with_participation = pd.concat([df_with_participation, pd.DataFrame([total_row])], ignore_index=True)
            else:
                df_with_participation['Participación (%)'] = 0
        else:
            df_with_participation['Participación (%)'] = 0
    
    # Detectar si hay columna de totales
    style_data_conditional = []
    if 'TOTAL' in df_with_participation.values:
        # Buscar la columna que contiene el total
        for col in df_with_participation.columns:
            if any(df_with_participation[col] == 'TOTAL'):
                style_data_conditional.append({
                    'if': {'filter_query': f'{{{col}}} = "TOTAL"'},
                    'backgroundColor': '#007bff',
                    'color': 'white',
                    'fontWeight': 'bold'
                })
    
    return dash_table.DataTable(
        data=df_with_participation.head(1000).to_dict('records'),
        columns=[{"name": i, "id": i} for i in df_with_participation.columns],
        style_cell={'textAlign': 'left', 'padding': '6px', 'fontFamily': 'Arial', 'fontSize': 14},
        style_header={'backgroundColor': '#e3e3e3', 'fontWeight': 'bold'},
        style_data={'backgroundColor': '#f8f8f8'},
        style_data_conditional=style_data_conditional,
        page_action="none",
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
    """Crear gráfico de líneas por región o río"""
    # Detectar columnas categóricas y numéricas
    cat_cols = [col for col in data.columns if data[col].dtype == 'object']
    num_cols = [col for col in data.columns if data[col].dtype in ['float64', 'int64']]
    
    if not cat_cols or not num_cols:
        return dbc.Alert("No se pueden crear gráficos de líneas con estos datos.", color="warning")
    
    cat_col = cat_cols[0]
    num_col = num_cols[0]
    
    # Si los datos tienen información de región, crear líneas por región
    if 'Region' in data.columns:
        # Agrupar por región y fecha para crear series temporales por región
        if 'Date' in data.columns:
            # Datos diarios por región - series temporales
            fig = px.line(
                data,
                x='Date',
                y='Value', 
                color='Region',
                title="Aportes de Caudal (GWh) por Región",
                labels={'Value': "Caudal (GWh)", 'Date': "Fecha", 'Region': "Región"},
                markers=True
            )
            # Asegurar que cada línea tenga información de región para el click
            fig.for_each_trace(lambda t: t.update(legendgroup=t.name, customdata=[t.name] * len(t.x)))
        else:
            # Datos agregados por región - convertir a líneas también
            region_data = data.groupby('Region')[num_col].sum().reset_index()
            region_data = region_data.sort_values(by=num_col, ascending=False)
            
            fig = px.line(
                region_data,
                x='Region',
                y=num_col,
                title="Aportes de Caudal (GWh) por Región",
                labels={num_col: "Caudal (GWh)", 'Region': "Región"},
                markers=True,
                color_discrete_sequence=px.colors.qualitative.Set1
            )
    else:
        # Agrupar y ordenar datos de mayor a menor - usar líneas en lugar de barras
        grouped_data = data.groupby(cat_col)[num_col].sum().reset_index()
        grouped_data = grouped_data.sort_values(by=num_col, ascending=False)
        
        fig = px.line(
            grouped_data.head(20),  # Top 20 para mejor visualización
            x=cat_col,
            y=num_col,
            title=f"Aportes de Caudal (GWh) por Río",
            labels={num_col: "Caudal (GWh)", cat_col: "Río"},
            markers=True
        )
    
    fig.update_layout(
        height=500,
        xaxis_tickangle=-45,
        template="plotly_white"
    )
    
    # Mejorar el estilo para todos los gráficos de líneas
    fig.update_traces(
        marker=dict(size=8),
        line=dict(width=3)
    )
    
    return dbc.Card([
        dbc.CardHeader([
            html.H6([
                html.I(className="bi bi-graph-up me-2"),
                "Aportes de Caudal por Región" if 'Region' in data.columns else "Aportes de Caudal por Río"
            ], className="mb-0")
        ]),
        dbc.CardBody([
            dcc.Graph(id="bar-rio-graph", figure=fig, clear_on_unhover=True)
        ])
    ])
# Callback para mostrar el modal con la tabla diaria al hacer click en un punto de la línea
@app.callback(
    [Output("modal-rio-table", "is_open"), Output("modal-table-content", "children"), 
     Output("modal-title-dynamic", "children"), Output("modal-description", "children")],
    [Input("bar-rio-graph", "clickData"), Input("modal-rio-table", "is_open")],
    [State("region-data-store", "data")]
)
def show_modal_table(clickData, is_open, region_data):
    ctx = dash.callback_context
    # Si se hace click en un punto de la línea, mostrar el modal con la tabla
    if ctx.triggered and ctx.triggered[0]["prop_id"].startswith("bar-rio-graph") and clickData:
        point_data = clickData["points"][0]
        df = pd.DataFrame(region_data) if region_data else pd.DataFrame()
        
        if df.empty:
            return False, None, "Sin datos", "No hay información disponible para mostrar."
            
        # Verificar si es un gráfico con datos agrupados por región (series temporales) 
        # o por río individual (gráfico de barras convertido a líneas)
        
        # Caso 1: Si hay 'legendgroup' o 'customdata', es un gráfico por región (series temporales)
        if ('legendgroup' in point_data or 'customdata' in point_data) and 'Region' in df.columns:
            # Gráfico de líneas por región - obtener región del legendgroup o customdata
            if 'legendgroup' in point_data:
                selected_region = point_data['legendgroup']
            elif 'customdata' in point_data:
                selected_region = point_data['customdata']
            else:
                return False, None, "Error de región", "No se pudo identificar la región seleccionada."
                    
            # Filtrar datos de la región seleccionada
            df_region = df[df["Region"] == selected_region].copy()
            
            # Crear título y descripción detallados para región
            title = f"📊 Aportes de Caudal - Región {selected_region}"
            total_rios = len(df_region['Name'].unique()) if 'Name' in df_region.columns else 0
            fecha_inicio = df_region['Date'].min() if 'Date' in df_region.columns else "N/A"
            fecha_fin = df_region['Date'].max() if 'Date' in df_region.columns else "N/A"
            total_registros = len(df_region)
            total_gwh = df_region['Value'].sum() if 'Value' in df_region.columns else 0
            
            description = f"Esta tabla muestra los aportes diarios de caudal agregados por fecha para la región {selected_region}. Incluye datos de {total_rios} ríos únicos desde {fecha_inicio} hasta {fecha_fin}, con un total de {total_registros} registros y {total_gwh:.2f} GWh acumulados."
            
            if not df_region.empty:
                # Agrupar por fecha para mostrar el total diario de la región
                if 'Date' in df_region.columns and 'Value' in df_region.columns:
                    df_display = df_region.groupby(["Date"])["Value"].sum().reset_index()
                    df_display = df_display.sort_values("Date")
                    df_display = df_display.rename(columns={"Date": "Fecha", "Value": "Caudal (GWh)"})
                else:
                    df_display = df_region.head(100)  # Fallback
                
        # Caso 2: Si hay 'x' pero NO es series temporales, es un gráfico por río individual
        elif 'x' in point_data:
            # Gráfico de líneas por río individual
            selected_rio = point_data["x"]
            
            # Filtrar datos del río seleccionado
            if 'Name' in df.columns:
                df_region = df[df["Name"] == selected_rio].copy()
            else:
                # Buscar por el nombre del río en cualquier columna que contenga el nombre
                df_region = df[df.eq(selected_rio).any(axis=1)].copy()
            
            # Obtener la región del río seleccionado
            if 'Region' in df_region.columns and not df_region.empty:
                selected_region = df_region['Region'].iloc[0]
            else:
                # Intentar obtener la región del diccionario RIO_REGION
                selected_region = RIO_REGION.get(selected_rio.upper(), "Región no identificada")
            
            # Crear título y descripción detallados para río específico
            fecha_inicio = df_region['Date'].min() if 'Date' in df_region.columns and not df_region.empty else "N/A"
            fecha_fin = df_region['Date'].max() if 'Date' in df_region.columns and not df_region.empty else "N/A"
            total_registros = len(df_region)
            total_gwh = df_region['Value'].sum() if 'Value' in df_region.columns and not df_region.empty else 0
            promedio_diario = df_region['Value'].mean() if 'Value' in df_region.columns and not df_region.empty else 0
            
            title = f"🌊 Río {selected_rio} - Región {selected_region}"
            description = f"Serie temporal completa del río {selected_rio} ubicado en la región {selected_region}. Período: {fecha_inicio} a {fecha_fin} ({total_registros} días). Total acumulado: {total_gwh:.2f} GWh. Promedio diario: {promedio_diario:.2f} GWh. Esta tabla incluye todos los registros diarios disponibles con su participación porcentual respecto al total del período."
            
            if not df_region.empty:
                # Mostrar datos temporales del río
                if 'Date' in df_region.columns and 'Value' in df_region.columns:
                    df_display = df_region[['Date', 'Value']].sort_values("Date")
                    df_display = df_display.rename(columns={"Date": "Fecha", "Value": "Caudal (GWh)"})
                else:
                    df_display = df_region.head(100)  # Fallback
            else:
                return False, None, f"Sin datos para {selected_rio}", f"No se encontraron datos para el río {selected_rio}."
                
        else:
            return False, None, "Error de selección", "No se pudo procesar la selección realizada en el gráfico."
        
        if 'df_display' in locals() and not df_display.empty:
            # Calcular participación porcentual
            total = df_display["Caudal (GWh)"].sum()
            if total > 0:
                df_display['Participación (%)'] = (df_display["Caudal (GWh)"] / total * 100).round(2)
                # Ajustar para que sume exactamente 100%
                diferencia = 100 - df_display['Participación (%)'].sum()
                if abs(diferencia) > 0.001:
                    idx_max = df_display['Participación (%)'].idxmax()
                    df_display.loc[idx_max, 'Participación (%)'] += diferencia
                    df_display['Participación (%)'] = df_display['Participación (%)'].round(2)
            else:
                df_display['Participación (%)'] = 0
                
            # Agregar fila total
            total_row = {}
            for col in df_display.columns:
                if col == df_display.columns[0]:  # Primera columna (Fecha)
                    total_row[col] = 'TOTAL'
                elif col == "Caudal (GWh)":
                    total_row[col] = round(total, 2)
                elif col == 'Participación (%)':
                    total_row[col] = 100.0
                else:
                    total_row[col] = ''
            
            data_with_total = df_display.to_dict('records') + [total_row]
            
            # Identificar la columna para el estilo TOTAL
            total_column = df_display.columns[0]
            
            table = dash_table.DataTable(
                data=data_with_total,
                columns=[{"name": i, "id": i} for i in df_display.columns],
                style_cell={'textAlign': 'left', 'padding': '6px', 'fontFamily': 'Arial', 'fontSize': 14},
                style_header={'backgroundColor': '#e3e3e3', 'fontWeight': 'bold'},
                style_data={'backgroundColor': '#f8f8f8'},
                style_data_conditional=[
                    {
                        'if': {'filter_query': f'{{{total_column}}} = "TOTAL"'},
                        'backgroundColor': '#007bff',
                        'color': 'white',
                        'fontWeight': 'bold'
                    }
                ],
                page_action="none",
                export_format="xlsx",
                export_headers="display"
            )
            return True, table, title, description
        else:
            return False, None, "Sin datos procesables", "Los datos seleccionados no se pudieron procesar correctamente."
    
    # Si se cierra el modal
    elif ctx.triggered and ctx.triggered[0]["prop_id"].startswith("modal-rio-table"):
        return False, None, "", ""
    
    # Por defecto, modal cerrado
    return False, None, "", ""

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
