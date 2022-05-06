

import minimalmodbus
import serial

class Renogy:
    def __init__(self, port, baud=9600, addr=1):
        self.modbus = minimalmodbus.Instrument(port, addr)
        self.modbus.serial.baudrate = baud
        self.modbus.serial.bytesize = 8
        self.modbus.serial.parity = serial.PARITY_NONE
        self.modbus.serial.stopbits = 1
        self.modbus.serial.timeout = 2


    def read_register(self, reg):
        return self.modbus.read_register(reg)


    def read(self):
        self.batt_soc = self.read_register(0x100)
        self.batt_volts = self.read_register(0x101) / 10
        self.charge_amps = self.read_register(0x102) / 100
        self.controller_temp = self.read_register(0x103)
        self.load_watts = self.read_register(0x106)
        self.pv_volts = self.read_register(0x107) / 10
        self.pv_amps = self.read_register(0x108) / 100
        self.pv_watts = self.read_register(0x109)

