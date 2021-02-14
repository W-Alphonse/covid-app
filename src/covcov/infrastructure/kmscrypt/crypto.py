"""Main module containing encryption and decryption routines."""

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Cipher.blockalgo import BlockAlgo
from botocore.client import BaseClient

import covcov.infrastructure.kmscrypt.pkcs7 as pkcs7
import covcov.infrastructure.kmscrypt.helpers as kmshelpers

AES_IV_BYTES = 16
AES_KEY_BYTES = 16  # 128 bits
AES_KEY_SPEC = 'AES_256'
AES_MODE = AES.MODE_CBC


def generate_data_key(kms_clt: BaseClient, key_id: str, encryption_context={}) -> (bytes, bytes) :
    res = kms_clt.generate_data_key(KeyId=key_id, KeySpec=AES_KEY_SPEC, EncryptionContext=encryption_context)
    iv = Random.new().read(16)        # To get a cryptographically secure random byte string, use GenerateRandom
    return res['CiphertextBlob'] , iv # kmshelpers.hexlify(iv) # returns 'bytes' that can be stored in a Blob

def get_plaintext_data_key(kms_clt: BaseClient, encrypted_data_key: bytes, encryption_context={}) -> str :
    res = kms_clt.decrypt(CiphertextBlob=encrypted_data_key, EncryptionContext=encryption_context)
    return res['Plaintext']

def get_cipher(kms_clt: BaseClient, encrypted_data_key: bytes, iv: bytes, encryption_context={}) -> BlockAlgo:
    return AES.new(get_plaintext_data_key(kms_clt, encrypted_data_key, encryption_context={}), AES_MODE, iv)

def encrypt(datas:[], kms_clt: BaseClient, encrypted_data_key: bytes, iv: bytes, encryption_context={}) -> ([], []): # b64_enc_data, binary_enc_data
    key = get_plaintext_data_key(kms_clt, encrypted_data_key, encryption_context={})
    b64_enc_data = []
    binary_enc_data = []
    #
    for data in datas :
        # https://www.kite.com/python/docs/Crypto.Cipher.AES.AESCipher.decrypt
        # The cipher object is stateful => you cannot reuse an object for encrypting or decrypting other data with the same key.
        cipher = get_cipher(kms_clt, encrypted_data_key, iv, encryption_context={})

        if not isinstance(data, bytes):
            data = data.encode('UTF-8')
        message = pkcs7.pad(data, block_size=AES_KEY_BYTES)
        ciphertext = cipher.encrypt(message)
        binary_enc_data.append(ciphertext)
        b64_enc_data.append(kmshelpers.b64encode(ciphertext))
    return b64_enc_data, binary_enc_data

def decrypt(benc_datas:[], kms_clt: BaseClient, encrypted_data_key: bytes, iv: bytes, encryption_context={}) -> []:
    key = get_plaintext_data_key(kms_clt, encrypted_data_key, encryption_context={})
    datas = []
    #
    for benc_data in benc_datas :
        if isinstance(benc_data,str) :
            datas.append(benc_data)
        else :
            cipher = get_cipher(kms_clt, encrypted_data_key, iv, encryption_context={})
            datas.append( pkcs7.unpad(cipher.decrypt(benc_data.tobytes()), block_size=AES_KEY_BYTES).decode('UTF-8'))
    return datas