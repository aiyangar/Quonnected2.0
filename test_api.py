#!/usr/bin/env python3
"""
Script para probar específicamente la API de UI.com y verificar el status code
"""

import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_api_connection():
    """
    Prueba la conexión a la API de UI.com
    """
    print("🧪 Prueba de conexión a la API de UI.com")
    print("=" * 50)
    
    url = "https://api.ui.com/v1/devices"
    
    # Obtener la API key
    api_key = os.getenv('UI_API_KEY')
    
    if not api_key:
        print("❌ Error: No se encontró la API key en las variables de entorno")
        print("💡 Asegúrate de tener un archivo .env con UI_API_KEY configurado")
        return False
    
    headers = {
        'Accept': 'application/json',
        'X-API-Key': api_key
    }
    
    print(f"🌐 URL: {url}")
    print(f"🔑 API Key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}")
    print(f"📋 Headers: {headers}")
    
    try:
        print(f"\n🚀 Enviando petición...")
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"\n📊 RESULTADO:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Status: {'✅ ÉXITO' if response.status_code == 200 else '❌ ERROR'}")
        
        if response.status_code == 200:
            print(f"   Tamaño respuesta: {len(response.text)} caracteres")
            print(f"   Content-Type: {response.headers.get('content-type', 'No especificado')}")
            
            try:
                json_data = response.json()
                print(f"   Tipo de datos: {type(json_data)}")
                
                if isinstance(json_data, list):
                    print(f"   Cantidad de dispositivos: {len(json_data)}")
                    if len(json_data) > 0:
                        print(f"   Primer dispositivo: {json_data[0]}")
                else:
                    print(f"   Contenido: {json_data}")
                    
            except Exception as e:
                print(f"   Error al parsear JSON: {e}")
                print(f"   Contenido raw: {response.text[:200]}...")
        else:
            print(f"   Mensaje de error: {response.text}")
            
        return response.status_code == 200
        
    except requests.exceptions.Timeout:
        print("❌ Error: Timeout - La API no respondió en 10 segundos")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar a la API")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la petición: {e}")
        return False

def test_different_endpoints():
    """
    Prueba diferentes endpoints de la API
    """
    print(f"\n🔍 Probando diferentes endpoints...")
    print("-" * 40)
    
    api_key = os.getenv('UI_API_KEY')
    if not api_key:
        print("❌ No hay API key configurada")
        return
    
    headers = {
        'Accept': 'application/json',
        'X-API-Key': api_key
    }
    
    endpoints = [
        "https://api.ui.com/v1/devices",
        "https://api.ui.com/v1/device",
        "https://api.ui.com/devices",
        "https://api.ui.com/v1/status"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n🌐 Probando: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=5)
            print(f"   Status: {response.status_code} - {'✅' if response.status_code == 200 else '❌'}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   Datos: {type(data)} con {len(data) if isinstance(data, list) else 'N/A'} elementos")
                except:
                    print(f"   Contenido: {response.text[:100]}...")
            else:
                print(f"   Error: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    success = test_api_connection()
    
    if not success:
        test_different_endpoints()
    
    print(f"\n{'✅ API funcionando correctamente' if success else '❌ API no está funcionando'}")
