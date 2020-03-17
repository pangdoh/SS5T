import socket
import threading
from core.protos import ss5, ss4
from core import Constants
from utils import Debug


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
        conn.settimeout(8)
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

        if Constants.debug:
            # 移除连接列表
            client_list_lock.acquire()
            client_list.remove((conn, address))
            print("当前连接：", client_list)
            print("数量：", len(client_list))
            client_list_lock.release()


def execute(conn):
    # 接收
    data = conn.recv(512)
    Debug.log("接收1: %s" % data)

    version = 5
    # 检查协议
    if data.startswith(b'\x04') and data.endswith(b'\x00'):
        Debug.log('使用socks4协议')
        version = 4

    if version == 5:
        # 使用socks5协议
        ss5.ss5forward(data, conn)
    elif version == 4:
        # 使用socks4协议
        ss4.ss4forward(data, conn)
