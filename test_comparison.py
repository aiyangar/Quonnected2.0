#!/usr/bin/env python3
"""
Script de prueba para verificar la comparación entre dispositivos y usuarios Simpat
"""

from simpat_loader import SimpatLoader

def test_comparison():
    """
    Prueba la comparación con datos simulados
    """
    print("🧪 Prueba de comparación de dispositivos con usuarios Simpat")
    print("=" * 60)
    
    # Cargar usuarios de Simpat
    print("\n📂 Cargando usuarios de Simpat...")
    simpat_loader = SimpatLoader()
    simpat_loader.print_users_summary()
    
    # Datos de prueba que coinciden con usuarios Simpat
    test_devices = [
        {"name": "Dispositivo Test 1", "ip": "10.0.0.2", "status": "online"},  # Simpat Gustavo Cárdenas
        {"name": "Dispositivo Test 2", "ip": "10.0.0.3", "status": "offline"}, # Simpat Gilberto Campos
        {"name": "Dispositivo Test 3", "ip": "10.0.0.4", "status": "online"},  # Simpat Carlos Retes
        {"name": "Dispositivo Test 4", "ip": "10.0.0.5", "status": "online"},  # Simpat JC
        {"name": "Dispositivo Test 5", "ip": "10.0.0.6", "status": "online"},  # Simpat Paola Sánchez
        {"name": "Dispositivo Test 6", "ip": "192.168.1.100", "status": "online"}, # No existe en Simpat
    ]
    
    print(f"\n📋 Dispositivos de prueba ({len(test_devices)}):")
    for device in test_devices:
        print(f"   📱 {device['name']} - {device['ip']} ({device['status']})")
    
    # Comparar dispositivos con usuarios Simpat
    print(f"\n🔍 Comparando IPs de dispositivos con usuarios Simpat (solo ONLINE):")
    print("=" * 65)
    
    online_matches = []
    
    for device in test_devices:
        device_ip = device.get('ip', '')
        device_status = device.get('status', '').lower()
        
        # Solo procesar dispositivos con status "online"
        if device_status == 'online':
            # Buscar usuario por IP
            simpat_user = simpat_loader.get_user_by_ip(device_ip)
            
            if simpat_user:
                online_matches.append({
                    'device': device,
                    'user': simpat_user
                })
    
    # Mostrar solo usuarios online que coinciden
    if online_matches:
        print(f"\n✅ Usuarios Simpat ONLINE ({len(online_matches)}):")
        print("-" * 40)
        for match in online_matches:
            user = match['user']
            device_ip = match['device'].get('ip', 'Sin IP')
            admin_icon = "👑" if user.is_admin else "👤"
            print(f"{admin_icon} {user.name} - {device_ip}")
    else:
        print("\n❌ No se encontraron usuarios Simpat con dispositivos ONLINE")
    
    # Mostrar resumen
    total_online_devices = len([d for d in test_devices if d.get('status', '').lower() == 'online'])
    print(f"\n📊 Resumen:")
    print(f"   Dispositivos ONLINE totales: {total_online_devices}")
    print(f"   Usuarios Simpat ONLINE: {len(online_matches)}")
    print(f"   Dispositivos sin usuario Simpat: {total_online_devices - len(online_matches)}")
    
    # Mostrar algunos usuarios de Simpat para referencia
    print(f"\n👥 Algunos usuarios de Simpat disponibles:")
    print("-" * 40)
    for user in simpat_loader.get_all_users()[:5]:  # Mostrar solo los primeros 5
        admin_icon = "👑" if user.is_admin else "👤"
        print(f"{admin_icon} {user.name} - {user.ip_address}")

if __name__ == "__main__":
    test_comparison()
