from __future__ import print_function
from covcov.infrastructure.kmscrypt.crypto import decrypt, encrypt


if __name__ == '__main__':
    import fileinput
    import json
    import sys

    # data = ''.join([line for line in fileinput.input()])
    data = "Toto va à l'école"
    
    # data = '{'\
    #     '"EncryptedData": "g53lN64f8g3UiAqsglOpVnEntezxyWoP/gMx73ijAKg=",' \
    #     '"EncryptedDataKey": "AQIDAHjhs/G99R67rkK/GmhDFqCVK7dO3+sCIEfxXzzPDmzUWwFM7BIoDhzdJ6jtkua+oNpUAAAAbjBsBgkqhkiG9w0BBwagXzBdAgEAMFgGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQModEKD8Fo/gzyYIYyAgEQgCvTEvHBy2MCJRl5+z3Mc/rXJwSbTDTD7IToyMpvVjj/8Xbk0t9HDRTDFy1q",' \
    #     '"EncryptionContext": {},' \
    #     '"Iv": "0972e01166cd3f0e28cd4d58fd06ae59"' \
    # '}'


    try:
        parsed = json.loads(data)
    except ValueError as e:
        parsed = {}

    if 'EncryptedData' in parsed:
        print('Decrypting data...', file=sys.stderr)
        print(decrypt(parsed) )
    else:
        print('Encrypting data...', file=sys.stderr)
        # print(json.dumps(encrypt(data, key_id='alias/FirstCMK'), indent=2))
        print(encrypt(data, key_id='alias/FirstCMK'))

# {
#     "EncryptedData": "+lsBtJ0j7LclLFZEq7r3Xwup8RhH2WOsZR9MAUZUbaY=",
#     "EncryptedDataKey": "AQIDAHjhs/G99R67rkK/GmhDFqCVK7dO3+sCIEfxXzzPDmzUWwG1lWcmRTRetK375z9a+tyrAAAAbjBsBgkqhkiG9w0BBwagXzBdAgEAMFgGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMm0MI/XRu13hYug7lAgEQgCthr4Qw3CUm4MWGYiiYp3Sqg4nHBN3o08vZJo5SzRtPwtL13Srl3ZR5wXaV",
#     "EncryptionContext": {},
#     "Iv": "16798d9251ee98881fad07af5fffa8f2"
# }

# {'EncryptedData': 'WOGBZ/vRPjUqxVLKAXvTuH+/IQyxgEoL/Pa9E+YPaak=', 
#  'EncryptedDataKey': 'AQIDAHjhs/G99R67rkK/GmhDFqCVK7dO3+sCIEfxXzzPDmzUWwEQ3Wj4HdH30xSgif2uqXuLAAAAfjB8BgkqhkiG9w0BBwagbzBtAgEAMGgGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQM+e+rPumDCmcaaGdEAgEQgDtK0V+DgkhP0SuHsmStSyG2VFyNFYxE3UN8vAWly8i2OMflWCPFdeun5DVATi6LE8APHoF+h00QR1ke4A==', 
#  'EncryptionContext': {}, 
#  'Iv': b'\xfe\xc5\\A)\x19{\x1cO\xc7\x1c?\x1evp\xdf'}
