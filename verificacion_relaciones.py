#!/usr/bin/env python3
"""
Script de verificación de relaciones río-región y embalse-región
para el Dashboard Hidrológico del MME
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'API_XM'))
import importlib.util
pydataxm_path = os.path.join(os.path.dirname(__file__), 'API_XM', 'pydataxm', 'pydataxm.py')
spec = importlib.util.spec_from_file_location('pydataxm', pydataxm_path)
pydataxm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pydataxm)
ReadDB = pydataxm.ReadDB

from datetime import date, timedelta

def main():
    print("=" * 60)
    print("REPORTE DE VERIFICACIÓN DE RELACIONES HIDROLÓGICAS")
    print("Dashboard MME - API XM")
    print("=" * 60)
    print()

    api = ReadDB()
    
    # === VERIFICACIÓN 1: RÍOS ===
    print("1. VERIFICACIÓN DE RÍOS")
    print("-" * 30)
    
    # Obtener listado oficial
    rios_oficiales = api.request_data('ListadoRios', 'Sistema', '2024-01-01', '2024-01-02')
    print(f"   Ríos en listado oficial: {len(rios_oficiales)}")
    
    # Obtener ríos con datos de caudal
    try:
        end_date = date.today().strftime('%Y-%m-%d')
        start_date = (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
        caudales = api.request_data('AporCaudal', 'Rio', start_date, end_date)
        rios_con_datos = set(caudales['Name'].unique())
        print(f"   Ríos con datos de caudal (últimos 30 días): {len(rios_con_datos)}")
    except Exception as e:
        print(f"   ERROR obteniendo caudales: {e}")
        rios_con_datos = set()
    
    # Crear mapeo como en la app
    rios_oficiales['Values_Name'] = rios_oficiales['Values_Name'].str.strip().str.upper()
    rios_oficiales['Values_HydroRegion'] = rios_oficiales['Values_HydroRegion'].str.strip().str.title()
    RIO_REGION = dict(zip(rios_oficiales['Values_Name'], rios_oficiales['Values_HydroRegion']))
    
    # Verificar mapeo
    rios_oficiales_norm = set(rios_oficiales['Values_Name'])
    rios_solo_oficiales = rios_oficiales_norm - rios_con_datos
    rios_solo_caudales = rios_con_datos - rios_oficiales_norm
    
    print(f"   Ríos SOLO en lista oficial: {len(rios_solo_oficiales)}")
    if rios_solo_oficiales:
        print(f"     {sorted(list(rios_solo_oficiales))}")
    
    print(f"   Ríos SOLO en caudales: {len(rios_solo_caudales)}")
    if rios_solo_caudales:
        print(f"     {sorted(list(rios_solo_caudales))}")
    
    # Verificar cobertura de mapeo
    if rios_con_datos:
        caudales['Region'] = caudales['Name'].map(RIO_REGION)
        mapeo_exitoso = len(caudales[caudales['Region'].notna()])
        mapeo_total = len(caudales)
        print(f"   Mapeo río-región exitoso: {mapeo_exitoso}/{mapeo_total} ({mapeo_exitoso/mapeo_total*100:.1f}%)")
        
        if mapeo_exitoso < mapeo_total:
            sin_mapear = caudales[caudales['Region'].isna()]['Name'].unique()
            print(f"   Ríos sin mapear: {sorted(sin_mapear)}")
    
    print()
    
    # === VERIFICACIÓN 2: EMBALSES ===
    print("2. VERIFICACIÓN DE EMBALSES")
    print("-" * 30)
    
    # Obtener listado oficial
    embalses_oficiales = api.request_data('ListadoEmbalses', 'Sistema', '2024-01-01', '2024-01-02')
    print(f"   Embalses en listado oficial: {len(embalses_oficiales)}")
    
    # Obtener embalses con datos de capacidad
    try:
        capacidad = api.request_data('CapaUtilDiarEner', 'Embalse', '2024-08-01', '2024-08-01')
        embalses_con_datos = set(capacidad['Name'].unique())
        print(f"   Embalses con datos de capacidad: {len(embalses_con_datos)}")
    except Exception as e:
        print(f"   ERROR obteniendo capacidades: {e}")
        embalses_con_datos = set()
    
    # Crear mapeo como en la app
    embalses_oficiales['Values_Name'] = embalses_oficiales['Values_Name'].str.strip().str.upper()
    embalses_oficiales['Values_HydroRegion'] = embalses_oficiales['Values_HydroRegion'].str.strip().str.title()
    EMBALSE_REGION = dict(zip(embalses_oficiales['Values_Name'], embalses_oficiales['Values_HydroRegion']))
    
    # Verificar diferencias
    embalses_oficiales_norm = set(embalses_oficiales['Values_Name'])
    embalses_solo_oficiales = embalses_oficiales_norm - embalses_con_datos
    embalses_solo_capacidad = embalses_con_datos - embalses_oficiales_norm
    
    print(f"   Embalses SOLO en lista oficial: {len(embalses_solo_oficiales)}")
    if embalses_solo_oficiales:
        print(f"     {sorted(list(embalses_solo_oficiales))}")
    
    print(f"   Embalses SOLO en capacidad: {len(embalses_solo_capacidad)}")
    if embalses_solo_capacidad:
        print(f"     {sorted(list(embalses_solo_capacidad))}")
    
    # Verificar cobertura de mapeo
    if embalses_con_datos:
        capacidad['Region'] = capacidad['Name'].map(EMBALSE_REGION)
        mapeo_exitoso = len(capacidad[capacidad['Region'].notna()])
        mapeo_total = len(capacidad)
        print(f"   Mapeo embalse-región exitoso: {mapeo_exitoso}/{mapeo_total} ({mapeo_exitoso/mapeo_total*100:.1f}%)")
    
    print()
    
    # === VERIFICACIÓN 3: REGIONES ===
    print("3. VERIFICACIÓN DE REGIONES")
    print("-" * 30)
    
    regiones_rios = set(rios_oficiales['Values_HydroRegion'])
    regiones_embalses = set(embalses_oficiales['Values_HydroRegion'])
    todas_regiones = regiones_rios.union(regiones_embalses)
    
    print(f"   Total de regiones encontradas: {len(todas_regiones)}")
    print(f"   Regiones: {sorted(todas_regiones)}")
    
    # Verificar cada región
    print("\n   Distribución por región:")
    for region in sorted(todas_regiones):
        rios_region = rios_oficiales[rios_oficiales['Values_HydroRegion'] == region]
        embalses_region = embalses_oficiales[embalses_oficiales['Values_HydroRegion'] == region]
        
        # Contar ríos con datos de caudal en esta región
        if rios_con_datos:
            rios_con_datos_region = [r for r in rios_con_datos if RIO_REGION.get(r) == region]
            count_rios_datos = len(rios_con_datos_region)
        else:
            count_rios_datos = 0
            
        print(f"     {region}:")
        print(f"       - Ríos oficiales: {len(rios_region)}")
        print(f"       - Ríos con datos: {count_rios_datos}")
        print(f"       - Embalses: {len(embalses_region)}")
    
    print()
    
    # === VERIFICACIÓN 4: PROBLEMAS DETECTADOS ===
    print("4. PROBLEMAS DETECTADOS")
    print("-" * 30)
    
    problemas = []
    
    # Problema 1: Ríos sin datos de caudal
    if rios_solo_oficiales:
        problemas.append(f"   • {len(rios_solo_oficiales)} ríos oficiales sin datos de caudal")
    
    # Problema 2: Ríos con datos pero no en listado oficial
    if rios_solo_caudales:
        problemas.append(f"   • {len(rios_solo_caudales)} ríos con caudal no están en listado oficial")
    
    # Problema 3: Embalses sin datos de capacidad
    if embalses_solo_oficiales:
        problemas.append(f"   • {len(embalses_solo_oficiales)} embalses oficiales sin datos de capacidad")
    
    # Problema 4: Regiones vacías en filtros
    for region in sorted(todas_regiones):
        if rios_con_datos:
            rios_con_datos_region = [r for r in rios_con_datos if RIO_REGION.get(r) == region]
            if len(rios_con_datos_region) == 0:
                problemas.append(f"   • Región '{region}' no tiene ríos con datos para filtrar")
    
    if not problemas:
        print("   ✅ No se detectaron problemas significativos")
    else:
        for problema in problemas:
            print(problema)
    
    print()
    print("=" * 60)
    print("REPORTE COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    main()
