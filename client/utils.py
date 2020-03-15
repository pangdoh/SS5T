from urllib import parse


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
    host = dst[0]
    path = up.path
    query = up.query
    if path is None or path == '':
        path = '/'
    return proto, host, port, path, query


proto, host, port, path, query = parse_urls('http://www.baidu.com/123/abc/456')
print("proto:", proto)
print("host:", host)
print("port:", port)
print("path:", path)
print("query:", query)
