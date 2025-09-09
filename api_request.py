import requests
import json
import re
import time
from datetime import datetime
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

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

def load_simpat_ips():
    """
    Carga las IPs de usuarios Simpat desde el archivo JSON
    """
    simpat_ips = {}
    
    try:
        with open('simpat_users.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'users' in data:
            for user in data['users']:
                ip = user.get('ip')
                hostname = user.get('hostname')
                user_id = user.get('userID')
                
                if ip:
                    simpat_ips[ip] = {
                        'hostname': hostname,
                        'userID': user_id
                    }
        
        print(f"📂 Cargados {len(simpat_ips)} usuarios de Simpat")
        return simpat_ips
        
    except FileNotFoundError:
        print("⚠️ Archivo simpat_users.json no encontrado")
        return {}
    except Exception as e:
        print(f"❌ Error cargando simpat_users.json: {e}")
        return {}

def scrape_unifi_clients():
    """
    Realiza web scraping de la interfaz web de UniFi para obtener clientes conectados
    """
    if not UNIFI_URL or not USERNAME or not PASSWORD:
        print("❌ Error: Faltan variables de entorno")
        print("💡 Asegúrate de tener en tu archivo .env:")
        print("   UNIFI_URL=https://tu_ip:8443")
        print("   UNIFI_USERNAME=tu_usuario")
        print("   UNIFI_PASSWORD=tu_contraseña")
        return None
    
    session = requests.Session()
    session.verify = False  # Deshabilitar verificación SSL para desarrollo
    
    try:
        print(f"🌐 Conectando a UniFi: {UNIFI_URL}")
        
        # Paso 1: Autenticación
        print("🔐 Autenticándose...")
        login_url = f'{UNIFI_URL}/api/auth/login'
        login_data = {
            'username': USERNAME,
            'password': PASSWORD
        }
        
        login_response = session.post(login_url, json=login_data, timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ Error de autenticación: {login_response.status_code}")
            return None
        
        print("✅ Autenticación exitosa")
        
        # Paso 2: Obtener la página principal de clientes
        print("🔍 Accediendo a la página de clientes...")
        clients_url = f'{UNIFI_URL}/network/default/clients/main'
        
        # Esperar 5 segundos antes del scraping
        print("⏳ Esperando 5 segundos para que la página se cargue completamente...")
        time.sleep(5)
        
        response = session.get(clients_url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Error accediendo a clientes: {response.status_code}")
            return None
        
        print("✅ Página de clientes accesible")
        
        # Paso 3: Guardar respuesta para análisis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_filename = f"unifi_response_{timestamp}.html"
        
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"📄 Respuesta guardada en: {html_filename}")
        print(f"📊 Tamaño: {len(response.text)} caracteres")
        
        # Paso 4: Buscar datos de clientes en el HTML
        print("🔍 Buscando datos de clientes en el HTML...")
        clients = extract_clients_from_html(response.text)
        
        if not clients:
            print("⚠️ No se encontraron clientes en el HTML")
            print("📄 Primeros 1000 caracteres de la respuesta:")
            print("-" * 60)
            print(response.text[:1000])
            return None
        
        print(f"✅ Encontrados {len(clients)} clientes")
        
        # Paso 5: Filtrar clientes de Simpat
        simpat_ips = load_simpat_ips()
        simpat_clients = []
        
        for client in clients:
            client_ip = client.get('ip') or client.get('ip_address')
            if client_ip in simpat_ips:
                client['simpat_user'] = simpat_ips[client_ip]
                simpat_clients.append(client)
        
        print(f"🎯 Clientes de Simpat encontrados: {len(simpat_clients)}")
        
        # Paso 6: Mostrar resultados
        display_results(simpat_clients)
        
        return simpat_clients
        
    except Exception as e:
        print(f"❌ Error durante el scraping: {e}")
        return None
    finally:
        session.close()

def extract_clients_from_html(html_content):
    """
    Extrae datos de clientes del HTML usando múltiples estrategias
    """
    clients = []
    
    print("🔍 Estrategia 1: Buscando JSON embebido...")
    # Estrategia 1: Buscar JSON embebido en scripts
    json_patterns = [
        r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
        r'window\.__DATA__\s*=\s*({.*?});',
        r'var\s+clients\s*=\s*(\[.*?\]);',
        r'clients:\s*(\[.*?\])',
        r'"clients":\s*(\[.*?\])',
        r'"devices":\s*(\[.*?\])',
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
        for match in matches:
            try:
                data = json.loads(match)
                if isinstance(data, list):
                    clients.extend(data)
                elif isinstance(data, dict):
                    for key in ['clients', 'data', 'items', 'devices']:
                        if key in data and isinstance(data[key], list):
                            clients.extend(data[key])
                            break
                
                if clients:
                    print(f"✅ Encontrados {len(clients)} clientes en JSON embebido")
                    return clients
            except:
                continue
    
    print("🔍 Estrategia 2: Buscando en tablas HTML...")
    # Estrategia 2: Buscar en tablas HTML
    table_pattern = r'<tr[^>]*>.*?<td[^>]*>([^<]+)</td>.*?<td[^>]*>([^<]+)</td>.*?<td[^>]*>([^<]+)</td>.*?</tr>'
    table_matches = re.findall(table_pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    for match in table_matches:
        if len(match) >= 3:
            client = {
                'name': match[0].strip(),
                'ip': match[1].strip(),
                'status': match[2].strip()
            }
            clients.append(client)
    
    if clients:
        print(f"✅ Encontrados {len(clients)} clientes en tablas HTML")
        return clients
    
    print("🔍 Estrategia 3: Buscando IPs en el texto...")
    # Estrategia 3: Buscar IPs directamente en el texto
    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    ip_matches = re.findall(ip_pattern, html_content)
    
    unique_ips = list(set(ip_matches))
    # Filtrar IPs comunes del sistema
    filtered_ips = [ip for ip in unique_ips if not ip.startswith(('127.', '169.254.', '224.', '255.'))]
    
    if filtered_ips:
        print(f"🔍 Encontradas {len(filtered_ips)} IPs únicas: {', '.join(filtered_ips)}")
        
        # Crear clientes básicos con las IPs encontradas
        for ip in filtered_ips:
            client = {
                'ip': ip,
                'name': f'Dispositivo-{ip.split(".")[-1]}',
                'status': 'unknown'
            }
            clients.append(client)
    
    return clients

def display_results(clients):
    """
    Muestra los resultados de clientes encontrados
    """
    if not clients:
        print("❌ No se encontraron clientes de Simpat")
        return
    
    print(f"\n📱 CLIENTES DE SIMPAT CONECTADOS: {len(clients)}")
    print("=" * 60)
    
    # Crear contenido para archivo
    output_content = []
    output_content.append("CLIENTES CONECTADOS DE SIMPAT")
    output_content.append("=" * 50)
    output_content.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_content.append(f"Total de clientes: {len(clients)}")
    output_content.append("")
    
    for i, client in enumerate(clients, 1):
        simpat_info = client.get('simpat_user', {})
        
        # Mostrar en consola
        print(f"{i:2d}. 📱 {client.get('name', 'Sin nombre')}")
        print(f"     🌐 IP: {client.get('ip', 'Sin IP')}")
        print(f"     🔗 MAC: {client.get('mac', 'Sin MAC')}")
        print(f"     👤 Simpat: {simpat_info.get('hostname', 'N/A')}")
        print(f"     🆔 UserID: {simpat_info.get('userID', 'N/A')}")
        print()
        
        # Agregar al archivo
        output_content.append(f"{i:2d}. {client.get('name', 'Sin nombre')}")
        output_content.append(f"     IP: {client.get('ip', 'Sin IP')}")
        output_content.append(f"     MAC: {client.get('mac', 'Sin MAC')}")
        output_content.append(f"     Simpat: {simpat_info.get('hostname', 'N/A')}")
        output_content.append(f"     UserID: {simpat_info.get('userID', 'N/A')}")
        output_content.append("")
    
    # Guardar en archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"clientes_simpat_{timestamp}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for line in output_content:
                f.write(line + '\n')
        print(f"✅ Resultados guardados en: {filename}")
    except Exception as e:
        print(f"❌ Error guardando archivo: {e}")

if __name__ == "__main__":
    scrape_unifi_clients()