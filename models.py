from abc import ABC, abstractmethod

class Cuenta(ABC):
    def __init__(self, id_cuenta, titular, saldo, pin):
        self._id = id_cuenta
        self._titular = titular
        self.__saldo = saldo  # ENCAPSULAMIENTO: Atributo privado
        self.__pin = pin      # ENCAPSULAMIENTO: Atributo privado

    # GETTER para el saldo (Control de acceso)
    @property
    def saldo(self):
        return self.__saldo

    # SETTER para el saldo (Validación lógica)
    @saldo.setter
    def saldo(self, monto):
        if monto >= 0:
            self.__saldo = monto

    def validar_pin(self, pin_ingresado):
        return self.__pin == pin_ingresado

    @abstractmethod
    def retirar(self, monto):
        """Método que será polimórfico en las subclases"""
        pass

# HERENCIA: CuentaAhorros extiende de Cuenta
class CuentaAhorros(Cuenta):
    def retirar(self, monto):
        # POLIMORFISMO: Lógica específica para ahorros
        if monto <= self.saldo:
            self.saldo -= monto
            return True, "Retiro exitoso de cuenta de ahorros."
        return False, "Saldo insuficiente."

# HERENCIA: CuentaCorriente extiende de Cuenta
class CuentaCorriente(Cuenta):
    def __init__(self, id_cuenta, titular, saldo, pin, sobregiro=500):
        super().__init__(id_cuenta, titular, saldo, pin)
        self.sobregiro = sobregiro

    def retirar(self, monto):
        # POLIMORFISMO: Esta cuenta permite quedar en negativo hasta el límite de sobregiro
        if monto <= (self.saldo + self.sobregiro):
            self.saldo -= monto
            return True, "Retiro exitoso usando sobregiro."
        return False, "Excede el límite de sobregiro permitido."