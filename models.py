from abc import ABC, abstractmethod

class Cuenta(ABC):
    def __init__(self, id_cuenta, titular, saldo, pin):
        self._id = id_cuenta
        self._titular = titular
        self.__saldo = saldo
        self.__pin = pin
        self.__intentos = 0      # Nuevo: Contador de fallos
        self.__bloqueada = False # Nuevo: Estado de la cuenta

    @property
    def saldo(self):
        return self.__saldo

    @saldo.setter
    def saldo(self, monto):
        if monto >= 0:
            self.__saldo = monto

    def validar_pin(self, pin_ingresado):
        # Si ya está bloqueada, ni siquiera revisamos el PIN
        if self.__bloqueada:
            return False, "CUENTA BLOQUEADA. Contacte al banco."
        
        if self.__pin == pin_ingresado:
            self.__intentos = 0 # Reiniciamos si acierta
            return True, "Acceso concedido."
        else:
            self.__intentos += 1
            if self.__intentos >= 3:
                self.__bloqueada = True
                return False, "PIN Incorrecto. CUENTA BLOQUEADA."
            return False, f"PIN Incorrecto. Intento {self.__intentos} de 3."

    @abstractmethod
    def retirar(self, monto):
        pass

class CuentaAhorros(Cuenta):
    def retirar(self, monto):
        if monto <= 0:
            return False, "Monto inválido. Debe ser mayor a cero."
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
            return False, "Monto inválido."
        if monto <= (self.saldo + self.sobregiro):
            self.saldo -= monto
            return True, "Retiro exitoso (usó sobregiro)."
        return False, "Excede límite de sobregiro."