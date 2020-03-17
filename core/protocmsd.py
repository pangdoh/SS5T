import socket
import threading
from utils import Debug
from core import Constants
from core.protos import ss5clt


# 转发数据
def forward_data(conn, target_host, target_port):

    # 创建连接对象
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)

    if Constants.proxy:
        clt_conn_flag = False
        forward_recv_flag = False
    else:
        clt_conn_flag = True
        forward_recv_flag = True

    while True:
        try:
            tmp_data = conn.recv(1024)
        except ConnectionAbortedError:
            break
        except OSError:
            break
        Debug.log('接收3：', tmp_data)
        if not tmp_data:
            break
        else:
            # 是否需要前置代理
            if Constants.proxy:
                ss5clt.ss5forward(tmp_data, s, conn)
            else:
                if clt_conn_flag:
                    clt_conn_flag = False
                    # 与目标建立连接
                    s.connect((target_host, target_port))

                if Constants.proxy is None:
                    # 转发数据
                    s.send(tmp_data)

                if forward_recv_flag:
                    forward_recv_flag = False
                    # 接收请求
                    tr = threading.Thread(target=forward_recv, args=(s, conn))
                    tr.start()

    # 关闭目标连接
    Debug.log("关闭目标连接")
    try:
        s.close()
    finally:
        conn.close()
    Debug.log("----------------------第三次交互完毕------------------------------")


# 接收并返还客户端
def forward_recv(s, conn):
    while True:
        try:
            tmp_data = s.recv(4096)
            Debug.log('响应3:', tmp_data)
            if not tmp_data:
                break
            else:
                conn.send(tmp_data)
        except ConnectionAbortedError:
            Debug.log('ConnectionAbortedError')
            break
        except OSError:
            Debug.log("OSError")
            break
        except socket.timeout:
            Debug.log('timeout')
            break
