# 🌊 Dashboard Hidrológico MME - Servidor Flask

## 📋 Descripción

El Dashboard Hidrológico del Ministerio de Minas y Energía de Colombia ahora está montado sobre un **servidor Flask personalizado** que proporciona funcionalidades adicionales de API y monitoreo.

## 🏗️ Arquitectura

```
Dashboard Hidrológico MME
├── Flask Server (Backend)
│   ├── Health Check Endpoints
│   ├── API Status Monitoring  
│   └── Application Info
└── Dash Application (Frontend)
    ├── Interactive Dashboard
    ├── Data Visualization
    └── User Interface
```

## 🚀 Características del Servidor Flask

### ✅ **Endpoints Adicionales**

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/health` | GET | Health check para monitoreo |
| `/api/status` | GET | Estado de conectividad con API XM |
| `/api/info` | GET | Información detallada de la aplicación |
| `/` | GET | Dashboard principal (Dash) |

### 🔧 **Configuración Avanzada**

- **Puerto configurable** mediante variable de entorno `PORT`
- **Host configurable** mediante variable de entorno `HOST` 
- **Modo debug** configurable mediante variable de entorno `FLASK_DEBUG`
- **Secret key** para sesiones seguras
- **Logging mejorado** con timestamps y contexto

## 📖 Guía de Uso

### 🎯 **Método 1: Script de Gestión (Recomendado)**

```bash
# Activar entorno virtual
source .venv/bin/activate

# Iniciar en modo desarrollo
python server.py start

# Iniciar en modo desarrollo con debug
python server.py dev

# Iniciar en modo producción (Gunicorn)
python server.py prod

# Verificar estado de endpoints
python server.py status

# Ver ayuda
python server.py help
```

### 🎯 **Método 2: Ejecución Directa**

```bash
# Activar entorno virtual
source .venv/bin/activate

# Ejecutar directamente
python app.py

# Con variables de entorno personalizadas
FLASK_DEBUG=true PORT=3000 python app.py
```

### 🎯 **Método 3: Producción con Gunicorn**

```bash
# Usando Gunicorn (recomendado para producción)
gunicorn app:server --bind 0.0.0.0:8050 --workers 2 --timeout 120
```

## 🔍 Monitoreo y Salud

### **Health Check**
```bash
curl http://localhost:8050/health
```
```json
{
  "status": "healthy",
  "service": "Dashboard Hidrológico MME",
  "timestamp": "2025-08-12 22:08:39",
  "version": "3.3"
}
```

### **Estado de API XM**
```bash
curl http://localhost:8050/api/status
```
```json
{
  "status": "ok",
  "api_xm_status": "connected",
  "timestamp": "2025-08-12 22:08:40"
}
```

### **Información de la Aplicación**
```bash
curl http://localhost:8050/api/info
```
```json
{
  "name": "Dashboard Hidrológico - MME Colombia",
  "description": "Sistema de Información Hidrológica del Ministerio de Minas y Energía",
  "version": "3.3",
  "last_update": "2025-08-12 22:08:21",
  "author": "Ministerio de Minas y Energía de Colombia",
  "data_source": "XM - Expertos en Mercados",
  "endpoints": {
    "health": "/health",
    "api_status": "/api/status", 
    "app_info": "/api/info"
  }
}
```

## 🔐 Variables de Entorno

| Variable | Valor por Defecto | Descripción |
|----------|------------------|-------------|
| `PORT` | `8050` | Puerto del servidor |
| `HOST` | `0.0.0.0` | Host del servidor |
| `FLASK_DEBUG` | `false` | Modo debug de Flask |

## 🏭 Despliegue en Producción

### **Render/Heroku**
El `Procfile` está configurado para usar Gunicorn:
```
web: gunicorn app:server --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

### **Docker (Opcional)**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8050
CMD ["gunicorn", "app:server", "--bind", "0.0.0.0:8050"]
```

## 🛠️ Ventajas de la Configuración Flask

1. **📊 Monitoreo Avanzado**: Endpoints de salud y estado
2. **🔧 Configuración Flexible**: Variables de entorno
3. **🚀 Escalabilidad**: Compatible con Gunicorn y servidores WSGI
4. **🔍 Debugging**: Logs detallados y herramientas de desarrollo
5. **🔐 Seguridad**: Secret key y configuraciones seguras
6. **📡 API Extendible**: Fácil agregar nuevos endpoints

## 🆘 Solución de Problemas

### **Problema: ModuleNotFoundError**
```bash
# Activar entorno virtual
source .venv/bin/activate
```

### **Problema: Puerto ocupado**
```bash
# Cambiar puerto
PORT=3000 python app.py
```

### **Problema: API XM desconectada**
```bash
# Verificar estado
curl http://localhost:8050/api/status
```

## 📞 Soporte

Para problemas técnicos, verificar:
1. Estado del entorno virtual: `which python`
2. Dependencias instaladas: `pip list`
3. Estado de endpoints: `python server.py status`
4. Logs del servidor en la terminal

---

**🏛️ Ministerio de Minas y Energía de Colombia**  
**📊 Sistema de Información Hidrológica v3.3**
