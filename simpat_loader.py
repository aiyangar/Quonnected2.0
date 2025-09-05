import json
import os
from typing import List, Dict, Optional

class SimpatUser:
    """
    Clase para representar un usuario de Simpat
    """
    def __init__(self, user_data: Dict):
        self.id = user_data.get('id', '')
        self.name = user_data.get('name', '')
        self.ip_address = user_data.get('ip_address', '')
        self.is_admin = user_data.get('is_admin', False)
    
    def __str__(self):
        admin_status = "👑 Admin" if self.is_admin else "👤 Usuario"
        return f"{self.name} ({self.ip_address}) - {admin_status}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ip_address': self.ip_address,
            'is_admin': self.is_admin
        }

class SimpatLoader:
    """
    Loader para cargar y gestionar usuarios de Simpat desde el archivo JSON
    """
    
    def __init__(self, json_file_path: str = "simpat_users.json"):
        self.json_file_path = json_file_path
        self.users: List[SimpatUser] = []
        self.load_users()
    
    def load_users(self) -> bool:
        """
        Carga los usuarios desde el archivo JSON
        """
        try:
            if not os.path.exists(self.json_file_path):
                print(f"❌ Error: No se encontró el archivo {self.json_file_path}")
                return False
            
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                users_data = json.load(file)
            
            self.users = [SimpatUser(user_data) for user_data in users_data]
            print(f"✅ Se cargaron {len(self.users)} usuarios desde {self.json_file_path}")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Error al decodificar JSON: {e}")
            return False
        except Exception as e:
            print(f"❌ Error al cargar usuarios: {e}")
            return False
    
    def get_all_users(self) -> List[SimpatUser]:
        """
        Retorna todos los usuarios cargados
        """
        return self.users
    
    def get_user_by_id(self, user_id: str) -> Optional[SimpatUser]:
        """
        Busca un usuario por su ID
        """
        for user in self.users:
            if user.id == user_id:
                return user
        return None
    
    def get_user_by_ip(self, ip_address: str) -> Optional[SimpatUser]:
        """
        Busca un usuario por su dirección IP
        """
        for user in self.users:
            if user.ip_address == ip_address:
                return user
        return None
    
    def get_user_by_name(self, name: str) -> Optional[SimpatUser]:
        """
        Busca un usuario por su nombre (búsqueda exacta)
        """
        for user in self.users:
            if user.name.lower() == name.lower():
                return user
        return None
    
    def search_users_by_name(self, search_term: str) -> List[SimpatUser]:
        """
        Busca usuarios por nombre (búsqueda parcial, case-insensitive)
        """
        search_term = search_term.lower()
        return [user for user in self.users if search_term in user.name.lower()]
    
    def get_admin_users(self) -> List[SimpatUser]:
        """
        Retorna solo los usuarios administradores
        """
        return [user for user in self.users if user.is_admin]
    
    def get_regular_users(self) -> List[SimpatUser]:
        """
        Retorna solo los usuarios regulares (no administradores)
        """
        return [user for user in self.users if not user.is_admin]
    
    def get_users_by_ip_range(self, ip_prefix: str) -> List[SimpatUser]:
        """
        Busca usuarios por rango de IP (ej: "10.0.0" para 10.0.0.x)
        """
        return [user for user in self.users if user.ip_address.startswith(ip_prefix)]
    
    def print_users_summary(self):
        """
        Imprime un resumen de los usuarios cargados
        """
        if not self.users:
            print("❌ No hay usuarios cargados")
            return
        
        admin_count = len(self.get_admin_users())
        regular_count = len(self.get_regular_users())
        
        print(f"\n📊 Resumen de usuarios Simpat:")
        print("=" * 40)
        print(f"👥 Total de usuarios: {len(self.users)}")
        print(f"👑 Administradores: {admin_count}")
        print(f"👤 Usuarios regulares: {regular_count}")
    
    def print_all_users(self, show_admin_only: bool = False):
        """
        Imprime todos los usuarios o solo los administradores
        """
        users_to_show = self.get_admin_users() if show_admin_only else self.users
        
        if not users_to_show:
            print("❌ No hay usuarios para mostrar")
            return
        
        title = "👑 Administradores" if show_admin_only else "👥 Todos los usuarios"
        print(f"\n{title}:")
        print("=" * 50)
        
        for i, user in enumerate(users_to_show, 1):
            admin_icon = "👑" if user.is_admin else "👤"
            print(f"{i:2d}. {admin_icon} {user.name}")
            print(f"     ID: {user.id} | IP: {user.ip_address}")
            print()

def main():
    """
    Función principal para probar el loader
    """
    print("🚀 Cargando usuarios de Simpat...")
    
    # Crear instancia del loader
    loader = SimpatLoader()
    
    # Mostrar resumen
    loader.print_users_summary()
    
    # Mostrar todos los usuarios
    loader.print_all_users()
    
    # Ejemplos de búsquedas
    print("\n🔍 Ejemplos de búsquedas:")
    print("-" * 30)
    
    # Buscar por nombre parcial
    search_results = loader.search_users_by_name("Paola")
    print(f"Búsqueda 'Paola': {len(search_results)} resultados")
    for user in search_results:
        print(f"  - {user}")
    
    # Buscar por IP específica
    user_by_ip = loader.get_user_by_ip("10.0.0.2")
    if user_by_ip:
        print(f"\nUsuario con IP 10.0.0.2: {user_by_ip}")
    
    # Mostrar solo administradores
    print(f"\n👑 Solo administradores:")
    loader.print_all_users(show_admin_only=True)

if __name__ == "__main__":
    main()
