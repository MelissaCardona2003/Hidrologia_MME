import dash
from dash import dcc, html, Input, Output, State, dash_table, ALL, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import datetime as dt
from datetime import date, timedelta
import warnings
import sys
import os
import time
import traceback
from flask import Flask, jsonify
# Use the installed pydataxm package instead of local module
from pydataxm.pydataxm import ReadDB
warnings.filterwarnings("ignore")

# Inicializar la aplicación Dash con tema Bootstrap

# --- NUEVO: Fecha/hora de última actualización del código ---
LAST_UPDATE = time.strftime('%Y-%m-%d %H:%M:%S')

# Funciones auxiliares para formateo de datos
def format_number(value):
    """Formatear números con separadores de miles usando puntos"""
    if pd.isna(value) or not isinstance(value, (int, float)):
        return value
    
    # Formatear con separador de miles usando puntos (formato colombiano)
    return f"{value:,.2f}".replace(",", ".")

def format_date(date_value):
    """Formatear fechas para mostrar solo la fecha sin hora"""
    if pd.isna(date_value):
        return date_value
    
    if isinstance(date_value, str):
        try:
            # Intentar convertir string a datetime
            dt_value = pd.to_datetime(date_value)
            return dt_value.strftime('%Y-%m-%d')
        except Exception:
            return date_value
    elif hasattr(date_value, 'strftime'):
        return date_value.strftime('%Y-%m-%d')
    else:
        return date_value

# Crear servidor Flask personalizado
server = Flask(__name__)
server.config['SECRET_KEY'] = 'hidrologia-mme-colombia-2025'

# Inicializar la aplicación Dash con tema Bootstrap y servidor Flask personalizado
app = dash.Dash(__name__, 
                server=server,
                external_stylesheets=[
                    dbc.themes.BOOTSTRAP, 
                    dbc.icons.BOOTSTRAP,
                    "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
                    "/assets/mme-style.css"
                ],
                suppress_callback_exceptions=True)

# Rutas adicionales de Flask para endpoints de salud y API
@server.route('/health')
def health_check():
    """Endpoint de salud para monitoreo"""
    return jsonify({
        'status': 'healthy',
        'service': 'Dashboard Hidrológico MME',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'version': '3.3'
    }), 200

@server.route('/api/status')
def api_status():
    """Endpoint de estado de la API XM"""
    try:
        # Verificar si la API XM está funcionando
        if objetoAPI is not None:
            # Hacer una consulta rápida para verificar conectividad
            test_data = objetoAPI.request_data('ListadoRios', 'Sistema', '2024-01-01', '2024-01-02')
            api_status = 'connected' if test_data is not None and not test_data.empty else 'disconnected'
        else:
            api_status = 'disconnected'
        
        return jsonify({
            'status': 'ok',
            'api_xm_status': api_status,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'api_xm_status': 'error',
            'error': str(e),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }), 500

@server.route('/api/info')
def app_info():
    """Endpoint con información de la aplicación"""
    return jsonify({
        'name': 'Dashboard Hidrológico - MME Colombia',
        'description': 'Sistema de Información Hidrológica del Ministerio de Minas y Energía',
        'version': '3.3',
        'last_update': LAST_UPDATE,
        'author': 'Ministerio de Minas y Energía de Colombia',
        'data_source': 'XM - Expertos en Mercados',
        'endpoints': {
            'health': '/health',
            'api_status': '/api/status',
            'app_info': '/api/info'
        }
    }), 200

# Custom CSS para aplicar el estilo del Ministerio de Minas y Energía de Colombia
## Se ha eliminado el uso de app.index_string y el paradigma de index_string, manteniendo el resto del código igual.

app.title = "Dashboard Hidrológico - Ministerio de Minas y Energía de Colombia"

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
    """
    Obtiene las regiones que tienen ríos con datos de caudal activos.
    Filtra regiones que no tienen datos para evitar confusión al usuario.
    """
    try:
        # Obtener ríos con datos de caudal recientes
        df = objetoAPI.request_data('AporCaudal', 'Rio', (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'), date.today().strftime('%Y-%m-%d'))
        if 'Name' in df.columns:
            rios_con_datos = set(df['Name'].unique())
            # Filtrar solo regiones que tienen ríos con datos
            regiones_con_datos = set()
            for rio, region in RIO_REGION.items():
                if rio in rios_con_datos:
                    regiones_con_datos.add(region)
            return sorted(regiones_con_datos)
        else:
            return sorted(set(RIO_REGION.values()))
    except Exception as e:
        print(f"Error filtrando regiones con datos: {e}")
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



# Layout moderno y responsive para el dashboard
app.layout = html.Div([
    # Container principal con clase CSS personalizada
    dbc.Container([
        # Header oficial del Ministerio de Minas y Energía
        dbc.Row([
            dbc.Col([
                html.Div([
                    # Branding oficial del MinEnergía
                    html.Div([
                        html.Div([
                            html.I(className="bi bi-lightning-charge-fill", style={"fontSize": "32px"})
                        ], className="logo"),
                        html.Div([
                            html.H1("Sistema de Información Hidrológica", 
                                   className="header-gradient mb-1",
                                   style={"fontSize": "2.2rem", "fontWeight": "700"}),
                            html.H2("Ministerio de Minas y Energía", 
                                   style={"fontSize": "1.5rem", "fontWeight": "600", "color": "#ffffff", "marginBottom": "8px"}),
                            html.P("República de Colombia - Datos Hidrológicos XM",
                                  className="text-light mb-2",
                                  style={"fontSize": "1.1rem", "fontWeight": "400", "opacity": "0.9"}),
                            dbc.Badge([
                                html.I(className="bi bi-clock me-1"),
                                f"Última actualización: {LAST_UPDATE}"
                            ], color="light", className="px-3 py-1", style={"color": "#003366"})
                        ])
                    ], className="brand-mme")
                ], className="header-mme")
            ], width=12)
        ], className="mb-4"),

        # Panel de controles moderno
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="bi bi-sliders me-2", style={"color": "#667eea"}),
                            html.Strong("Panel de Control", style={"fontSize": "1.1rem"})
                        ], className="mb-3 d-flex align-items-center"),
                        
                        dbc.Row([
                            dbc.Col([
                                html.Label([
                                    html.I(className="bi bi-geo-alt me-2"),
                                    "Región Hidrológica"
                                ], className="fw-bold mb-2 d-flex align-items-center"),
                                dcc.Dropdown(
                                    id="region-dropdown",
                                    options=[{"label": "🌎 Todas las regiones", "value": "__ALL_REGIONS__"}] + 
                                           [{"label": f"📍 {r}", "value": r} for r in regiones],
                                    placeholder="Selecciona una región...",
                                    className="form-control-modern mb-0",
                                    style={"fontSize": "0.95rem"}
                                )
                            ], lg=3, md=6, sm=12),
                            
                            dbc.Col([
                                html.Label([
                                    html.I(className="bi bi-water me-2"),
                                    "Río Específico"
                                ], className="fw-bold mb-2 d-flex align-items-center"),
                                dcc.Dropdown(
                                    id="rio-dropdown",
                                    options=[{"label": f"🌊 {r}", "value": r} for r in rios],
                                    placeholder="Selecciona un río...",
                                    className="form-control-modern mb-0",
                                    style={"fontSize": "0.95rem"}
                                )
                            ], lg=3, md=6, sm=12),
                            
                            dbc.Col([
                                html.Label([
                                    html.I(className="bi bi-calendar-date me-2"),
                                    "Fecha Inicio"
                                ], className="fw-bold mb-2 d-flex align-items-center"),
                                dcc.DatePickerSingle(
                                    id="start-date",
                                    date=date.today() - timedelta(days=30),
                                    display_format="DD/MM/YYYY",
                                    className="form-control-modern",
                                    style={"width": "100%"}
                                )
                            ], lg=2, md=6, sm=12),
                            
                            dbc.Col([
                                html.Label([
                                    html.I(className="bi bi-calendar-check me-2"),
                                    "Fecha Final"
                                ], className="fw-bold mb-2 d-flex align-items-center"),
                                dcc.DatePickerSingle(
                                    id="end-date",
                                    date=date.today(),
                                    display_format="DD/MM/YYYY",
                                    className="form-control-modern",
                                    style={"width": "100%"}
                                )
                            ], lg=2, md=6, sm=12),
                            
                            dbc.Col([
                                html.Label("\u00A0", className="d-block"),
                                dbc.Button([
                                    html.I(className="bi bi-search me-2"),
                                    "Analizar Datos"
                                ],
                                id="query-button",
                                color="primary",
                                className="w-100 btn-modern",
                                style={"marginTop": "0.5rem", "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", "border": "none"}
                                )
                            ], lg=2, md=12, sm=12)
                        ], className="g-3 align-items-end")
                    ], className="p-4")
                ], className="card-modern shadow-lg")
            ], width=12)
        ], className="mb-4"),

        # Área de contenido con loading moderno
        dbc.Row([
            dbc.Col([
                dcc.Loading(
                    id="loading-indicator",
                    children=[html.Div(id="tab-content")],
                    type="dot",
                    color="#667eea",
                    className="loading-spinner"
                )
            ], width=12)
        ], className="mb-4"),

        # Sección adicional para análisis de ríos
        dbc.Row([
            dbc.Col([
                html.Hr(style={"margin": "2rem 0", "border": "2px solid #e1e8ed", "borderRadius": "2px"}),
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="bi bi-database me-2", style={"color": "#667eea"}),
                            html.Strong("Explorador de Datos", style={"fontSize": "1.1rem"})
                        ], className="mb-3 d-flex align-items-center")
                    ], className="p-3")
                ], className="card-modern")
            ], width=12)
        ])
    ], className="main-container", fluid=True),
    
    # Modal global para todas las tablas de datos
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(id="modal-title-dynamic", children="Detalle de datos hidrológicos"), close_button=True),
        dbc.ModalBody([
            html.Div(id="modal-description", className="mb-3", style={"fontSize": "0.9rem", "color": "#666"}),
            html.Div(id="modal-table-content")
        ]),
    ], id="modal-rio-table", is_open=False, size="xl", backdrop=True, centered=True, style={"zIndex": 2000})
], style={"background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", "minHeight": "100vh"})


