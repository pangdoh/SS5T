import argparse
from client import core


# 命令行参数解析对象
parser = argparse.ArgumentParser()
parser.add_argument('-bind_address', dest='bind_address', default='0.0.0.0', help='bind_address')
parser.add_argument('-bind_port', dest='bind_port', type=int, default=1080, help='bind_port')
parser.add_argument('-host', dest='host', help='Proxy-Server Host')
parser.add_argument('-port', dest='port', type=int, help='Proxy-Server Port')

# 解析命令行参数
args = parser.parse_args()
bind_address = args.bind_address
bind_port = args.bind_port
host = args.host
port = args.port

core.start(bind_address, bind_port)


