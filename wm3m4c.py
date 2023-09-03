from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian

import json
import math
from wm3m4c_constants import *


def translate_measurement_status(measurement_status):
    return MEASUREMENT_STATUS_MAP[measurement_status]


def translate_signature_status(signature_status):
    return SIGNATURE_STATUS_MAP[signature_status]


def build_billing_dataset(FV="1.0", GI="", GS="", PG="", MV="", MM="", MS="", MF="", IS=True, IF=[], IT="NONE", ID="1",
                          CT="1", CI="", RD=[]):
    return {"FV": FV,
            "GI": GI,
            "GS": GS,
            "PG": PG,
            "MV": MV,
            "MM": MM,
            "MS": MS,
            "MF": MF,
            "IS": IS,
            "IF": IF,
            "IT": IT,
            "ID": ID,
            "CT": CT,
            "CI": CI,
            "RD": RD}


class WM3M4C:
    def __init__(self, device_id=1):
        self.client = None
        self.deviceId = device_id

    def connect(self, port, baud=115200):
        # self.client = ModbusClient(
        #     method='rtu',
        #     port=port,
        #     stopbits=1,
        #     bytesize=8,
        #     parity='N',
        #     timeout=2,
        #     baudrate=baud)

        self.client = ModbusTcpClient('127.0.0.1', port=5020)

        self.client.connect()

    def set_time(self, timestamp):
        # write unix timestamp
        ct = hex(round(timestamp))[2:]
        self.client.write_register(ADDRESS_TIME_HIGH_16, int(ct[:4], 16), unit=self.deviceId)
        self.client.write_register(ADDRESS_TIME_LOW_16, int(ct[4:], 16), unit=self.deviceId)
        # set time status to synchronised
        self.client.write_register(ADDRESS_TIME_STATUS, CLOCK_SYNC_SYNCHRONIZED, unit=self.deviceId)
        # set time status timeout to one day (1440 minutes)
        self.client.write_register(ADDRESS_TIME_STATUS_TIMEOUT, 1440, unit=self.deviceId)
        # set timezone (offset from UTC in minutes)
        self.client.write_register(ADDRESS_TIME_TIMEZONE, 60, unit=self.deviceId)
        # set all time representations to local time
        self.client.write_register(ADDRESS_TIME_PRESENTATION, TIME_PRESENTSTION_LOCAL_TIME, unit=self.deviceId)

    def set_signing_profile(self, sig_format="hex"):
        if sig_format == "hex":
            signature_format = SIGNATURE_FORMAT_HEX
        elif sig_format == "base64":
            signature_format = SIGNATURE_FORMAT_BASE64
        else:
            raise ValueError("unknow signature format, only hex and base64 are supported")
        # set signature format
        self.client.write_register(ADDRESS_SIGNATURE_FORMAT, signature_format, unit=self.deviceId)
        # set signature algorithm to CDSA-secp256r1-SHA256
        self.client.write_register(ADDRESS_SIGNATURE_ALGORITHM, SIGNATURE_ALGORITHM_ECDSA, unit=self.deviceId)

    def set_billing_dataset(self, dataset):
        data = json.dumps(dataset).replace(" ", "")
        data_length_bytes = len(data.encode("utf-8"))
        data_length_registers = math.ceil(data_length_bytes / 2)
        builder = BinaryPayloadBuilder()
        builder.add_string(data)
        payload = builder.to_registers()
        # write billing dataset in steps by 120 registers in each step
        for i in range(0, data_length_registers, MAX_TRANSACTION_REGISTERS):
            if i + MAX_TRANSACTION_REGISTERS < data_length_registers:
                self.client.write_registers(ADDRESS_BILLING_DATASET + i, payload[i:i + MAX_TRANSACTION_REGISTERS],
                                            unit=self.deviceId)
            else:
                self.client.write_registers(ADDRESS_BILLING_DATASET + i, payload[i:], unit=self.deviceId)

        # write billing dataset length
        self.client.write_register(ADDRESS_BILLING_DATASET_LENGTH, data_length_bytes, unit=self.deviceId)

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
        else:
            raise Exception('Measurement status must not be "Idle"')

    def get_output_billing_dataset(self, output_format='json'):
        if output_format == "json":
            data_register = ADDRESS_BILLING_JSON_OUTPUT
            data_length_register = ADDRESS_BILLING_JSON_OUTPUT_LENGTH
        elif output_format == "binary":
            data_register = ADDRESS_BILLING_BINARY_OUTPUT
            data_length_register = ADDRESS_BILLING_BINARY_OUTPUT_LENGTH
        else:
            raise ValueError("Unsupported file type")

        result = self.client.read_holding_registers(data_length_register, 1, unit=self.deviceId)
        dataset_length_bytes = result.registers[0]
        dataset_length_registers = math.ceil(dataset_length_bytes / 2)
        registers = []

        for i in range(0, dataset_length_registers, MAX_TRANSACTION_REGISTERS):
        # Calculate the number of registers to read in this transaction
            num_registers = min(MAX_TRANSACTION_REGISTERS, dataset_length_registers - i)
            
            # Read the registers and append them to the list
            response = self.client.read_holding_registers(data_register + i, num_registers, unit=self.deviceId)
            if response.isError():
                print("Modbus error:", response)
            else:
                registers += response.registers

        decoder = BinaryPayloadDecoder.fromRegisters(registers)
        return decoder.decode_string(dataset_length_bytes)

    def get_signature(self):
        status = self.get_signature_status()
        if status == 15:
            result = self.client.read_holding_registers(ADDRESS_SIGNATURE_OUTPUT_LENGTH, 1, unit=self.deviceId)
            signature_length_bytes = result.registers[0]
            signature_length_registers = math.ceil(signature_length_bytes / 2)
            registers = self.client.read_holding_registers(ADDRESS_SIGNATURE_OUTPUT, signature_length_registers,
                                                           unit=self.deviceId).registers
            decoder = BinaryPayloadDecoder.fromRegisters(registers)
            return decoder.decode_string(signature_length_bytes)
        else:
            raise Exception(
                'Signature status must be "Signature OK", current status is: "{}"'.format(SIGNATURE_STATUS_MAP[status]))

    def get_public_key(self):
        result = self.client.read_holding_registers(ADDRESS_SIGNATURE_PUBLIC_KEY, 66, unit=self.deviceId)
        decoder = BinaryPayloadDecoder.fromRegisters(result.registers,wordorder=Endian.Big, byteorder=Endian.Big)
        str=decoder.decode_string(66)
        return str
