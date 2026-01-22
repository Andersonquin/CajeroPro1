import sqlite3

def inicializar_db():
    conn = sqlite3.connect('cajero.db')
    cursor = conn.cursor()
    
    # Borrar si existe para empezar limpio
    cursor.execute('DROP TABLE IF EXISTS cuentas')
    
    cursor.execute('''
        CREATE TABLE cuentas (
            id INTEGER PRIMARY KEY,
            titular TEXT NOT NULL,
            tipo_cuenta TEXT NOT NULL,
            saldo REAL NOT NULL,
            pin TEXT NOT NULL,
            sobregiro REAL DEFAULT 0
        )
    ''')

    # Insertamos 15 usuarios variados
    usuarios = [
        (1, 'Admin Juan', 'ahorros', 1500.0, '1234', 0),
        (2, 'Maria Lopez', 'corriente', 200.0, '4321', 1000),
        (3, 'Carlos Ruiz', 'ahorros', 50.0, '0000', 0),
        # ... (añade 12 más con diferentes saldos y tipos)
    ]
    
    # Generar algunos automáticos para completar 15
    for i in range(4, 16):
        tipo = 'ahorros' if i % 2 == 0 else 'corriente'
        usuarios.append((i, f'Usuario {i}', tipo, 100.0 * i, '1111', 500 if tipo == 'corriente' else 0))

    cursor.executemany('INSERT INTO cuentas VALUES (?,?,?,?,?,?)', usuarios)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    inicializar_db()
    print("Base de datos creada con 15 usuarios.")