import socket
import threading
from client import utils


def start(bind_address, bind_port, host=None, port=None):
    # 创建server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((bind_address, bind_port))
    s.listen(127)
    global client_list
    global client_list_lock
    global sem
    client_list = []
    client_list_lock = threading.Lock()
    sem = threading.Semaphore(127)
    while True:
        conn, address = s.accept()
        conn.settimeout(10)
        print("连接地址: %s" % str(address))
        t = threading.Thread(target=wait_connect, args=(conn, address))
        t.start()


def wait_connect(conn, address):
    with sem:
        # 加入连接列表
        client_list_lock.acquire()
        client_list.append((conn, address))
        client_list_lock.release()
        try:
            target_host = ''
            forward_return_flag = True
            while True:
                data = conn.recv(1024)
                if not data:
                    break

                if target_host == '':
                    # 提取目标并处理data
                    target_host, target_port, data = getTarget(data)
                    # 与目标建立连接
                    clt_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    clt_s.connect((target_host, target_port))

                # 转发至目标
                print('转发至目标:', data)
                clt_s.send(data)

                # 接收数据并返还客户端
                if forward_return_flag:
                    # 只创建一次子线程
                    forward_return_flag = False
                    tr = threading.Thread(target=forward_return, args=(clt_s, conn))
                    tr.start()

        except Exception as e:
            print(e)
        # 移除连接列表
        client_list_lock.acquire()
        client_list.remove((conn, address))
        client_list_lock.release()
        print("当前连接：", client_list)
        print("数量：", len(client_list))


# 提取目标
def getTarget(data):
    target_host = ''
    target_port = 0
    if data.find(b'HTTP/1.') != -1:
        headerStateLine = data[:data.find(b'\n')]
        print('headerStateLine:', headerStateLine)
        lines = headerStateLine.split(b' ')
        target = lines[1]

        if not target.startswith(b'http'):
            target = b'http' + target
        utils.parse_urls(target.decode())


        # 获取地址
        if target.startswith(b'http://'):
            target = target[7:]
            target_port = 80
            target = target[:target.find(b'/')]
        elif target.startswith(b'https://'):
            target = target[8:]
            target_port = 443
            target = target[:target.find(b'/')]

        if target.find(b':') != -1:
            targets = target.split(b':')
            target_host = targets[0].decode()
            target_port = int(targets[1])
        else:
            target_host = target.decode()

        print('获取目标地址:', target_host)
        print('获取目标端口', target_port)

    return target_host, target_port, data


# 接收并返还客户端
def forward_return(clt_s, conn):
    while True:
        try:
            tmp_date = clt_s.recv(1024)
            if not tmp_date:
                break
            print('返还给客户端:', tmp_date)
            # 返还给客户端
            conn.send(tmp_date)
        except ConnectionResetError:
            print('ConnectionResetError')
            break
        except ConnectionAbortedError:
            print('ConnectionAbortedError')
            break
    clt_s.close()
    conn.close()

