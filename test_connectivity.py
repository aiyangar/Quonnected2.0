#!/usr/bin/env python3
"""
Script para probar la conectividad con el controlador UniFi
"""

import requests
import socket
import urllib3
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_ping(host, port):
    """
    Prueba si un host y puerto están accesibles
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Error en ping: {e}")
        return False

def test_http_connection(url):
    """
    Prueba la conexión HTTP/HTTPS
    """
    try:
        response = requests.get(url, verify=False, timeout=5)
        return response.status_code, response.text[:200]
    except requests.exceptions.ConnectTimeout:
        return "TIMEOUT", "Conexión agotó el tiempo"
    except requests.exceptions.ConnectionError as e:
        return "CONNECTION_ERROR", str(e)
    except Exception as e:
        return "ERROR", str(e)

def main():
    print("🔍 DIAGNÓSTICO DE CONECTIVIDAD UNIFI")
    print("=" * 40)
    
    # Obtener configuración
    unifi_url = os.getenv('UNIFI_URL')
    username = os.getenv('UNIFI_USERNAME')
    password = os.getenv('UNIFI_PASSWORD')
    
    print(f"📋 Configuración:")
    print(f"   UNIFI_URL: {unifi_url}")
    print(f"   UNIFI_USERNAME: {username}")
    print(f"   UNIFI_PASSWORD: {'*' * len(password) if password else 'No configurado'}")
    
    if not unifi_url:
        print("\n❌ UNIFI_URL no está configurado en el archivo .env")
        return
    
    # Extraer host y puerto
    if '://' in unifi_url:
        host = unifi_url.split('://')[1].split(':')[0]
    else:
        host = unifi_url.split(':')[0]
    
    # Probar diferentes puertos comunes
    ports_to_test = [8443, 443, 80, 8080]
    
    print(f"\n🌐 Probando conectividad con {host}:")
    print("-" * 30)
    
    accessible_ports = []
    for port in ports_to_test:
        print(f"   Puerto {port}: ", end="")
        if test_ping(host, port):
            print("✅ Accesible")
            accessible_ports.append(port)
        else:
            print("❌ No accesible")
    
    if not accessible_ports:
        print(f"\n❌ No se puede alcanzar {host} en ningún puerto")
        print("\n💡 Posibles soluciones:")
        print("   1. Verifica que la IP del controlador sea correcta")
        print("   2. Verifica que el controlador esté encendido")
        print("   3. Verifica la conectividad de red")
        print("   4. Verifica el firewall")
        return
    
    print(f"\n✅ Puertos accesibles: {accessible_ports}")
    
    # Probar URLs HTTP
    print(f"\n🌐 Probando URLs HTTP:")
    print("-" * 30)
    
    for port in accessible_ports:
        for protocol in ['https', 'http']:
            url = f"{protocol}://{host}:{port}"
            print(f"   {url}: ", end="")
            status, response = test_http_connection(url)
            if status == 200:
                print("✅ OK")
                if "unifi" in response.lower() or "ubiquiti" in response.lower():
                    print(f"      🎯 ¡Posible controlador UniFi encontrado!")
            elif status == "TIMEOUT":
                print("⏱️ Timeout")
            elif status == "CONNECTION_ERROR":
                print("❌ Error de conexión")
            else:
                print(f"⚠️ Status: {status}")

def suggest_alternatives():
    """
    Sugiere alternativas si no se puede conectar
    """
    print(f"\n🔄 ALTERNATIVAS:")
    print("=" * 30)
    print("1. 📱 Usar la API de UI.com (cloud):")
    print("   - Cambiar a la API original de UI.com")
    print("   - Usar API key en lugar de credenciales locales")
    print()
    print("2. 🌐 Verificar configuración de red:")
    print("   - ¿Estás en la misma red que el controlador?")
    print("   - ¿El controlador tiene IP estática?")
    print("   - ¿Hay firewall bloqueando el puerto?")
    print()
    print("3. 🔧 Verificar controlador UniFi:")
    print("   - ¿Está encendido y funcionando?")
    print("   - ¿Qué versión de firmware tiene?")
    print("   - ¿Está configurado para permitir API?")
    print()
    print("4. 📊 Usar datos de prueba:")
    print("   - Crear archivo JSON con datos simulados")
    print("   - Para desarrollo y pruebas")

if __name__ == "__main__":
    main()
    suggest_alternatives()
