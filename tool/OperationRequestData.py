import re
import hashlib
import base64
import time
import datetime
import sys
sys.path.append('../')
from tool.OperationDatas import OperationYaml
from tool.operation_logging import logs
from jsonpath_rw import parse
today=datetime.datetime.now().strftime('%Y%m%d')#获取当前日期


class operationRequestData(object):
    def __init__(self):
        config=OperationYaml().read_data()
        self.fwhConfig=config['config']
        self.log=logs()
        
    # 根据jsonpath提取数据
    def depend_data_parse(self,depend_key,response_data,index='one'):
        __dict={}#存放字典
        '''处理依赖'''
        if depend_key:
            # 定义要获取的key
            json_exe = parse(depend_key)
            # 定义响应数据,key从响应数据里获取
            madle = json_exe.find(depend_key)
            depend_data_index = depend_key.rfind('.')
            depend_data_str = depend_key[depend_data_index + 1:]
            # math.value返回的是一个list，可以使用索引访问特定的值jsonpath_rw的作用就相当于从json里面提取响应的字段值
            try:
                math_value = [i.value for i in madle]
                if math_value:
                    math_value=math_value
                    if index=='one':
                        math_value=math_value[0]
                    __dict[depend_data_str]=math_value
                    return __dict
            except IndexError as indexerror:
                return None
        else:
            return None

    # 输入字符串，输出字符串的大小写与首字母大写以及字符串本身
    def strOutputCase(self,str_in):
        if isinstance(str_in,str):
            str_in=str_in
        else:
            str_in=str(str_in)
        out_str_tuple=(str_in,str_in.lower(),str_in.upper(),str_in.capitalize())
        return out_str_tuple
    
    # '''将带有time关键字的参数放到字符串末尾'''
    def standardStr(self,str_in,kw_str='time',kw_str2='sign'):
        spilt_sign='\n'
        split_list=str_in.split(spilt_sign)
        # print(self.log.out_varname(split_list))
        str_out=''
        # '''获取参数中带有time、sign得参数'''
        __time=[i for i in split_list if kw_str in i ]
        __sign=[i for i in split_list if kw_str2 in i]
        # '''过滤参数中带有time得参数'''
        __nottime=[i for i in split_list if not i in __time or __sign]
        # '''如果list个数大于等于2，代表至少有两个请求参数，直接正常拼接字符串'''
        if len(__nottime)>=2:
            str_out = spilt_sign.join(__nottime)
        # '''如果list个数为0，代表至少过滤后没有请求参数，这时候手动将time参数赋值给list，防止处理出错,直接使用空字符串拼接'''
        elif len(__nottime)==0 :
            __nottime.extend(__time)
            # '''判断__time的个数'''
            if len(__time) == 1:
                str_out = ''.join(__nottime)
            elif len(__time)==0:
                print("参数都没有，还处理个球嘛")
                return None
            else:
                str_out = spilt_sign.join(__nottime)
        # 否则代表list只有一个参数，直接使用空字符串拼接
        else:
            str_out =''.join(__nottime)
        return str_out

    def strToDict(self, str_in):
        # '''将str转换为dict输出'''
        # '''将带有time关键字的参数放到字符串末尾'''
        str_in=self.standardStr(str_in)
        # print(str_in)
        if str_in:
            match_str = ':'
            split_str = '\n'
            split_list = str_in.split(split_str)
            str_in_dict = {}
            for i in split_list:
                colon_str_index = i.find(match_str)
                if colon_str_index == -1:
                    # '''处理firefox复制出来的参数'''
                    match_str = '\t' or ' '
                    colon_str_index = i.find(match_str)
                # '''去掉key、value的空格,key中的引号'''
                str_in_key = i[:colon_str_index].strip()
                str_in_key = str_in_key.replace('"','')
                str_in_key = str_in_key.replace("'",'')
                # 正则过滤无用key,只保留key第一位为字母数据获取[]_
                str_sign = re.search('[^a-zA-Z0-9\_\[\]+]', str_in_key[0])
                if str_sign is None:
                    # 处理value中的空格与转义符
                    str_in_value = i[colon_str_index + 1:].strip()
                    str_in_value=str_in_value.replace('\\','')
                    try:
                        # 遇到是object类型的数据转换一下
                        str_in_value=eval(str_in_value)
                    except BaseException as error:
                        str_in_value=str_in_value
                    str_in_dict[str_in_key] = str_in_value
            return str_in_dict
        else:
            print("参数都没有，还处理个球嘛")
            return None
    
    #将断言中的true/false/null，转换为python对象
    def assert_pyobject(self,str_in):
        str_dict=self.strToDict(str_in)
        __temp_dict={}
        for k,v in str_dict.items():
            if v=='true':
                v=True
            elif v=='flase':
                v=False
            elif v=='null':
                v=None
            __temp_dict[k]=v
        # print(__temp_dict)
        return __temp_dict
        
        
    # dependkey生成
    def denpendKeyGenerate(self,str_in,join_str=''):
        if not isinstance(str_in,dict):
            str_dict=self.strToDict(str_in)
        else:
            str_dict=str_in
        if str_dict:
            out_list=[str(join_str)+str(i) for i in str_dict.keys()]
            return out_list
        else:
            return None
            
    # 将dependfield替换至请求数据，输出dict
    def denpendFiledToRequestData(self, denpend_filed, str_in):
        # '''将str_in输出的dict中的key批量替换为denpend_filedkey的值'''
        # print(self.log.out_varname(denpend_filed))
        if isinstance(denpend_filed, dict):
            str_in_dict = self.strToDict(str_in)
            # '''完成参数替换'''
            str_in_dict.update(denpend_filed)
            # for k in str_in_dict.keys():
            #     if k not in denpend_filed.keys():
            #         value = str_in_dict[k]
            #         str_in_dict[k] = value
            #     else:
            #         str_in_dict[k] = denpend_filed[k]
            # # print(self.log.out_varname(str_in_dict))
            return str_in_dict
    
    # 将替换完成的请求数据，转换为str并输出
    def requestDataDepend(self, denpend_filed,str_in,space_one=':',space_two='\n'):
        '''数据依赖请求专用，输入依赖字段信息，输出处理完成的字符串'''
        str_dict = self.denpendFiledToRequestData(denpend_filed, str_in)
        str_out = ''
        for k, v in str_dict.items():
            str_out += '{}{}{}{}'.format(k,space_one,v,space_two)
        if str_out[-1] == space_two:
            str_out=str_out[:-1]
        # print(self.log.out_varname(str_out))
        return str_out

    # '''常规字符处理，用于处理chrome复制出来的表单数据，输出k1=v1&k2=v2... '''
    def requestDataGeneral(self,str_in,space_one='=',space_two='&'):
        # 将str转换为dict输出
        str_dict=self.strToDict(str_in)
        str_out = ''
        if str_dict:
            for k, v in str_dict.items():
                str_out += '{}{}{}{}'.format(k,space_one,v,space_two)
            if str_out[-1] == space_two:
                str_out=str_out[:-1]
            return str_out.encode()
        else:
            return None

    # ''' 针对服务号请求单独处理，单独处理sign'''
    def requestDatafwh(self,str_in): #特殊处理
        kw_sign='sign:'#sign关键字
        str_inSource=re.search("(%s.+)"%(kw_sign),str_in)
        #处理sign是字符串最后一个参数/非最后一个参数，参数与value之间是否存在空格，的情况
        if  str_inSource:
            str_inSource=str_inSource.group()#提前处理sign
            str_equalSource = re.sub(str_inSource, '{}'.format(kw_sign) + self.fwhConfig['sign_str'] + today, str_in)
            return self.requestDataGeneral(str_in=str_equalSource)
        elif str_inSource==None :
            str_inSource = re.search("%s(\s+){1,}" %(kw_sign), str_in)
            if str_inSource:
                str_inSource = str_inSource.group()  # 提前处理sign
                str_equalSource = re.sub(str_inSource, '{}{}'.format(kw_sign,str_inSource) + self.fwhConfig['sign_str'] + today, str_in)
                return self.requestDataGeneral(str_in=str_equalSource)
            else:
                print("字段“sign”不存在")
                return None
        else:
            return None
    

    # ''' 一个用于指定输出的方法，一般不使用'''
    def requestDataCustom(self,str_in,str_custom='=>'):
        try:
            str_colon=re.search('\s*:\W?',str_in).group() #匹配出字符串中所有的冒号
            str_tihuan='"'+str_custom+'"'
            str_equal=re.sub(str_colon,str_tihuan,str_in) #将字符串中的冒号替换为目标符号即定义的str_custom的值
            str_lin=re.search("(\s\n*){2,}|(\s\n*)",str_equal).group() #匹配出字符串中所有的换行符与空格,不写表示不限定匹配次数
            str_give=re.sub(str_lin,'"'+str_lin+'"',str_equal) #将字符串中的换行符替换为& (\n >>> &)
            str_lin2=re.search('^',str_give).group() #匹配字符串开头
            str_give2=re.sub('^','"'+str_lin2,str_give) #替换结果为'"'+匹配结果加
            str_lin3=re.search('$',str_give2).group() #匹配字符串末尾
            str_give3=re.sub('$',str_lin3+'"',str_give2)#替换结果为匹配结果加+'"'
            return str_give.encode() #返回字符串，并对数据进行编码处理
        except Exception as error:
            print("数据处理失败，原因为:\n%s"%(error))

    # ''' 一个用于指定输出的postman的方法，去除空格'''
    def requestDataTostr_postman(self,str_in,space_one=':'):
        try:
            str_colon=re.search('\s*:\W*',str_in).group() #匹配出字符串中所有的冒号与空格
            str_equal=re.sub(str_colon,space_one,str_in) #将字符串中的冒号替换为目标符号即定义的str_custom的值
            str_lin=re.search("(\s\n*){2,}|(\s\n*)",str_equal).group() #匹配出字符串中所有的换行符与空格,不写表示不限定匹配次数
            str_give=re.sub(str_lin,'\n',str_equal)
            print(str_give)
        except Exception as error:
            print("数据处理失败，原因为:\n%s"%(error))

    # '''批量生成数组格式的数据'''
    def createBatchData(self,str_in,list_in): #创建批量审核的格式数据
        list2=[]#用于存放替换后的数据
        try:
            str_in_list=str_in.split('\n')
            str_out_list=[]
            for str_tab in str_in_list :
                search_str_tab=re.search('\s',str_tab)
                # '''匹配字符串所有得空白字符，包含（\t\n\r\s等）,并处理'''
                if search_str_tab:
                    search_str_tab=search_str_tab.group()
                    str_tab=re.sub(search_str_tab,'',str_tab)
                str_out_list.append(str_tab)
            out_str='\n'.join(str_out_list)
            batchAudit=out_str.find('\n')
            for a in list_in:
                str_Batch=out_str[:batchAudit]#匹配出第一行数据
                find_str=str_Batch.rfind(' ')#匹配出结果空格所处下标
                if find_str==-1:
                    find_str=str_Batch.rfind(':')
                Batch_value_source=str_Batch[find_str:] #取出value值
                Batch_value_now=Batch_value_source.replace(str(Batch_value_source),str(a)) #替换value值为list里面的数据
                str_pinjie_first=str_Batch[:find_str+1]+Batch_value_now #字符拼接
                find_str2=str_pinjie_first.find(':') #匹配出结果冒号所处下标
                Batch_key=str_pinjie_first[:find_str2] #取出冒号左边的值
                Batch_key_brackets_source=re.search('(\W\d+\W)',Batch_key)
                if Batch_key_brackets_source:
                    Batch_key_brackets_source=Batch_key_brackets_source.group()#匹配出[0]
                else:
                    print('请求参数中不包含list')
                    return None
                Batch_key_brackets_now=re.sub(Batch_key_brackets_source,str(list_in.index(a)),Batch_key)#替换[0]为list对应的下标
                str_pinjie_second=Batch_key_brackets_now+str_pinjie_first[find_str2:] #字符拼接
                list2.append(str_pinjie_second) #将替换好的数据添加至list2
            list_to_str='\n'.join(list2) #将list2转换为字符串，并以换行符间隔
            if batchAudit==-1:#返回-1则代表没有匹配到数值，代表当前字符串不存在换行，即只有一行
                last_replace = re.sub(str_Batch, '', list_to_str)  # 最后用正则完成替换
            else:
                last_replace = out_str.replace(str_Batch, list_to_str)  # 最后替换字符串
            if not ( 'sign' in out_str):#如果传入字符串不包含‘sign’,调用正常处理字符串的方法
                str_give=self.requestDataGeneral(last_replace) #调用字符转换方法进行请求数据处理
            else:#如果传入字符串包含‘sign’,调用特殊服务号处理字符串的方法
                str_give=self.requestDatafwh(last_replace)
            return str_give
        except Exception as error:
            print("数据处理失败，原因为:\n%s"%(error))

    def time_to_str(self,timeOrTimeStr=0):#时间戳转换为字符串
        try:
            timeStamp = timeOrTimeStr
            timeArray = time.localtime(timeStamp)
            otherStyleTime = time.strftime("%Y--%m--%d %H:%M:%S", timeArray)
            # print(otherStyleTime)
            return otherStyleTime
        except Exception as error:
            print("数据处理失败，原因为:\n%s"%(error))

    def str_to_time(self,time_to_str='2018-03-10 18:26:27'):#字符串转换为时间戳
        try:
            d = datetime.datetime.strptime(time_to_str, "%Y-%m-%d %H:%M:%S")
            t = d.timetuple()
            timeStamp = int(time.mktime(t))
            # print(timeStamp)
            return timeStamp
        except Exception as error:
            print("数据处理失败，原因为:\n%s"%(error))
    
    #'''生成md5加密字符串'''
    def md5_Encry(self,str_in):
        str_out=hashlib.md5() #采用md5加密
        str_out.update(str(str_in+self.fwhConfig['Encay_str']).encode(encoding='utf-8'))
        print(str_out.hexdigest())
        return str_out.hexdigest()

    # '''生成sha1加密字符串'''
    def sha1_Encry(self,str_in):#对字符串进行加密
        # print(str_in)
        str_out=hashlib.sha1() #采用sha1加密
        str_out.update(str('%s%s'%(str_in,self.fwhConfig['Encay_str'])).encode(encoding='utf-8'))
        return str_out.hexdigest()


    def get_timestamp(self):#输出当前时间的13位时间戳
        current_milli_time = lambda: int(round(time.time() * 1000))#输出13位时间戳,round:对浮点数进行四舍五入
        return str(current_milli_time())

    # '''使用非通用sign完成加密字符串计算'''
    def fwh_sign_sha1(self,str_in):#服务号请求签名处理封装
        '''主要过程：
            1.替换输入字符串中的时间戳为最新的时间戳
            2.将字符串中的sign字段过滤掉并通过ascii对其进行排序，因为加密时不需要此字段
            3.将排序且处理后的字符串通过sha1算法，得到加密字符串
            4.将得到的加密字符串替换至原字符串'''
        search_time_str='timestamp:'
        search_sign_str='sign:'
        str_inSource=re.search('(%s.+)'%(search_time_str),str_in)#匹配字段时间戳（timestamp）
        if str_inSource:
            time_str=self.get_timestamp()#最终需要的时间戳，13位
            str_inSource=str_inSource.group()
            search_str_inSource=re.search('\s',str_inSource)
            #匹配时间戳,key与value是否包含空格
            #如果包含空格,替换时加上空格，如果不处理会有问题(字符串格式与其他地方不一致)
            if search_str_inSource:
                str_equalSource=re.sub(str_inSource,'%s%s%s'%(search_time_str,search_str_inSource.group(),time_str),
                str_in)#将输入的时间戳替换为需要的时间戳,并加上匹配出来得空格
            else:
                str_equalSource=re.sub(str_inSource,'%s%s'%(search_time_str,time_str),
                str_in)#将输入的时间戳替换为需要的时间戳
            input_list_source=str_equalSource.split('\n')#以换行符分隔字符串并转换位列表
            input_list=[a for a in input_list_source 
                if (search_sign_str or '%s\s'%(search_sign_str) ) not in a]#列表过滤字段sign
            out_list=sorted(input_list)#对list进行排序
            out_str='\n'.join(out_list)#将排序后的list拼接为字符串
            # print(out_str)
            input_sign_str=self.requestDataGeneral(out_str,'','').decode()#获取拼接完成后的请求参数字符串(sign)
            '''这个方法默认对请求参数进行了编码处理，所以这里需手动解码'''
            out_sign_str=self.sha1_Encry(input_sign_str)#得到加密后的加密字符串
            str_inSource_sign=re.search('(%s.+)'%(search_sign_str),str_in)#匹配字段签名验证（sign）
            if str_inSource_sign:
                str_inSource_sign=str_inSource_sign.group()
                search_inSource_sign=re.search('\s',str_inSource)
                #匹配sign,key与value是否包含空格
                #如果包含空格,替换时加上空格，如果不处理会有问题(字符串格式与其他地方不一致)
                if search_inSource_sign is not None:
                    str_last_sign=re.sub(str_inSource_sign,'%s%s%s'%(search_sign_str,search_inSource_sign.group(),
                    out_sign_str),str_equalSource)#将输入的时间戳替换为需要的时间戳
                else:
                    str_last_sign=re.sub(str_inSource_sign,'%s%s'%(search_sign_str,out_sign_str),
                    str_equalSource)#将输入的时间戳替换为需要的时间戳
                # print(str_last_sign)
                str_give=self.requestDataGeneral(str_last_sign)
                # print(str_give)
                return str_give

            else:
                print('输入字符串没有sign对象:sign，无法完成数据转换')
                return None

        else:
            print('输入字符串没有时间戳对象:timestamp，无法完成数据转换')
            return None
    
    # '''封装服务号请求数据格式为数组得加密字符串处理'''
    def fwh_sign_sha1_Array(self, str_in):  # 服务请求签名处理封装（请求格式为数组时的封装）
        search_time_str = 'timestamp:'
        search_sign_str = 'sign:'
        str_inSource = re.search('(%s.+)' % (search_time_str), str_in)  # 匹配字段时间戳（timestamp）
        if str_inSource is not None:
            time_str = self.get_timestamp()  # 最终需要的时间戳，13位
            str_inSource = str_inSource.group()
            search_str_inSource = re.search('\s', str_inSource)
            # 匹配时间戳,key与value是否包含空格
            # 如果包含空格,替换时加上空格，如果不处理会有问题(字符串格式与其他地方不一致)
            if search_str_inSource is not None:
                str_equalSource = re.sub(str_inSource,
                                         '%s%s%s' % (search_time_str, search_str_inSource.group(), time_str),
                                         str_in)  # 将输入的时间戳替换为需要的时间戳,并加上匹配出来得空格
            else:
                str_equalSource = re.sub(str_inSource, '%s%s' % (search_time_str, time_str),
                                         str_in)  # 将输入的时间戳替换为需要的时间戳
            input_list_source = str_equalSource.split('\n')  # 以换行符分隔字符串并转换位列表
            input_list = [a for a in input_list_source
                          if (search_sign_str or '%s\s' % (search_sign_str)) not in a]  # 列表过滤字段sign
            out_list = sorted(input_list)  # 对list进行排序
            out_str = '\n'.join(out_list)  # 将排序后的list拼接为字符串
            out_list_join_course = [a for a in out_list if '[' in a]  # 去除数组外的其他参数
            out_list_other = [a for a in out_list if '[' not in a]  # 获取数组外的其他参数
            out_list_other_str = '\n'.join(out_list_other)
            input_out_list_other_str = self.requestDataGeneral(out_list_other_str, '',
                                                                              '').decode()  # 获取拼接完成后的请求参数字符串(sign)
            join_course_list = []  # 数组
            join_course_dict = {}  # 数组中的dict
            for index, i in enumerate(out_list_join_course):
                join_course_index = i.find('[')
                join_course = i[:join_course_index]  # 匹配join_course
                Array_index = i[join_course_index:].find(']')  # 匹配[index]的下标
                Array = i[join_course_index:][:Array_index + 1]  # 取出[index]
                Array_key_data = i[join_course_index:][Array_index + 1:]  # 取出[0]后面的值
                search_colon = Array_key_data.find(':')  # 匹配出冒号的index
                Array_key = Array_key_data[1:search_colon - 1]  # 匹配key(冒号前面的值)并去除[]
                Array_value = Array_key_data[search_colon + 1:]  # 匹配value(冒号后面的值)
                join_course_dict[Array_key] = Array_value
                if (index + 1) % 4 == 0:
                    # 判断索引为4的倍数时，将dict添加至list，并清空字典（不清除会导致最终插入的值是重复的）
                    join_course_list.append(join_course_dict)
                    join_course_dict = {}
            join_course_str = join_course + str(join_course_list) + input_out_list_other_str  # 拼接加密前的请求字符串
            out_sign_str = self.sha1_Encry(join_course_str)  # 得到加密后的加密字符串
            str_inSource_sign = re.search('(%s.+)' % (search_sign_str), str_in)  # 匹配字段签名验证（sign）
            if str_inSource_sign is not None:
                str_inSource_sign = str_inSource_sign.group()
                search_inSource_sign = re.search('\s', str_inSource)
                # 匹配sign,key与value是否包含空格
                # 如果包含空格,替换时加上空格，如果不处理会有问题(字符串格式与其他地方不一致)
                if search_inSource_sign is not None:
                    str_last_sign = re.sub(str_inSource_sign, '%s%s%s' % (search_sign_str, search_inSource_sign.group(),
                                                                          out_sign_str),
                                           str_equalSource)  # 将输入的时间戳替换为需要的时间戳
                else:
                    str_last_sign = re.sub(str_inSource_sign, '%s%s' % (search_sign_str, out_sign_str),
                                           str_equalSource)  # 将输入的时间戳替换为需要的时间戳
                # print(str_last_sign)
                str_give = self.requestDataGeneral(str_last_sign)
                # print(str_give)
                return str_give
        
            else:
                print('输入字符串没有sign对象:sign，无法完成数据转换')
                return None
    
        else:
            print('输入字符串没有时间戳对象:timestamp，无法完成数据转换')
            return None
    
    # '''根据请求参数格式返回对应得加密字符串处理方法'''
    def fwh_request_sha1(self,str_in):
        out_str_list=str_in.split('\n')
        temp_list=[]
        for out_str in out_str_list:
            search_colon_index=out_str.find(':')#匹配冒号的下标
            key_str=out_str[:search_colon_index]#取出冒号前的值，即相应的key(前提是参数中不带冒号)
            if ('[' and ']') in key_str: #如果参数中带有‘[]’,则认为参数是数组参数
                # print('参数格式为数组的参数%s'%(key_str))
                temp_list.append(key_str)
        if temp_list :
            #如果list为真，则代表输入的字符串中带有数组参数，调用数组加密方法计算sign
            #否则，使用普通的加密方法计算sign
            return self.fwh_sign_sha1_Array(str_in)
        else:
            return self.fwh_sign_sha1(str_in)

