import requests
import os
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def conectar_api():
    """
    Conecta a la API de UI.com y obtiene todos los dispositivos (maneja paginación)
    """
    url = "https://api.ui.com/v1/devices"
    
    # Obtener API key desde variables de entorno
    api_key = os.getenv('UI_API_KEY')
    
    if not api_key:
        print("❌ Error: No se encontró UI_API_KEY en las variables de entorno")
        return None
    
    headers = {
        'Accept': 'application/json',
        'X-API-Key': api_key
    }
    
    all_data = []
    next_token = None
    page = 1
    
    try:
        while True:
            print(f"🌐 Conectando a la API de UI.com... Página {page}")
            
            # Agregar parámetros de paginación si existe next_token
            params = {}
            if next_token:
                params['nextToken'] = next_token
            
            response = requests.request("GET", url, headers=headers, params=params)
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Agregar datos de esta página
                if 'data' in data:
                    all_data.extend(data['data'])
                    print(f"✅ Página {page}: {len(data['data'])} hosts encontrados")
                
                # Verificar si hay más páginas
                next_token = data.get('nextToken')
                if not next_token:
                    print("✅ Todas las páginas obtenidas")
                    break
                
                page += 1
            else:
                print(f"❌ Error en la API: {response.status_code}")
                print(f"Respuesta: {response.text}")
                return None
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return None
    
    # Retornar estructura similar a la respuesta original
    return {
        'data': all_data,
        'httpStatusCode': 200,
        'totalPages': page
    }

def extraer_dispositivos_conectados(data):
    """
    Extrae solo los dispositivos conectados (status: online)
    """
    dispositivos_conectados = []
    total_dispositivos = 0
    dispositivos_online = 0
    
    if not data or 'data' not in data:
        print("⚠️  No hay datos para procesar")
        return dispositivos_conectados
    
    print(f"\n🔍 Procesando {len(data['data'])} hosts...")
    
    for host in data['data']:
        host_name = host.get('hostName', 'Host desconocido')
        print(f"   📂 Host: {host_name}")
        
        if 'devices' in host:
            host_devices = host['devices']
            total_dispositivos += len(host_devices)
            print(f"      📱 Dispositivos en host: {len(host_devices)}")
            
            for dispositivo in host_devices:
                status = dispositivo.get('status', '').lower()
                if status == 'online':
                    dispositivos_online += 1
                    dispositivo_info = {
                        "name": dispositivo.get('name', 'Sin nombre'),
                        "ip": dispositivo.get('ip', 'Sin IP'),
                        "status": dispositivo.get('status', 'Desconocido'),
                    }
                    dispositivos_conectados.append(dispositivo_info)
                    print(f"         ✅ {dispositivo.get('name', 'Sin nombre')} - {dispositivo.get('ip', 'Sin IP')}")
                else:
                    print(f"         ❌ {dispositivo.get('name', 'Sin nombre')} - {status}")
    
    print(f"\n📊 Resumen:")
    print(f"   Total dispositivos: {total_dispositivos}")
    print(f"   Dispositivos online: {dispositivos_online}")
    print(f"   Dispositivos offline: {total_dispositivos - dispositivos_online}")
    
    return dispositivos_conectados

def guardar_json(dispositivos, archivo="dispositivos_conectados.json"):
    """
    Guarda los dispositivos conectados en un archivo JSON
    """
    try:
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(dispositivos, f, indent=2, ensure_ascii=False)
        print(f"✅ Archivo guardado: {archivo}")
        return True
    except Exception as e:
        print(f"❌ Error al guardar archivo: {e}")
        return False

if __name__ == "__main__":
    print("🚀 GENERANDO ARCHIVO JSON DE DISPOSITIVOS CONECTADOS")
    print("=" * 55)
    
    # Conectar a la API
    data = conectar_api()
    
    if data:
        print(f"\n✅ Conexión establecida correctamente")
        
        # Extraer dispositivos conectados
        dispositivos_conectados = extraer_dispositivos_conectados(data)
        
        print(f"\n📱 Dispositivos conectados encontrados: {len(dispositivos_conectados)}")
        
        if dispositivos_conectados:
            # Guardar en archivo JSON
            if guardar_json(dispositivos_conectados):
                print(f"\n📄 Contenido del archivo:")
                print("-" * 40)
                json_formateado = json.dumps(dispositivos_conectados, indent=2, ensure_ascii=False)
                print(json_formateado)
            else:
                print("\n❌ No se pudo guardar el archivo")
        else:
            print("\n⚠️  No se encontraron dispositivos conectados")
    else:
        print("\n❌ No se pudo establecer la conexión")