# Mostrar ríos en el dashboard al hacer clic en el botón
# Callback para actualizar ríos según región seleccionada
@callback(
    Output("rio-dropdown", "options"),
    [Input("region-dropdown", "value")]
)
def update_rio_options(region):
    # Si se selecciona "Todas las regiones", mostrar todos los ríos disponibles
    if region == "__ALL_REGIONS__":
        rios_region = get_rio_options()  # Obtener todos los ríos sin filtro de región
    else:
        rios_region = get_rio_options(region)
    
    options = [{"label": "Todos los ríos", "value": "__ALL__"}]
    options += [{"label": r, "value": r} for r in rios_region]
    return options
def update_rio_options(region):
    # Si se selecciona "Todas las regiones", mostrar todos los ríos disponibles
    if region == "__ALL_REGIONS__":
        rios_region = get_rio_options()  # Obtener todos los ríos sin filtro de región
    else:
        rios_region = get_rio_options(region)
    
    options = [{"label": "Todos los ríos", "value": "__ALL__"}]
    options += [{"label": r, "value": r} for r in rios_region]
    return options


# Callback principal para consultar y mostrar datos filtrando por río y fechas
@callback(
    Output("tab-content", "children"),
    [Input("query-button", "n_clicks")],
    [State("rio-dropdown", "value"),
     State("start-date", "date"),
     State("end-date", "date"),
     State("region-dropdown", "value")]
)
def update_content(n_clicks, rio, start_date, end_date, region):
    # Función auxiliar para mostrar la vista por defecto (panorámica nacional)
    def show_default_view(start_date, end_date):
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
                        dbc.Col(create_total_timeline_chart(data, "Aportes totales nacionales"), md=12)
                    ]),
                    dcc.Store(id="region-data-store", data=data.to_dict('records')),
                    dcc.Store(id="embalses-completo-data", data=df_completo_embalses.to_dict('records')),
                    html.Hr(),
                    html.H5("⚡ Capacidad Útil Diaria de Energía por Región Hidrológica", className="text-center mt-4 mb-2"),
                    html.P("📋 Interfaz jerárquica expandible: Haga clic en cualquier región para desplegar sus embalses. Cada región muestra dos tablas lado a lado con participación porcentual y capacidad detallada en GWh. Los datos están ordenados de mayor a menor valor. Los símbolos ⊞ indican regiones contraídas y ⊟ regiones expandidas.", className="text-center text-muted mb-3", style={"fontSize": "0.9rem"}),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader([
                                    html.I(className="bi bi-pie-chart me-2", style={"color": "#667eea"}),
                                    html.Strong("📊 Participación Porcentual por Región")
                                ], style={"background": "linear-gradient(135deg, #e3f2fd 0%, #f3f4f6 100%)",
                                         "border": "none", "borderRadius": "8px 8px 0 0"}),
                                dbc.CardBody([
                                    html.P("Distribución porcentual de la capacidad energética entre regiones y sus embalses. Haga clic en los botones [+]/[-] para expandir/contraer cada región.", 
                                          className="text-muted mb-3", style={"fontSize": "0.85rem"}),
                                    html.Div([
                                        # Botones superpuestos para cada región
                                        html.Div(id="participacion-toggle-buttons", style={
                                            'position': 'absolute', 
                                            'zIndex': 10, 
                                            'pointerEvents': 'none'
                                        }),
                                        # Tabla principal
                                        html.Div(id="tabla-participacion-jerarquica-container", children=[
                                            html.Div("Cargando datos...", className="text-center text-muted")
                                        ])
                                    ], style={'position': 'relative'})
                                ], className="p-3")
                            ], className="card-modern h-100")
                        ], md=6),
                        
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader([
                                    html.I(className="bi bi-battery-full me-2", style={"color": "#28a745"}),
                                    html.Strong("🏭 Capacidad Detallada por Región")
                                ], style={"background": "linear-gradient(135deg, #e8f5e8 0%, #f3f4f6 100%)",
                                         "border": "none", "borderRadius": "8px 8px 0 0"}),
                                dbc.CardBody([
                                    html.P("Valores específicos de capacidad útil diaria en GWh por región y embalses. Haga clic en los botones [+]/[-] para expandir/contraer cada región.", 
                                          className="text-muted mb-3", style={"fontSize": "0.85rem"}),
                                    html.Div([
                                        # Botones superpuestos para cada región
                                        html.Div(id="capacidad-toggle-buttons", style={
                                            'position': 'absolute', 
                                            'zIndex': 10, 
                                            'pointerEvents': 'none'
                                        }),
                                        # Tabla principal
                                        html.Div(id="tabla-capacidad-jerarquica-container", children=[
                                            html.Div("Cargando datos...", className="text-center text-muted")
                                        ])
                                    ], style={'position': 'relative'})
                                ], className="p-3")
                            ], className="card-modern h-100")
                        ], md=6)
                    ], className="g-3"),
                    
                    # Stores para manejar los datos jerárquicos y estados de expansión
                    dcc.Store(id="participacion-jerarquica-data", data=[]),
                    dcc.Store(id="capacidad-jerarquica-data", data=[]),
                    dcc.Store(id="regiones-expandidas", data=[])
                ])
            else:
                return dbc.Alert("No se pueden procesar los datos obtenidos.", color="warning")
        except Exception as e:
            return dbc.Alert(f"Error al obtener datos por defecto: {str(e)}", color="danger")
    
    # Verificar si los filtros están vacíos o en valores por defecto
    filtros_vacios = (
        (region is None or region == "__ALL_REGIONS__") and 
        (rio is None or rio == "__ALL__")
    )
    
    # Si no se ha hecho clic, o faltan fechas, o todos los filtros están vacíos pero hay fechas
    if not n_clicks or not start_date or not end_date:
        # Mostrar datos por defecto de todas las regiones al cargar la página
        if start_date and end_date and not n_clicks:
            return show_default_view(start_date, end_date)
        else:
            return dbc.Alert("Selecciona una región, fechas y/o río, luego haz clic en Consultar.", color="info", className="text-center")
    
    # Si se hizo clic pero todos los filtros están vacíos, mostrar vista por defecto
    if filtros_vacios:
        return show_default_view(start_date, end_date)
    
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
        
        if region and region != "__ALL_REGIONS__":
            data_filtered = data[data['Region'] == region]
            title_suffix = f"en la región {region}"
            embalses_df = get_embalses_capacidad(region)
            # Aplicar formateo de números a la capacidad
            if not embalses_df.empty and 'Capacidad Útil Diaria (GWh)' in embalses_df.columns:
                embalses_df_formatted = embalses_df.copy()
                embalses_df_formatted['Capacidad Útil Diaria (GWh)'] = embalses_df['Capacidad Útil Diaria (GWh)'].apply(format_number)
                
                # Agregar fila TOTAL para capacidad de embalses
                if not embalses_df_formatted.empty:
                    total_capacity = embalses_df['Capacidad Útil Diaria (GWh)'].sum()
                    total_row = pd.DataFrame({
                        'Embalse': ['TOTAL'],
                        'Capacidad Útil Diaria (GWh)': [format_number(total_capacity)]
                    })
                    embalses_df_formatted = pd.concat([embalses_df_formatted, total_row], ignore_index=True)
            else:
                embalses_df_formatted = embalses_df
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
            # Si no hay región específica o es "Todas las regiones", mostrar vista nacional
            if region == "__ALL_REGIONS__":
                # Mostrar la vista panorámica nacional igual que al cargar la página
                region_df = data.groupby(['Region', 'Date'])['Value'].sum().reset_index()
                region_df = region_df[region_df['Region'].notna()]  # Filtrar regiones válidas
                
                return html.Div([
                    html.H5("🇨🇴 Contribución Energética por Región Hidrológica de Colombia", className="text-center mb-2"),
                    html.P("Vista panorámica nacional: Series temporales comparativas de aportes de caudal por región hidrológica. Haga clic en cualquier punto para ver el detalle agregado diario de la región. Los datos incluyen todos los ríos monitoreados en el período seleccionado, agrupados por región para análisis comparativo nacional.", className="text-center text-muted mb-3", style={"fontSize": "0.9rem"}),
                    dbc.Row([
                        dbc.Col(create_total_timeline_chart(data, "Aportes totales nacionales"), md=12)
                    ]),
                    dcc.Store(id="region-data-store", data=data.to_dict('records')),
                    html.Hr(),
                ])
            
            data_filtered = data
            title_suffix = "- Todas las regiones"
            embalses_df = get_embalses_capacidad()
            # Aplicar formateo de números a la capacidad
            if not embalses_df.empty and 'Capacidad Útil Diaria (GWh)' in embalses_df.columns:
                embalses_df_formatted = embalses_df.copy()
                embalses_df_formatted['Capacidad Útil Diaria (GWh)'] = embalses_df['Capacidad Útil Diaria (GWh)'].apply(format_number)
                
                # Agregar fila TOTAL para capacidad de embalses
                if not embalses_df_formatted.empty:
                    total_capacity = embalses_df['Capacidad Útil Diaria (GWh)'].sum()
                    total_row = pd.DataFrame({
                        'Embalse': ['TOTAL'],
                        'Capacidad Útil Diaria (GWh)': [format_number(total_capacity)]
                    })
                    embalses_df_formatted = pd.concat([embalses_df_formatted, total_row], ignore_index=True)
            else:
                embalses_df_formatted = embalses_df
            embalses_region = embalses_df['Embalse'].unique() if not embalses_df.empty else []

        if data_filtered.empty:
            return dbc.Alert("No se encontraron datos para la región seleccionada." if region else "No se encontraron datos.", color="warning")
        
        # Asegurar que embalses_df_formatted esté definido para todos los casos
        if 'embalses_df_formatted' not in locals():
            if not embalses_df.empty and 'Capacidad Útil Diaria (GWh)' in embalses_df.columns:
                embalses_df_formatted = embalses_df.copy()
                embalses_df_formatted['Capacidad Útil Diaria (GWh)'] = embalses_df['Capacidad Útil Diaria (GWh)'].apply(format_number)
                
                # Agregar fila TOTAL para capacidad de embalses
                if not embalses_df_formatted.empty:
                    total_capacity = embalses_df['Capacidad Útil Diaria (GWh)'].sum()
                    total_row = pd.DataFrame({
                        'Embalse': ['TOTAL'],
                        'Capacidad Útil Diaria (GWh)': [format_number(total_capacity)]
                    })
                    embalses_df_formatted = pd.concat([embalses_df_formatted, total_row], ignore_index=True)
            else:
                embalses_df_formatted = embalses_df
            
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
                            data=embalses_df_formatted.to_dict('records'),
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
                dcc.Store(id="embalse-cap-data", data=embalses_df_formatted.to_dict('records')),
                dcc.Store(id="participacion-data", data=get_participacion_embalses(embalses_df).to_dict('records'))
            ])
        else:
            return dbc.Alert("No se pueden graficar los datos de la región." if region else "No se pueden graficar los datos.", color="warning")
    except Exception as e:
        return dbc.Alert(f"Error al consultar los datos: {str(e)}", color="danger")

