import serial
import time

class SerialConnection:
    def __init__(self, port, baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None

    def connect(self):
        try:
            self.connection = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(2)
            print(f"Conexión establecida en el puerto {self.port}")
        except serial.SerialException as e:
            print(f"Error al conectar con el puerto {self.port}: {e}")

    def disconnect(self):
        if self.connection and self.connection.is_open:
            self.connection.close()
            print(f"Conexión cerrada en el puerto {self.port}")

    def send_data(self, data):
        if self.connection and self.connection.is_open:
            self.connection.write(data.encode())
            print(f"Datos enviados: {data}")

    def read_data(self):
        if self.connection and self.connection.is_open:
            return self.connection.readline().decode().strip()
        return None

    def __del__(self):
        self.disconnect()