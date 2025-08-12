# 🚀 Guía para Despliegue del Dashboard Hidrológico

Este documento te guía paso a paso para desplegar tu dashboard como una página web accesible a través de una URL.

## Opción 1: Heroku (Gratis con limitaciones)

### Requisitos previos:
1. Cuenta en GitHub (gratis)
2. Cuenta en Heroku (gratis)
3. Git instalado en tu computadora

### Pasos para el despliegue:

#### 1. Preparar el repositorio Git
```bash
cd "/home/melissa/Documentos/MME/Utlidades del proyecto 1/Hidrologia_MME-main"
git init
git add .
git commit -m "Primera versión del dashboard hidrológico"
```

#### 2. Subir a GitHub
1. Ve a GitHub.com y crea un nuevo repositorio llamado `dashboard-hidrologico-mme`
2. No añadas README, .gitignore ni licencia (ya tienes archivos)
3. Ejecuta estos comandos:
```bash
git remote add origin https://github.com/TU_USUARIO/dashboard-hidrologico-mme.git
git branch -M main
git push -u origin main
```

#### 3. Desplegar en Heroku
1. Ve a heroku.com e inicia sesión
2. Haz clic en "New" → "Create new app"
3. Escribe un nombre único como `dashboard-hidrologico-mme-2025`
4. Selecciona región (United States)
5. En "Deployment method" selecciona "GitHub"
6. Conecta tu cuenta de GitHub
7. Busca tu repositorio `dashboard-hidrologico-mme` y conecta
8. Habilita "Automatic deploys" para actualizaciones automáticas
9. Haz clic en "Deploy Branch"

### ¡Listo! Tu dashboard estará disponible en:
`https://dashboard-hidrologico-mme-2025.herokuapp.com`

---

## Opción 2: Render (Gratis, más confiable)

### Pasos:
1. Ve a render.com y crea una cuenta
2. Conecta tu cuenta de GitHub
3. Selecciona "New Web Service"
4. Conecta tu repositorio
5. Configura:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:server`
   - **Python Version**: 3.9.18

---

## Opción 3: Railway (Gratis con límites)

### Pasos:
1. Ve a railway.app
2. Conecta con GitHub
3. Selecciona tu repositorio
4. Railway detectará automáticamente que es una app Python
5. Se desplegará automáticamente

---

## Opción 4: Google Cloud Platform (Créditos gratis)

### Crear archivo app.yaml:
```yaml
runtime: python39
env: standard

instance_class: F2

handlers:
- url: /.*
  script: auto
```

### Pasos:
1. Instala Google Cloud CLI
2. `gcloud app deploy`
3. Tu app estará en `https://PROJECT_ID.appspot.com`

---

## Opción 5: AWS Elastic Beanstalk

### Crear archivo .ebextensions/python.config:
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: application.py
```

---

## Recomendaciones:

### Para uso profesional/gubernamental:
- **AWS** o **Google Cloud**: Más control, escalabilidad y confiabilidad
- Configura dominio personalizado (ej: hidro.minenergia.gov.co)

### Para pruebas/desarrollo:
- **Heroku**: Fácil de usar, gratis con limitaciones
- **Render**: Alternativa confiable a Heroku
- **Railway**: Despliegue muy simple

---

## Consideraciones de seguridad:

1. **Variables de entorno**: Si tienes API keys, úsalas como variables de entorno
2. **HTTPS**: Todas las plataformas mencionadas incluyen HTTPS automático
3. **Dominio personalizado**: Configura un dominio gubernamental oficial

---

## Mantenimiento:

- Las actualizaciones se pueden hacer automáticamente conectando con GitHub
- Cada push al repositorio actualizará la aplicación
- Configura alertas de monitoreo para problemas de disponibilidad

---

## URLs de ejemplo después del despliegue:

- Heroku: `https://tu-app.herokuapp.com`
- Render: `https://tu-app.onrender.com`
- Railway: `https://tu-app.up.railway.app`
- Google Cloud: `https://tu-proyecto.appspot.com`
- AWS: `https://tu-app.region.elasticbeanstalk.com`

¡Tu dashboard estará disponible 24/7 para cualquier persona con el URL!
