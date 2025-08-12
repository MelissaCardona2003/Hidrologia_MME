#!/bin/bash

# Script de instalación para el dashboard hidrológico
# Ejecutar con: bash deploy_setup.sh

echo "🚀 Configurando el dashboard para despliegue web..."

# Verificar que todos los archivos necesarios existen
echo "📋 Verificando archivos necesarios..."

files=("app.py" "requirements.txt" "Procfile" "runtime.txt")
for file in "${files[@]}"
do
    if [ -f "$file" ]; then
        echo "✅ $file existe"
    else
        echo "❌ $file no encontrado"
        exit 1
    fi
done

echo "🔧 Verificando estructura del proyecto..."

# Mostrar estructura
echo "📁 Estructura del proyecto:"
ls -la

echo ""
echo "🌐 Tu dashboard está listo para desplegarse en:"
echo "• Heroku: https://heroku.com"
echo "• Render: https://render.com"
echo "• Railway: https://railway.app"
echo "• Google Cloud: https://cloud.google.com"
echo "• AWS Elastic Beanstalk: https://aws.amazon.com"

echo ""
echo "📖 Lee el archivo DESPLIEGUE_WEB.md para instrucciones detalladas"
echo "✨ ¡Tu dashboard hidrológico estará disponible 24/7 en internet!"
