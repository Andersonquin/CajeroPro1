from flask import Flask, render_template, request, jsonify
from models import CuentaAhorros, CuentaCorriente, TransaccionError, SaldoInsuficienteError, CuentaBloqueadaError #
import sqlite3

app = Flask(__name__)

def obtener_cuenta_db(cuenta_id):
    """Función de soporte para recuperar datos y aplicar Polimorfismo al instanciar."""
    conn = sqlite3.connect('cajero.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cuentas WHERE id=?", (cuenta_id,))
    datos = cursor.fetchone()
    conn.close()

    if datos:
        # Según la columna de 'tipo' en la DB, creamos el objeto correcto
        if datos[2] == 'ahorros':
            return CuentaAhorros(datos[0], datos[1], datos[3], datos[4])
        else:
            # Para cuenta corriente pasamos el sobregiro si existe en la columna 5
            sobregiro = datos[5] if len(datos) > 5 else 500
            return CuentaCorriente(datos[0], datos[1], datos[3], datos[4], sobregiro)
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/operacion', methods=['POST'])
def operacion():
    data = request.json
    try:
        # 1. Buscamos la cuenta en la base de datos
        cuenta = obtener_cuenta_db(data['id'])
        if not cuenta:
            return jsonify({"success": False, "msg": "Cuenta no encontrada en el sistema."})

        # 2. Verificamos identidad (Encapsulamiento de seguridad)
        # Este método puede lanzar CuentaBloqueadaError
        if not cuenta.verificar_identidad(data['pin']):
            return jsonify({"success": False, "msg": "PIN incorrecto."})

        monto = float(data['monto'])
        accion = data['accion']

        if accion == 'retirar':
            # 3. IMPLEMENTACIÓN DE EXCEPCIONES: Intentamos retirar efectivo
            # Si el retiro falla, el modelo lanzará una excepción y saltará al bloque 'except'
            mensaje_exito = cuenta.retirar_efectivo(monto) #
            
            # 4. PERSISTENCIA: Solo si el retiro fue exitoso, actualizamos la DB
            conn = sqlite3.connect('cajero.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE cuentas SET saldo=? WHERE id=?", (cuenta.saldo, data['id']))
            conn.commit()
            conn.close()

            return jsonify({
                "success": True, 
                "msg": mensaje_exito, 
                "nuevo_saldo": cuenta.saldo
            })

    # --- MANEJO PROFESIONAL DE ERRORES ---
    except SaldoInsuficienteError as e:
        return jsonify({"success": False, "msg": str(e)})
    except CuentaBloqueadaError as e:
        return jsonify({"success": False, "msg": str(e)})
    except TransaccionError as e:
        return jsonify({"success": False, "msg": str(e)})
    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({"success": False, "msg": "Error interno del cajero. Intente más tarde."})

    return jsonify({"success": False, "msg": "Acción no reconocida."})

if __name__ == '__main__':
    app.run(debug=True)