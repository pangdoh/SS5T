import socket

ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '0.0.0.0'
port = 1088
ss.bind((host, port))
ss.listen(50)

while True:
    # 建立客户端连接
    conn, address = ss.accept()

    print("连接地址: %s" % str(address))

    data = conn.recv(1024)
    print(data)

    target_host = ''
    target_port = 80
    # 获取目标地址
    if data.find(b'HTTP/1.') != -1:
        h_data = data[:data.find(b'\r\n\r\n')]
        header_lines = h_data.split(b'\r\n')
        for header_line in header_lines:
            if header_line.find(b': ') == -1:
                continue
            tmp_key = header_line.split(b': ')[0]
            if tmp_key.lower() == b'host':
                tmp_value = header_line.split(b': ')[1]
                if tmp_value.find(b':') != -1:
                    target_host = tmp_value.split(b':')[0].decode()
                    target_port = tmp_value.split(b':')
                else:
                    target_host = tmp_value.decode()
                break

    print("转发至: %s %d" % (target_host, target_port))
    # 发送请求
    tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpCliSock.connect((target_host, target_port))
    while True:
        tcpCliSock.send(data)  # 发送消息
        data = tcpCliSock.recv(1024)  # 读取消息
        if not data:
            break
        print(data)

    tcpCliSock.close()  # 关闭连接

    # 返回给客户端
    conn.send(data)
    # conn.close()
