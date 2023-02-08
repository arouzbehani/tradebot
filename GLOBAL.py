import os

# BASE_DIR = '/root/trader_webapp/'

BASE_DIR = 'C:\\Users\\Ahmad\\Desktop\\tradebot\\'
local_base_dir = 'C:\\Users\\Ahmad\\Desktop\\tradebot\\'
server_base_dir = '/root/trader_webapp/'

def BASE(relp=False):
    if relp : return local_base_dir
    return server_base_dir
def LOCALIZE(path,local=False):
    if local:
        return os.path.join(BASE(local),path.replace("/","\\"))
    return os.path.join(BASE(local),path)
    