# Callback para inicializar las tablas jerárquicas al cargar la página
@callback(
    [Output("participacion-jerarquica-data", "data"),
     Output("capacidad-jerarquica-data", "data")],
    [Input("start-date", "date"), Input("end-date", "date")],
    prevent_initial_call=False
)
def initialize_hierarchical_tables(start_date, end_date):
    """Inicializar las tablas jerárquicas con datos de regiones al cargar la página"""
    try:
        regiones_totales, df_completo_embalses = get_tabla_regiones_embalses()
        
        if regiones_totales.empty:
            return [], [], [], []
        
        # Crear datos para tabla de participación (solo regiones inicialmente)
        participacion_data = []
        capacidad_data = []
        
        for _, row in regiones_totales.iterrows():
            # Datos de participación
            participacion_data.append({
                'nombre': f"▶️ {row['Región']}",  # Flecha indicando que se puede expandir
                'participacion': f"{row['Participación (%)']}%",
                'tipo': 'region',
                'region_name': row['Región'],
                'expandida': False,
                'id': f"region_{row['Región']}"
            })
            
            # Datos de capacidad
            capacidad_data.append({
                'nombre': f"▶️ {row['Región']}",  # Flecha indicando que se puede expandir
                'capacidad': f"{format_number(row['Total (GWh)'])} GWh",
                'tipo': 'region',
                'region_name': row['Región'],
                'expandida': False,
                'id': f"region_{row['Región']}"
            })
        
        # Agregar fila TOTAL al final
        participacion_data.append({
            'nombre': 'TOTAL SISTEMA',
            'participacion': '100.0%',
            'tipo': 'total',
            'region_name': '',
            'expandida': False,
            'id': 'total'
        })
        
        total_sistema = regiones_totales['Total (GWh)'].sum()
        capacidad_data.append({
            'nombre': 'TOTAL SISTEMA',
            'capacidad': f"{format_number(total_sistema)} GWh",
            'tipo': 'total',
            'region_name': '',
            'expandida': False,
            'id': 'total'
        })
        
        # Datos completos para los stores (incluye embalses)
        participacion_completa = participacion_data.copy()
        capacidad_completa = capacidad_data.copy()
        
        # Agregar datos de embalses a los stores completos
        for region_name in regiones_totales['Región'].unique():
            embalses_region = get_embalses_by_region(region_name, df_completo_embalses)
            
            if not embalses_region.empty:
                for _, embalse_row in embalses_region.iterrows():
                    embalse_name = embalse_row['Región'].replace('    └─ ', '')
                    
                    # Datos de participación para embalses
                    participacion_completa.append({
                        'nombre': f"    └─ {embalse_name}",
                        'participacion': f"{embalse_row['Participación (%)']}%",
                        'tipo': 'embalse',
                        'region_name': region_name,
                        'expandida': False,
                        'id': f"embalse_{region_name}_{embalse_name}"
                    })
                    
                    # Datos de capacidad para embalses  
                    capacidad_completa.append({
                        'nombre': f"    └─ {embalse_name}",
                        'capacidad': f"{format_number(embalse_row['Total (GWh)'])} GWh",
                        'tipo': 'embalse',
                        'region_name': region_name,
                        'expandida': False,
                        'id': f"embalse_{region_name}_{embalse_name}"
                    })
        
        # Retornar: datos completos para stores
        return participacion_completa, capacidad_completa
        
    except Exception as e:
        print(f"Error inicializando tablas jerárquicas: {e}")
        return [], []

