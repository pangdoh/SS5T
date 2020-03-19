# 系统信息
class Constants:
    publicKey = None
    privateKey = None
    bind_address = None
    bind_port = None
    current_num = None
    proxy = None
    auth = None
    debug = None
    debug_dev = None
    auth_usr_lst = None
    conn_encryption = None
    local_ssl = None
    remote_ssl = None
    random_key = None


# 连接信息
class ConnVariable:
    def __init__(self, conn):
        self.conn = conn
        self.conn = None
        self.VER_C2 = None
        self.CMD_C2 = None
        self.RSV_C2 = None
        self.ATYP_C2 = None
        self.DST_ADDR_LEN_C2 = None
        self.DST_ADDR_C2 = None
        self.DST_PORT_C2 = None
        self.SYMMETRIC_KEY = None
        self.client_public_key = None
        self.server_public_key = None
        self.clt_random_key = None
        self.random_key = None
        self.clt_end_flag = None
        self.end_flag = None
