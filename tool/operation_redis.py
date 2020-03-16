import redis
from tool.OperationDatas import OperationYaml


class OperationRedis(object):
    '''
    redis操作
    '''''
    def __init__(self, db_index=0):
        config = OperationYaml().read_data()
        self.DataBaseConfig = config['config']
        self.redisConfig = self.DataBaseConfig['tencent_cloud_redis']
        self.pool = redis.Connection(host=self.redisConfig['host'], password=self.redisConfig['password'], port=self.redisConfig['port'], db=db_index)
        self.r = redis.Redis(connection_pool=self.pool)
        self.pipeline = self.r.pipeline(transaction=True)

    # String操作
    # 在Redis中设置值，默认不存在则创建，存在则修改

    def string_set(self, key, valuve):
        # 参数：set(name, value, ex=None, px=None, nx=False, xx=False)
        #      ex，过期时间（秒）
        #      px，过期时间（毫秒）
        #      nx，如果设置为True，则只有name不存在时，当前set操作才执行,同setnx(name, value)
        #      xx，如果设置为True，则只有name存在时，当前set操作才执行
        return self.r.set(key, valuve)

    def string_mset(self, **kwargs):
        for k, v in kwargs.items():
            self.r.mset(k, v)

    # 设置过期时间，单位秒
    def string_set_EX(self, key, value, time):
        return self.r.setex(key, value, time=time)

    # 设置过期时间，单位毫秒
    def string_set_PX(self, key, time_ms, value):
        return self.r.psetex(key, time_ms=time_ms, value=value)

    def string_get(self, key):
        return self.r.get(key)

    def string_mget(self, key_list):
        return self.r.mget(key_list)

    # #在key对应的值后面追加内容
    def string_append(self, key, value):
        return self.r.append(key, value=value)

    # 设置新值，打印原值
    def string_getset(self, key, value):
        old_value = self.r.getset(key, value)
        return old_value

    # hash操作

    # 增
    def hash_hset(self, name, key, value):
        return self.r.hset()

    # 取多个值
    def hash_hmget(self, name, key_list):
        temp = {}
        for i in key_list:
            temp.setdefault(i, self.r.hget(name, i))
        return temp

    # 获取对应name所有的键值对
    def hash_hgetall(self, name):
        return self.r.hgetall(name)

    # 获取name对应的键值对个数
    def hash_hlen(self, name):
        return self.r.hlen(name)

    # 获取name中所有的key
    def hash_getkeys(self, name):
        return self.r.hkeys(name)

    # 获取name中所有的values
    def hash_getvalues(self, name):
        return self.r.hvals(name)

    # 检查传入的key是否存在于name的hash中
    def hash_hexists(self, name, key):
        return self.r.hexists(name, key)

    # 删除name中的key对应的键值
    def hash_delete(self, name, key):
        self.r.hdel(name, key)
        return None

    # list操作

    # 往list的最左边添加值
    def list_lpush(self, list_name, value):
        return self.r.lpush(list_name, value)

    # 往list的最右边添加值
    def list_rpush(self, list_name, value):
        return self.r.rpush(list_name, value)

    # 在name对应的list中添加元素，只有name已经存在时，值添加到列表的最左边
    def list_lpushx(self, list_name, value):
        return self.r.lpushx(list_name, value)

    # 在name对应的list中添加元素，只有name已经存在时，值添加到列表的最右边
    def list_rpushx(self, list_name, value):
        return self.r.rpushx(list_name, value)

    # 往list中置顶位置插入值
    # linsert(name, where, refvalue, value))  其中where: BEFORE（前）或AFTER（后）, refvalue: 列表内的值
    # value: 要插入的数据
    def list_insert(self, name, where, refvalue, value):
        return self.r.linsert(name, where, refvalue, value)

    # 对list中某个索引重新赋值
    def list_lset(self, name, index, value):
        return self.r.lset(name, index, value)

    # 弹出最左侧第一个元素
    def list_pop(self, name):
        return self.r.lpop(name)

    # 从一个列表取出最右边的元素，同时将其添加至另一个列表的最左边
    def list_rpoplpush(self, from_pop_name, to_push_name):
        return self.r.rpoplpush(from_pop_name, to_push_name)

    # 查询list对应的元素个数
    def list_len(self, name):
        return self.r.llen(name)

    # 根据索引获取list对应的值
    def list_index(self, name, index):
        return self.lindex(name, index)

    # 移除list中索引没在范围内的值
    def list_trim(self, name, start_index, end_index):
        return self.r.ltrim(name, start_index, end_index)

    # set 操作

    # set中添加元素
    def set_add(self, name, value):
        return self.r.sadd(name, value)

    # 从某个set只移动至另外一个set
    def set_move(self, from_set_name, to_set_name, value):
        return self.r.smove(from_set_name, to_set_name, value)

    # 从set的最右侧弹出一个元素并返回
    def set_pop(self, name):
        return self.r.spop(name)

    # 查询name中的所有成员
    def set_members(self, name):
        return self.r.smembers(name)

    # 获取name对应的集合中的元素个数
    def set_len(self, name):
        return self.r.scard(name)

    # 从name对应的集合中随机获取numbers个元素
    def set_randmember(self, name, num):
        return self.r.srandmember(name, num)

    # 检查value是否是name对应的集合内的元素
    def set_ismember(self, name, value):
        return self.r.sismember(name, value)

    def execute(self):
        self.pipeline.execute()

if __name__=="__main__":
    OperationRedis()