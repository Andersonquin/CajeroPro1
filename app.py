from flask import Flask, render_template, request, jsonify
from models import CuentaAhorros, CuentaCorriente
import sqlite3

app = Flask(__name__)

def obtener_cuenta_db(cuenta_id):
    conn = sqlite3.connect('cajero.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cuentas WHERE id=?", (cuenta_id,))
    datos = cursor.fetchone()
    conn.close()
    
    if datos:
        if datos[2] == 'ahorros':
            return CuentaAhorros(datos[0], datos[1], datos[3], datos[4])
        else:
            return CuentaCorriente(datos[0], datos[1], datos[3], datos[4], datos[5])
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/operacion', methods=['POST'])
def operacion():
    data = request.json
    cuenta = obtener_cuenta_db(data['id'])
    
    if not cuenta or not cuenta.validar_pin(data['pin']):
        return jsonify({"success": False, "msg": "Credenciales inválidas"})

    monto = float(data['monto'])
    accion = data['accion']

    if accion == 'retirar':
        success, msg = cuenta.retirar(monto)
        if success:
            conn = sqlite3.connect('cajero.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE cuentas SET saldo=? WHERE id=?", (cuenta.saldo, data['id']))
            conn.commit()
            conn.close()
        return jsonify({"success": success, "msg": msg, "nuevo_saldo": cuenta.saldo})

    return jsonify({"success": False, "msg": "Acción no reconocida"})

if __name__ == '__main__':
    app.run(debug=True)