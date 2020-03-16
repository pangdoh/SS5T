import argparse
import threading
import time
from core import runserver
from core import Constants

# 命令行参数解析对象
parser = argparse.ArgumentParser()
parser.add_argument('-host', dest='bind_address', default='0.0.0.0', help='Listen Host(default=%s)' % '0.0.0.0')
parser.add_argument('-port', dest='bind_port', type=int, default=1899, help='Listen Port(default=%d)' % 1899)
parser.add_argument('-auth', dest='auth', help='User authentication, -auth /etc/users')
parser.add_argument('--debug', dest='debug', help='Start by Debug', action='store_true')
parser.add_argument('--daemon', dest='daemon', help='Start by Daemons', action='store_true')

# 解析命令行参数
args = parser.parse_args()
bind_address = args.bind_address
bind_port = args.bind_port
auth = args.auth
debug = args.debug
daemon = args.daemon

# 日志
print("Listening %s:%d" % (bind_address, bind_port))

# 研发过程默认开启debug
debug = True

# 设置常量
Constants.auth_usr_lst = []
Constants.bind_address = bind_address
Constants.bind_port = bind_port
Constants.current_num = 512
Constants.auth = auth
Constants.debug = debug

# 设置认证密码
if auth:
    if auth.find(":") != -1:
        usr = auth.split(':')[0]
        pwd = auth.split(':')[1]
        Constants.auth_usr_lst.append({'usr': usr, 'pwd': pwd})
    else:
        with open(auth) as f:
            for line in f:
                line = line.strip()
                usr = line.split(':')[0]
                pwd = line.split(':')[1]
                Constants.auth_usr_lst.append({'usr': usr, 'pwd': pwd})
    print(Constants.auth_usr_lst)


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