def build_hierarchical_table_view(data_complete, expanded_regions, view_type="participacion"):
    """Construir vista de tabla jerárquica con botones integrados en la primera columna"""
    if not data_complete:
        return dash_table.DataTable(
            data=[],
            columns=[
                {"name": "Región / Embalse", "id": "nombre"},
                {"name": "Participación (%)" if view_type == "participacion" else "Capacidad (GWh)", "id": "valor"}
            ]
        )
    
    table_data = []
    processed_regions = set()
    
    # Obtener todas las regiones únicas
    all_regions = set()
    for item in data_complete:
        if item.get('tipo') == 'region':
            region_name = item.get('region_name')
            if region_name:
                all_regions.add(region_name)
    
    # Crear lista de regiones con sus valores para ordenar de mayor a menor
    region_items = []
    for item in data_complete:
        if item.get('tipo') == 'region':
            region_name = item.get('region_name')
            if region_name and region_name not in processed_regions:
                # Obtener el valor para ordenar
                valor_str = item.get('participacion', item.get('capacidad', '0'))
                try:
                    # Extraer valor numérico del string (ej: "25.5%" -> 25.5)
                    if isinstance(valor_str, str):
                        valor_num = float(valor_str.replace('%', '').replace(',', '').strip())
                    else:
                        valor_num = float(valor_str) if valor_str else 0
                except:
                    valor_num = 0
                
                region_items.append({
                    'item': item,
                    'region_name': region_name,
                    'valor_num': valor_num
                })
                processed_regions.add(region_name)
    
    # Ordenar regiones por valor de mayor a menor
    region_items.sort(key=lambda x: x['valor_num'], reverse=True)
    
    # Procesar cada región en orden descendente
    for region_data in region_items:
        region_item = region_data['item']
        region_name = region_data['region_name']
        
        is_expanded = region_name in expanded_regions
        
        # Fila de región con botón integrado en el nombre
        button_icon = "⊟" if is_expanded else "⊞"  # Símbolos más elegantes
        table_data.append({
            "nombre": f"{button_icon} {region_name}",
            "valor": region_item.get('participacion', region_item.get('capacidad', '')),
            "tipo": "region",
            "region_name": region_name,
            "id": f"region_{region_name}",
            "clickable": True  # Marcar como clickeable
        })
        
        # Si está expandida, agregar embalses ordenados de mayor a menor
        if is_expanded:
            embalses = []
            processed_embalses = set()
            
            for item in data_complete:
                if (item.get('tipo') == 'embalse' and 
                    item.get('region_name') == region_name):
                    embalse_id = item.get('id', '')
                    if embalse_id not in processed_embalses:
                        processed_embalses.add(embalse_id)
                        # Agregar valor numérico para ordenar
                        valor_str = item.get('participacion', item.get('capacidad', '0'))
                        try:
                            if isinstance(valor_str, str):
                                valor_num = float(valor_str.replace('%', '').replace(',', '').strip())
                            else:
                                valor_num = float(valor_str) if valor_str else 0
                        except:
                            valor_num = 0
                        item['valor_num'] = valor_num
                        embalses.append(item)
            
            # Ordenar embalses de mayor a menor
            embalses.sort(key=lambda x: x.get('valor_num', 0), reverse=True)
            
            for embalse in embalses:
                        embalse_name = embalse.get('nombre', '').replace('    └─ ', '')
                        table_data.append({
                            "nombre": f"    └─ {embalse_name}",
                            "valor": embalse.get('participacion', embalse.get('capacidad', '')),
                            "tipo": "embalse",
                            "region_name": region_name,
                            "id": embalse.get('id', f"embalse_{region_name}_{embalse_name}"),
                            "clickable": False  # Embalses no son clickeables
                        })
    
    # Agregar fila TOTAL
    total_item = None
    for item in data_complete:
        if item.get('tipo') == 'total':
            total_item = item
            break
    
    if total_item:
        table_data.append({
            "nombre": "TOTAL SISTEMA",
            "valor": total_item.get('participacion', total_item.get('capacidad', '')),
            "tipo": "total",
            "region_name": "",
            "id": "total",
            "clickable": False
        })
    
    # Crear tabla con estructura de 2 columnas
    return dash_table.DataTable(
        id=f"tabla-{view_type}-jerarquica-display",
        data=table_data,
        columns=[
            {"name": "Región / Embalse", "id": "nombre"},
            {"name": "Participación (%)" if view_type == "participacion" else "Capacidad (GWh)", "id": "valor"}
        ],
        style_cell={
            'textAlign': 'left',
            'padding': '8px',
            'fontFamily': 'Inter, Arial, sans-serif',
            'fontSize': 13,
            'backgroundColor': '#f8f9fa',
            'border': '1px solid #dee2e6'
        },
        style_header={
            'backgroundColor': '#667eea' if view_type == 'participacion' else '#28a745',
            'color': 'white',
            'fontWeight': 'bold',
            'fontSize': 14,
            'textAlign': 'center',
            'border': f'1px solid {"#5a6cf0" if view_type == "participacion" else "#218838"}'
        },
        style_data_conditional=[
            {
                'if': {'filter_query': '{tipo} = "region"'},
                'backgroundColor': '#e3f2fd' if view_type == 'participacion' else '#e8f5e8',
                'fontWeight': 'bold',
                'cursor': 'pointer',
                'border': f'2px solid {"#2196f3" if view_type == "participacion" else "#28a745"}'
            },
            {
                'if': {'filter_query': '{tipo} = "embalse"'},
                'backgroundColor': '#f8f9fa',
                'fontStyle': 'italic'
            },
            {
                'if': {'filter_query': '{tipo} = "total"'},
                'backgroundColor': '#007bff',
                'color': 'white',
                'fontWeight': 'bold'
            }
        ],
        page_action="none"
    )

# Callback para manejar clics en las regiones y expandir/colapsar embalses
@callback(
    [Output("tabla-participacion-jerarquica-container", "children"),
     Output("tabla-capacidad-jerarquica-container", "children"),
     Output("regiones-expandidas", "data")],
    [Input("tabla-participacion-jerarquica-display", "active_cell"),
     Input("tabla-capacidad-jerarquica-display", "active_cell")],
    [State("participacion-jerarquica-data", "data"),
     State("capacidad-jerarquica-data", "data"),
     State("regiones-expandidas", "data")],
    prevent_initial_call=True
)
def toggle_region_from_table(active_cell_part, active_cell_cap, participacion_complete, capacidad_complete, regiones_expandidas):
    """Manejar clics en los nombres de región con botones integrados"""
    try:
        if not participacion_complete or not capacidad_complete:
            return dash.no_update, dash.no_update, regiones_expandidas or []
        
        if regiones_expandidas is None:
            regiones_expandidas = []
        
        # Obtener el clic activo
        active_cell = active_cell_part or active_cell_cap
        if not active_cell:
            return dash.no_update, dash.no_update, regiones_expandidas
        
        # Solo responder a clics en la columna "nombre"
        if active_cell.get('column_id') != 'nombre':
            return dash.no_update, dash.no_update, regiones_expandidas
        
        # Obtener el nombre de la celda clicada directamente de la tabla
        # Construir la tabla actual para obtener los datos exactos
        current_table = build_hierarchical_table_view(participacion_complete, regiones_expandidas, "participacion")
        
        # Obtener los datos de la tabla actual
        table_data = current_table.data if hasattr(current_table, 'data') else []
        
        # Verificar qué fila se clicó
        row_id = active_cell['row']
        if row_id < len(table_data):
            clicked_row = table_data[row_id]
            clicked_name = clicked_row.get('nombre', '')
            
            # Extraer el nombre de la región del texto (remover símbolos ⊞/⊟)
            region_name = clicked_name.replace('⊞ ', '').replace('⊟ ', '').strip()
            
            # Verificar si es una fila de región (no embalse ni total)
            if clicked_row.get('tipo') == 'region' and region_name:
                # Toggle la región
                if region_name in regiones_expandidas:
                    regiones_expandidas.remove(region_name)
                else:
                    regiones_expandidas.append(region_name)
        
        # Reconstruir las vistas
        participacion_view = build_hierarchical_table_view(participacion_complete, regiones_expandidas, "participacion")
        capacidad_view = build_hierarchical_table_view(capacidad_complete, regiones_expandidas, "capacidad")
        
        return participacion_view, capacidad_view, regiones_expandidas
        
    except Exception as e:
        print(f"Error en toggle_region_from_table: {e}")
        import traceback
        traceback.print_exc()
        return dash.no_update, dash.no_update, regiones_expandidas or []

