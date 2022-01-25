from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.payload import BinaryPayloadDecoder
import json
import math
from wm3m4c_constants import *


class WM3M4C:
    def __init__(self, device_id=33):
        self.client = None
        self.deviceId = device_id

    def connect(self, port, baud=115200):
        self.client = ModbusClient(
            method='rtu',
            port=port,
            stopbits=1,
            bytesize=8,
            parity='N',
            timeout=1,
            baudrate=baud)
        self.client.connect()

    def set_time(self, timestamp):
        # write unix timestamp
        ct = hex(round(timestamp))[2:]
        self.client.write_register(ADDRESS_TIME_HIGH_16, int(ct[:4],16), unit=self.deviceId)
        self.client.write_register(ADDRESS_TIME_LOW_16, int(ct[4:],16), unit=self.deviceId)
        # set time status to synchronised
        self.client.write_register(ADDRESS_TIME_STATUS, CLOCK_SYNC_SYNCHRONIZED, unit=self.deviceId)
        # set time status timeout to one day (1440 minutes)
        self.client.write_register(ADDRESS_TIME_STATUS_TIMEOUT, 1440, unit=self.deviceId)
        # set timezone (offset from UTC in minutes)
        self.client.write_register(ADDRESS_TIME_TIMEZONE, 60, unit=self.deviceId)
        # set all time representations to local time
        self.client.write_register(ADDRESS_TIME_PRESENTATION, TIME_PRESENTSTION_LOCAL_TIME, unit=self.deviceId)

    def set_signing_profile(self):
        # set signature format to base64
        self.client.write_register(ADDRESS_SIGNATURE_FORMAT, SIGNATURE_FORMAT_BASE64, unit=self.deviceId)
        # set signature algorithm to CDSA-secp256r1-SHA256
        self.client.write_register(ADDRESS_SIGNATURE_ALGORITHM, SIGNATURE_ALGORITHM_ECDSA, unit=self.deviceId)

    def set_billing_dataset(self, dataset):
        data = json.dumps(dataset).replace(" ", "")
        data_length = len(data.encode("utf-8"))
        builder = BinaryPayloadBuilder()
        builder.add_string(data)
        payload = builder.to_registers()
        if len(payload) <= 120:
            self.client.write_registers(ADDRESS_BILLING_DATASET, payload, unit=self.deviceId)
        elif len(payload) <= 240:
            self.client.write_registers(ADDRESS_BILLING_DATASET, payload[:120], unit=self.deviceId)
            self.client.write_registers(ADDRESS_BILLING_DATASET + 120, payload[120:], unit=self.deviceId)
        else:
            print("dataset too long")
            #TODO: implement with for loop, max len in actualy 1024 bytes
        # write billing dataset length
        self.client.write_register(ADDRESS_BILLING_DATASET_LENGTH, data_length, unit=self.deviceId)

    def get_measurement_status(self):
        result = self.client.read_holding_registers(ADDRESS_MEASUREMENT_STATUS, 1, unit=self.deviceId)
        return result.registers[0]

    def get_signature_status(self):
        result = self.client.read_holding_registers(ADDRESS_SIGNATURE_STATUS_REGISTER, 1, unit=self.deviceId)
        return result.registers[0]

    def start_measurement(self):
        # measurement can be started only if idle
        if self.get_measurement_status() == 0:
            self.client.write_register(ADDRESS_TRANSACTION_COMMAND, COMMAND_BEGIN_MEASUREMENT, unit=self.deviceId)

    def stop_measurement(self):
        # measurement can be started only if idle
        if self.get_measurement_status() > 0:
            self.client.write_register(ADDRESS_TRANSACTION_COMMAND, COMMAND_END_MEASUREMENT, unit=self.deviceId)

    def get_output_billing_dataset(self, format='json'):
        data_length_register, data_register = None, None

        if format == "json":
            data_register = ADDRESS_BILLING_JSON_OUTPUT
            data_length_register = ADDRESS_BILLING_JSON_OUTPUT_LENGTH
        elif format == "binary":
            data_register = ADDRESS_BILLING_BINARY_OUTPUT
            data_length_register = ADDRESS_BILLING_BINARY_OUTPUT_LENGTH
        else:
            raise ValueError("Unsupported file type")

        result = self.client.read_holding_registers(data_length_register, 1, unit=self.deviceId)
        dataset_length_bytes = result.registers[0]
        dataset_length_registers = math.ceil(dataset_length_bytes / 2)
        registers = []

        for i in range(0,dataset_length_registers,MAX_TRANSACTION_REGISTERS):
            if i + MAX_TRANSACTION_REGISTERS < dataset_length_registers:
                registers += self.client.read_holding_registers(data_register + i, MAX_TRANSACTION_REGISTERS, unit=self.deviceId).registers
            else:
                registers += self.client.read_holding_registers(data_register + i, dataset_length_registers - i, unit=self.deviceId).registers

            decoder = BinaryPayloadDecoder.fromRegisters(registers)
            return decoder.decode_string(dataset_length_bytes)

    def get_signature(self):
        status = self.get_signature_status()
        if status == 15:
            result = self.client.read_holding_registers(ADDRESS_SIGNATURE_OUTPUT_LENGTH, 1, unit=self.deviceId)
            signature_length_bytes = result.registers[0]
            signature_length_registers = math.ceil(signature_length_bytes / 2)
            registers = self.client.read_holding_registers(ADDRESS_SIGNATURE_OUTPUT, signature_length_registers, unit=self.deviceId).registers
            decoder = BinaryPayloadDecoder.fromRegisters(registers)
            return decoder.decode_string(signature_length_bytes)
        else:
            raise Exception('Signature status must be "Signature OK", current status is: "{}"'.format(SIGNATURE_STATUS_MAP[status]))

    def get_public_key(self):
        result = self.client.read_holding_registers(ADDRESS_SIGNATURE_PUBLIC_KEY, 32, unit=self.deviceId)
        decoder = BinaryPayloadDecoder.fromRegisters(result.registers)
        return decoder.decode_string(64)



