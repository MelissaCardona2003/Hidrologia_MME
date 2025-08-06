# Dashboard Energético XM - Colombia

## 🚀 Descripción

Dashboard interactivo desarrollado con **Plotly Dash** para visualizar datos del mercado energético colombiano usando la API de XM (Operador del Sistema Interconectado Nacional).

## ✨ Características

- 📊 **Consulta dinámica** de métricas por MetricId y Entity
- 📅 **Selector de fechas** para análisis temporal
- 📈 **Visualizaciones interactivas**: tablas, gráficos de líneas y barras
- 📋 **Resumen estadístico** automático
- 🎨 **Diseño moderno** con Bootstrap
- 📱 **Interfaz responsive**
- 📤 **Exportación de datos** a Excel
- ⚡ **Alto rendimiento** y filtros en tiempo real

## 🛠️ Instalación

1. **Clona el repositorio:**
   ```bash
   git clone <repository-url>
   cd dashboard-energia-xm
   ```

2. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecuta la aplicación:**
   ```bash
   python app.py
   ```

4. **Abre tu navegador** en: http://localhost:8050

## 📊 Uso del Dashboard

### 1. Selección de Métricas
- **MetricId**: Elige la métrica que deseas consultar (ej: "Gene", "DemaCome", "PrecBolsNaci")
- **Entity**: Selecciona la entidad de agregación (ej: "Sistema", "Recurso", "Agente")

### 2. Rango de Fechas
- **Fecha Inicio**: Fecha de inicio de la consulta
- **Fecha Fin**: Fecha de fin de la consulta

### 3. Visualizaciones Disponibles

#### 📊 Tabla de Datos
- Tabla interactiva con todos los datos consultados
- Filtros por columna
- Ordenamiento ascendente/descendente
- Paginación automática
- Exportación a Excel

#### 📈 Gráfico de Líneas
- Visualización temporal de las métricas
- Ideal para analizar tendencias
- Hover interactivo con detalles

#### 📊 Gráfico de Barras
- Distribución por categorías
- Perfecto para comparar valores
- Top 20 automático para mejor visualización

#### 📋 Resumen Estadístico
- Estadísticas descriptivas automáticas
- Media, mediana, desviación estándar
- Valores mínimos y máximos

## 📈 Métricas Disponibles

El dashboard puede consultar todas las métricas disponibles en la API XM, incluyendo:

- **Generación**: Gene, GeneIdea, GeneProgDesp
- **Demanda**: DemaCome, DemaMaxPot, DemaSIN
- **Precios**: PrecBolsNaci, PrecEsca, PrecPromCont
- **Aportes**: AporEner, AporCaudal, PorcApor
- **Embalses**: VoluUtilDiarEner, CapaUtilDiarEner
- **Intercambios**: ImpoEner, ExpoEner
- **Y muchas más...**

## 🔧 Dependencias Principales

- **Dash**: Framework web interactivo
- **Plotly**: Visualizaciones avanzadas
- **Pandas**: Manipulación de datos
- **pydataxm**: Cliente oficial para API XM
- **Dash Bootstrap Components**: Componentes UI modernos

## 🎯 Ejemplos de Uso

### Consultar Generación Real del Sistema
```python
MetricId: "Gene"
Entity: "Sistema"
Fechas: 2025-01-01 a 2025-01-31
```

### Analizar Precios de Bolsa
```python
MetricId: "PrecBolsNaci"
Entity: "Sistema"
Fechas: 2025-01-01 a 2025-01-31
```

### Revisar Demanda Comercial por Agente
```python
MetricId: "DemaCome"
Entity: "Agente"
Fechas: 2025-01-01 a 2025-01-31
```

## 🚀 Características Técnicas

- **Arquitectura**: Aplicación web basada en Dash
- **Rendimiento**: Optimizado para grandes volúmenes de datos
- **Compatibilidad**: Funciona en todos los navegadores modernos
- **Responsivo**: Adaptable a dispositivos móviles y desktop
- **API**: Integración completa con pydataxm

## 📱 Capturas de Pantalla

*[Aquí puedes agregar capturas de pantalla del dashboard]*

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Para soporte y preguntas:
- 📧 Email: [tu-email@ejemplo.com]
- 🐛 Issues: [GitHub Issues]
- 📖 Documentación API XM: https://www.xm.com.co/

---

**Desarrollado con ❤️ para el sector energético colombiano**
# Hidrolog-a_MME
