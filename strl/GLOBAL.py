import os

local_base_dir = 'C:\\Users\\Ahmad\\Desktop\\tradebot\\'
server_base_dir = '/root/trader_webapp/'

def BASE_DIR(local=False):
    if local : return local_base_dir
    return server_base_dir
def ABSOLUTE(path,local=False):
    if local:
        return os.path.join(BASE_DIR(local),path.replace("/","\\"))
    return os.path.join(BASE_DIR(local),path)
    