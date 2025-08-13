#!/usr/bin/env python3
"""
Script de control del servidor Flask-Dash para el Dashboard Hidrológico MME
Ministerio de Minas y Energía de Colombia
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

def check_virtual_env():
    """Verificar que el entorno virtual esté activado"""
    if 'VIRTUAL_ENV' not in os.environ:
        venv_path = Path('.venv')
        if venv_path.exists():
            print("⚠️  Activando entorno virtual...")
            activate_script = venv_path / 'bin' / 'activate'
            return f"source {activate_script} && "
        else:
            print("❌ No se encontró el entorno virtual (.venv)")
            sys.exit(1)
    return ""

def start_server(debug=False, port=8050, host='0.0.0.0'):
    """Iniciar el servidor Flask-Dash"""
    env_prefix = check_virtual_env()
    
    # Configurar variables de entorno
    env_vars = {
        'FLASK_DEBUG': 'true' if debug else 'false',
        'PORT': str(port),
        'HOST': host
    }
    
    # Construir comando
    env_string = ' '.join([f"{k}={v}" for k, v in env_vars.items()])
    cmd = f"{env_prefix}{env_string} python app.py"
    
    print(f"🚀 Iniciando servidor Dashboard Hidrológico MME...")
    print(f"🌐 URL: http://{host}:{port}")
    print(f"🔧 Debug: {debug}")
    print(f"📝 Comando: {cmd}")
    
    try:
        process = subprocess.Popen(cmd, shell=True)
        return process
    except KeyboardInterrupt:
        print("\n⏹️  Deteniendo servidor...")
        return None

def start_production():
    """Iniciar en modo producción con Gunicorn"""
    env_prefix = check_virtual_env()
    port = os.environ.get('PORT', '8050')
    
    cmd = f"{env_prefix}gunicorn app:server --bind 0.0.0.0:{port} --workers 2 --timeout 120 --access-logfile -"
    
    print(f"🏭 Iniciando servidor de producción...")
    print(f"🌐 Puerto: {port}")
    print(f"👥 Workers: 2")
    
    try:
        process = subprocess.Popen(cmd, shell=True)
        return process
    except KeyboardInterrupt:
        print("\n⏹️  Deteniendo servidor de producción...")
        return None

def show_status():
    """Mostrar estado de los endpoints"""
    import requests
    import json
    
    base_url = "http://localhost:8050"
    endpoints = ['/health', '/api/status', '/api/info']
    
    print("📊 Estado de los endpoints:")
    print("=" * 50)
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint}: OK")
                print(f"   {json.dumps(data, indent=2, ensure_ascii=False)}")
            else:
                print(f"❌ {endpoint}: Error {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint}: No disponible ({str(e)})")
        print("-" * 30)

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("""
🌊 Dashboard Hidrológico MME Colombia - Gestor de Servidor
========================================================

Uso: python server.py [comando] [opciones]

Comandos disponibles:
  start           - Iniciar en modo desarrollo (debug=False)
  dev             - Iniciar en modo desarrollo (debug=True)
  prod            - Iniciar en modo producción (Gunicorn)
  status          - Mostrar estado de endpoints
  help            - Mostrar esta ayuda

Ejemplos:
  python server.py start
  python server.py dev --port 3000
  python server.py prod
  python server.py status
        """)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'start':
        port = 8050
        if '--port' in sys.argv:
            port_idx = sys.argv.index('--port') + 1
            if port_idx < len(sys.argv):
                port = int(sys.argv[port_idx])
        
        process = start_server(debug=False, port=port)
        if process:
            try:
                process.wait()
            except KeyboardInterrupt:
                process.terminate()
    
    elif command == 'dev':
        port = 8050
        if '--port' in sys.argv:
            port_idx = sys.argv.index('--port') + 1
            if port_idx < len(sys.argv):
                port = int(sys.argv[port_idx])
        
        process = start_server(debug=True, port=port)
        if process:
            try:
                process.wait()
            except KeyboardInterrupt:
                process.terminate()
    
    elif command == 'prod':
        process = start_production()
        if process:
            try:
                process.wait()
            except KeyboardInterrupt:
                process.terminate()
    
    elif command == 'status':
        show_status()
    
    elif command in ['help', '-h', '--help']:
        # Mostrar ayuda
        print("""
🌊 Dashboard Hidrológico MME Colombia - Gestor de Servidor
========================================================

Uso: python server.py [comando] [opciones]

Comandos disponibles:
  start           - Iniciar en modo desarrollo (debug=False)
  dev             - Iniciar en modo desarrollo (debug=True)
  prod            - Iniciar en modo producción (Gunicorn)
  status          - Mostrar estado de endpoints
  help            - Mostrar esta ayuda

Ejemplos:
  python server.py start
  python server.py dev --port 3000
  python server.py prod
  python server.py status
        """)
    
    else:
        print(f"❌ Comando desconocido: {command}")
        print("💡 Use 'python server.py help' para ver los comandos disponibles")
        sys.exit(1)

if __name__ == '__main__':
    main()
