# -*- coding: utf-8 -*-
"""    
__author__ = qtclm
File Name：     Mongo_connect
date：          2020/4/17 13:12 
"""

import sys
sys.path.append('../')
from tool.Mongo_public import OperationMongo
from tool.OperationDatas import OperationYaml

class Config(object):
    def __init__(self):
        config=OperationYaml().read_data()
        self.dataBaseConfig=config['config']

class Mongo_tencentcloud(OperationMongo,Config):
    def __init__(self):
        Config.__init__(self)
        host=self.dataBaseConfig['tencent_cloud_mongodb']['host']
        user=self.dataBaseConfig['tencent_cloud_mongodb']['user']
        password=self.dataBaseConfig['tencent_cloud_mongodb']['password']
        port=self.dataBaseConfig['tencent_cloud_mongodb']['port']
        db='creeper_test'
        super().__init__(host=host,user=user,password=password,port=port,db=db)
        # print('链接成功')

if __name__=='__main__':
    gld=Mongo_My()
    gld.select_one_collection('TestDataInfo',({}))
    # Mongo_gldexp()