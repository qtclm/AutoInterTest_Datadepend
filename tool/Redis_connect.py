import sys
sys.path.append('../')
from tool.Redis_public import OperationRedis
from tool.OperationDatas import OperationYaml

class Config(object):
    def __init__(self):
        config=OperationYaml().read_data()
        self.dataBaseConfig=config['config']

class Redis_tencentcloud(OperationRedis,Config):
    def __init__(self):
        Config.__init__(self)
        tencent_cloud_redis=self.dataBaseConfig['tencent_cloud_redis']
        tencent_cloud_redis['db'] = 0
        super().__init__(**tencent_cloud_redis)



if __name__=="__main__":
    pass
    # re=Redis_tencentcloud()
    # print(re.hash_getvalues('py'))


