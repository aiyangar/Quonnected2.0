#!/usr/bin/env python3
"""
Script para explorar todos los endpoints disponibles en UniFi
"""

import requests
import urllib3
import os
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def explore_endpoints():
    """
    Explora todos los endpoints posibles de UniFi
    """
    # Obtener configuración
    unifi_url = os.getenv('UNIFI_URL')
    username = os.getenv('UNIFI_USERNAME')
    password = os.getenv('UNIFI_PASSWORD')
    
    if not unifi_url or not username or not password:
        print("❌ Faltan variables de entorno")
        return
    
    # Asegurar que la URL tenga el esquema https:// y puerto correcto
    if not unifi_url.startswith(('http://', 'https://')):
        unifi_url = f'https://{unifi_url}'
    if ':8443' not in unifi_url and ':443' not in unifi_url and ':80' not in unifi_url:
        unifi_url = f'{unifi_url}:8443'
    
    session = requests.Session()
    
    try:
        # Autenticación
        print(f"🌐 Conectando a: {unifi_url}")
        login_url = f'{unifi_url}/api/auth/login'
        login_payload = {'username': username, 'password': password}
        
        login_response = session.post(login_url, json=login_payload, verify=False, timeout=10)
        if login_response.status_code != 200:
            print(f"❌ Error de autenticación: {login_response.status_code}")
            return
        
        print("✅ Autenticación exitosa")
        
        # Lista de endpoints a probar
        endpoints = [
            # Endpoints clásicos de UniFi
            '/api/s/default/stat/sta',           # Clientes conectados
            '/api/s/default/stat/device',        # Dispositivos
            '/api/s/default/stat/user',          # Usuarios
            '/api/s/default/stat/client',        # Clientes
            '/api/s/default/stat/networkconf',   # Configuración de red
            '/api/s/default/stat/wlanconf',      # Configuración WiFi
            '/api/s/default/stat/health',        # Estado del sistema
            
            # Endpoints nuevos de UniFi Network
            '/network/default/clients/main',     # Clientes principales
            '/network/default/devices',          # Dispositivos
            '/network/default/insights',         # Insights
            '/network/default/events',           # Eventos
            
            # Endpoints de sistema
            '/api/self',                         # Información del sistema
            '/api/status',                       # Estado
            '/api/sites',                        # Sitios
        ]
        
        print(f"\n🔍 Explorando {len(endpoints)} endpoints...")
        print("=" * 60)
        
        working_endpoints = []
        
        for endpoint in endpoints:
            try:
                url = f'{unifi_url}{endpoint}'
                response = session.get(url, verify=False, timeout=5)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        data_count = len(data.get('data', [])) if isinstance(data.get('data'), list) else 'N/A'
                        print(f"✅ {endpoint:<35} - {data_count} elementos")
                        working_endpoints.append((endpoint, data))
                    except:
                        print(f"✅ {endpoint:<35} - Respuesta no JSON")
                elif response.status_code == 404:
                    print(f"❌ {endpoint:<35} - No encontrado")
                else:
                    print(f"⚠️ {endpoint:<35} - Status {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {endpoint:<35} - Error: {str(e)[:30]}")
        
        # Mostrar detalles de endpoints que funcionan
        if working_endpoints:
            print(f"\n📊 Endpoints que funcionan ({len(working_endpoints)}):")
            print("=" * 60)
            
            for endpoint, data in working_endpoints:
                print(f"\n🔗 {endpoint}")
                if isinstance(data, dict):
                    if 'data' in data and isinstance(data['data'], list):
                        print(f"   📱 Elementos: {len(data['data'])}")
                        if data['data']:
                            # Mostrar estructura del primer elemento
                            first_item = data['data'][0]
                            if isinstance(first_item, dict):
                                print(f"   📋 Campos: {', '.join(first_item.keys())[:50]}...")
                    else:
                        print(f"   📄 Estructura: {list(data.keys())}")
                print(f"   📏 Tamaño respuesta: {len(str(data))} caracteres")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    explore_endpoints()
