####################
###   OFFSETTS   ###
####################
HOLDING_REGISTER_OFFSET = 40000

#####################
###   REGISTERS   ###
#####################

# TIME
ADDRESS_TIME_HIGH_16 = 47054 - HOLDING_REGISTER_OFFSET
ADDRESS_TIME_LOW_16 = 47055 - HOLDING_REGISTER_OFFSET
ADDRESS_TIME_STATUS = 47071 - HOLDING_REGISTER_OFFSET
ADDRESS_TIME_STATUS_TIMEOUT = 47072 - HOLDING_REGISTER_OFFSET
ADDRESS_TIME_TIMEZONE = 47053 - HOLDING_REGISTER_OFFSET
ADDRESS_TIME_PRESENTATION = 47073 - HOLDING_REGISTER_OFFSET
# SIGNATURE
ADDRESS_SIGNATURE_FORMAT = 47059 - HOLDING_REGISTER_OFFSET
ADDRESS_SIGNATURE_ALGORITHM = 47060 - HOLDING_REGISTER_OFFSET
ADDRESS_SIGNATURE_STATUS_REGISTER = 47052 - HOLDING_REGISTER_OFFSET
ADDRESS_SIGNATURE_OUTPUT = 48188 - HOLDING_REGISTER_OFFSET
ADDRESS_SIGNATURE_OUTPUT_LENGTH = 47058 - HOLDING_REGISTER_OFFSET
ADDRESS_SIGNATURE_PUBLIC_KEY = 48124 - HOLDING_REGISTER_OFFSET
# BILLING
ADDRESS_BILLING_DATASET = 47100 - HOLDING_REGISTER_OFFSET
ADDRESS_BILLING_DATASET_LENGTH = 47056 - HOLDING_REGISTER_OFFSET
ADDRESS_BILLING_JSON_OUTPUT = 47612 - HOLDING_REGISTER_OFFSET
ADDRESS_BILLING_JSON_OUTPUT_LENGTH = 47057 - HOLDING_REGISTER_OFFSET
ADDRESS_BILLING_BINARY_OUTPUT = 48317 - HOLDING_REGISTER_OFFSET
ADDRESS_BILLING_BINARY_OUTPUT_LENGTH = 48316 - HOLDING_REGISTER_OFFSET
# TRANSACTION
ADDRESS_TRANSACTION_COMMAND = 47051 - HOLDING_REGISTER_OFFSET

###############################
###   VALUES AND COMMANDS   ###
###############################

# TRANSACTION LIMITS
MAX_TRANSACTION_BYTES = 240
MAX_TRANSACTION_REGISTERS = 120
# SIGNATURE FORMATS
SIGNATURE_FORMAT_HEX = 0
SIGNATURE_FORMAT_BASE64 = 1
# SIGNATURE ALGORITHMS
SIGNATURE_ALGORITHM_NO_SIGNATURE = 0
SIGNATURE_ALGORITHM_ECDSA = 4
# CLOCK SYNC STATUS VALUES
CLOCK_SYNC_NOT_SYNC = 0
CLOCK_SYNC_INFORMATIVE = 1
CLOCK_SYNC_SYNCHRONIZED = 2
CLOCK_SYNC_RELATIVE = 3
# TIME PRESENTATION SETTINGS
TIME_PRESENTSTION_LOCAL_TIME = 0
TIME_PRESENTATION_UTC = 1
# TRANSACTION COMMANDS
COMMAND_BEGIN_MEASUREMENT = 0x42 << 8 & 0xffff
COMMAND_END_MEASUREMENT = 0x45 << 8 & 0xffff
COMMAND_INTERMEDIATE_READING = 0x43 << 8 & 0xffff
COMMAND_EXCEPTION = 0x58 << 8 & 0xffff
COMMAND_TARIFF_CHANGE = 0x54 << 8 & 0xffff
COMMAND_SUSPENDED_COMMAND = 0x53 << 8 & 0xffff
COMMAND_END_MEASUREMENT_WITH_BEGIN = 0x72 << 8 & 0xffff
COMMAND_FISCAL_READING = 0x66 << 8 & 0xffff
COMMAND_HOLD = 0x68 << 8 & 0xffff
# MEASUREMENT REGISTERS
ADDRESS_MEASUREMENT_STATUS = 47000 - HOLDING_REGISTER_OFFSET
# MAPS
MEASUREMENT_STATUS_MAP = {0: "Idle",
                          1: "Active",
                          2: "Active after power failure",
                          3: "Active after reset"}
SIGNATURE_STATUS_MAP = {0: "Not initialised",
                        1: "Idle",
                        2: "Signature in progress",
                        15: "Signature OK",
                        128: "Invalid date time",
                        129: "CheckSum error",
                        130: "Invalid command",
                        131: "Invalid state",
                        132: "Invalid state",
                        133: "Test mode error",
                        243: "Verify state error",
                        244: "Signature state error",
                        245: "Keypair generation Error",
                        246: "SHA failed",
                        247: "Init failed",
                        248: "Data not locked",
                        249: "Config not locked",
                        250: "Verify error",
                        251: "Public key error",
                        252: "Invalid message format",
                        253: "Invalid message size",
                        254: "Signature error",
                        255: "Undefined error"}
