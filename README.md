Running the code
```
pip install -r requirements.txt 
python example.py 
```
output
```
$ python example.py
connected to meter
signature status:  15
billing data:  b'{"FV": "1.0", "GI": "Gateway1", "GS": "123456789", "PG": "T84563", "MV": "iskra", "MM": "", "MS": "123456789", "MF": "2.03", "IS": true, "IF": [], "IT": "NONE", "ID": "1", "CT": "controller1", "CI": "", "RD": [{"TM": "2023-09-03T10:34:55.955", "TX": "B", "RV": 84758, "RI": "1-b:1.8.0", "RU": "kWh", "RT": "AC", "EF": "", "ST": "G"}, {"TM": "2023-09-03T10:35:05.987", "TX": "r", "RV": 84870, "RI": "1-b:1.8.0", "RU": "kWh", "RT": "AC", "EF": "", "ST": "G"}]}'
signature:  302E021501DE33DEA393297F3E90EB0E3D0305258C16A766FD0215022A87183DA62E3D98983380BD294EDC394DECD042
public key:  3040301006072A8648CE3D020106052B8104000F032C000401EF477899469F0AB5B52FFB37EFB8D923A2AC38220715EAD254810B1EEB7B1996AAA2652974A18D87C0
Signature is valid.
```