from server import protocmsd


def ss5forward(data, conn, auth):

    # 初始化变量
    METHODS_D1 = b''
    REP_D2 = b'\x00'

    VER_C1 = data[0:1]
    print("版本:", VER_C1)
    NMETHODS_C1 = data[1:2]
    print("客户端支持的方法数量:", NMETHODS_C1)
    METHODS_C1 = data[2:]
    print("客户端支持的方法:", METHODS_C1)
    if auth:
        if METHODS_C1.find(b'\x02') != -1:
            METHODS_D1 = b'\x02'
    else:
        if METHODS_C1.find(b'\x00') != -1:
            METHODS_D1 = b'\x00'
        elif METHODS_C1.find(b'\x02') != -1:
            METHODS_D1 = b'\x02'

    # 响应
    print("准备响应")
    if len(METHODS_D1) > 0:
        print("服务端选择的方法:", METHODS_D1)
    else:
        print('server没有支持的方法')
        METHODS_D1 = '\xff'

    res1 = VER_C1 + METHODS_D1
    print("响应1: %s" % res1)
    conn.send(res1)
    print("----------------------第一次交互完毕------------------------------")

    # 如果需要用户认证
    if METHODS_D1 == b'\x02':
        if not auth:
            res_auth = b'\x01\x00'
        else:
            print('----------需要认证------------')
            data = conn.recv(512)
            auth_version = data[0:1]
            ulen = int(data[1:2].hex(), 16)
            uname = data[2:2 + ulen].decode()
            plen = int(data[2 + ulen:3 + ulen].hex(), 16)
            passwd = data[3 + ulen:4 + ulen + plen].decode()

            print('--认证信息--')
            print("认证版本", auth_version)
            print("用户名长度", ulen)
            print("用户名", uname)
            print("密码长度", plen)
            print("密码", passwd)

            auth_success = False
            if auth_version == b'\x01':
                u_list = protocmsd.auth_users()
                for user in u_list:
                    if user.get('usr') == uname:
                        if user.get('pwd') == passwd:
                            print('认证通过')
                            auth_success = True
                        else:
                            print('密码不正确')
                        break
            else:
                print('不支持的认证版本')

            if auth_success:
                res_auth = b'\x01\x00'
            else:
                res_auth = b'\x01\x01'

        print('响应认证', res_auth)
        conn.send(res_auth)

        print('----------认证结束------------')

    # 客户端向服务端发送请求
    data = conn.recv(512)
    print("接收2: %s" % data)
    VER_C2 = data[0:1]
    CMD_C2 = data[1:2]
    RSV_C2 = data[2:3]
    ATYP_C2 = data[3:4]
    DST_ADDR_LEN_C2 = data[4]
    DST_ADDR_C2 = data[5:5 + DST_ADDR_LEN_C2]
    DST_PORT_C2 = data[5 + DST_ADDR_LEN_C2:7 + DST_ADDR_LEN_C2]

    print("版本:", VER_C2)
    print("CMD:", CMD_C2)
    print("RSV:", RSV_C2)
    print("地址类型:", ATYP_C2)
    print("目标地址长度:", DST_ADDR_LEN_C2)
    print("目标地址:", DST_ADDR_C2)
    # print("目标端口:", DST_PORT_C2)
    print("目标端口:", int(DST_PORT_C2.hex(), 16))
    print("准备响应")
    ATYP_D2 = b'\x01'
    BND_ADDR_D2 = b'\x00\x00\x00\x00'
    BND_PORT_D2 = b'\x00\x00'
    res2 = VER_C2 + REP_D2 + RSV_C2 + ATYP_D2 + BND_ADDR_D2 + BND_PORT_D2
    print("响应2: %s" % res2)
    conn.send(res2)

    print("----------------------第二次交互完毕------------------------------")

    # 开始转发数据
    target_host = DST_ADDR_C2.decode()
    target_port = int(DST_PORT_C2.hex(), 16)
    protocmsd.forward_data(conn, target_host, target_port)
