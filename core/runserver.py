import socket
import threading
from core.protos import ss5, ss4
from core import Constants
from core import ConnVariable
from utils import Debug
from utils.encrypt import symmetric


def start():
    bind_address = Constants.bind_address
    bind_port = Constants.bind_port
    current_num = Constants.current_num

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((bind_address, bind_port))
    s.listen(current_num)
    global client_list
    global client_list_lock
    global sem
    client_list = []
    client_list_lock = threading.Lock()
    sem = threading.Semaphore(current_num)
    while True:
        conn, address = s.accept()
        conn.settimeout(10)
        print("连接地址: %s" % str(address))
        t = threading.Thread(target=wait_connect, args=(conn, address,))
        t.start()


def wait_connect(conn, address):
    with sem:
        if Constants.debug:
            # 加入连接列表
            client_list_lock.acquire()
            client_list.append((conn, address))
            client_list_lock.release()

            try:
                execute(conn)
            except Exception as e:
                print(e)
        else:
            execute(conn)

        if Constants.debug:
            # 移除连接列表
            client_list_lock.acquire()
            client_list.remove((conn, address))
            print("当前连接：", client_list)
            print("数量：", len(client_list))
            client_list_lock.release()


def execute(conn):
    conn_box = ConnVariable(conn)

    # 判断是否需要和客户端进行加密传输
    if Constants.local_ssl:
        # 接收公钥
        data = conn.recv(1024)
        Debug.log('接收公钥：', data)
        conn_box.client_public_key = b'-----BEGIN RSA PUBLIC KEY-----\n' + data + b'\n-----END RSA PUBLIC KEY-----\n'
        # 发送加密公钥
        tmp_pub_key = Constants.publicKey[31:-30]
        tmp_pub_key_1 = symmetric.encrypt(tmp_pub_key[:100], conn_box.client_public_key)
        tmp_pub_key_2 = symmetric.encrypt(tmp_pub_key[100:], conn_box.client_public_key)
        conn.send(tmp_pub_key_1 + tmp_pub_key_2)
        # 接收随机密钥
        clt_random_key = conn.recv(1024)
        Debug.log("接收随机密钥：", clt_random_key)
        # 设置客户端结束标记
        conn_box.clt_end_flag = clt_random_key
        # 解密随机密钥
        clt_random_key = symmetric.decrypt(clt_random_key, Constants.privateKey)
        Debug.log("解密随机密钥：", clt_random_key)
        conn_box.clt_random_key = clt_random_key

    # 接收
    data = conn.recv(512)
    Debug.log("接收1: %s" % data)
    if Constants.local_ssl:
        # 非对称解密
        # data = asymmetric.decrypt(data, conn_box.clt_random_key)
        data = symmetric.decrypt(data, Constants.privateKey)
        Debug.log('非对称解密接收1:', data)

    version = 5
    # 检查协议
    if data.startswith(b'\x04') and data.endswith(b'\x00'):
        Debug.log('使用socks4协议')
        version = 4

    if version == 5:
        # 使用socks5协议
        ss5.ss5forward(data, conn, conn_box)
    elif version == 4:
        # 使用socks4协议
        ss4.ss4forward(data, conn, conn_box)
