# pylint: disable=no-member
import DB

# Crear tabla
DB.crear_tabla()

# Registrar usuario de prueba
DB.registrar_usuario("Juan", "Pepe", "Noveno", "2025-2026", "pepe@example.com", "123")

# Listar usuarios
print(DB.listar_usuarios())
