import sys
sys.path.append('../')
from tool.get_token import Crm_token
from tool.fwh_get_token import fwh_token
from tool.fwh_admin_get_token import fwh_admin_token

class global_val:
    #case_id
    __initnum=0
    Id=str(__initnum+1)
    request_name=str(__initnum+2)
    url=str(__initnum+3)
    run=str(__initnum+4)
    request_method=str(__initnum+5)
    header=str(__initnum+6)
    case_dapend=str(__initnum+7)
    key_depend=str(__initnum+8)
    field_depend=str(__initnum+9)
    data=str(__initnum+10)
    sql_statement=str(__initnum+11)
    sql_execute_result=str(__initnum+12)
    redis_statement=str(__initnum+13)
    redis_execute_result=str(__initnum+14)
    expect=str(__initnum+15)
    result=str(__initnum+16)
    #获取case_id及每列的数据

#  获取caseId
def get_case_id():
    return global_val.Id

# 获取请求名称
def get_request_name():
    return global_val.request_name

# 获取url
def get_url():
    return global_val.url

# 获取是否需要运行
def get_run():
    return global_val.run

#获取请求方式
def get_request_method():
    return global_val.request_method

# 获取header
def get_header():
    return global_val.header

#获取crmheader值
def get_crm_header():
    get_token=Crm_token()
    tokenValue=get_token.loadTokenList()[0]
    header={"Content-Type": "application/x-www-form-urlencoded","token":tokenValue}
    return header

#获取fwhheader值
def get_fwh_header():
    get_token=fwh_token()
    tokenValue=get_token.loadTokenList()[0]
    header={"Content-Type": "application/x-www-form-urlencoded","token":tokenValue}
    return header

#获取fwhadminheader值
def get_fwhadmin_header():
    get_token=fwh_admin_token()
    header=get_token.loadTokenList() 
    return header

#获取无token 认证header值
def get_header_no_token():
    header = {"Content-Type": "application/json"}
    return header

# 获取用例依赖
def get_case_dapend():
    return global_val.case_dapend

#获取数据依赖
def get_key_depend():
    return global_val.key_depend

#获取数据依赖字段
def get_field_depend():
    return global_val.field_depend

# 获取请求数据
def get_data():
    return global_val.data

# 获取预期结果
def get_expect():
    return global_val.expect

# 获取实际结果
def get_result():
    return global_val.result

# 获取sql语句
def get_sql_statement():
    return global_val.sql_statement

# 获取sql执行结果
def get_sql_execute_result():
    return global_val.sql_execute_result

# 获取redis语句
def get_redis_statement():
    return global_val.redis_statement

# 获取redis执行结果
def get_redis_execute_result():
    return global_val.redis_execute_result

if __name__=='__main__':
    pass
    # print(get_fwh_header())
    # print(get_crm_header())
    # print(get_fwhadmin_header())