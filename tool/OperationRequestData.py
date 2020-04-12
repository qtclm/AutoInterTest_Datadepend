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
            madle = json_exe.find(response_data)
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
                # print(indexerror)
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

    # 将str转换为dict
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
                if str_in_key:
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


    # 输入tuple（1.file字段：例如：file，head，具体以系统定义为准，2.文件绝对路径）,输出需要得files对象，用于文件上传
    def out_join_files(self,tuple_in,mode='rb'):
        # 输出files示例
        #  files = {'file': ('git.docx', open('C:/Users/Acer/Downloads/git.docx', 'rb'))}
        if not isinstance(tuple_in,(tuple,list)) and len(tuple_in)==2:
            print('类型不是tuple或者list，或长度不标准')
            return None
        else:
            tuple_field,tuple_filepath=tuple_in
            file_index=tuple_filepath.rfind('/')
            if file_index=='-1':
                file_index=tuple_filepath.rfind('\\')
                if not file_index==-1:
                    filename=tuple_filepath[file_index+1:]
                else:
                    filename='git(默认值).docx'
                    tuple_filepath='C:/Users/Acer/Downloads/git.docx'
            else:
                filename=tuple_filepath[file_index+1:]
            files={tuple_field:(filename,open(tuple_filepath,mode))}
            return files

    # 将dict转换为str
    def dictToStr(self,dict_in,space_one='=',space_two='&'):
        if isinstance(dict_in,dict) and dict_in:
            str_out = ''
            for k, v in dict_in.items():
                str_out += '{}{}{}{}'.format(k, space_one, v, space_two)
            if str_out[-1] == space_two:
                str_out = str_out[:-1]
            return str_out
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
            return str_in_dict
        return None
    
    # 将替换完成的请求数据，转换为str并输出
    def requestDataDepend(self, denpend_filed,str_in,space_one=':',space_two='\n'):
        '''数据依赖请求专用，输入依赖字段信息，输出处理完成的字符串'''
        str_dict = self.denpendFiledToRequestData(denpend_filed, str_in)
        str_out = self.dictToStr(str_dict,space_one,space_two)
        return str_out

    # '''常规字符处理，用于处理chrome复制出来的表单数据，输出k1=v1&k2=v2... '''
    def requestDataGeneral(self,str_in,space_one='=',space_two='&'):
        # 将str转换为dict输出
        str_dict=self.strToDict(str_in)
        if str_dict:
            str_out = self.dictToStr(str_dict,space_one,space_two)
            return str_out.encode()
        else:
            return None

    # ''' 针对服务号请求单独处理，单独处理sign,输出dict'''
    def requestDatafwh(self,str_in): #特殊处理
        kw_sign='sign'#sign关键字
        request_dict=self.strToDict(str_in)
        if kw_sign in request_dict.keys():
            request_dict[kw_sign]=self.fwhConfig['sign_str'] + today
            return request_dict
        else:
            print('字段sign不存在')
            return request_dict


    # ''' 针对服务号请求单独处理，单独处理sign,输出str'''
    def requestDatafwh_str(self, str_in,space_one='=',space_two='&'):  # 特殊处理
        kw_sign='sign'#sign关键字
        request_dict=self.strToDict(str_in)
        if kw_sign in request_dict.keys():
            request_dict[kw_sign]=self.fwhConfig['sign_str'] + today
            out_str=self.dictToStr(request_dict,space_one,space_two).encode()
        else:
            out_str=self.dictToStr(request_dict,space_one,space_two).encode()
        return out_str

    # 最终输出得请求数据，此方法输出str
    def requestToStr(self, str_in,space_one='=',space_two='&'):
        requests_dict = self.strToDict(str_in)
        if 'sign' in requests_dict.keys():
            return self.requestDatafwh_str(str_in,space_one,space_two)
        else:
            return self.requestDataGeneral(str_in,space_one,space_two)

    def requestToDict(self,str_in):
        requests_dict=self.strToDict(str_in)
        if 'sign' in requests_dict.keys():
            return self.requestDatafwh(str_in)
        else:
            return requests_dict

    # ''' 一个用于指定输出的方法，一般不使用'''
    def requestDataCustom(self,str_in,str_custom='=>',space_two='\n'):
        str_dict = self.strToDict(str_in)
        str_out = self.dictToStr(str_dict, space_one=str_custom,space_two=space_two)
        return str_out

    # ''' 一个用于指定输出的postman的方法，去除空格'''
    def requestDataTostr_postman(self,str_in,space_one=':',space_two='\n'):
        str_dict=self.strToDict(str_in)
        str_out=self.dictToStr(str_dict,space_one=space_one,space_two=space_two)
        return str_out

    # '''批量生成数组格式的数据'''
    def createBatchData(self, str_in, list_in):
        str_dict=self.strToDict(str_in)
        array_str='[0]'
        array_list=[i for i in str_dict.keys() if array_str in i]
        if array_list:
            array_key=array_list[0]
        else:
            return None
        for index,value in enumerate(list_in):
            _dict_key='{}{}{}'.format(array_key[:-2],index,array_key[-1])
            str_dict[_dict_key]=value
        out_str=self.dictToStr(str_dict)
        return out_str.encode()


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
    tuple1=('file', 'C:\\Users\\Acer\\Pictures\\Screenshots\\10086.png')
    # print(request_data_to_str.out_join_files(tuple1))
    # jsonpath='$.data.data[*].course_name_id'
    str_in='''page: 1
limit: 10
uid: 
keywords: 
start_date: 
end_date: '''
    str_batch='''course_finance_id[0]: 275365
course_finance_id[1]: 275364
total_price: 9800
state: 1'''
    list_in=[1,2,3,4,5,6]
    print(request_data_to_str.createBatchData(str_batch,list_in))

