import pandas as pd

# Ruta al archivo CSV (ajusta si está en otra carpeta)
csv_path = "data.csv"

# Leer el archivo CSV
df = pd.read_csv(csv_path)

# Filtrar columnas necesarias
df = df[['Nombre Río', 'Region Hidrologica']].dropna()

# Normalizar nombres
df['Nombre Río'] = df['Nombre Río'].str.strip().str.upper()
df['Region Hidrologica'] = df['Region Hidrologica'].str.strip().str.title()

# Crear diccionario
embalse_region = dict(zip(df['Nombre Río'], df['Region Hidrologica']))

# Ordenar alfabéticamente
embalse_region = dict(sorted(embalse_region.items()))

# Imprimir todo el diccionario
for embalse, region in embalse_region.items():
    print(f'"{embalse}": "{region}",')
