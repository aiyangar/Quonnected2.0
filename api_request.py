import requests
import json
import urllib3
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Deshabilitar las advertencias de SSL (no recomendado para producción)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Obtener configuración desde variables de entorno
UNIFI_URL = os.getenv('UNIFI_URL')
USERNAME = os.getenv('UNIFI_USERNAME')
PASSWORD = os.getenv('UNIFI_PASSWORD')

# Asegurar que la URL tenga el esquema https:// y puerto correcto
if UNIFI_URL and not UNIFI_URL.startswith(('http://', 'https://')):
    UNIFI_URL = f'https://{UNIFI_URL}'

# Asegurar que tenga el puerto 8443 si no se especifica puerto
if UNIFI_URL and ':8443' not in UNIFI_URL and ':443' not in UNIFI_URL and ':80' not in UNIFI_URL:
    UNIFI_URL = f'{UNIFI_URL}:8443'

def get_unifi_clients():
    """
    Se conecta al controlador UniFi, autentica y obtiene la lista de clientes.
    """
    # Verificar que las variables de entorno estén configuradas
    if not UNIFI_URL or not USERNAME or not PASSWORD:
        print("❌ Error: Faltan variables de entorno")
        print("💡 Asegúrate de tener en tu archivo .env:")
        print("   UNIFI_URL=https://tu_ip:8443")
        print("   UNIFI_USERNAME=tu_usuario")
        print("   UNIFI_PASSWORD=tu_contraseña")
        return None
    
    try:
        # Paso 1: Crear una sesión para mantener las cookies de autenticación
        session = requests.Session()

        # Paso 2: Intentar acceso a la interfaz web primero
        print(f"🌐 Conectando a UniFi: {UNIFI_URL}")
        print("🔍 Verificando acceso a la interfaz web...")
        
        # Probar acceso a la página principal
        main_page_url = f'{UNIFI_URL}/'
        try:
            main_response = session.get(main_page_url, verify=False, timeout=10)
            print(f"✅ Interfaz web accesible (Status: {main_response.status_code})")
        except Exception as e:
            print(f"⚠️  No se puede acceder a la interfaz web: {e}")
        
        # Paso 3: Autenticación
        login_url = f'{UNIFI_URL}/api/auth/login'
        login_payload = {
            'username': USERNAME,
            'password': PASSWORD
        }
        print("🔐 Intentando autenticarse...")
        login_response = session.post(login_url, json=login_payload, verify=False, timeout=10)
        login_response.raise_for_status() # Lanza un error si la solicitud no fue exitosa
        print("✅ Autenticación exitosa. Obteniendo clientes...")

        # Paso 4: Obtener la lista de clientes conectados
        clients_url = f'{UNIFI_URL}/api/s/default/stat/sta'
        clients_response = session.get(clients_url, verify=False, timeout=10)
        clients_response.raise_for_status()
        
        clients_data = clients_response.json()
        
        # Paso 4: Procesar y mostrar la información de los clientes
        clients = clients_data.get('data', [])
        
        if not clients:
            print("No se encontraron clientes conectados.")
            return

        formatted_clients = []
        for client in clients:
            client_info = {
                "id": client.get("_id"),
                "name": client.get("hostname") or client.get("name"),
                "ip_address": client.get("ip"),
                "mac_address": client.get("mac")
            }
            formatted_clients.append(client_info)
        
        # Opcional: Imprimir el JSON completo para verificar el formato
        # print(json.dumps(formatted_clients, indent=2))
        
        # Mostrar la lista de clientes formateada
        print(f"\n📱 Total de clientes conectados: {len(formatted_clients)}")
        print("=" * 50)
        for i, client in enumerate(formatted_clients, 1):
            print(f"{i:2d}. 📱 {client['name'] or 'Sin nombre'}")
            print(f"     🌐 IP: {client['ip_address'] or 'Sin IP'}")
            print(f"     🔗 MAC: {client['mac_address'] or 'Sin MAC'}")
            print(f"     🆔 ID: {client['id']}")
            print()
        
        return formatted_clients
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error durante la solicitud: {e}")
        return None
    finally:
        # Cerrar la sesión
        session.close()

if __name__ == "__main__":
    get_unifi_clients()