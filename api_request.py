import requests
import os
import json
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

def get_devices():
    """
    Función para obtener la lista de dispositivos desde la API de UI.com
    """
    url = "https://api.ui.com/v1/devices"
    
    # Obtener la API key desde las variables de entorno
    api_key = os.getenv('UI_API_KEY')
    
    if not api_key:
        print("Error: No se encontró la API key en las variables de entorno")
        print("Asegúrate de tener un archivo .env con UI_API_KEY configurado")
        return None
    
    headers = {
        'Accept': 'application/json',
        'X-API-Key': api_key
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        # Verificar si la petición fue exitosa
        if response.status_code == 200:
            print("✅ Petición exitosa!")
            print(f"📊 Status Code: {response.status_code}")
            print(f"📋 Headers de respuesta:")
            for key, value in response.headers.items():
                print(f"   {key}: {value}")
            
            print("\n📄 Respuesta formateada:")
            try:
                json_data = response.json()
                print(json.dumps(json_data, indent=2, ensure_ascii=False))
                return json_data
            except json.JSONDecodeError:
                print("⚠️  La respuesta no es JSON válido:")
                print(response.text)
                return response.text
        else:
            print(f"❌ Error en la petición. Status Code: {response.status_code}")
            print(f"📄 Respuesta de error:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print(response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error al hacer la petición: {e}")
        return None

def format_device_info(devices):
    """
    Función para formatear la información de los dispositivos mostrando solo name, ip y status
    """
    if not devices:
        return "No hay dispositivos disponibles"
    
    if isinstance(devices, list):
        print(f"\n🔍 Se encontraron {len(devices)} dispositivos:")
        print("=" * 50)
        
        for i, device in enumerate(devices, 1):
            print(f"\n📱 Dispositivo #{i}:")
            print("-" * 25)
            
            # Mostrar solo los campos solicitados
            fields_to_show = ['name', 'ip', 'status']
            
            for field in fields_to_show:
                if field in device:
                    value = device[field]
                    print(f"   {field.capitalize()}: {value}")
                else:
                    print(f"   {field.capitalize()}: No disponible")
                
    else:
        print(f"\n📄 Datos recibidos:")
        print(json.dumps(devices, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    print("🚀 Haciendo petición a la API de UI.com...")
    print("=" * 50)
    
    devices = get_devices()
    
    if devices:
        format_device_info(devices)
    else:
        print("\n❌ No se pudieron obtener los dispositivos")
