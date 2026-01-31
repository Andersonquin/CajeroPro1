import sqlite3
import os
from werkzeug.security import generate_password_hash # <--- Nueva importación

# Nombre de la base de datos centralizado
DB_NAME = 'cajero.db'

def obtener_conexion():
    """Establece una conexión útil para Flask."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row 
    return conn

def inicializar_db(resetear=False):
    """
    Crea la base de datos y las tablas con PINs encriptados.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        if resetear:
            cursor.execute('DROP TABLE IF EXISTS transacciones')
            cursor.execute('DROP TABLE IF EXISTS cuentas')
            print("⚠️ Base de datos reseteada por completo.")

        # 1. Tabla de Cuentas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cuentas (
                id INTEGER PRIMARY KEY,
                titular TEXT NOT NULL,
                tipo_cuenta TEXT NOT NULL,
                saldo REAL NOT NULL,
                pin TEXT NOT NULL, -- Aquí guardaremos el HASH, no el número
                sobregiro REAL DEFAULT 0
            )
        ''')

        # 2. Tabla de Transacciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transacciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cuenta_id INTEGER NOT NULL,
                tipo_operacion TEXT NOT NULL,
                monto REAL NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cuenta_id) REFERENCES cuentas (id)
            )
        ''')

        cursor.execute('SELECT COUNT(*) FROM cuentas')
        if cursor.fetchone()[0] == 0:
            # Lista temporal para procesar los usuarios con hashing
            usuarios_base = [
                (1, 'Admin Juan', 'ahorros', 1500.0, '1234', 0),
                (2, 'Maria Lopez', 'corriente', 200.0, '4321', 1000),
                (3, 'Carlos Ruiz', 'ahorros', 50.0, '0000', 0),
            ]
            
            # Generar automáticos hasta 15
            for i in range(4, 16):
                tipo = 'ahorros' if i % 2 == 0 else 'corriente'
                sobregiro = 500.0 if tipo == 'corriente' else 0.0
                usuarios_base.append((i, f'Usuario {i}', tipo, float(100 * i), '1111', sobregiro))

            # --- LA MAGIA DEL HASHING ---
            # Convertimos cada PIN de texto plano a un Hash seguro antes de insertar
            usuarios_encriptados = []
            for u in usuarios_base:
                u_lista = list(u)
                u_lista[4] = generate_password_hash(u_lista[4]) # Encriptamos el PIN (posición 4)
                usuarios_encriptados.append(tuple(u_lista))

            cursor.executemany('INSERT INTO cuentas VALUES (?,?,?,?,?,?)', usuarios_encriptados)
            conn.commit()
            print(f"✅ Se han creado {len(usuarios_encriptados)} usuarios con PINs encriptados.")
        else:
            print("ℹ️ La base de datos ya contiene datos.")

def registrar_movimiento(cuenta_id, tipo, monto):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transacciones (cuenta_id, tipo_operacion, monto)
                VALUES (?, ?, ?)
            ''', (cuenta_id, tipo, monto))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error registrando movimiento: {e}")
        return False

def obtener_historial(cuenta_id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT tipo_operacion, monto, fecha 
        FROM transacciones 
        WHERE cuenta_id = ? 
        ORDER BY fecha DESC 
        LIMIT 10
    ''', (cuenta_id,))
    movimientos = cursor.fetchall()
    conn.close()
    return movimientos

if __name__ == "__main__":
    # IMPORTANTE: Ejecuta esto para aplicar los cambios de seguridad
    inicializar_db(resetear=True)