if __name__=="__main__":
    request_data_to_str=operationRequestData()
    depend_key = {'course_name_id': 86}
    v=request_data_to_str.denpendKeyGenerate(depend_key, '$..')
    # print(v[0])
    response= {'code': 200, 'msg': '成功', 'data': {'current_page': 1, 'last_page': 1, 'per_page': 20, 'total': 6, 'data': [{'course_name_id': 188, 'course_name_sn': 'ZB_01_04_01', 'course_name': '抢跑“开学季”——朗培F4导师开学21天陪练营”', 'course_class_id': 7, 'course_broker_id': 1, 'perf_comp_id': 0, 'price': '1980.00', 'member_price': '1980.00', 'least_price': '1980.00', 'hr_id': 2, 'org_id': 1, 'meth_id': 2, 'use_card_number': 1, 'use_ticket_number': 1, 'is_deposit': 1, 'is_put': 1, 'is_auto_refund': 1, 'is_refund_audit': 0, 'current_daiding_course_id': 1615, 'create_time': '2020-03-17 09:51:43', 'update_time': '2020-03-20 18:30:19', 'delete_time': 0, 'is_auto_legacy': 0, 'legacy_hours': 0, 'course_class_name': '校长必修课', 'course_class_sn': 'G', 'hr_name': '成都朗培教育咨询有限公司', 'meth_name': '教育咨询-中国银行城南支行', 'org_name': '终身', 'create_admin_name': '向鹏贤3755', 'update_admin_name': '艾照友0025', 'share_url': 'https://front.lpcollege.com/#/courseDetails/1615?is_need_share=1', 'card': []}, {'course_name_id': 184, 'course_name_sn': 'ZA010101', 'course_name': '校长，别再那么累--招生赢天下，管理定江山test', 'course_class_id': 7, 'course_broker_id': 1, 'perf_comp_id': 0, 'price': '2.00', 'member_price': '1.00', 'least_price': '1.00', 'hr_id': 2, 'org_id': 1, 'meth_id': 13, 'use_card_number': 1, 'use_ticket_number': 1, 'is_deposit': 0, 'is_put': 1, 'is_auto_refund': 0, 'is_refund_audit': 0, 'current_daiding_course_id': 1568, 'create_time': '2019-12-21 09:46:54', 'update_time': '2020-03-07 15:04:12', 'delete_time': 0, 'is_auto_legacy': 0, 'legacy_hours': 0, 'course_class_name': '校长必修课', 'course_class_sn': 'G', 'hr_name': '成都朗培教育咨询有限公司', 'meth_name': '教育咨询-民生银行高新支行', 'org_name': '终身', 'create_admin_name': '向鹏贤3755', 'update_admin_name': '秦敏0157', 'share_url': 'https://front.lpcollege.com/#/courseDetails/1568?is_need_share=1', 'card': []}, {'course_name_id': 170, 'course_name_sn': 'ZA_01_01_02', 'course_name': '校长，别再那么累--招生赢天下，管理定江山', 'course_class_id': 7, 'course_broker_id': 1, 'perf_comp_id': 0, 'price': '2000.00', 'member_price': '1000.00', 'least_price': '100.00', 'hr_id': 2, 'org_id': 1, 'meth_id': 2, 'use_card_number': 1, 'use_ticket_number': 1, 'is_deposit': 1, 'is_put': 1, 'is_auto_refund': 1, 'is_refund_audit': 0, 'current_daiding_course_id': 1562, 'create_time': '2019-08-06 17:50:00', 'update_time': '2020-01-14 16:14:30', 'delete_time': 0, 'is_auto_legacy': 0, 'legacy_hours': 0, 'course_class_name': '校长必修课', 'course_class_sn': 'G', 'hr_name': '成都朗培教育咨询有限公司', 'meth_name': '教育咨询-中国银行城南支行', 'org_name': '终身', 'create_admin_name': None, 'update_admin_name': '孟飞', 'share_url': 'https://front.lpcollege.com/#/courseDetails/1562?is_need_share=1', 'card': [{'study_card_type_id': '3', 'study_card_name': '孵化营9800'}]}, {'course_name_id': 2, 'course_name_sn': 'ZA_01_01_01', 'course_name': '校长，别再那么累2.0-打赢营销战', 'course_class_id': 7, 'course_broker_id': 1, 'perf_comp_id': 0, 'price': '280.00', 'member_price': '280.00', 'least_price': '180.00', 'hr_id': 2, 'org_id': 1, 'meth_id': 2, 'use_card_number': 1, 'use_ticket_number': 1, 'is_deposit': 0, 'is_put': 1, 'is_auto_refund': 0, 'is_refund_audit': 0, 'current_daiding_course_id': 1560, 'create_time': '2019-03-01 10:30:21', 'update_time': '2019-12-11 13:41:11', 'delete_time': 0, 'is_auto_legacy': 0, 'legacy_hours': 0, 'course_class_name': '校长必修课', 'course_class_sn': 'G', 'hr_name': '成都朗培教育咨询有限公司', 'meth_name': '教育咨询-中国银行城南支行', 'org_name': '终身', 'create_admin_name': None, 'update_admin_name': 'admin', 'share_url': 'https://front.lpcollege.com/#/courseDetails/1560?is_need_share=1', 'card': []}, {'course_name_id': 86, 'course_name_sn': 'ZA_01_03_01', 'course_name': '教培业盈利高增长运营模式3.0', 'course_class_id': 7, 'course_broker_id': 1, 'perf_comp_id': 0, 'price': '2980.00', 'member_price': '2980.00', 'least_price': '980.00', 'hr_id': 2, 'org_id': 1, 'meth_id': 2, 'use_card_number': 1, 'use_ticket_number': 1, 'is_deposit': 0, 'is_put': 1, 'is_auto_refund': 1, 'is_refund_audit': 0, 'current_daiding_course_id': 583, 'create_time': '2019-03-01 10:30:21', 'update_time': '2020-03-21 15:37:47', 'delete_time': 0, 'is_auto_legacy': 0, 'legacy_hours': 0, 'course_class_name': '校长必修课', 'course_class_sn': 'G', 'hr_name': '成都朗培教育咨询有限公司', 'meth_name': '教育咨询-中国银行城南支行', 'org_name': '终身', 'create_admin_name': None, 'update_admin_name': '秦敏0157', 'share_url': 'https://front.lpcollege.com/#/courseDetails/583?is_need_share=1', 'card': []}, {'course_name_id': 3, 'course_name_sn': 'ZA_01_02_01', 'course_name': '解放校长，管理不再累2.0', 'course_class_id': 7, 'course_broker_id': 1, 'perf_comp_id': 0, 'price': '1980.00', 'member_price': '1980.00', 'least_price': '580.00', 'hr_id': 2, 'org_id': 1, 'meth_id': 2, 'use_card_number': 1, 'use_ticket_number': 1, 'is_deposit': 0, 'is_put': 0, 'is_auto_refund': 0, 'is_refund_audit': 0, 'current_daiding_course_id': 21, 'create_time': '2019-03-01 10:30:21', 'update_time': '2019-12-05 11:23:55', 'delete_time': 0, 'is_auto_legacy': 0, 'legacy_hours': 0, 'course_class_name': '校长必修课', 'course_class_sn': 'G', 'hr_name': '成都朗培教育咨询有限公司', 'meth_name': '教育咨询-中国银行城南支行', 'org_name': '终身', 'create_admin_name': None, 'update_admin_name': '向鹏贤3755', 'share_url': 'https://front.lpcollege.com/#/courseDetails/21?is_need_share=1', 'card': []}]}}
    str1='json'
    print(request_data_to_str.strOutputCase(None))
