# -*- coding: utf-8 -*-

from tool.Operation_logging import logs

#判断字符串是否包含，判断字典是否相等
class CommonAssert(object):
    def __init__(self):
        self.log=logs().get_logger()
    def is_contain(self,str_one,str_two):
        '''判断字符串是否在另一个字符串中
        str_one:查找的字符串
        str_two:被查找的字符串
        '''
        flag=None
        '''
        if isinstance(str_one,unicode):
            str_one = str_one.encode('unicode-escape').decode('string_escape')
        return cmp(str_one,str_two)
        '''
        if str_one and str_two:
            if not (isinstance(str_one,str) and isinstance(str_two,str)):
                str_one=str(str_one)
                str_two=str(str_two)
            # 手动忽略空格与单双引号
            str_one=str_one.replace(' ', '')
            str_two=str_two.replace(' ', '')
            str_one=str_one.replace("'", '"')
            str_two=str_two.replace("'", '"')
            if str_one in str_two :
                flag=True
            else:
                flag=False
            self.log.info('flag:{}'.format(flag))
            self.log.info('dict_one:{}'.format(str_one))
            self.log.info('dict_two:{}'.format(str_two))
            return flag
        else:
            return False
    
    def is_equal_dict(self,dict_one,dict_two):
        '''判断字典1是否存在于字典2,将两个字典转换为set来实现'''
        flag=None
        # set的issubset方法，a.issubset(b) :判断集合 a 的所有元素是否都包含在集合 b 中,a必须是set，b可以是set，可以是dict
        if isinstance(dict_one,dict) and isinstance(dict_two,dict):
            if dict_one and dict_two:
                # 将字典key对应的value批量转换为字符串，避免转换为set时错误，因为set对象不能是可变类型
                dict_one=dict(zip( [i for i in dict_one.keys()],[str(v) for v in dict_one.values() ] ))
                dict_two = dict(zip([i for i in dict_two.keys()], [str(v) for v in dict_two.values()]))
                # 将dict转换为set
                dict_one = set(dict_one.items())
                dict_two=set(dict_two.items())
                self.log.info('dict_one:{}'.format(dict_one))
                self.log.info('dict_two:{}'.format(dict_two))
                flag=dict_one.issubset(dict_two)
            else:
                flag=False
        else:
            flag=False
        self.log.info('flag:{}'.format(flag))
        return flag
            
    def is_equal_dict_sql_except(self,dict_one,dict_two):
        '''判断字典1是否存在于字典2,将两个字典转换为set来实现'''
        # set的issubset方法，a.issubset(b) :判断集合 a 的所有元素是否都包含在集合 b 中,a必须是set，b可以是set，可以是dict
        temp = False
        if isinstance(dict_one,dict) and isinstance(dict_two,dict):
            if dict_one and dict_two:
                self.log.info('dict_one:{}'.format(dict_one))
                self.log.info('dict_two:{}'.format(dict_two))
                # 获取两个dict所有的key，用来比较
                dict_one_k=[s for s in dict_one.keys()]
                dict_two_k = [s for s in dict_two.keys()]
                if dict_one_k==dict_two_k:
                    for i in dict_one_k:
                        # 拿到两个字典key对应的value拿来比较
                        one_str=dict_one[i]
                        two_str=dict_two[i]
                        if isinstance(two_str,list):
                            # 如果dcit的元素不在dict2中：直接判定失败，否则：标识true继续循环
                            if  not (one_str in two_str):
                                temp=False
                                return temp
                            else:
                                temp=True
                                continue
                        else:
                            if one_str==two_str:
                               temp=True
                            else:
                                temp=False
                                return temp
                    return temp
                else:
                    temp=False
                    return temp
            else:
                temp=False
                return temp
        else:
            temp=False
            return temp
            

        
if __name__=="__main__":
    import json
    cm=CommonAssert()
    dict1={'course_name_id': 170, 'course_name': '校长，别再那么累--招生赢天下，管理定江山'}
    dict2={'course_name_id': [188, 184, 170, 2, 86, 3], 'course_name': ['抢跑“开学季”——朗培F4导师开学21天陪练营”', '校长，别再那么累--招生赢天下，管理定江山test', '校长，别再那么累--招生赢天下，管理定江山', '校长，别再那么累2.0-打赢营销战', '教培业盈利高增长运营模式3.0', '解放校长，管理不再累2.0']}
    falg=cm.is_equal_dict_sql_except(dict1,dict2)


