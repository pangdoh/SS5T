import socket
import threading

bind_address = '0.0.0.0'
bind_port = 1099
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((bind_address, bind_port))
s.listen(127)
conn, address = s.accept()
print("连接地址: %s" % str(address))
data = conn.recv(1024)
print("接收1: %s" % data)

target_host = ''
target_port = 0

# 提取目标
if data.find(b'HTTP/1.') != -1:
    headerStateLine = data[:data.find(b'\n')]
    print('headerStateLine:', headerStateLine)
    lines = headerStateLine.split(b' ')
    target = lines[1]
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


# 建立连接
clt_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clt_s.connect((target_host, target_port))
clt_s.send(data)

while True:
    tmp_date = clt_s.recv(1024)
    if not tmp_date:
        break
    print(tmp_date)

    # 返还给客户端
    conn.send(tmp_date)
conn.close()
