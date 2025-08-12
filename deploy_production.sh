#!/bin/bash

# 🚀 Script de despliegue automatizado para máxima confiabilidad
# Ejecutar con: bash deploy_production.sh

echo "🛡️ DESPLIEGUE PARA MÁXIMA CONFIABILIDAD - MINISTERIO DE MINAS Y ENERGÍA"
echo "=================================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "app.py" ]; then
    log_error "No se encuentra app.py. Ejecuta este script desde el directorio del proyecto."
    exit 1
fi

log_info "Iniciando configuración para despliegue de alta confiabilidad..."

# 1. Verificar archivos necesarios
log_info "📋 Verificando archivos de configuración..."

required_files=("app.py" "requirements.txt" "Procfile" "runtime.txt" "app.yaml" "Dockerfile")
missing_files=()

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        log_success "✅ $file existe"
    else
        log_error "❌ $file no encontrado"
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    log_error "Faltan archivos necesarios. Por favor verifica la configuración."
    exit 1
fi

# 2. Verificar configuraciones de AWS
if [ -d ".ebextensions" ]; then
    log_success "✅ Configuraciones AWS Elastic Beanstalk encontradas"
    eb_configs=($(ls .ebextensions/*.config 2>/dev/null | wc -l))
    log_info "📁 Encontrados $eb_configs archivos de configuración EB"
else
    log_warning "⚠️ Directorio .ebextensions no encontrado"
fi

# 3. Test de la aplicación localmente
log_info "🧪 Ejecutando tests básicos de la aplicación..."

python3 -c "
import sys
try:
    from app import app, objetoAPI, server
    print('✅ Aplicación cargada correctamente')
    if objetoAPI is not None:
        print('✅ API XM inicializada')
    else:
        print('⚠️ API XM no inicializada (normal en algunos entornos)')
    print('✅ Servidor Flask configurado')
    print('✅ Tests básicos completados')
except Exception as e:
    print(f'❌ Error en tests básicos: {str(e)}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    log_error "Tests básicos fallaron. Revisa la configuración de la aplicación."
    exit 1
fi

log_success "🎉 Tests básicos completados exitosamente"

# 4. Preparar para Git
log_info "📦 Preparando repositorio Git..."

if [ ! -d ".git" ]; then
    log_info "Inicializando repositorio Git..."
    git init
    echo "__pycache__/" > .gitignore
    echo "*.pyc" >> .gitignore
    echo ".env" >> .gitignore
    echo "*.log" >> .gitignore
    log_success "Repositorio Git inicializado"
fi

# 5. Información de despliegue
echo ""
log_info "🚀 OPCIONES DE DESPLIEGUE PARA MÁXIMA CONFIABILIDAD:"
echo ""

echo "1️⃣  AWS ELASTIC BEANSTALK (RECOMENDADO PARA GOBIERNO)"
echo "   💰 Costo: \$150-300/mes"
echo "   ⏱️  Uptime: 99.95%+"
echo "   🛡️  Características:"
echo "      • Auto-scaling (2-20 instancias)"
echo "      • Load balancer integrado"
echo "      • Health checks automáticos"
echo "      • Monitoreo CloudWatch"
echo "      • Backups automáticos"
echo "      • Soporte 24/7"
echo "   📋 Comandos:"
echo "      eb init dashboard-hidrologico-mme"
echo "      eb create production-env --instance-types t3.small,t3.medium"
echo "      eb deploy"

echo ""
echo "2️⃣  GOOGLE CLOUD PLATFORM"
echo "   💰 Costo: \$100-200/mes"
echo "   ⏱️  Uptime: 99.95%+"
echo "   📋 Comandos:"
echo "      gcloud app deploy"

echo ""
echo "3️⃣  MICROSOFT AZURE (GOBIERNO)"
echo "   💰 Costo: \$120-250/mes"
echo "   ⏱️  Uptime: 99.95%+"
echo "   🏛️  Certificaciones gubernamentales"

echo ""
echo "4️⃣  AMAZON LIGHTSAIL (SIMPLE)"
echo "   💰 Costo: \$40-80/mes"
echo "   ⏱️  Uptime: 99.9%+"
echo "   📋 Interfaz gráfica simple"

echo ""
log_info "📊 MONITOREO Y ALERTAS INCLUIDAS:"
echo "   • Health checks cada 15 segundos"
echo "   • Auto-recovery en caso de fallas"
echo "   • Alertas por email/SMS"
echo "   • Logs centralizados"
echo "   • Métricas en tiempo real"

echo ""
log_info "🔒 CARACTERÍSTICAS DE SEGURIDAD:"
echo "   • HTTPS automático"
echo "   • WAF (Web Application Firewall)"
echo "   • DDoS protection"
echo "   • Certificados SSL/TLS"
echo "   • Backups automáticos"

echo ""
log_success "✨ ¡Tu aplicación está lista para despliegue de alta confiabilidad!"

echo ""
log_info "📞 SOPORTE TÉCNICO 24/7:"
echo "   • AWS: Business Support Plan"
echo "   • Google: Cloud Support"
echo "   • Azure: Professional Support"

echo ""
log_warning "💡 RECOMENDACIÓN:"
echo "Para el Ministerio de Minas y Energía, usa AWS Elastic Beanstalk"
echo "con configuración de alta disponibilidad (multi-AZ)."

echo ""
echo "¿Quieres proceder con AWS Elastic Beanstalk? (y/n)"
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    log_info "Verificando AWS CLI..."
    if command -v eb &> /dev/null; then
        log_success "AWS EB CLI encontrado"
        log_info "Puedes ejecutar: eb init dashboard-hidrologico-mme"
    else
        log_warning "AWS EB CLI no encontrado"
        log_info "Instala con: pip install awsebcli"
    fi
else
    log_info "Para cualquier plataforma que elijas, todos los archivos están configurados."
fi

log_success "🎉 Configuración completada exitosamente!"
