import argparse
from server import runserver


# 命令行参数解析对象
parser = argparse.ArgumentParser()
parser.add_argument('-host', dest='bind_address', default='0.0.0.0', help='Listen Host(default=%s)' % '0.0.0.0')
parser.add_argument('-port', dest='bind_port', type=int, default=1080, help='Listen Port(default=%d)' % 1080)

# 解析命令行参数
args = parser.parse_args()
bind_address = args.bind_address
bind_port = args.bind_port

current_num = 127

runserver.start(bind_address, bind_port, current_num, auth=False)
