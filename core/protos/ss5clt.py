from utils import Debug
from core import Constants


# ss5转发
def ss5conn(s):
    proxy = Constants.proxy
    proxy_address = proxy.get('proxy_address')
    proxy_port = proxy.get('proxy_port')
    usr = proxy.get('usr')
    pwd = proxy.get('pwd')
    Debug.log('使用socks5前置代理>>>>> %s:%d' % (proxy_address, proxy_port))
    s.connect((proxy_address, proxy_port))

    # 建立socks5连接
    Debug.log('建立socks5连接')
    if usr:
        req1 = b'\x05\x02\x00\x02'
    else:
        req1 = b'\x05\x01\x00'
    Debug.log('req1:', req1)
    s.send(req1)

    res1 = s.recv(512)
    Debug.log('res1:', res1)

    if res1 == b'\x05\x00':
        proxy_continue = True
    elif res1 == b'\x05\x02':
        auth_info_req = b'\x01' + len(usr).to_bytes(1, 'big') + usr.encode('utf-8') + len(pwd).to_bytes(1, 'big') + pwd.encode('utf-8')
        Debug.log("发送认证信息:", auth_info_req)
        s.send(auth_info_req)
        auth_info_res = s.recv(512)
        Debug.log('auth_info_res:', auth_info_res)
        if auth_info_res == b'\x01\x00':
            proxy_continue = True
        else:
            print('前置代理用户认证失败')
            proxy_continue = False
    else:
        proxy_continue = False

    if proxy_continue:
        if Constants.ATYP_C2 == b'\x03':
            req2 = Constants.VER_C2 + Constants.CMD_C2 + Constants.RSV_C2 + Constants.ATYP_C2 + Constants.DST_ADDR_LEN_C2 +Constants.DST_ADDR_C2 + Constants.DST_PORT_C2
        else:
            req2 = Constants.VER_C2 + Constants.CMD_C2 + Constants.RSV_C2 + Constants.ATYP_C2 + Constants.DST_ADDR_C2 + Constants.DST_PORT_C2
        Debug.log('发送连接信息至前置代理req：', req2)
        s.send(req2)

        res2 = s.recv(512)
        Debug.log('前置代理返回res2:', res2)
        if res2.startswith(b'\x05\x00'):
            # ss5连接握手成功
            Debug.log('ss5连接握手成功')
        else:
            print("前置代理连接过程阶段二发生错误！停止访问！")

    else:
        print("前置代理连接过程发生错误！停止访问！")
