"""
Dashboard Energético XM - Configuración y Utilidades

Este módulo contiene las configuraciones y funciones auxiliares 
para el dashboard de visualización de datos energéticos.
"""

import os
from datetime import datetime, timedelta

# Configuración de la aplicación
class Config:
    # API XM Configuration
    API_BASE_URL = "https://servapibi.xm.com.co/"
    DEFAULT_MAX_RECORDS = 1000
    
    # Dashboard Configuration
    APP_TITLE = "Dashboard Energético XM - Colombia"
    APP_DESCRIPTION = "Sistema de Información del Mercado Eléctrico Mayorista"
    
    # Fechas por defecto
    DEFAULT_START_DATE = datetime.now() - timedelta(days=30)
    DEFAULT_END_DATE = datetime.now()
    
    # Colores del tema
    COLORS = {
        'primary': '#1f77b4',
        'secondary': '#ff7f0e',
        'success': '#2ca02c',
        'warning': '#d62728',
        'info': '#17a2b8',
        'light': '#f8f9fa',
        'dark': '#343a40'
    }
    
    # Configuración de gráficos
    CHART_CONFIG = {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'dashboard_energetico_xm',
            'height': 500,
            'width': 1200,
            'scale': 1
        }
    }

# Mapeo de métricas a descripciones más amigables
METRIC_DESCRIPTIONS = {
    'Gene': 'Generación Real del Sistema',
    'DemaCome': 'Demanda Comercial',
    'PrecBolsNaci': 'Precio de Bolsa Nacional',
    'AporEner': 'Aportes de Energía',
    'VoluUtilDiarEner': 'Volumen Útil Diario de Embalses',
    'ImpoEner': 'Importaciones de Energía',
    'ExpoEner': 'Exportaciones de Energía',
    'DemaMaxPot': 'Demanda Máxima de Potencia',
    'PrecEsca': 'Precio de Escasez'
}

# Unidades por tipo de métrica
METRIC_UNITS = {
    'Gene': 'MWh',
    'DemaCome': 'MWh', 
    'PrecBolsNaci': '$/MWh',
    'AporEner': 'GWh',
    'VoluUtilDiarEner': 'GWh',
    'ImpoEner': 'MWh',
    'ExpoEner': 'MWh',
    'DemaMaxPot': 'MW',
    'PrecEsca': '$/MWh'
}

def format_metric_name(metric_id, metric_name):
    """
    Formatear el nombre de la métrica para mostrar en la interfaz
    """
    friendly_name = METRIC_DESCRIPTIONS.get(metric_id, metric_name)
    return f"{metric_id} - {friendly_name}"

def get_metric_unit(metric_id):
    """
    Obtener la unidad de una métrica específica
    """
    return METRIC_UNITS.get(metric_id, 'Unidad')

def validate_date_range(start_date, end_date):
    """
    Validar que el rango de fechas sea correcto
    """
    if start_date > end_date:
        return False, "La fecha de inicio debe ser anterior a la fecha de fin"
    
    date_diff = (end_date - start_date).days
    if date_diff > 365:
        return False, "El rango de fechas no puede ser mayor a 365 días"
    
    return True, "Rango de fechas válido"

def format_number(value, metric_id=None):
    """
    Formatear números para mostrar en la interfaz
    """
    if pd.isna(value):
        return "N/A"
    
    if metric_id in ['PrecBolsNaci', 'PrecEsca']:
        return f"${value:,.2f}"
    elif abs(value) >= 1000000:
        return f"{value/1000000:.1f}M"
    elif abs(value) >= 1000:
        return f"{value/1000:.1f}K"
    else:
        return f"{value:.2f}"
