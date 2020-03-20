# 对称加密 AES

from Cryptodome.Cipher import AES
from binascii import b2a_hex, a2b_hex
from Cryptodome import Random


# 生成key
def generate_key():
    return Random.new().read(AES.block_size)


# 加密
def encrypt(data, key):
    aes = AES.new(key, AES.MODE_CFB, key)
    return b2a_hex(aes.encrypt(data))


# 解密
def decrypt(data, key):
    aes = AES.new(key, AES.MODE_CFB, key)
    return aes.decrypt(a2b_hex(data))

