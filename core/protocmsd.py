import socket
import threading

from core import Constants
from core.protos import ss5clt
from utils import Debug
from utils.encrypt import asymmetric


# 转发数据
def forward_data(conn, target_host, target_port, conn_box):

    # 创建连接对象
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)

    conn_box.clt_conn_flag = True
    conn_box.forward_recv_flag = True

    end_flag = conn_box.clt_end_flag
    retain_data = b''

    while True:
        if Constants.local_ssl:
            buffer = 2048
        else:
            buffer = 1024
        try:
            tmp_data = conn.recv(buffer)
        except ConnectionAbortedError:
            break
        except OSError:
            break
        if not tmp_data:
            break
        else:
            Debug.log('接收3：', tmp_data)
            if Constants.local_ssl:
                tmp_data = retain_data + tmp_data
                retain_data = b''
                if tmp_data.find(end_flag) == -1:
                    while True:
                        # 接收结束标记
                        tmp_data += conn.recv(buffer)
                        if tmp_data.find(end_flag) != -1:
                            break

                tmp_data_s = tmp_data.split(end_flag)
                for n in range(len(tmp_data_s)):
                    if n == len(tmp_data_s) - 1:
                        retain_data = tmp_data_s[n]
                        break
                    # 发送至下一节点
                    send_next_node(tmp_data_s[n], s, conn, conn_box, target_host, target_port)
            else:
                # 发送至下一节点
                send_next_node(tmp_data, s, conn, conn_box, target_host, target_port)

    Debug.log("----------------------第三次交互完毕------------------------------")


# 发送至下一节点
def send_next_node(tmp_data, s, conn, conn_box, target_host, target_port):
    if Constants.local_ssl:
        # 对称解密
        tmp_data = asymmetric.decrypt(tmp_data, conn_box.clt_random_key)
        Debug.log('对称解密接收3:', tmp_data)
    if conn_box.clt_conn_flag:
        conn_box.clt_conn_flag = False
        # 是否需要前置代理
        if Constants.proxy:
            # 与前置代理建立连接
            ss5clt.ss5conn(s, conn_box)
        else:
            # 与目标建立连接
            s.connect((target_host, target_port))

    # 转发数据
    Debug.log('转发数据：', tmp_data)
    if Constants.remote_ssl:
        # 对称加密
        tmp_data = asymmetric.encrypt(tmp_data, conn_box.random_key)
        Debug.log('对称加密:', tmp_data)
    s.send(tmp_data)
    if Constants.remote_ssl:
        # 发送结束标记
        s.send(conn_box.end_flag)

    if conn_box.forward_recv_flag:
        conn_box.forward_recv_flag = False
        # 接收数据并返还客户端
        tr = threading.Thread(target=forward_recv, args=(s, conn, conn_box))
        tr.start()


# 接收并返还客户端
def forward_recv(s, conn, conn_box):
    end_flag = conn_box.end_flag
    retain_data = b''
    while True:
        if Constants.remote_ssl:
            buffer = 4096
        else:
            buffer = 2048
        Debug.log("设置接收缓冲区大小", buffer)
        try:
            # 接收数据
            tmp_data = s.recv(buffer)
            if not tmp_data:
                break
            else:
                if Constants.remote_ssl:
                    tmp_data = retain_data + tmp_data
                    retain_data = b''
                    if tmp_data.find(end_flag) == -1:
                        while True:
                            # 接收结束标记
                            tmp_data += s.recv(buffer)
                            if tmp_data.find(end_flag) != -1:
                                break

                    tmp_data_s = tmp_data.split(end_flag)
                    for n in range(len(tmp_data_s)):
                        if n == len(tmp_data_s) - 1:
                            retain_data = tmp_data_s[n]
                            break
                        Debug.log('响应3:', tmp_data)
                        res_to_ctl(tmp_data_s[n], conn, conn_box)
                else:
                    Debug.log('响应3:', tmp_data)
                    res_to_ctl(tmp_data, conn, conn_box)
        except ConnectionAbortedError:
            Debug.log('ConnectionAbortedError')
            break
        except OSError:
            break
        except socket.timeout:
            Debug.log('timeout')
            break

    Debug.log('关闭连接', s, conn)
    try:
        s.close()
    except Exception as e:
        print(e)
    finally:
        conn.close()


# 发送给客户端数据
def res_to_ctl(data, conn, conn_box):
    if Constants.remote_ssl:
        # 对称解密
        data = asymmetric.decrypt(data, conn_box.random_key)
        Debug.log('对称解密响应3:', data)
    if Constants.local_ssl:
        # 对称加密
        data = asymmetric.encrypt(data, conn_box.clt_random_key)
        Debug.log('对称加密返还客户端响应3:', data)
    conn.send(data)
    if Constants.local_ssl:
        # 发送结束标记
        conn.send(conn_box.clt_end_flag)
