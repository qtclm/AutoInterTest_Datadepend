#Author:Mr.Qin
import sys
sys.path.append('../')
from tool.get_token import Crm_token
from tool.fwh_get_token import fwh_token
from tool.Operation_logging import logs

def token_crm(func):
    token=Crm_token()
    def test_in(*args,**kwargs):
        token_list=token.loadTokenList()
        if token_list is None:
            token.writeTokenToFile()
            print("token写入成功")
            token_list=token.loadTokenList()
            print("token读取成功")
        return func(*args,**kwargs)
    return test_in


def token_fwh(func):
    token=fwh_token()
    def test_in(*args,**kwargs):
        token_list=token.loadTokenList()
        if token_list is None:
            token.writeTokenToFile()
            print("token写入成功")
            token_list=token.loadTokenList()
            print("token读取成功")
        return func(*args,**kwargs)
    return test_in

def log_control(func):
    log=logs()
    def test_in(*args,**kwargs):
        log.info('开始执行')
        return func(*args,**kwargs)
    log.info('执行完毕')
    return test_in

# 检测参数是否为空
def args_None(func):
    def test_in(*args,**kwargs):
        # print(len(args))
        # print(kwargs)
        if (len(args)==1 or args is None) and  (kwargs)=={}:
            return None
        else:
            return func(*args,**kwargs)
    return test_in

