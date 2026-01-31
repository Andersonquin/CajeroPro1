from abc import ABC, abstractmethod
from werkzeug.security import check_password_hash # <--- IMPORTANTE: Nueva herramienta

# --- 2. MANEJO DE EXCEPCIONES PERSONALIZADAS ---
class TransaccionError(Exception):
    """Clase base para errores del cajero."""
    pass

class SaldoInsuficienteError(TransaccionError):
    """Se lanza cuando el monto solicitado excede el disponible."""
    pass

class CuentaBloqueadaError(TransaccionError):
    """Se lanza cuando se intenta operar una cuenta restringida."""
    pass

# --- 1. USO DE INTERFACES (CONTRATO) ---
class IServiciosBancarios(ABC):
    @abstractmethod
    def retirar_efectivo(self, monto: float):
        pass

    @abstractmethod
    def consultar_disponibilidad(self):
        pass

# --- IMPLEMENTACIÓN ---
class Cuenta(IServiciosBancarios, ABC):
    def __init__(self, id_cuenta, titular, saldo_inicial, pin_seguridad):
        self.id = id_cuenta # Lo dejamos público para facilitar el acceso en app.py
        self.titular = titular
        self.__saldo_actual = saldo_inicial
        self.__pin_autorizado = pin_seguridad # Este ahora recibe un HASH
        self.__intentos_fallidos = 0
        self.__esta_bloqueada = False

    @property
    def saldo(self):
        return self.__saldo_actual

    @saldo.setter
    def saldo(self, valor):
        """Permite actualizar el saldo desde fuera (ej: depósitos)"""
        if valor < -5000: # Un límite de seguridad genérico
             raise TransaccionError("Saldo fuera de límites permitidos.")
        self.__saldo_actual = valor

    # --- CAMBIO CLAVE PASO 4.3 ---
    def verificar_identidad(self, pin_ingresado):
        if self.__esta_bloqueada:
            raise CuentaBloqueadaError("La cuenta se encuentra bloqueada por seguridad.")
        
        # check_password_hash hace la magia: 
        # toma el hash de la DB y el pin plano, y verifica si coinciden
        if check_password_hash(self.__pin_autorizado, str(pin_ingresado)):
            self.__intentos_fallidos = 0
            return True
        else:
            self.__intentos_fallidos += 1
            if self.__intentos_fallidos >= 3:
                self.__esta_bloqueada = True
            return False

    def _actualizar_balance(self, nuevo_monto):
        self.__saldo_actual = nuevo_monto

    def consultar_disponibilidad(self):
        return self.__saldo_actual

class CuentaAhorros(Cuenta):
    def retirar_efectivo(self, monto: float):
        COMISION_RETIRO = 2.0
        costo_total = monto + COMISION_RETIRO
        
        if monto <= 0:
            raise TransaccionError("El monto a retirar debe ser positivo.")
        
        if costo_total > self.consultar_disponibilidad():
            raise SaldoInsuficienteError(f"Fondos insuficientes. Requiere ${costo_total}.")
            
        self._actualizar_balance(self.consultar_disponibilidad() - costo_total)
        return f"Retiro exitoso. Comisión: ${COMISION_RETIRO}."

class CuentaCorriente(Cuenta):
    def __init__(self, id_cuenta, titular, saldo, pin, limite_sobregiro=500):
        super().__init__(id_cuenta, titular, saldo, pin)
        self.limite_sobregiro = limite_sobregiro

    def retirar_efectivo(self, monto: float):
        if monto <= 0:
            raise TransaccionError("Monto de retiro no válido.")
        
        disponible_total = self.consultar_disponibilidad() + self.limite_sobregiro
        
        if monto > disponible_total:
            raise SaldoInsuficienteError("Excede el límite de sobregiro.")
        
        self._actualizar_balance(self.consultar_disponibilidad() - monto)
        return "Retiro procesado con sobregiro."