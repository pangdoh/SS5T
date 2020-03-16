from core import protocmsd
from utils import Debug
import socket
import struct


def ss4forward(data, conn):
    VN_C = data[0:1]
    CD_C = data[1:2]
    DSTPORT_C = data[2:4]
    DSTIP_C = data[4:8]
    USERID_C = data[8:-1]
    NULL_C = data[-1:]

    dst_port = int(DSTPORT_C.hex(), 16)
    if DSTIP_C == b'\x00\x00\x00\x01':
        dspip = USERID_C[1:].decode()
    else:
        dspip = socket.inet_ntoa(struct.pack('!L', int(DSTIP_C.hex(), 16)))

    Debug.log('VN', VN_C)
    Debug.log('CD', CD_C)
    Debug.log('DSTPORT', dst_port)
    Debug.log('DSTIP', DSTIP_C)
    Debug.log('USERID', USERID_C)
    Debug.log('Null', NULL_C)
    Debug.log('dspip', dspip)

    # 响应
    VN_C = b'\x00'
    CD_D = b'\x5A'
    DSTPORT_D = DSTPORT_C
    DSTIP_D = DSTIP_C
    r_send = VN_C + CD_D + DSTPORT_D + DSTIP_D
    Debug.log("响应1:", r_send)
    conn.send(r_send)

    Debug.log('------------认证过程结束-----------')

    # 开始转发数据
    target_host = dspip
    target_port = dst_port
    protocmsd.forward_data(conn, target_host, target_port)
