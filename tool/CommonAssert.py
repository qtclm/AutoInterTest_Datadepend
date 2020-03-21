from tool.operation_logging import logs

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
            if str_one in str_two :
                flag=True
            else:
                flag=False
            self.log.info('flag:{}'.format(flag))
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
                # 将字典key对应的value批量转换为字符串，避免转换为set时错误，因为set对象不能是可变类型
                dict_one_k=[s for s in dict_one.keys()]
                dict_two_k = [s for s in dict_two.keys()]
                if dict_one_k==dict_two_k:
                    for i in dict_one_k:
                        one_str=dict_one[i]
                        two_str=dict_two[i]
                        if isinstance(two_str,list):
                            for _two in two_str:
                                # 如果元素在list中，直接跳出循环
                                if one_str==_two:
                                    temp=True
                                    break
                                else:
                                    temp=False
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
    cm=CommonUtil()
    cm.is_equal_dict('122','kkkdkdk')
    a = '1222as@@'