# Callback para inicializar las vistas HTML desde los stores
@callback(
    [Output("tabla-participacion-jerarquica-container", "children", allow_duplicate=True),
     Output("tabla-capacidad-jerarquica-container", "children", allow_duplicate=True)],
    [Input("participacion-jerarquica-data", "data"),
     Input("capacidad-jerarquica-data", "data")],
    [State("regiones-expandidas", "data")],
    prevent_initial_call='initial_duplicate'
)
def update_html_tables_from_stores(participacion_complete, capacidad_complete, regiones_expandidas):
    """Actualizar las vistas HTML basándose en los stores"""
    try:
        if not participacion_complete or not capacidad_complete:
            return (
                html.Div("No hay datos de participación disponibles", className="text-center text-muted p-3"),
                html.Div("No hay datos de capacidad disponibles", className="text-center text-muted p-3")
            )
        
        if not regiones_expandidas:
            regiones_expandidas = []
        
        # Construir vistas de tabla iniciales (todas las regiones colapsadas)
        participacion_view = build_hierarchical_table_view(participacion_complete, regiones_expandidas, "participacion")
        capacidad_view = build_hierarchical_table_view(capacidad_complete, regiones_expandidas, "capacidad")
        
        return participacion_view, capacidad_view
        
    except Exception as e:
        print(f"Error en update_html_tables_from_stores: {e}")
        return (
            html.Div("Error al cargar datos de participación", className="text-center text-danger p-3"),
            html.Div("Error al cargar datos de capacidad", className="text-center text-danger p-3")
        )
        
    except Exception as e:
        print(f"Error en update_tables_from_stores: {e}")
        import traceback
        traceback.print_exc()
        return [], []

# Callback adicional para cargar datos por defecto al iniciar la página
@callback(
    Output("tab-content", "children", allow_duplicate=True),
    [Input("start-date", "date"), Input("end-date", "date")],
    prevent_initial_call='initial_duplicate'
)
def load_default_data(start_date, end_date):
    """Cargar datos por defecto al inicializar la página"""
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
                
                return html.Div([
                    html.H5("🇨🇴 Contribución Energética por Región Hidrológica de Colombia", className="text-center mb-2"),
                    html.P("Vista panorámica nacional: Timeline del total nacional de aportes de caudal. Haga clic en cualquier punto para ver el desglose detallado por región para esa fecha específica. Los datos incluyen todos los ríos monitoreados en el período seleccionado, agregados por día.", className="text-center text-muted mb-3", style={"fontSize": "0.9rem"}),
                    dbc.Row([
                        dbc.Col(create_total_timeline_chart(data, "Aportes totales nacionales"), md=12)
                    ]),
                    dcc.Store(id="region-data-store", data=data.to_dict('records')),
                    html.Hr(),
                ])
            else:
                return dbc.Alert("No se pueden procesar los datos obtenidos.", color="warning", className="text-center")
        except Exception as e:
            return dbc.Alert(f"Error al cargar datos iniciales: {str(e)}", color="danger", className="text-center")
    
    return dbc.Alert("Cargando datos iniciales...", color="info", className="text-center")

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
    df_final = df_participacion[['Embalse', 'Participación (%)']].reset_index(drop=True)
    
    # Agregar fila TOTAL
    total_row = pd.DataFrame({
        'Embalse': ['TOTAL'],
        'Participación (%)': [100.0]
    })
    
    df_final = pd.concat([df_final, total_row], ignore_index=True)
    
    return df_final

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
    
    # Formatear números en la capacidad
    df_resultado['Capacidad Útil Diaria (GWh)'] = df_resultado['Capacidad Útil Diaria (GWh)'].apply(format_number)
    
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

def create_collapsible_regions_table():
    """
    Crea una tabla expandible elegante con regiones que se pueden plegar/desplegar para ver embalses.
    """
    try:
        regiones_totales, df_completo_embalses = get_tabla_regiones_embalses()
        
        if regiones_totales.empty:
            return dbc.Alert("No se encontraron datos de regiones.", color="warning", className="text-center")
        
        # Crear componentes colapsables elegantes para cada región
        region_components = []
        
        for idx, region_row in regiones_totales.iterrows():
            region_name = region_row['Región']
            total_gwh = region_row['Total (GWh)']
            participacion = region_row['Participación (%)']
            
            # Obtener embalses de la región
            embalses_region = get_embalses_by_region(region_name, df_completo_embalses)
            
            # Contar embalses para mostrar en el header
            num_embalses = len(embalses_region) if not embalses_region.empty else 0
            
            # Crear contenido de embalses con las dos tablas lado a lado
            if not embalses_region.empty:
                # Preparar datos para las tablas con formateo
                embalses_data_formatted = []
                embalses_data_raw = []  # Para cálculos
                for _, embalse_row in embalses_region.iterrows():
                    embalse_name = embalse_row['Región'].replace('    └─ ', '')
                    embalse_capacidad = embalse_row['Total (GWh)']
                    embalse_participacion = embalse_row['Participación (%)']
                    
                    embalses_data_formatted.append({
                        'Embalse': embalse_name,
                        'Capacidad Útil Diaria (GWh)': format_number(embalse_capacidad),  # Formatear números
                        'Participación (%)': embalse_participacion
                    })
                    
                    embalses_data_raw.append({
                        'Embalse': embalse_name,
                        'Capacidad Útil Diaria (GWh)': embalse_capacidad,  # Sin formatear para cálculos
                        'Participación (%)': embalse_participacion
                    })
                
                # Calcular total para la tabla de capacidad
                total_capacidad = sum([row['Capacidad Útil Diaria (GWh)'] for row in embalses_data_raw])
                
                # Crear tabla de participación porcentual
                tabla_participacion = dash_table.DataTable(
                    data=[{
                        'Embalse': row['Embalse'],
                        'Participación (%)': row['Participación (%)']
                    } for row in embalses_data_formatted] + [{'Embalse': 'TOTAL', 'Participación (%)': '100.0%'}],
                    columns=[
                        {"name": "Embalse", "id": "Embalse"},
                        {"name": "Participación (%)", "id": "Participación (%)"}
                    ],
                    style_cell={
                        'textAlign': 'left',
                        'padding': '8px',
                        'fontFamily': 'Inter, Arial, sans-serif',
                        'fontSize': 13,
                        'backgroundColor': '#f8f9fa',
                        'border': '1px solid #dee2e6'
                    },
                    style_header={
                        'backgroundColor': '#667eea',
                        'color': 'white',
                        'fontWeight': 'bold',
                        'fontSize': 14,
                        'textAlign': 'center',
                        'border': '1px solid #5a6cf0'
                    },
                    style_data_conditional=[
                        {
                            'if': {'filter_query': '{Embalse} = "TOTAL"'},
                            'backgroundColor': '#007bff',
                            'color': 'white',
                            'fontWeight': 'bold'
                        }
                    ],
                    page_action="none"
                )
                
                # Crear tabla de capacidad detallada
                tabla_capacidad = dash_table.DataTable(
                    data=embalses_data_formatted + [{
                        'Embalse': 'TOTAL',
                        'Capacidad Útil Diaria (GWh)': format_number(total_capacidad),
                        'Participación (%)': ''
                    }],
                    columns=[
                        {"name": "Embalse", "id": "Embalse"},
                        {"name": "Capacidad Útil Diaria (GWh)", "id": "Capacidad Útil Diaria (GWh)"}
                    ],
                    style_cell={
                        'textAlign': 'left',
                        'padding': '8px',
                        'fontFamily': 'Inter, Arial, sans-serif',
                        'fontSize': 13,
                        'backgroundColor': '#f8f9fa',
                        'border': '1px solid #dee2e6'
                    },
                    style_header={
                        'backgroundColor': '#28a745',
                        'color': 'white',
                        'fontWeight': 'bold',
                        'fontSize': 14,
                        'textAlign': 'center',
                        'border': '1px solid #218838'
                    },
                    style_data_conditional=[
                        {
                            'if': {'filter_query': '{Embalse} = "TOTAL"'},
                            'backgroundColor': '#007bff',
                            'color': 'white',
                            'fontWeight': 'bold'
                        }
                    ],
                    page_action="none"
                )
                
                embalses_content = html.Div([
                    html.Div([
                        html.I(className="bi bi-building me-2", style={"color": "#28a745"}),
                        html.Strong(f"Análisis Detallado - {region_name}", 
                                  className="text-success", style={"fontSize": "1.1rem"})
                    ], className="mb-4 d-flex align-items-center"),
                    
                    # Las dos tablas lado a lado
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader([
                                    html.I(className="bi bi-pie-chart me-2", style={"color": "#667eea"}),
                                    html.Strong("📊 Participación Porcentual por Embalse")
                                ], style={"background": "linear-gradient(135deg, #e3f2fd 0%, #f3f4f6 100%)",
                                         "border": "none", "borderRadius": "8px 8px 0 0"}),
                                dbc.CardBody([
                                    html.P("Distribución porcentual de la capacidad energética entre embalses. La tabla incluye una fila TOTAL que suma exactamente 100%.", 
                                          className="text-muted mb-3", style={"fontSize": "0.85rem"}),
                                    tabla_participacion
                                ], className="p-3")
                            ], className="card-modern h-100")
                        ], md=6),
                        
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader([
                                    html.I(className="bi bi-battery-full me-2", style={"color": "#28a745"}),
                                    html.Strong("🏭 Capacidad Detallada por Embalse")
                                ], style={"background": "linear-gradient(135deg, #e8f5e8 0%, #f3f4f6 100%)",
                                         "border": "none", "borderRadius": "8px 8px 0 0"}),
                                dbc.CardBody([
                                    html.P(f"Valores específicos de capacidad útil diaria en GWh para los {num_embalses} embalses de la región.", 
                                          className="text-muted mb-3", style={"fontSize": "0.85rem"}),
                                    tabla_capacidad
                                ], className="p-3")
                            ], className="card-modern h-100")
                        ], md=6)
                    ], className="g-3")
                ])
            else:
                embalses_content = dbc.Alert([
                    html.I(className="bi bi-exclamation-triangle me-2"),
                    f"No se encontraron embalses para la región {region_name}."
                ], color="light", className="text-center my-3 alert-modern")
            
            # Crear card principal elegante para la región
            region_card = dbc.Card([
                # Header clickeable de la región
                dbc.CardHeader([
                    dbc.Button([
                        html.Div([
                            html.Div([
                                html.I(className="bi bi-chevron-right me-3", 
                                       id={"type": "chevron-region", "index": idx},
                                       style={"fontSize": "1.1rem", "color": "#007bff", "transition": "transform 0.3s ease"}),
                                html.I(className="bi bi-geo-alt-fill me-2", style={"color": "#28a745"}),
                                html.Strong(region_name, style={"fontSize": "1.1rem", "color": "#2d3748"})
                            ], className="d-flex align-items-center"),
                            html.Div([
                                dbc.Badge(f"{format_number(total_gwh)} GWh", color="primary", className="me-2 px-2 py-1"),
                                dbc.Badge(f"{participacion}%", color="success", className="px-2 py-1"),
                                html.Small(f" • {num_embalses} embalse{'s' if num_embalses != 1 else ''}", 
                                         className="text-muted ms-2")
                            ], className="d-flex align-items-center mt-1")
                        ], className="d-flex justify-content-between align-items-start w-100")
                    ], 
                    id={"type": "toggle-region", "index": idx},
                    className="w-100 text-start border-0 bg-transparent p-0",
                    style={"background": "transparent !important"}
                    )
                ], className="border-0 bg-gradient", 
                style={
                    "background": f"linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)",
                    "borderRadius": "12px 12px 0 0",
                    "padding": "1rem"
                }),
                
                # Contenido colapsable
                dbc.Collapse([
                    dbc.CardBody([
                        html.Hr(className="mt-0 mb-3", style={"borderColor": "#dee2e6"}),
                        embalses_content
                    ], className="pt-0", style={"backgroundColor": "#fdfdfe"})
                ],
                id={"type": "collapse-region", "index": idx},
                is_open=False
                )
            ], className="mb-3 shadow-sm",
            style={
                "border": "1px solid #e3e6f0",
                "borderRadius": "12px",
                "transition": "all 0.3s ease",
                "overflow": "hidden"
            })
            
            region_components.append(region_card)
        
        return html.Div([
            # Header explicativo elegante
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="bi bi-info-circle-fill me-2", style={"color": "#0d6efd"}),
                        html.Strong("⚡ Capacidad Útil Diaria de Energía por Región Hidrológica", style={"fontSize": "1.2rem"})
                    ], className="d-flex align-items-center mb-2"),
                    html.P([
                        "Haz clic en cualquier región para expandir y ver sus tablas detalladas. ",
                        html.Strong("Cada región muestra dos tablas lado a lado:", className="text-primary"),
                        " participación porcentual de embalses y capacidad energética detallada en GWh."
                    ], className="mb-0 text-dark", style={"fontSize": "0.95rem"})
                ], className="py-3")
            ], className="mb-4", 
            style={
                "background": "linear-gradient(135deg, #e3f2fd 0%, #f3f4f6 100%)",
                "border": "1px solid #bbdefb",
                "borderRadius": "12px"
            }),
            
            # Container de regiones
            html.Div(region_components, id="regions-container")
        ])
        
    except Exception as e:
        print(f"Error creando tabla colapsable: {e}")
        return dbc.Alert(f"Error al crear tabla: {str(e)}", color="danger")


