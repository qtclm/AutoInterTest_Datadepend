from tool.OperationRequestData import operationRequestData
from tool.operation_logging import MyLog,logs
from tool.runmethod import RunMethod
from tool.CommonAssert import CommonAssert
from tool.send_email import SendEmail
from tool.OperationDatas import OperationYaml,OperationJson

# '''基础方法'''
class Tool(object):
    def __init__(self):
        self.requestDataDispose=operationRequestData()#请求数据处理
        self.mylog=MyLog.get_log()#日志
        self.log = self.mylog.get_logger()#获取日志创建对象
        self.run_method = RunMethod()#通过请求封装
        self.com_assert = CommonAssert()#通用预期与实际结果判断
        self.send_mail=SendEmail()#邮件发送
        self.json=OperationJson()
        # 默认读取config，此文件只读不写
        self.yaml=OperationYaml().readDataForKey('config')
        

# '''数据库操作相关'''
from tool.Mysql_connect import Mysql_tencentcloud
from tool.operation_redis import OperationRedis
from tool.operation_mongodb import OperationMongo
class ToolALL(Tool):
    def __init__(self):
        super().__init__()
        # self.my_op_crm=Mysql_test_crm()
        # self.my_op_fwh=Mysql_test_fwh()
        self.tencent_cloud=Mysql_tencentcloud()
        self.redis=OperationRedis()
        self.mongo=OperationMongo()
