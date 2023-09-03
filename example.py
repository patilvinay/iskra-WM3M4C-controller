from wm3m4c import *
import time
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
import base64
import hashlib

# initialise and connect to meter
meter = WM3M4C(1)
meter.connect(port="COM11", baud=115200)
print("connected to meter")
#  set meter time
meter.set_time(time.time())

# set signing profile
meter.set_signing_profile(sig_format="hex")

# create and upload billing dataset
billing_dataset = build_billing_dataset(CT="controller1",GI="Gateway 1",GS="123456789",FV="1.0")
meter.set_billing_dataset(billing_dataset)

# if meter is idle start new measurement
if meter.get_measurement_status() == 0:
    meter.start_measurement()

# wait some time
time.sleep(10)

# stop measurement
meter.stop_measurement()

# wait for meter to sign measurement (it takes around 1 s)
time.sleep(1.5)

# print out billing dataset, signature and public key

billing_data = meter.get_output_billing_dataset()
signature_hex = meter.get_signature().hex().upper()
public_key_der_hex = meter.get_public_key().hex().upper()
print("signature status: ", meter.get_signature_status())
print("billing data: ",billing_data)
print("signature: ", signature_hex)
print("public key: ",public_key_der_hex)


# Convert hex to bytes
signature = bytes.fromhex(signature_hex)
public_key_der = bytes.fromhex(public_key_der_hex)

# Load the public key
public_key = serialization.load_der_public_key(public_key_der)
# print("public key: ", public_key.public_bytes( encoding=serialization.Encoding.DER,
#     format=serialization.PublicFormat.SubjectPublicKeyInfo))

# print("signature: ", signature)
_bytes = billing_data
hash_object =hashlib.sha256(_bytes)
hash_value = hash_object.digest()
# print("hash: ", hash_value)

# Verify the signature
try:
    public_key.verify(
        signature,
        hash_value,
        ec.ECDSA(hashes.SHA256())
    )
    print("Signature is valid.")
except InvalidSignature:
    print("Signature is invalid.")
