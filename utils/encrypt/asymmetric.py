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


# if __name__ == '__main__':
#     # key为32位长度
#     key = generate_key()
#     print("len key", len(key))
#     print('key', key)
#     data = b'd6as5d67as567d4s4d7as8d6as89d698asd954das78d578as5d8s48as57858f75a785f78asf78as65d78fa7s86da'
#     print(len(data))
#     print('加密前', data)
#     data = encrypt(data, key)  # 调用加密函数
#     print(len(data))
#     print('加密后:', data)
#     data = decrypt(data, key)  # 调用解密函数
#     print('解密后:', data)
