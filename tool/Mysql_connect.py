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



if __name__=="__main__":
    Mysql_gld()

