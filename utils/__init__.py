from urllib import parse
from core import Constants


# 解析url
def parse_urls(url):
    proto = 'http'
    up = parse.urlparse(url)
    if up.scheme != "":
        proto = up.scheme
    dst = up.netloc.split(":")
    if len(dst) == 2:
        port = int(dst[1])
    else:
        if proto == "http":
            port = 80
        elif proto == "https":
            port = 443
        else:
            port = 0
    host = dst[0]
    path = up.path
    query = up.query
    if path is None or path == '':
        path = '/'
    return proto, host, port, path, query


# 数字类型IP地址转换为字符串
def ip_int2str(num):
    s = []
    for i in range(4):
        s.append(str(num % 256))
        num /= 256
    result = ''
    for i in s[::-1]:
        result += str(int(float(i))) + '.'
    if result.endswith('.'):
        result = result[:-1]
    return result


class Debug:

    @staticmethod
    def log(s, *args):
        if Constants.debug:
            print(s, *args)
