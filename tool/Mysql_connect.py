import sys
sys.path.append('../')
from tool.Mysql_public import Mysql_operation
from tool.OperationDatas import OperationYaml
import pymysql

class Config(object):
    def __init__(self):
        config=OperationYaml().read_data()
        self.dataBaseConfig=config['config']

class Mysql_tencentcloud(Mysql_operation,Config):
    def __init__(self):
        Config.__init__(self)
        tencent_cloud_mysql_conf=self.dataBaseConfig['tencent_cloud_mysql_conf']
        tencent_cloud_mysql_conf['db'] = 'test_datas'
        tencent_cloud_mysql_conf["cursorclass"]=pymysql.cursors.DictCursor
        super().__init__(**tencent_cloud_mysql_conf)

#
# class Mysql_local(Mysql_operation):
#     def __init__(self):
#         local_mysql_conf['db']='blocwechat'
#         super().__init__(**local_mysql_conf)


if __name__=="__main__":
    pass
    # fwh=Mysql_test_fwh()
    # crm = Mysql_test_crm()
    tencent_cloud=Mysql_tencentcloud()
    data=tencent_cloud.sql_operation_limit('''select  course_name_id from nc_course_name where course_class_id='7' and is_put=1''')
    print(data)
    # dev=Mysql_CorporateUniversity_dev()
    # test=Mysql_CorporateUniversity_test()
    #
    # sql='''select *from fw_course_order_push_crmlog where co_id='47875' ;'''
    # a=fwh.sql_operation(sql)
    # print(a)
    # sql='''select *from nc_admin where tel='18883612485' ;'''
    # b=crm.sql_operation(sql)
    # print(b)
    # t=tencent_cloud.sql_operation('''select *from order_info limit 10;''')
    # print(t)
