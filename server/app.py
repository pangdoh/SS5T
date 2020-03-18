import argparse
import threading
import time

from core import Constants
from core import runserver

# 命令行参数解析对象
parser = argparse.ArgumentParser()
parser.add_argument('-host', dest='bind_address', default='0.0.0.0', help='Listen Host(default=%s)' % '0.0.0.0')
parser.add_argument('-port', dest='bind_port', type=int, default=1899, help='Listen Port(default=%d)' % 1899)
parser.add_argument('-auth', dest='auth', help='User authentication, -auth /etc/users')
parser.add_argument('-proxy', dest='proxy', help='Preposition proxy. eg. -proxy user1:pass1@10.0.0.2:1088')
parser.add_argument('--debug', dest='debug', help='Start by Debug', action='store_true')
parser.add_argument('--daemon', dest='daemon', help='Start by Daemons', action='store_true')

# 解析命令行参数
args = parser.parse_args()
bind_address = args.bind_address
bind_port = args.bind_port
auth = args.auth
proxy = args.proxy
debug = args.debug
daemon = args.daemon

# 日志
print("Listening %s:%d" % (bind_address, bind_port))

debug = True
# 研发过程默认开启debug
proxy = 'admin:123456@192.168.0.100:1899'
# auth = "admin:123"

# 设置前置代理信息
if proxy:
    if proxy.find('@') != -1:
        proxy_ss = proxy.split('@')
        proxy_ss1 = proxy_ss[0]
        proxy_ss2 = proxy_ss[1]
        proxy_s1 = proxy_ss1.split(':')
        proxy_s2 = proxy_ss2.split(':')
    else:
        proxy_s1 = [None, None]
        proxy_s2 = proxy.split(':')
    proxy = {
        'usr': proxy_s1[0],
        'pwd': proxy_s1[1],
        'proxy_address': proxy_s2[0],
        'proxy_port': int(proxy_s2[1]),
    }
    print('前置代理:', proxy)

# 设置认证密码
auth_usr_lst = []
if auth:
    if auth.find(":") != -1:
        usr = auth.split(':')[0]
        pwd = auth.split(':')[1]
        auth_usr_lst.append({'usr': usr, 'pwd': pwd})
    else:
        with open(auth) as f:
            for line in f:
                line = line.strip()
                usr = line.split(':')[0]
                pwd = line.split(':')[1]
                auth_usr_lst.append({'usr': usr, 'pwd': pwd})
    print('用户认证：', auth_usr_lst)

# 设置常量
Constants.auth_usr_lst = auth_usr_lst
Constants.bind_address = bind_address
Constants.bind_port = bind_port
Constants.current_num = 512
Constants.proxy = proxy
Constants.auth = auth
Constants.debug = debug

t = threading.Thread(target=runserver.start)
t.setDaemon(True)
t.start()
try:
    while True:
        # 使用Ctrl + c 终止服务
        time.sleep(60)
except KeyboardInterrupt:
    print('---------------------------------------------')
    print('end server')
