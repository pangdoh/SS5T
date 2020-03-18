from core import protocmsd
from core import Constants
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
        Constants.ATYP_C2 = b'\x03'
        Constants.DST_ADDR_LEN_C2 = len(USERID_C[1:]).to_bytes(1, 'big')
        Constants.DST_ADDR_C2 = USERID_C[1:]
    else:
        dspip = socket.inet_ntoa(struct.pack('!L', int(DSTIP_C.hex(), 16)))
        Constants.ATYP_C2 = b'\x01'
        Constants.DST_ADDR_C2 = DSTIP_C

    Constants.DST_PORT_C2 = DSTPORT_C

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
