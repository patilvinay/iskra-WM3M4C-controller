from wm3m4c import *
import time


billingDataset = {  "FV":"1.0",
                    "GI":"",
                    "GS":"",
                    "PG":"",
                    "MV":"",
                    "MM":"",
                    "MS":"",
                    "MF": "",
                    "IS":True,
                    "IF":[],
                    "IT":"NONE",
                    "ID":"1",
                    "CT":"EVSEID48864864864",
                    "CI":"",
                    "RD":[]}

meter = WM3M4C(33)
meter.connect("/dev/ttyUSB0")
meter.set_time(time.time())
meter.set_signing_profile()
meter.set_billing_dataset(billingDataset)
print("measurement status: ", translate_measurement_status(meter.get_measurement_status()))
meter.start_measurement()
print("measurement status: ", translate_measurement_status(meter.get_measurement_status()))
time.sleep(10)
meter.stop_measurement()
print("measurement status: ", translate_measurement_status(meter.get_measurement_status()))
time.sleep(1.5)
print("billing data: ", meter.get_output_billing_dataset())
print("signature status: ", meter.get_signature_status())
print("signature: ", meter.get_signature())
print("public key: ", meter.get_public_key())
