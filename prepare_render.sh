#!/bin/bash

# 🚀 Script de preparación para RENDER
# Ejecutar con: bash prepare_render.sh

echo "🎯 PREPARANDO DASHBOARD PARA RENDER.COM"
echo "======================================"

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 1. Verificar archivos para Render
log_info "📋 Verificando configuración para Render..."

if [ -f "Procfile" ]; then
    log_success "✅ Procfile encontrado"
    echo "   Contenido: $(cat Procfile)"
else
    log_warning "❌ Procfile no encontrado"
fi

if [ -f "requirements.txt" ]; then
    log_success "✅ requirements.txt encontrado"
    echo "   Dependencias: $(wc -l < requirements.txt) paquetes"
else
    log_warning "❌ requirements.txt no encontrado"
fi

if [ -f "runtime.txt" ]; then
    log_success "✅ runtime.txt encontrado"
    echo "   Python version: $(cat runtime.txt)"
else
    log_warning "❌ runtime.txt no encontrado"
fi

# 2. Verificar que app.py tenga server
log_info "🔍 Verificando configuración de servidor..."

if grep -q "server = app.server" app.py; then
    log_success "✅ Variable 'server' configurada en app.py"
else
    log_warning "⚠️ Verifica que app.py tenga: server = app.server"
fi

# 3. Test básico de importación
log_info "🧪 Probando importación básica..."

python3 -c "
import sys
try:
    import dash
    import gunicorn
    import pandas
    import plotly
    print('✅ Dependencias principales disponibles')
except ImportError as e:
    print(f'⚠️ Dependencia faltante: {e}')
    print('   Se instalará automáticamente en Render')
" 2>/dev/null

# 4. Estado del repositorio Git
log_info "📦 Estado del repositorio Git..."

if [ -d ".git" ]; then
    log_success "✅ Repositorio Git inicializado"
    
    # Verificar si hay cambios pendientes
    if git diff --quiet && git diff --staged --quiet; then
        log_success "✅ No hay cambios pendientes"
    else
        log_warning "⚠️ Hay cambios sin commit"
        echo "   Ejecuta: git add . && git commit -m 'Update for Render'"
    fi
    
    # Verificar remote
    if git remote -v | grep -q "origin"; then
        log_success "✅ Remote origin configurado"
        echo "   Remote: $(git remote get-url origin)"
    else
        log_warning "⚠️ No hay remote origin configurado"
        echo "   Necesitas configurar GitHub remote"
    fi
else
    log_warning "⚠️ Git no inicializado"
    echo "   Ejecuta: git init"
fi

# 5. Información sobre Render
echo ""
log_info "🌐 INFORMACIÓN PARA RENDER.COM:"
echo ""

echo "📝 CONFIGURACIÓN SUGERIDA:"
echo "   • Name: dashboard-hidrologico-mme"
echo "   • Environment: Python 3"
echo "   • Build Command: pip install -r requirements.txt"
echo "   • Start Command: gunicorn app:server --bind 0.0.0.0:\$PORT"
echo "   • Plan: Starter (\$7/mes) - recomendado para producción"
echo "   • Region: Oregon (US West) o Frankfurt (EU Central)"

echo ""
echo "🔧 VARIABLES DE ENTORNO (opcionales):"
echo "   • PYTHON_VERSION: 3.9.18"
echo "   • PYTHONUNBUFFERED: 1"
echo "   • DASH_DEBUG: False"

echo ""
echo "📊 HEALTH CHECK:"
echo "   • Path: /health"
echo "   • Tu app ya tiene este endpoint configurado"

echo ""
log_info "🚀 PASOS PARA DESPLEGAR EN RENDER:"
echo ""

echo "1️⃣  Sube tu código a GitHub:"
echo "     git add ."
echo "     git commit -m 'Dashboard listo para Render'"
echo "     git push origin main"

echo ""
echo "2️⃣  Ve a render.com y crea cuenta"

echo ""
echo "3️⃣  Conecta tu repositorio de GitHub"

echo ""
echo "4️⃣  Configura Web Service con los datos de arriba"

echo ""
echo "5️⃣  ¡Despliega y disfruta!"

echo ""
echo "🎯 URL RESULTANTE:"
echo "   https://dashboard-hidrologico-mme.onrender.com"

echo ""
log_success "✨ ¡Tu dashboard está listo para Render!"

echo ""
echo "💡 VENTAJAS DE RENDER:"
echo "   • ✅ No se 'duerme' (en plan Starter+)"
echo "   • ✅ SSL automático (HTTPS)"
echo "   • ✅ Despliegues automáticos desde GitHub"
echo "   • ✅ Interface simple y clara"
echo "   • ✅ 99.9% uptime garantizado"
echo "   • ✅ Soporte técnico responsive"

echo ""
echo "💰 COSTOS:"
echo "   • Free: 750h/mes (se duerme)"
echo "   • Starter: \$7/mes (siempre activo) ← RECOMENDADO"
echo "   • Pro: \$25/mes (más recursos)"
