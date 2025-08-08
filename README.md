# Hidrologia_MME

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

## 🆕 Funcionalidades Nuevas

### 📊 Tablas Jerárquicas Interactivas
- **Ordenamiento automático** de mayor a menor valor
- **Expansión/Compresión independiente** de regiones
- **Botones integrados** (⊞/⊟) para control intuitivo
- **Dos vistas simultáneas**: Participación porcentual y Capacidad detallada

### 🔧 Mejoras Técnicas
- **Callbacks optimizados** con `suppress_callback_exceptions=True`
- **Sincronización perfecta** entre tabla visual y lógica de datos
- **Interfaz completamente funcional** sin restricciones de orden

## 🛠️ Instalación

1. **Clona el repositorio:**
```bash
git clone https://github.com/MelissaCardona2003/Hidrolog-a_MME.git
cd Hidrologia_MME
```

2. **Crea un entorno virtual:**
```bash
python -m venv .venv
source .venv/bin/activate  # En Linux/Mac
# .venv\Scripts\activate   # En Windows
```

3. **Instala las dependencias:**
```bash
pip install -r requirements.txt
```

4. **Ejecuta la aplicación:**
```bash
python app.py
```

5. **Abre tu navegador** y ve a: `http://localhost:8050`

## 📋 Requisitos del Sistema

- Python 3.8+
- Conexión a Internet (para API de XM)
- Navegador web moderno

## 🔧 Configuración

El archivo `config.py` contiene las configuraciones principales:
- URL base de la API XM
- Parámetros de conexión
- Configuraciones de visualización

## 📈 Uso

1. **Selecciona fechas** usando los selectores de fecha de inicio y fin
2. **Visualiza datos automáticamente** cargados en las tablas jerárquicas
3. **Expande regiones** haciendo clic en los botones ⊞/⊟
4. **Compara datos** entre participación porcentual y capacidad
5. **Navega libremente** entre diferentes regiones sin restricciones

## 🏗️ Estructura del Proyecto

```
Hidrolog-a_MME/
├── app.py              # Aplicación principal
├── config.py           # Configuraciones
├── requirements.txt    # Dependencias
├── install.sh         # Script de instalación
├── API_XM/            # Módulo de la API XM
├── README.md          # Este archivo
└── .venv/             # Entorno virtual (generado)
```

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👥 Autores

- **Melissa Cardona** - Desarrollo principal - [@MelissaCardona2003](https://github.com/MelissaCardona2003)

## 🙏 Agradecimientos

- Ministerio de Minas y Energía de Colombia
- XM S.A. E.S.P. por proporcionar la API de datos
- Comunidad de Plotly Dash por la documentación y recursos

---

⚡ **Desarrollado para el Ministerio de Minas y Energía de Colombia** ⚡
# Hidrologia_MME
