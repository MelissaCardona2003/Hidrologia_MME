#!/bin/bash

echo "🚀 Instalando Dashboard Energético XM..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado. Por favor instala Python 3.8 o superior."
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
echo "⬆️ Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install -r requirements.txt

echo "✅ Instalación completada!"
echo ""
echo "🎯 Para ejecutar el dashboard:"
echo "   source venv/bin/activate"
echo "   python app.py"
echo ""
echo "🌐 Luego abre: http://localhost:8050"
