from abc import ABC, abstractmethod

class Cuenta(ABC):
    def __init__(self, id_cuenta, titular, saldo, pin):
        self._id = id_cuenta
        self._titular = titular
        self.__saldo = saldo
        self.__pin = pin

    @property
    def saldo(self):
        return self.__saldo

    @saldo.setter
    def saldo(self, monto):
        if monto >= 0:
            self.__saldo = monto

    def validar_pin(self, pin_ingresado):
        return self.__pin == pin_ingresado

    @abstractmethod
    def retirar(self, monto):
        pass

class CuentaAhorros(Cuenta):
    def retirar(self, monto):
        if monto <= 0:
            return False, "Error: El monto debe ser positivo."
        if monto <= self.saldo:
            self.saldo -= monto
            return True, "Retiro exitoso de ahorros."
        return False, "Saldo insuficiente."

class CuentaCorriente(Cuenta):
    def __init__(self, id_cuenta, titular, saldo, pin, sobregiro=500):
        super().__init__(id_cuenta, titular, saldo, pin)
        self.sobregiro = sobregiro

    def retirar(self, monto):
        if monto <= 0:
            return False, "Error: El monto debe ser positivo."
        if monto <= (self.saldo + self.sobregiro):
            self.saldo -= monto
            return True, "Retiro exitoso con sobregiro."
        return False, "Límite de sobregiro excedido."