# 非对称加密

import Crypto.PublicKey.RSA
import Crypto.Random
import Crypto.Cipher.PKCS1_v1_5
import Crypto.Signature.PKCS1_v1_5
import Crypto.Hash


# 生成密钥
def generate_key():
    # x = Crypto.PublicKey.RSA.generate(4096)
    x = Crypto.PublicKey.RSA.generate(1024, Crypto.Random.new().read)  # 使用 Crypto.Random.new().read 伪随机数生成器
    private_key = x.exportKey("PEM")  # 生成私钥
    print(private_key.decode())
    print('----------------------------------------------------------------')
    public_key = x.publickey().exportKey()  # 生成公钥
    print(public_key.decode())

    with open("private.pem", "wb") as x:
        x.write(private_key)
    with open("public.pem", "wb") as x:
        x.write(public_key)


# 加密
def encrypt(data, key='public.pem'):
    cipher_public = Crypto.Cipher.PKCS1_v1_5.new(Crypto.PublicKey.RSA.importKey(key))
    return cipher_public.encrypt(data)


# 解密
def decrypt(data, key='private.pem'):
    cipher_private = Crypto.Cipher.PKCS1_v1_5.new(Crypto.PublicKey.RSA.importKey(key))
    return cipher_private.decrypt(data, Crypto.Random.new().read)


# test
# generate_key()

# a = b'fmM/\x0f\xa2+I\xbb\xfev\xed\xc6\x1e\xdcv'
a = b'123asdafaaaaaaaareqwrqdasggfsdczxcqweeasdsadsdaeqwrsd213'
a = encrypt(a)
print(a)
