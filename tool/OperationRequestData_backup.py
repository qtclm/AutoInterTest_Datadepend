import re
import hashlib
import base64
import time
import datetime
import sys
sys.path.append('../')
from tool.OperationDatas import OperationYaml
# today=datetime.date.today() #获取当前日期
today=datetime.datetime.now().strftime('%Y%m%d')#获取当前日期

class operationRequestData(object):
    def __init__(self):
        config=OperationYaml().read_data()
        self.fwhConfig=config['fwh']
        
    # '''将带有time关键字的参数放到字符串末尾'''
    def standardStr(self, str_in):
        spilt_sign = '\n'
        split_list = str_in.split(spilt_sign)
        # '''获取参数中带有time得参数'''
        __time = [i for i in split_list if 'time' in i]
        # '''过滤参数中带有time得参数'''
        __nottime = [i for i in split_list if 'time' not in i]
        # 将带有time参数的str追加至不带time的末尾
        __nottime.extend(__time)
        str_out = spilt_sign.join(__nottime)
        return str_out, __nottime
    
    # ''' 针对时间特殊处理'''
    def format_timeStr(self, str_in, space_one, space_two, colon_search, str_lin2_search='\s.*'):
        # '''str_lin2_search：正则表达式3：用于匹配时间'''
        # print(str_in)
        time_str = re.search('time.*', str_in)
        lastTime_list = []
        if time_str:
            time_str = time_str.group()
            split_time = time_str.split(space_two)
            for i in split_time:
                regex_str1 = re.search(str_lin2_search, i)
                if regex_str1:
                    regex_str1 = regex_str1.group()
                    regex_sub1 = re.sub(space_one, colon_search, regex_str1)
                    i = re.sub(regex_str1, regex_sub1, i)
                    lastTime_list.append(i)
                else:
                    return None
            lastTime_str = space_two.join(lastTime_list)
            str_out = re.sub(time_str, lastTime_str, str_in)
            return str_out
        else:
            return None
    
    # '''常规字符处理，用于处理chrome复制出来的表单数据，输出k1=v1&k2=v2... '''
    def requestDataConventions(self, str_in, space_one='=', space_two='&', time_str='time', colon_search=':',
                               str_colon_search=':\W?|\s*:\W?', str_lin_search="(\s\n*){2,}|(\s\n*)"):
        '''space_one:用于将冒号替换（key——value），space_two：key-value连接符，colon_search:针对时间添加冒好，'time_str':时间字符串
        str_colon_search：正则表达式1（匹配冒号），str_lin_search:正则表达式（匹配换行符）'''
        str_in = self.standardStr(str_in)[0]
        try:
            str_colon = re.search(str_colon_search, str_in)  # 匹配出字符串中所有的冒号
            if str_colon:
                str_colon = str_colon.group()
                str_equal = re.sub(str_colon, space_one, str_in)  # 将字符串中的冒号替换为等于号(: >>> =)
                str_lin = re.search(str_lin_search, str_equal)  # 匹配出字符串中所有的换行符与空格,不写表示不限定匹配次数
                if str_lin:
                    str_lin = str_lin.group()
                    str_give = re.sub(str_lin, space_two, str_equal)  # 将字符串中的换行符替换为& (\n >>> &)
                    # '''参数time特殊处理'''
                    last_give = self.format_timeStr(str_give, space_one, space_two, colon_search)
                    if last_give:
                        return last_give.encode()
                    else:
                        return str_give.encode()
                else:
                    return str_equal.encode()
            else:
                print("字符串格式匹配错误")
                return None
        except Exception as error:
            print("数据处理失败，原因为:\n%s" % (error))
    
    # '''针对firefox复制出来的请求参数做单独处理'''
    def requestDataSpecial(self, str_in, space_one='=', space_two='&', time_str='time', colon_search=':',
                           str_colon_search='(\s+){1,}', str_lin_search="(\s\n*){2,}|(\s\n*)"):  # 特殊处理
        '''space_one:用于将冒号替换（key——value），space_two：key-value连接符，colon_search:针对时间添加冒好，'time_str':时间字符串
        str_colon_search：正则表达式1（匹配冒号），str_lin_search:正则表达式（匹配换行符）'''
        return self.requestDataConventions(str_in, str_colon_search=str_colon_search)