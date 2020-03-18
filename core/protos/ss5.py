from core import protocmsd
from core import Constants
import socket
import struct
from utils import Debug
import utils


def ss5forward(data, conn):
    # 初始化
    auth = Constants.auth
    METHODS_D1 = b''
    REP_D2 = b'\x00'

    VER_C1 = data[0:1]
    Debug.log("版本:", VER_C1)
    NMETHODS_C1 = data[1:2]
    Debug.log("客户端支持的方法数量:", NMETHODS_C1)
    METHODS_C1 = data[2:]
    Debug.log("客户端支持的方法:", METHODS_C1)
    if auth:
        if METHODS_C1.find(b'\x02') != -1:
            METHODS_D1 = b'\x02'
    else:
        if METHODS_C1.find(b'\x00') != -1:
            METHODS_D1 = b'\x00'
        elif METHODS_C1.find(b'\x02') != -1:
            METHODS_D1 = b'\x02'

    # 响应
    Debug.log("准备响应")
    if len(METHODS_D1) > 0:
        Debug.log("服务端选择的方法:", METHODS_D1)
    else:
        Debug.log('server没有支持的方法')
        METHODS_D1 = '\xff'

    res1 = VER_C1 + METHODS_D1
    Debug.log("响应1: %s" % res1)
    conn.send(res1)
    Debug.log("----------------------第一次交互完毕------------------------------")

    # 如果需要用户认证
    if METHODS_D1 == b'\x02':
        if not auth:
            res_auth = b'\x01\x00'
        else:
            Debug.log('----------需要认证------------')
            data = conn.recv(512)
            auth_version = data[0:1]
            ulen = int(data[1:2].hex(), 16)
            uname = data[2:2 + ulen].decode()
            plen = int(data[2 + ulen:3 + ulen].hex(), 16)
            passwd = data[3 + ulen:4 + ulen + plen].decode()

            Debug.log('--认证信息--')
            Debug.log("认证版本", auth_version)
            Debug.log("用户名长度", ulen)
            Debug.log("用户名", uname)
            Debug.log("密码长度", plen)
            Debug.log("密码", passwd)

            auth_success = False
            if auth_version == b'\x01':
                u_list = Constants.auth_usr_lst
                for user in u_list:
                    if user.get('usr') == uname:
                        if user.get('pwd') == passwd:
                            Debug.log('认证通过')
                            auth_success = True
                        else:
                            Debug.log('密码不正确')
                        break
            else:
                Debug.log('不支持的认证版本')

            if auth_success:
                res_auth = b'\x01\x00'
            else:
                res_auth = b'\x01\x01'

        Debug.log('响应认证', res_auth)
        conn.send(res_auth)

        Debug.log('----------认证结束------------')

    # 客户端向服务端发送请求
    data = conn.recv(512)
    Debug.log("接收2: %s" % data)
    VER_C2 = data[0:1]
    CMD_C2 = data[1:2]
    RSV_C2 = data[2:3]
    ATYP_C2 = data[3:4]
    Debug.log("版本:", VER_C2)
    Debug.log("CMD:", CMD_C2)
    Debug.log("RSV:", RSV_C2)
    Debug.log("地址类型:", ATYP_C2)
    if ATYP_C2 == b'\x01':
        DST_ADDR_C2 = data[4:8]
        DST_PORT_C2 = data[8:10]
        target_host = socket.inet_ntoa(struct.pack('!L', int(DST_ADDR_C2.hex(), 16)))
        # target_host = utils.ip_int2str(int(DST_ADDR_C2.hex(), 16))
    elif ATYP_C2 == b'\x03':
        Constants.DST_ADDR_LEN_C2 = data[4:5]
        DST_ADDR_LEN_C2 = data[4]
        Debug.log("目标地址长度:", DST_ADDR_LEN_C2)
        DST_ADDR_C2 = data[5:5 + DST_ADDR_LEN_C2]
        DST_PORT_C2 = data[5 + DST_ADDR_LEN_C2:7 + DST_ADDR_LEN_C2]
        target_host = DST_ADDR_C2.decode()
    else:
        Debug.log('使用ipv6')
        DST_ADDR_C2 = data[4:20]
        DST_PORT_C2 = data[20:22]
        # target_host = socket.inet_ntoa(struct.pack('!L', int(DST_ADDR_C2.hex(), 16)))
        target_host = utils.ip_int2str(int(DST_ADDR_C2.hex(), 16))

    # 如果需要前置代理，记录此信息
    if Constants.proxy:
        Debug.log('使用前置代理先保留客户端交互信息')
        Constants.VER_C2 = VER_C2
        Constants.CMD_C2 = CMD_C2
        Constants.RSV_C2 = RSV_C2
        Constants.ATYP_C2 = ATYP_C2
        Constants.DST_ADDR_C2 = DST_ADDR_C2
        Constants.DST_PORT_C2 = DST_PORT_C2

    Debug.log("目标地址:", DST_ADDR_C2)
    # Debug.log("目标端口:", DST_PORT_C2)
    Debug.log("目标端口:", int(DST_PORT_C2.hex(), 16))
    Debug.log("准备响应")
    ATYP_D2 = b'\x01'
    BND_ADDR_D2 = b'\x00\x00\x00\x00'
    BND_PORT_D2 = b'\x00\x00'
    res2 = VER_C2 + REP_D2 + RSV_C2 + ATYP_D2 + BND_ADDR_D2 + BND_PORT_D2
    Debug.log("响应2: %s" % res2)
    conn.send(res2)

    Debug.log("----------------------第二次交互完毕------------------------------")

    # 开始转发数据
    target_port = int(DST_PORT_C2.hex(), 16)
    protocmsd.forward_data(conn, target_host, target_port)