# Callback elegante para manejar el pliegue/despliegue de regiones
@callback(
    [Output({"type": "collapse-region", "index": dash.dependencies.MATCH}, "is_open"),
     Output({"type": "chevron-region", "index": dash.dependencies.MATCH}, "className")],
    [Input({"type": "toggle-region", "index": dash.dependencies.MATCH}, "n_clicks")],
    [State({"type": "collapse-region", "index": dash.dependencies.MATCH}, "is_open")]
)
def toggle_region_collapse(n_clicks, is_open):
    """
    Callback elegante para manejar el toggle de una región específica usando pattern-matching
    """
    if not n_clicks:
        return False, "bi bi-chevron-right me-3"
    
    new_state = not is_open
    if new_state:
        # Expandido - rotar chevron hacia abajo
        return True, "bi bi-chevron-down me-3"
    else:
        # Contraído - chevron hacia la derecha
        return False, "bi bi-chevron-right me-3"


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
    
    # Formatear para mostrar como sub-elementos - usar la columna correcta 'Embalse'
    if 'Embalse' in embalses_region.columns:
        resultado = embalses_region[['Embalse', 'Capacidad Útil Diaria (GWh)', 'Participación (%)']].copy()
        resultado = resultado.rename(columns={'Embalse': 'Región', 'Capacidad Útil Diaria (GWh)': 'Total (GWh)'})
        resultado['Región'] = '    └─ ' + resultado['Región'].astype(str)  # Identar embalses
        resultado['Tipo'] = 'embalse'
        return resultado
    else:
        print(f"Warning: Columnas disponibles en df_completo: {embalses_region.columns.tolist()}")
        return pd.DataFrame()
