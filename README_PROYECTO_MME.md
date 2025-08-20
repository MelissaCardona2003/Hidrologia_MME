# 🌊 Dashboard Hidrológico MME Colombia

## 📋 Descripción General
Este proyecto es un dashboard interactivo para visualizar y analizar datos hidrológicos de Colombia, desarrollado por el Ministerio de Minas y Energía. Utiliza Python, Dash y Flask para crear una aplicación web moderna y fácil de usar.

---

## 🚀 ¿Qué hace la aplicación?
- Consulta datos hidrológicos desde la API oficial XM.
- Permite filtrar por región, río y rango de fechas.
- Muestra gráficos de líneas, barras y tablas interactivas.
- Calcula y visualiza la capacidad energética útil diaria por embalse y región.
- Incluye endpoints de salud y monitoreo para integración profesional.

---

## 🏗️ Estructura del Proyecto

```
Hidrologia_MME-main/
├── app.py                  # Código principal del dashboard Dash/Flask
├── server.py               # Script para gestionar el servidor (desarrollo/producción)
├── requirements.txt        # Lista de dependencias Python
├── install.sh              # Instalador automático para Linux
├── Dockerfile              # Configuración opcional para despliegue con Docker
├── FLASK_SERVER_GUIDE.md   # Guía técnica sobre el servidor Flask
├── REPORTE_VERIFICACION_FINAL.md # Informe técnico de verificación
├── .venv/                  # Entorno virtual Python
├── .gitignore              # Exclusiones para Git
└── .git/                   # Carpeta de control de versiones
```

---

## 🧑‍💻 ¿Cómo instalar y ejecutar?

### 1. Instalar dependencias y entorno
```bash
bash install.sh
```

### 2. Activar entorno virtual
```bash
source venv/bin/activate
```

### 3. Ejecutar el dashboard
```bash
python app.py
```

### 4. Abrir en el navegador
```
http://localhost:8050
```

### 5. (Opcional) Usar el gestor avanzado
```bash
python server.py start      # Modo desarrollo
python server.py prod       # Modo producción (Gunicorn)
python server.py status     # Verificar endpoints
```

---

## 🗂️ Explicación de los archivos principales

- **app.py**: Código principal. Define el dashboard, callbacks, gráficos y lógica de consulta a la API XM. Montado sobre un servidor Flask para mayor flexibilidad y monitoreo.
- **server.py**: Script para iniciar el servidor en diferentes modos (desarrollo, producción, monitoreo). Útil para automatizar despliegue y pruebas.
- **requirements.txt**: Lista de librerías necesarias (Dash, Flask, pandas, pydataxm, etc).
- **install.sh**: Script para instalar todo automáticamente en Linux.
- **Dockerfile**: Permite crear una imagen Docker para despliegue en cualquier servidor o nube.
- **FLASK_SERVER_GUIDE.md**: Guía técnica sobre el servidor Flask y endpoints disponibles.
- **REPORTE_VERIFICACION_FINAL.md**: Informe técnico sobre la verificación y funcionamiento del dashboard.

---

## 🧩 ¿Cómo funciona el código?

### 1. **Inicio y configuración**
- Se importa Dash, Flask y las librerías necesarias.
- Se inicializa un servidor Flask y se monta la app Dash sobre él.
- Se configuran estilos visuales y el layout del dashboard.

### 2. **Consulta de datos**
- Se conecta a la API XM usando la librería `pydataxm`.
- Se obtienen datos de ríos, regiones y embalses.
- Se procesan y agrupan los datos para visualización.

### 3. **Interactividad**
- El usuario puede seleccionar región, río y fechas.
- Los callbacks de Dash actualizan los gráficos y tablas en tiempo real.
- Si no hay filtros, se muestra una vista nacional por defecto.

### 4. **Visualización**
- Gráficos de líneas para series temporales.
- Gráficos de barras para comparación entre ríos/regiones.
- Tablas interactivas para detalles y porcentajes.

### 5. **Endpoints Flask**
- `/health`: Verifica que el servidor está activo.
- `/api/status`: Verifica la conectividad con la API XM.
- `/api/info`: Muestra información técnica de la app.

---

## 🛠️ Recomendaciones para el equipo
- Usar siempre el entorno virtual (`.venv`) para evitar conflictos de dependencias.
- Leer el archivo `FLASK_SERVER_GUIDE.md` para entender el servidor y los endpoints.
- Consultar `REPORTE_VERIFICACION_FINAL.md` para detalles técnicos y validaciones.
- Si no se usa Docker, se puede ignorar/eliminar el `Dockerfile`.
- Mantener el código en Git para control de versiones y colaboración.

---

## 🆘 ¿Problemas comunes?
- **No se instala una librería**: Verificar que el entorno virtual esté activado.
- **Puerto ocupado**: Cambiar el puerto en el comando de ejecución.
- **API XM desconectada**: Verificar el endpoint `/api/status`.
- **Errores de permisos**: Usar `chmod +x install.sh` si el instalador no se ejecuta.

---

## 📞 Contacto y soporte
Para dudas técnicas, consulta primero los archivos de guía y documentación. Si el problema persiste, comunícate con el responsable técnico del proyecto.

---

**🏛️ Ministerio de Minas y Energía de Colombia**  
**📊 Sistema de Información Hidrológica v3.3**
