from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from models import CuentaAhorros, CuentaCorriente, TransaccionError, SaldoInsuficienteError, CuentaBloqueadaError 
from database import obtener_conexion, registrar_movimiento, obtener_historial 

app = Flask(__name__)

# --- CONFIGURACIÓN DE SEGURIDAD ---
# Clave para firmar las cookies de sesión (imprescindible para el login)
app.secret_key = 'cajero_pro_super_secret_key_2026'

def obtener_cuenta_db(cuenta_id):
    """
    Busca en la DB y retorna un objeto de la clase CuentaAhorros o CuentaCorriente.
    Aplica Polimorfismo.
    """
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cuentas WHERE id=?", (cuenta_id,))
    datos = cursor.fetchone()
    conn.close()

    if datos:
        # Los datos del PIN vienen de la DB como un Hash (Paso 4.2)
        tipo = datos['tipo_cuenta']
        if tipo == 'ahorros':
            return CuentaAhorros(datos['id'], datos['titular'], datos['saldo'], datos['pin'])
        else:
            return CuentaCorriente(datos['id'], datos['titular'], datos['saldo'], datos['pin'], datos['sobregiro'])
    return None

@app.route('/')
def index():
    return render_template('index.html')

# --- RUTA DE LOGIN (Punto de entrada) ---
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    cuenta_id = data.get('id')
    pin_plano = data.get('pin') # El PIN que viene del formulario (texto plano)
    
    cuenta = obtener_cuenta_db(cuenta_id)
    
    # El modelo se encarga de comparar el pin_plano con el hash de la DB
    if cuenta and cuenta.verificar_identidad(pin_plano):
        session['user_id'] = cuenta.id
        session['user_name'] = cuenta.titular
        return jsonify({"success": True, "msg": f"Bienvenido, {cuenta.titular}"})
    
    return jsonify({"success": False, "msg": "ID o PIN incorrectos."})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/operacion', methods=['POST'])
def operacion():
    # Seguridad: Bloquea el acceso si no hay sesión activa
    if 'user_id' not in session:
        return jsonify({"success": False, "msg": "Sesión no válida. Inicie sesión."}), 401

    data = request.json
    try:
        # Recuperamos la cuenta del usuario logueado
        cuenta = obtener_cuenta_db(session['user_id'])
        if not cuenta:
            return jsonify({"success": False, "msg": "Error al recuperar cuenta."})

        monto = float(data.get('monto', 0))
        accion = data.get('accion')

        # --- RETIRO ---
        if accion == 'retirar':
            mensaje = cuenta.retirar_efectivo(monto) 
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("UPDATE cuentas SET saldo=? WHERE id=?", (cuenta.saldo, cuenta.id))
            conn.commit()
            conn.close()
            registrar_movimiento(cuenta.id, 'Retiro', monto)
            return jsonify({"success": True, "msg": mensaje, "nuevo_saldo": cuenta.saldo})

        # --- DEPÓSITO ---
        elif accion == 'depositar':
            cuenta.saldo += monto
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("UPDATE cuentas SET saldo=? WHERE id=?", (cuenta.saldo, cuenta.id))
            conn.commit()
            conn.close()
            registrar_movimiento(cuenta.id, 'Depósito', monto)
            return jsonify({"success": True, "msg": "Dinero ingresado correctamente.", "nuevo_saldo": cuenta.saldo})

        # --- TRANSFERENCIA (Atómica) ---
        elif accion == 'transferir':
            id_dest = data.get('id_destino')
            if not id_dest or int(id_dest) == cuenta.id:
                return jsonify({"success": False, "msg": "Destino no válido."})

            cuenta_destino = obtener_cuenta_db(id_dest)
            if not cuenta_destino:
                return jsonify({"success": False, "msg": "La cuenta destino no existe."})

            # Lógica en objetos
            cuenta.retirar_efectivo(monto)
            cuenta_destino.saldo += monto

            # Persistencia en DB
            conn = obtener_conexion()
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE cuentas SET saldo=? WHERE id=?", (cuenta.saldo, cuenta.id))
                cursor.execute("UPDATE cuentas SET saldo=? WHERE id=?", (cuenta_destino.saldo, id_dest))
                conn.commit()
                registrar_movimiento(cuenta.id, f'Transferencia a {cuenta_destino.titular}', monto)
                registrar_movimiento(id_dest, f'Transferencia de {cuenta.titular}', monto)
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
            return jsonify({"success": True, "msg": "Transferencia exitosa.", "nuevo_saldo": cuenta.saldo})

    except SaldoInsuficienteError as e:
        return jsonify({"success": False, "msg": str(e)})
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        return jsonify({"success": False, "msg": "Operación fallida en el servidor."})

@app.route('/historial', methods=['GET'])
def ver_historial():
    if 'user_id' not in session:
        return jsonify({"success": False, "msg": "No autorizado."}), 401
        
    try:
        movimientos = obtener_historial(session['user_id'])
        # Formateamos para el frontend
        lista = [{"tipo": m['tipo_operacion'], "monto": m['monto'], "fecha": m['fecha']} for m in movimientos]
        return jsonify({"success": True, "historial": lista})
    except Exception as e:
        return jsonify({"success": False, "msg": "No se pudo cargar el historial."})

if __name__ == '__main__':
    app.run(debug=True)