def get_embalses_capacidad(region=None):
    """
    Obtiene la capacidad útil diaria de energía por embalse desde la API XM (CapaUtilDiarEner).
    Si se pasa una región, filtra los embalses de esa región.
    Solo incluye embalses que tienen datos de capacidad activos.
    """
    try:
        df = objetoAPI.request_data('CapaUtilDiarEner','Embalse','2024-01-01','2024-01-02')
        if 'Name' in df.columns and 'Value' in df.columns:
            # Obtener información de región para embalses
            embalses_info = objetoAPI.request_data('ListadoEmbalses','Sistema','2024-01-01','2024-01-02')
            embalses_info['Values_Name'] = embalses_info['Values_Name'].str.strip().str.upper()
            embalses_info['Values_HydroRegion'] = embalses_info['Values_HydroRegion'].str.strip().str.title()
            embalse_region_dict = dict(zip(embalses_info['Values_Name'], embalses_info['Values_HydroRegion']))
            
            # Solo incluir embalses que tienen datos de capacidad
            embalses_con_datos = set(df['Name'].unique())
            embalse_region_dict_filtrado = {
                embalse: region for embalse, region in embalse_region_dict.items() 
                if embalse in embalses_con_datos
            }
            
            df['Region'] = df['Name'].map(embalse_region_dict_filtrado)
            if region:
                df = df[df['Region'] == region]
            df_grouped = df.groupby('Name')['Value'].sum().reset_index()
            df_grouped = df_grouped.rename(columns={'Name': 'Embalse', 'Value': 'Capacidad Útil Diaria (GWh)'})
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
    
    # Formatear fechas si existe columna de fecha
    date_columns = [col for col in df_with_participation.columns if 'fecha' in col.lower() or 'date' in col.lower()]
    for col in date_columns:
        df_with_participation[col] = df_with_participation[col].apply(format_date)
    
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
                            total_row[col] = format_number(total)
                        elif col == 'Participación (%)':
                            total_row[col] = '100.0%'
                        else:
                            total_row[col] = ''
                    
                    # Agregar la fila total al dataframe
                    df_with_participation = pd.concat([df_with_participation, pd.DataFrame([total_row])], ignore_index=True)
            else:
                df_with_participation['Participación (%)'] = 0
        else:
            df_with_participation['Participación (%)'] = 0
    
    # Formatear columnas numéricas (GWh, capacidades, etc.)
    numeric_columns = [col for col in df_with_participation.columns 
                      if any(keyword in col.lower() for keyword in ['gwh', 'capacidad', 'caudal', 'valor', 'value'])]
    
    for col in numeric_columns:
        if col != 'Participación (%)':  # No formatear porcentajes
            df_with_participation[col] = df_with_participation[col].apply(
                lambda x: format_number(x) if pd.notnull(x) and x != 'TOTAL' else x
            )
    
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
    """Gráfico de líneas moderno de caudal"""
    if data is None or data.empty:
        return dbc.Alert("No se pueden crear gráficos con estos datos.", color="warning", className="alert-modern")
    
    # Esperar columnas 'Fecha' y 'GWh' tras el renombrado
    if 'Fecha' in data.columns and 'GWh' in data.columns:
        fig = px.line(data, x='Fecha', y='GWh', 
                     labels={'GWh': "Energía (GWh)", 'Fecha': "Fecha"}, 
                     markers=True)
        
        # Aplicar tema moderno
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, Arial, sans-serif", size=12),
            title_font_size=16,
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)',
                showline=True,
                linewidth=2,
                linecolor='rgba(128,128,128,0.3)'
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)',
                showline=True,
                linewidth=2,
                linecolor='rgba(128,128,128,0.3)'
            )
        )
        
        # Estilo moderno de la línea
        fig.update_traces(
            line=dict(width=3, color='#667eea'),
            marker=dict(size=8, color='#764ba2', 
                       line=dict(width=2, color='white')),
            hovertemplate='<b>Fecha:</b> %{x}<br><b>Energía:</b> %{y:.2f} GWh<extra></extra>'
        )
        
        return dbc.Card([
            dbc.CardHeader([
                html.I(className="bi bi-graph-up-arrow me-2", style={"color": "#667eea"}),
                html.Strong("Evolución Temporal", style={"fontSize": "1.1rem"})
            ]),
            dbc.CardBody([
                dcc.Graph(figure=fig)
            ], className="p-2")
        ], className="card-modern chart-container")
    else:
        return dbc.Alert("No se pueden crear gráficos con estos datos.", color="warning", className="alert-modern")

def create_bar_chart(data, metric_name):
    """Crear gráfico de líneas moderno por región o río"""
    # Detectar columnas categóricas y numéricas
    cat_cols = [col for col in data.columns if data[col].dtype == 'object']
    num_cols = [col for col in data.columns if data[col].dtype in ['float64', 'int64']]
    
    if not cat_cols or not num_cols:
        return dbc.Alert("No se pueden crear gráficos de líneas con estos datos.", 
                        color="warning", className="alert-modern")
    
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
                title="Aportes Energéticos por Región Hidrológica",
                labels={'Value': "Energía (GWh)", 'Date': "Fecha", 'Region': "Región"},
                markers=True,
                color_discrete_sequence=px.colors.qualitative.Set2
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
                title="Contribución Total por Región Hidrológica",
                labels={num_col: "Energía (GWh)", 'Region': "Región"},
                markers=True,
                color_discrete_sequence=['#667eea']
            )
    else:
        # Agrupar y ordenar datos de mayor a menor - usar líneas en lugar de barras
        grouped_data = data.groupby(cat_col)[num_col].sum().reset_index()
        grouped_data = grouped_data.sort_values(by=num_col, ascending=False)
        
        fig = px.line(
            grouped_data.head(15),  # Top 15 para mejor visualización
            x=cat_col,
            y=num_col,
            title="Aportes Energéticos por Río",
            labels={num_col: "Energía (GWh)", cat_col: "Río"},
            markers=True,
            color_discrete_sequence=['#667eea']
        )
    
    # Aplicar estilo moderno
    fig.update_layout(
        height=550,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, Arial, sans-serif", size=12),
        title=dict(
            font_size=16,
            x=0.5,
            xanchor='center',
            font_color='#2d3748'
        ),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            showline=True,
            linewidth=2,
            linecolor='rgba(128,128,128,0.3)',
            tickangle=-45
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            showline=True,
            linewidth=2,
            linecolor='rgba(128,128,128,0.3)'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Mejorar el estilo para todos los gráficos de líneas
    fig.update_traces(
        marker=dict(size=10, line=dict(width=2, color='white')),
        line=dict(width=4),
        hovertemplate='<b>%{fullData.name}</b><br>Valor: %{y:.2f} GWh<extra></extra>'
    )
    
    chart_title = "Aportes de Energía por Región" if 'Region' in data.columns else "Aportes de Energía por Río"
    
    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.I(className="bi bi-graph-up me-2", style={"color": "#667eea"}),
                html.Strong(chart_title, style={"fontSize": "1.2rem"})
            ], className="d-flex align-items-center"),
            html.Small("Haz clic en cualquier punto para ver detalles", className="text-muted")
        ]),
        dbc.CardBody([
            dcc.Graph(id="rio-detail-graph", figure=fig, clear_on_unhover=True)
        ], className="p-2")
    ], className="card-modern chart-container shadow-lg")

def create_total_timeline_chart(data, metric_name):
    """Crear gráfico de línea temporal con total nacional por día"""
    if data is None or data.empty:
        return dbc.Alert("No se pueden crear gráficos con estos datos.", 
                        color="warning", className="alert-modern")
    
    # Verificar que tengamos las columnas necesarias
    if 'Date' not in data.columns or 'Value' not in data.columns:
        return dbc.Alert("No se encuentran las columnas necesarias (Date, Value).", 
                        color="warning", className="alert-modern")
    
    # Agrupar por fecha y sumar todos los valores de todas las regiones
    daily_totals = data.groupby('Date')['Value'].sum().reset_index()
    daily_totals = daily_totals.sort_values('Date')
    
    # Crear gráfico de línea con una sola línea negra
    fig = px.line(
        daily_totals,
        x='Date',
        y='Value',
        title="Total Nacional de Aportes de Caudal por Día",
        labels={'Value': "Total Energía (GWh)", 'Date': "Fecha"},
        markers=True
    )
    
    # Estilo moderno con línea negra
    fig.update_layout(
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, Arial, sans-serif", size=12),
        title=dict(
            font_size=16,
            x=0.5,
            xanchor='center',
            font_color='#2d3748'
        ),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            showline=True,
            linewidth=2,
            linecolor='rgba(128,128,128,0.3)',
            title="Fecha"
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            showline=True,
            linewidth=2,
            linecolor='rgba(128,128,128,0.3)',
            title="Total Energía (GWh)"
        ),
        showlegend=False
    )
    
    # Aplicar línea negra con marcadores
    fig.update_traces(
        line=dict(width=3, color='black'),
        marker=dict(size=8, color='black', 
                   line=dict(width=2, color='white')),
        hovertemplate='<b>Fecha:</b> %{x}<br><b>Total Nacional:</b> %{y:.2f} GWh<extra></extra>'
    )
    
    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.I(className="bi bi-graph-up me-2", style={"color": "#000"}),
                html.Strong("Total Nacional por Día", style={"fontSize": "1.2rem"})
            ], className="d-flex align-items-center"),
            html.Small("Haz clic en cualquier punto para ver detalles por región", className="text-muted")
        ]),
        dbc.CardBody([
            dcc.Graph(id="total-timeline-graph", figure=fig, clear_on_unhover=True)
        ], className="p-2")
    ], className="card-modern chart-container shadow-lg")
