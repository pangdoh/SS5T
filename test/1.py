import socket
import threading
import sys


# 用户列表
def auth_users():
    u_list = []
    user1 = {
        'usr': 'admin',
        'pwd': '123456',
    }
    u_list.append(user1)
    return u_list

# 接收并返还客户端
def forward_recv(s, conn):
    while True:
        try:
            print(2222222222222)
            tmp_data = s.recv(1024)
            print('响应3:', tmp_data)
            if not tmp_data:
                break
            else:
                conn.send(tmp_data)
        except ConnectionAbortedError:
            print('ConnectionAbortedError')
            break
        except OSError:
            print("OSError")
            break
        except socket.timeout:
            print('timeout')
            break
    print("子线程关闭连接")
    s.close()
    conn.close()


ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '0.0.0.0'
port = 1088
ss.bind((host, port))
ss.listen(50)

# 初始化变量
METHODS_D1 = b''
REP_D2 = b'\x00'

while True:
    # 建立客户端连接
    conn, address = ss.accept()

    print("连接地址: %s" % str(address))

    '''
    客户端第一次发送格式
    +----+----------+----------+
    |VER | NMETHODS | METHODS  |
    +----+----------+----------+
    | 1  |    1     |  1~255   |
    +----+----------+----------+
    1.VER
        字段是当前协议的版本号，也就是 5  例：0x05

    2.NMETHODS
        字段是 METHODS 字段占用的字节数 例：0x01

    3.METHODS
        字段的每一个字节表示一种认证方式，表示客户端支持的全部认证方式。
        0x00: NO AUTHENTICATION REQUIRED
        0x01: GSSAPI
        0x02: USERNAME/PASSWORD
        0x03: to X’7F’ IANA ASSIGNED
        0x80: to X’FE’ RESERVED FOR PRIVATE METHODS
        0xFF: NO ACCEPTABLE METHODS

        例： 0x00
    '''
    data = conn.recv(512)
    print("接收1: %s" % data)
    VER_C1 = data[0:1]
    print("版本:", VER_C1)
    NMETHODS_C1 = data[1:2]
    print("客户端支持的方法数量:", NMETHODS_C1)
    METHODS_C1 = data[2:]
    print("客户端支持的方法:", METHODS_C1)
    if METHODS_C1.find(b'\x02') != -1:
        METHODS_D1 = b'\x02'
    elif METHODS_C1.find(b'\x00') != -1:
        METHODS_D1 = b'\x00'

    '''
    服务端第一次响应格式
    +----+--------+
    |VER | METHOD |
    +----+--------+
    | 1  |   1    |
    +----+--------+
    1.VER
        字段是当前协议的版本号，也就是 5  例：0x05
    2.METHOD
        服务器从“METHOD”中给出的方法之一中进行选择
        0x00: NO AUTHENTICATION REQUIRED
        0x01: GSSAPI
        0x02: USERNAME/PASSWORD
        0x03: to X’7F’ IANA ASSIGNED
        0x80: to X’FE’ RESERVED FOR PRIVATE METHODS
        0xFF: NO ACCEPTABLE METHODS

        例：0x05 0x00：告诉客户端采用无认证的方式建立连接
    '''
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

    '''
    认证格式
    +-------+-----+------+-----+-------+
    |version| ulen| uname| plen| passwd|
    +-------+-----+------+-----+-------+
    |  	1   |  1  | 0~255|	1  | 0~255 |
    +-------+-----+------+-----+-------+
    这里的version字段表示身份验证版本,一般为1.
    Demo:
    接收数据例如：b'\x01\x05admin\x06123456'
    '''
    # 如果需要用户认证
    if METHODS_D1 == b'\x02':
        print('----------需要认证------------')
        data = conn.recv(512)
        auth_version = data[0:1]
        ulen = int(data[1:2].hex(), 16)
        uname = data[2:2+ulen].decode()
        plen = int(data[2+ulen:3+ulen].hex(), 16)
        passwd = data[3+ulen:4+ulen+plen].decode()

        print('--认证信息--')
        print("认证版本", auth_version)
        print("用户名长度", ulen)
        print("用户名", uname)
        print("密码长度", plen)
        print("密码", passwd)

        auth_success = False
        if auth_version == b'\x01':
            u_list = auth_users()
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

        '''
        认证响应格式
        +-------+-------+
        |version| status|
        +-------+-------+
        |  	1   |   1   |
        +-------+-------+
        status字段0表示成功的授权，而其他值则被视为失败。
        例：0x01 0x00
        '''
        if auth_success:
            res_auth = b'\x01\x00'
        else:
            res_auth = b'\x01\x01'

        print('响应认证', res_auth)
        conn.send(res_auth)

        print('----------认证结束------------')
    '''
    认证完成，客户端向服务端发送请求
    +----+-----+-------+------+----------+----------+
    |VER | CMD |  RSV  | ATYP | DST.ADDR | DST.PORT |
    +----+-----+-------+------+----------+----------+
    | 1  |  1  |   1   |  1   | Variable |    2     |
    +----+-----+-------+------+----------+----------+
    1.VER
        字段是当前协议的版本号，也就是 5  例：0x05
    2.CMD
        CONNECT 0x01 建立 TCP 连接
        BIND 0x02 上报反向连接地址
        UDP ASSOCIATE 0x03 关联 UDP 请求
    3.RSV
        RESERVED保留字段，值为 0x00
    4.ATYP
        address type,取值为:
        0x01：IPv4
        0x03：域名
        0x04：IPv6
    5.DST.ADDR
        destination address,取值随 ATYP 变化
        ATYP == 0x01：4 个字节的 IPv4 地址
        ATYP == 0x03：1 个字节表示域名长度，紧随其后的是对应的域名
        ATYP == 0x04：16 个字节的 IPv6 地址
        例：127.0.0.1 --> 0x7f 0x00 0x00 0x01
    6.DST.PORT 字段：目的服务器的端口
        例子：8000  --> 0x1f 0x40

    Demo: 客户端通过 127.0.0.1:8000 的代理发送请求
    client -> server:
    |VER | CMD | RSV | ATYP| DST.ADDR           | DST.PORT
    |0x05| 0x01| 0x00| 0x01| 0x7f 0x00 0x00 0x01| 0x1f 0x40
    '''
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

    '''
    服务端返回格式
    +----+-----+-------+------+----------+----------+
    |VER | REP |  RSV  | ATYP | BND.ADDR | BND.PORT |
    +----+-----+-------+------+----------+----------+
    | 1  |  1  |   1   |  1   | Variable |    2     |
    +----+-----+-------+------+----------+----------+
    1.VER
        字段是当前协议的版本号，也就是 5  例：0x05
    2.REP
        0x00 succeeded 成功
        0x01 general SOCKS server failure 常规SOCKS服务器故障
        0x02 connection not allowed by ruleset 规则集不允许连接
        0x03 Network unreachable 网络不可达
        0x04 Host unreachable 主机不能到达
        0x05 Connection refused 连接被拒绝
        0x06 TTL expired TTL过期
        0x07 Command not supported 不支持命令
        0x08 Address type not supported 不支持地址类型
        0x09 to X'FF' unassigned 到X'FF'未分配
    3.RSV
        RESERVED保留字段，值为 0x00
    4.ATYP
        address type,取值为:
        0x01：IPv4
        0x03：域名
        0x04：IPv6
    5.BND.ADDR
        server bound address
        ATYP == 0x01：4 个字节的 IPv4 地址
        ATYP == 0x03：1 个字节表示域名长度，紧随其后的是对应的域名
        ATYP == 0x04：16 个字节的 IPv6 地址
        例：127.0.0.1 --> 0x7f 0x00 0x00 0x01
        例：0.0.0.0 --> 0x00 0x00 0x00 0x00
    6.BND.PORT
        server bound port in network octet order
        例： 0x00 0x00

    Demo:客户端通过 127.0.0.1:8000 的代理发送请求
    server -> client:
    |VER | REP | RSV | ATYP| BND.ADDR           | BND.PORT
    |0x05| 0x00| 0x00| 0x01| 0x00 0x00 0x00 0x00| 0x10 0x10
    '''
    print("准备响应")
    ATYP_D2 = b'\x01'
    BND_ADDR_D2 = b'\x00\x00\x00\x00'
    BND_PORT_D2 = b'\x00\x00'
    res2 = VER_C2 + REP_D2 + RSV_C2 + ATYP_D2 + BND_ADDR_D2 + BND_PORT_D2
    print("响应2: %s" % res2)
    conn.send(res2)

    print("----------------------第二次交互完毕------------------------------")

    '''
    传输阶段,接下来就开始传输数据
    '''

    # 定义变量
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    host = DST_ADDR_C2.decode()
    port = int(DST_PORT_C2.hex(), 16)
    clt_conn_flag = True
    forward_recv_flag = True

    while True:
        print(111111111111111)
        try:
            tmp_data = conn.recv(1024)
        except ConnectionAbortedError:
            break
        print('接收3：', tmp_data)
        if not tmp_data:
            break
        else:
            if clt_conn_flag:
                clt_conn_flag = False
                # 与目标建立连接
                s.connect((host, port))

            # 转发数据
            s.send(tmp_data)

            if forward_recv_flag:
                forward_recv_flag = False
                # 接收请求
                tr = threading.Thread(target=forward_recv, args=(s, conn))
                tr.start()

    # 关闭目标连接
    print("关闭目标连接")
    s.close()
    conn.close()
    print("----------------------第三次交互完毕------------------------------")


