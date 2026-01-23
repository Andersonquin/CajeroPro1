from abc import ABC, abstractmethod

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
        # 3. TIP DE ORO: Nombres de variables claros y legibles
        self.__id = id_cuenta
        self.__titular = titular
        self.__saldo_actual = saldo_inicial
        self.__pin_autorizado = pin_seguridad
        self.__intentos_fallidos = 0
        self.__esta_bloqueada = False

    @property
    def saldo(self):
        return self.__saldo_actual

    def verificar_identidad(self, pin_ingresado):
        if self.__esta_bloqueada:
            raise CuentaBloqueadaError("La cuenta se encuentra bloqueada por seguridad.")
        
        if str(self.__pin_autorizado) == str(pin_ingresado):
            self.__intentos_fallidos = 0
            return True
        else:
            self.__intentos_fallidos += 1
            if self.__intentos_fallidos >= 3:
                self.__esta_bloqueada = True
            return False

    def _actualizar_balance(self, nuevo_monto):
        """Método protegido para cambios internos de balance."""
        self.__saldo_actual = nuevo_monto

    def consultar_disponibilidad(self):
        return self.__saldo_actual

class CuentaAhorros(Cuenta):
    def retirar_efectivo(self, monto: float):
        COMISION_RETIRO = 2.0
        costo_total = monto + COMISION_RETIRO
        
        if monto <= 0:
            raise TransaccionError("El monto a retirar debe ser positivo.")
        
        # Uso de Excepciones en lugar de simples If/Else para lógica de negocio
        if costo_total > self.consultar_disponibilidad():
            raise SaldoInsuficienteError(f"Fondos insuficientes. Requiere ${costo_total} (monto + comisión).")
            
        self._actualizar_balance(self.consultar_disponibilidad() - costo_total)
        return f"Retiro exitoso. Se aplicó una comisión de ${COMISION_RETIRO}."

class CuentaCorriente(Cuenta):
    def __init__(self, id_cuenta, titular, saldo, pin, limite_sobregiro=500):
        super().__init__(id_cuenta, titular, saldo, pin)
        self.limite_sobregiro = limite_sobregiro

    def retirar_efectivo(self, monto: float):
        if monto <= 0:
            raise TransaccionError("Monto de retiro no válido.")
        
        disponible_total = self.consultar_disponibilidad() + self.limite_sobregiro
        
        if monto > disponible_total:
            raise SaldoInsuficienteError("El monto excede el límite de crédito disponible.")
        
        self._actualizar_balance(self.consultar_disponibilidad() - monto)
        return "Retiro procesado correctamente mediante línea de crédito."