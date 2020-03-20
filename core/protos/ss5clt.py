from core import Constants
from utils import Debug
from utils.encrypt import symmetric


# ss5连接
def ss5conn(s, conn_box):
    proxy = Constants.proxy
    proxy_address = proxy.get('proxy_address')
    proxy_port = proxy.get('proxy_port')
    usr = proxy.get('usr')
    pwd = proxy.get('pwd')
    Debug.log('使用socks5前置代理>>>>> %s:%d' % (proxy_address, proxy_port))
    s.connect((proxy_address, proxy_port))

    if Constants.remote_ssl:
        # 发送公钥
        tmp_pub_key = Constants.publicKey[31:-30]
        Debug.log("发送公钥：", tmp_pub_key)
        s.send(tmp_pub_key)
        data = b''
        while True:
            # 接收加密公钥
            data += s.recv(1024)
            if not data or len(data) >= 256:
                break
        Debug.log('接收公钥：', data)
        # 解密公钥
        tmp_ser_pub_key_1 = symmetric.decrypt(data[:128], Constants.privateKey)
        tmp_ser_pub_key_2 = symmetric.decrypt(data[128:], Constants.privateKey)
        conn_box.server_public_key = b'-----BEGIN RSA PUBLIC KEY-----\n' \
                                     + tmp_ser_pub_key_1 \
                                     + tmp_ser_pub_key_2 \
                                     + b'\n-----END RSA PUBLIC KEY-----\n'
        # # 生成随机密钥
        # random_key = asymmetric.generate_key()
        # 获取随机密钥
        random_key = Constants.random_key
        conn_box.random_key = random_key
        Debug.log('生成随机密钥：', random_key)
        # 加密随机密钥
        random_key = symmetric.encrypt(conn_box.random_key, conn_box.server_public_key)
        Debug.log("加密随机密钥：", random_key)
        # 发送随机密钥
        s.send(random_key)
        # 设置结束标记
        conn_box.end_flag = random_key

    # 建立socks5连接
    Debug.log('建立socks5连接')
    if usr:
        req1 = b'\x05\x02\x00\x02'
    else:
        req1 = b'\x05\x01\x00'
    Debug.log('req1:', req1)
    if Constants.remote_ssl:
        # 非对称加密
        req1 = symmetric.encrypt(req1, conn_box.server_public_key)
        # req1 = asymmetric.encrypt(req1, conn_box.random_key)
        Debug.log('非对称加密req1:', req1)
    s.send(req1)

    # res1 = s.recv(512)
    res1 = b''
    while True:
        res1 += s.recv(512)
        if not res1 or len(res1) >= 128:
            break
    Debug.log('res1:', res1)
    if Constants.remote_ssl:
        # 非对称解密
        # res1 = asymmetric.decrypt(res1, conn_box.random_key)
        res1 = symmetric.decrypt(res1, Constants.privateKey)
        Debug.log('非对称解密res1:', res1)

    if res1 == b'\x05\x00':
        proxy_continue = True
    elif res1 == b'\x05\x02':
        auth_info_req = b'\x01' + len(usr).to_bytes(1, 'big') + usr.encode('utf-8') + len(pwd).to_bytes(1, 'big') + pwd.encode('utf-8')
        Debug.log("发送认证信息:", auth_info_req)
        if Constants.remote_ssl:
            # 非对称加密
            # auth_info_req = asymmetric.encrypt(auth_info_req, conn_box.random_key)
            auth_info_req = symmetric.encrypt(auth_info_req, conn_box.server_public_key)
            Debug.log('非对称加密auth_info_req:', auth_info_req)
        s.send(auth_info_req)

        auth_info_res = b''
        while True:
            auth_info_res += s.recv(512)
            if not auth_info_res or len(auth_info_res) >= 128:
                break

        # auth_info_res = s.recv(512)
        Debug.log('接收认证响应:', auth_info_res)
        if Constants.remote_ssl:
            # 非对称解密
            auth_info_res = symmetric.decrypt(auth_info_res, Constants.privateKey)
            # auth_info_res = asymmetric.decrypt(auth_info_res, conn_box.random_key)
            Debug.log('非对称解密接收认证响应:', auth_info_res)
        if auth_info_res == b'\x01\x00':
            proxy_continue = True
        else:
            print('前置代理用户认证失败')
            proxy_continue = False
    else:
        proxy_continue = False

    if proxy_continue:
        if conn_box.ATYP_C2 == b'\x03':
            req2 = b'\x05' + b'\x01' + b'\x00' + conn_box.ATYP_C2 + conn_box.DST_ADDR_LEN_C2 +conn_box.DST_ADDR_C2 + conn_box.DST_PORT_C2
        else:
            req2 = b'\x05' + b'\x01' + b'\x00' + conn_box.ATYP_C2 + conn_box.DST_ADDR_C2 + conn_box.DST_PORT_C2
        Debug.log('发送连接信息至前置代理req：', req2)
        if Constants.remote_ssl:
            # 非对称加密
            req2 = symmetric.encrypt(req2, conn_box.server_public_key)
            # req2 = asymmetric.encrypt(req2, conn_box.random_key)
            Debug.log('对称加密req2:', req2)
        s.send(req2)

        res2 = b''
        while True:
            res2 += s.recv(512)
            if not res2 or len(res2) >= 128:
                break

        # res2 = s.recv(512)
        Debug.log('前置代理返回res2:', res2)
        if Constants.remote_ssl:
            # 非对称解密
            # res2 = asymmetric.decrypt(res2, conn_box.random_key)
            res2 = symmetric.decrypt(res2, Constants.privateKey)
            Debug.log('非对称解密res2:', res2)
        if res2.startswith(b'\x05\x00'):
            # ss5连接握手成功
            Debug.log('ss5连接握手成功')
        else:
            print("前置代理连接过程阶段二发生错误！停止访问！")

    else:
        print("前置代理连接过程发生错误！停止访问！")
