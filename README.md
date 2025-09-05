# API Request - UI.com

Este proyecto contiene un script de Python para hacer peticiones a la API de UI.com.

## Configuración

1. Instala las dependencias:
```bash
pip install -r requirements.txt
```

2. Configura tu API key:
   - Copia el archivo `config.env` y renómbralo a `.env`
   - Reemplaza `<X-API-Key>` con tu API key real de UI.com

3. Ejecuta el script:
```bash
python api_request.py
```

## Archivos

- `api_request.py`: Script principal que hace la petición a la API
- `config.env`: Archivo de configuración con la API key (renombrar a `.env`)
- `requirements.txt`: Dependencias de Python necesarias
- `README.md`: Este archivo de documentación

## Uso

El script `api_request.py` incluye:
- Manejo de errores
- Validación de la API key
- Respuestas detalladas del servidor
- Función reutilizable para obtener dispositivos
