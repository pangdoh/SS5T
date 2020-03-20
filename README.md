# SS5T

socks4/5连接工具（懂得都懂，不解释） 支持前置代理

正常启动ss服务：python3 app.py

python3 app.py -h 查看更多参数

远端代理目前只支持socks5

远端加密传输方式启动：

浏览器 ---> 节点1:python3 app.py -proxy admin:123@10.0.1.30:1899 --remotessl ---> 节点2:python3 app.py -auth admin:123 --localssl