# Callback para mostrar el modal con la tabla diaria al hacer click en un punto de la línea
@callback(
    [Output("modal-rio-table", "is_open"), Output("modal-table-content", "children"), 
     Output("modal-title-dynamic", "children"), Output("modal-description", "children")],
    [Input("total-timeline-graph", "clickData"), Input("modal-rio-table", "is_open")],
    [State("region-data-store", "data")],
    prevent_initial_call=True
)
def show_modal_table(timeline_clickData, is_open, region_data):
    ctx = dash.callback_context
    
    print(f"🚀 CALLBACK EJECUTADO! Triggered: {[prop['prop_id'] for prop in ctx.triggered]}")
    print(f" Timeline click data: {timeline_clickData}")
    
    # Determinar qué fue clicado
    clickData = None
    graph_type = None
    
    if ctx.triggered:
        trigger_id = ctx.triggered[0]["prop_id"]
        print(f"🔍 DEBUG: Callback triggered - trigger_id: {trigger_id}")
        
        if trigger_id.startswith("total-timeline-graph") and timeline_clickData:
            clickData = timeline_clickData
            graph_type = "timeline"
            print(f"🎯 DEBUG: Timeline click detected! clickData: {clickData}")
        elif trigger_id.startswith("modal-rio-table"):
            print(f"❌ DEBUG: Modal close triggered")
            return False, None, "", ""
    
    # Si se hace click en un punto del timeline, mostrar el modal con la tabla
    if clickData and graph_type == "timeline":
        point_data = clickData["points"][0]
        print(f"🔍 DEBUG: point_data extraído: {point_data}")
        
        df = pd.DataFrame(region_data) if region_data else pd.DataFrame()
        print(f"📊 DEBUG: region_data recibido: {type(region_data)}, length: {len(region_data) if region_data else 'None'}")
        print(f"📈 DEBUG: DataFrame creado - shape: {df.shape}, columns: {df.columns.tolist() if not df.empty else 'DataFrame vacío'}")
        
        if df.empty:
            print(f"❌ DEBUG: DataFrame está vacío - retornando mensaje de error")
            return False, None, "Sin datos", "No hay información disponible para mostrar."
        
        # Obtener la fecha clicada
        selected_date = point_data['x']
        total_value = point_data['y']
        print(f"📅 DEBUG: Fecha seleccionada: {selected_date}, Total: {total_value}")
        print(f"📅 DEBUG: Tipo de fecha seleccionada: {type(selected_date)}")
        
        # Ver qué fechas están disponibles en el DataFrame
        unique_dates = df['Date'].unique()[:10]  # Primeras 10 fechas únicas
        print(f"📆 DEBUG: Primeras fechas disponibles en DataFrame: {unique_dates}")
        print(f"📆 DEBUG: Tipo de fechas en DataFrame: {type(df['Date'].iloc[0]) if not df.empty else 'N/A'}")
        
        # Filtrar datos de esa fecha específica
        df_date = df[df['Date'] == selected_date].copy()
        print(f"🗓️ DEBUG: Datos filtrados por fecha - shape: {df_date.shape}")
        
        # Si no hay datos, intentar convertir la fecha a diferentes formatos
        if df_date.empty:
            print(f"🔄 DEBUG: Intentando conversiones de fecha...")
            # Intentar convertir la fecha seleccionada a datetime
            try:
                from datetime import datetime
                if isinstance(selected_date, str):
                    selected_date_dt = pd.to_datetime(selected_date)
                    print(f"🔄 DEBUG: Fecha convertida a datetime: {selected_date_dt}")
                    # Intentar filtrar con la fecha convertida
                    df_date = df[df['Date'] == selected_date_dt].copy()
                    print(f"🔄 DEBUG: Datos filtrados con fecha convertida - shape: {df_date.shape}")
                
                # Si aún no hay datos, intentar convertir las fechas del DataFrame
                if df_date.empty:
                    print(f"🔄 DEBUG: Convirtiendo fechas del DataFrame...")
                    df['Date'] = pd.to_datetime(df['Date'])
                    df_date = df[df['Date'] == selected_date_dt].copy()
                    print(f"🔄 DEBUG: Datos filtrados después de conversión DF - shape: {df_date.shape}")
                    
            except Exception as e:
                print(f"❌ DEBUG: Error en conversión de fechas: {e}")
        
        print(f"🔍 DEBUG: Primeras filas de df_date: {df_date.head(3).to_dict() if not df_date.empty else 'No hay datos'}")
        
        if df_date.empty:
            print(f"❌ DEBUG: No hay datos para la fecha {selected_date}")
            return False, None, f"Sin datos para {selected_date}", f"No se encontraron datos para la fecha {selected_date}."
        
        # Agrupar por región para esa fecha
        region_summary = df_date.groupby('Region')['Value'].sum().reset_index()
        region_summary = region_summary.sort_values('Value', ascending=False)
        region_summary = region_summary.rename(columns={'Region': 'Región', 'Value': 'Caudal (GWh)'})
        print(f"📊 DEBUG: region_summary creado - shape: {region_summary.shape}")
        print(f"📈 DEBUG: region_summary contenido: {region_summary.to_dict() if not region_summary.empty else 'Vacío'}")
        
        # Calcular participación porcentual
        total = region_summary['Caudal (GWh)'].sum()
        print(f"💰 DEBUG: Total calculado: {total}")
        
        if total > 0:
            region_summary['Participación (%)'] = (region_summary['Caudal (GWh)'] / total * 100).round(2)
            # Ajustar para que sume exactamente 100%
            diferencia = 100 - region_summary['Participación (%)'].sum()
            if abs(diferencia) > 0.001:
                idx_max = region_summary['Participación (%)'].idxmax()
                region_summary.loc[idx_max, 'Participación (%)'] += diferencia
                region_summary['Participación (%)'] = region_summary['Participación (%)'].round(2)
        else:
            region_summary['Participación (%)'] = 0
        
        # Formatear números
        region_summary['Caudal (GWh)'] = region_summary['Caudal (GWh)'].apply(format_number)
        
        # Agregar fila total
        total_row = {
            'Región': 'TOTAL',
            'Caudal (GWh)': format_number(total),
            'Participación (%)': '100.0%'
        }
        
        data_with_total = region_summary.to_dict('records') + [total_row]
        
        # Crear tabla
        table = dash_table.DataTable(
            data=data_with_total,
            columns=[
                {"name": "Región", "id": "Región"},
                {"name": "Caudal (GWh)", "id": "Caudal (GWh)"},
                {"name": "Participación (%)", "id": "Participación (%)"}
            ],
            style_cell={'textAlign': 'left', 'padding': '8px', 'fontFamily': 'Inter, Arial', 'fontSize': 14},
            style_header={'backgroundColor': '#000000', 'color': 'white', 'fontWeight': 'bold'},
            style_data={'backgroundColor': '#f8f9fa'},
            style_data_conditional=[
                {
                    'if': {'filter_query': '{Región} = "TOTAL"'},
                    'backgroundColor': '#000000',
                    'color': 'white',
                    'fontWeight': 'bold'
                }
            ],
            page_action="none",
            export_format="xlsx",
            export_headers="display"
        )
        
        # Crear título y descripción
        formatted_date = format_date(selected_date)
        total_regions = len(region_summary) - 1 if len(region_summary) > 0 else 0
        title = f"📅 Detalles del {formatted_date} - Total Nacional: {format_number(total_value)} GWh"
        description = f"Detalle por región hidrológica para el día {formatted_date}. Se muestran los aportes de caudal de {total_regions} regiones que registraron actividad en esta fecha, con su respectiva participación porcentual sobre el total nacional de {format_number(total_value)} GWh."
        
        print(f"✅ DEBUG: Título: {title}")
        print(f"✅ DEBUG: Descripción: {description}")
        print(f"✅ DEBUG: Retornando modal abierto con tabla de {len(data_with_total)} filas")
        
        return True, table, title, description
    
    # Si se cierra el modal
    elif ctx.triggered and ctx.triggered[0]["prop_id"].startswith("modal-rio-table"):
        return False, None, "", ""
    
    # Por defecto, modal cerrado
    print(f"⚠️ DEBUG: No se detectó ningún click válido - modal cerrado por defecto")
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
                    'backgroundColor': '#3498db',
                    'color': 'white',
                    'fontWeight': 'bold'
                },
                style_data={'backgroundColor': '#f8f9fa'},
            )
        ])
    ])

# Función principal para ejecutar la aplicación
if __name__ == '__main__':
    # Configuración para desarrollo
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 8050))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"🚀 Iniciando Dashboard Hidrológico MME Colombia")
    print(f"🌐 Servidor: http://{host}:{port}")
    print(f"🔧 Debug: {debug_mode}")
    print(f"📡 Endpoints disponibles:")
    print(f"   - Dashboard: http://{host}:{port}")
    print(f"   - Health Check: http://{host}:{port}/health")
    print(f"   - API Status: http://{host}:{port}/api/status") 
    print(f"   - App Info: http://{host}:{port}/api/info")
    
    # Ejecutar el servidor Dash-Flask
    app.run_server(
        debug=debug_mode, 
        host=host, 
        port=port,
        dev_tools_hot_reload=debug_mode,
        dev_tools_ui=debug_mode
    )
