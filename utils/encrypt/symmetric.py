# 非对称加密

import rsa


# 生成密钥
def generate_key():
    public_key, private_key = rsa.newkeys(1024)
    public_key = public_key.save_pkcs1()
    print(public_key.decode())
    with open('public.pem', 'wb+')as f:
        f.write(public_key)
    private_key = private_key.save_pkcs1()
    print(private_key.decode())
    with open('private.pem', 'wb+')as f:
        f.write(private_key)


# 生成临时密钥
def generate_temp_key():
    public_key, private_key = rsa.newkeys(1024)
    public_key = public_key.save_pkcs1()
    private_key = private_key.save_pkcs1()
    return public_key, private_key


# 加密
def encrypt(data, key):
    rsa_public_key = rsa.PublicKey.load_pkcs1(key)
    return rsa.encrypt(data, rsa_public_key)


# 解密
def decrypt(data, key):
    rsa_private_key = rsa.PrivateKey.load_pkcs1(key)
    return rsa.decrypt(data, rsa_private_key)
