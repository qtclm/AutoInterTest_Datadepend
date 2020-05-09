import json
import re
import hashlib
import time
import datetime
import sys
sys.path.append('../')
from tool.OperationDatas import OperationYaml
from tool.Operation_logging import logs
from jsonpath_rw_ext import parse
today = datetime.datetime.now().strftime('%Y%m%d')  # 获取当前日期


class operationRequestData(object):
    def __init__(self):
        config = OperationYaml().read_data()
        self.fwhConfig = config['config']
        self.log = logs()

    # 返回依赖数据
    def depend_data_parse(self,dependkey,response_data,index='one'):
        __dict={}#存放字典
        '''处理依赖'''
        if dependkey:
            # 匹配字典key
            depend_data_index = dependkey.rfind('.')
            depend_data_str = dependkey[depend_data_index + 1:]
            try:
                math_value = self.json_path_parse_public(json_path=dependkey,json_obj=response_data)
                if math_value:
                    if index=='one':
                        math_value=math_value[0]
                    __dict[depend_data_str]=math_value
                    return __dict
                else:
                    return None
            except IndexError as indexerror:
                return None
        else:
            return None

    # 根据jsonpath表达式获取json对象公共方法,部分功能还需要测试
    def json_path_parse_public(self,json_path,json_obj):
        if json_path:
            # 定义要获取的key
            json_exe = parse(json_path)
            # 定义响应数据,key从响应数据里获取
            madle = json_exe.find(json_obj)
            # math.value返回的是一个list，可以使用索引访问特定的值jsonpath_rw的作用就相当于从json里面提取响应的字段值
            try:
                math_value = [i.value for i in madle]
                return math_value
            except IndexError as indexerror:
                return None
        else:
            return None

    # 处理robo 3t复制出来的mongo查询结果，序列化为list
    def mongodata_Serialize(self, str_in):
        str_out = self.jsonStr_pyobject(str_in)
        '''处理集合间的分隔符'''
        mongo_separator_list = re.findall("\/\*\s?\d+\s?\*\/", str_out)
        if not mongo_separator_list:
            return False
        for i in mongo_separator_list:
            mongo_separator = re.search('\d+', i)
            if mongo_separator:
                if mongo_separator.group() == '1':
                    mongo_separator = '['
                else:
                    mongo_separator = ','
                str_out = str_out.replace(i, mongo_separator)
        str_out += ']'
        '''处理NumberLong'''
        mongo_numberLong_list = re.findall('NumberLong\([-+]?\d+\)', str_out)
        if not mongo_separator_list:
            return False
        for i in mongo_numberLong_list:
            mongo_numberLong = re.search('\d+', i)
            if mongo_numberLong:
                mongo_numberLong = mongo_numberLong.group()
                str_out = str_out.replace(i, mongo_numberLong)
        return eval(str_out)


    # 输入字符串，输出字符串的大小写与首字母大写以及字符串本身
    def strOutputCase(self, str_in):
        if isinstance(str_in, str):
            str_in = str_in
        else:
            str_in = str(str_in)
        out_str_tuple = (str_in, str_in.lower(), str_in.upper(), str_in.capitalize())
        return out_str_tuple

    # '''将带有time关键字的参数放到字符串末尾'''
    def standardStr(self, str_in, kw_str='time', kw_str2='sign'):
        spilt_sign = '\n'
        split_list = str_in.split(spilt_sign)
        # print(self.log.out_varname(split_list))
        str_out = ''
        # '''获取参数中带有time、sign得参数'''
        __time = [i for i in split_list if kw_str in i]
        __sign = [i for i in split_list if kw_str2 in i]
        # '''过滤参数中带有time得参数'''
        __nottime = [i for i in split_list if not i in __time or __sign]
        # '''如果list个数大于等于2，代表至少有两个请求参数，直接正常拼接字符串'''
        if len(__nottime) >= 2:
            str_out = spilt_sign.join(__nottime)
        # '''如果list个数为0，代表至少过滤后没有请求参数，这时候手动将time参数赋值给list，防止处理出错,直接使用空字符串拼接'''
        elif len(__nottime) == 0:
            __nottime.extend(__time)
            # '''判断__time的个数'''
            if len(__time) == 1:
                str_out = ''.join(__nottime)
            elif len(__time) == 0:
                print("参数都没有，还处理个球嘛")
                return None
            else:
                str_out = spilt_sign.join(__nottime)
        # 否则代表list只有一个参数，直接使用空字符串拼接
        else:
            str_out = ''.join(__nottime)
        return str_out

    # 将str转换为dict
    def strToDict(self, str_in,space_one=':',space_two='\n'):
        # '''将str转换为dict输出'''
        # '''将带有time关键字的参数放到字符串末尾'''
        str_in = self.standardStr(str_in)
        # print(str_in)
        if str_in:
            split_list = str_in.split(space_two)
            str_in_dict = {}
            for i in split_list:
                colon_str_index = i.find(space_one)
                if colon_str_index == -1:
                    # '''处理firefox复制出来的参数'''
                    space_one = '\t' or ' '
                    colon_str_index = i.find(space_one)
                # '''去掉key、value的空格,key中的引号'''
                str_in_key = i[:colon_str_index].strip()
                if str_in_key:
                    str_in_key = str_in_key.replace('"', '')
                    str_in_key = str_in_key.replace("'", '')
                    # 正则过滤无用key,只保留key第一位为字母数据获取[]_
                    str_sign = re.search('[^a-zA-Z0-9\_\[\]+]', str_in_key[0])
                    if str_sign is None:
                        # 处理value中的空格与转义符
                        str_in_value = i[colon_str_index + 1:].strip()
                        str_in_value = str_in_value.replace('\\', '')
                        try:
                            # 遇到是object类型的数据转换一下
                            str_in_value = eval(str_in_value)
                        except BaseException as error:
                            str_in_value = str_in_value
                        str_in_dict[str_in_key] = str_in_value
            return str_in_dict
        else:
            print("参数都没有，还处理个球嘛")
            return None

    # 输入tuple（1.file字段：例如：file，head，具体以系统定义为准，2.文件绝对路径）,输出需要得files对象，用于文件上传
    def out_join_files(self, tuple_in, mode='rb'):
        # 输出files示例
        #  files = {'file': ('git.docx', open('C:/Users/Acer/Downloads/git.docx', 'rb'))}
        if not isinstance(tuple_in, (tuple, list)) and len(tuple_in) == 2:
            print('类型不是tuple或者list，或长度不标准')
            return None
        else:
            tuple_field, tuple_filepath = tuple_in
            file_index = tuple_filepath.rfind('/')
            if file_index == '-1':
                file_index = tuple_filepath.rfind('\\')
                if not file_index == -1:
                    filename = tuple_filepath[file_index + 1:]
                else:
                    filename = 'git(默认值).docx'
                    tuple_filepath = 'C:/Users/Acer/Downloads/git.docx'
            else:
                filename = tuple_filepath[file_index + 1:]
            files = {tuple_field: (filename, open(tuple_filepath, mode))}
            return files

    # 将dict转换为str
    def dictToStr(self, dict_in, space_one='=', space_two='&'):
        if isinstance(dict_in, dict) and dict_in:
            str_out = ''
            for k, v in dict_in.items():
                str_out += '{}{}{}{}'.format(k, space_one, v, space_two)
            if str_out[-1] == space_two:
                str_out = str_out[:-1]
            return str_out
        return None

    # 将断言中的true/false/null，转换为python对象
    def assert_pyobject(self, str_in):
        str_dict = self.strToDict(str_in)
        __temp_dict = {}
        for k, v in str_dict.items():
            if v == 'true':
                v = True
            elif v == 'flase':
                v = False
            elif v == 'null':
                v = None
            __temp_dict[k] = v
        return __temp_dict

    # 将json_str中的true/false/null，转换为python对象
    def jsonStr_pyobject(self,str_in):
        str_in=str(str_in)
        str_in = str_in.replace('true', 'True')
        str_in = str_in.replace('false', 'False')
        str_in = str_in.replace('null', 'None')
        try:
            json_pyobj=eval(str_in)
            return json_pyobj
        except BaseException as e:
            print('字符串处理失败，原因:{}'.format(e))
            return None

    # dependkey生成
    def denpendKeyGenerate(self, str_in, join_str=''):
        if not isinstance(str_in, dict):
            str_dict = self.strToDict(str_in)
        else:
            str_dict = str_in
        if str_dict:
            out_list = [str(join_str) + str(i) for i in str_dict.keys()]
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
    def requestDataDepend(self, denpend_filed, str_in, space_one=':', space_two='\n'):
        '''数据依赖请求专用，输入依赖字段信息，输出处理完成的字符串'''
        str_dict = self.denpendFiledToRequestData(denpend_filed, str_in)
        str_out = self.dictToStr(str_dict, space_one, space_two)
        return str_out

    # '''常规字符处理，用于处理chrome复制出来的表单数据，输出k1=v1&k2=v2... '''
    def requestDataGeneral(self, str_in, space_one='=', space_two='&'):
        # 将str转换为dict输出
        str_dict = self.strToDict(str_in)
        if str_dict:
            str_out = self.dictToStr(str_dict, space_one, space_two)
            return str_out.encode()
        else:
            return None

    # ''' 针对服务号请求单独处理，单独处理sign,输出dict'''
    def requestDatafwh(self, str_in):  # 特殊处理
        kw_sign = 'sign'  # sign关键字
        request_dict = self.strToDict(str_in)
        if kw_sign in request_dict.keys():
            request_dict[kw_sign] = self.fwhConfig['sign_str'] + today
            return request_dict
        else:
            # print('字段sign不存在')
            return request_dict

    # ''' 针对服务号请求单独处理，单独处理sign,输出str'''
    def requestDatafwh_str(self, str_in, space_one='=', space_two='&'):  # 特殊处理
        request_dict=self.requestDatafwh(str_in)
        out_str = self.dictToStr(request_dict, space_one, space_two).encode()
        return out_str

    # 最终输出得请求数据，此方法输出str
    def requestToStr(self, str_in, space_one='=', space_two='&'):
        out_str = self.requestDatafwh_str(str_in)
        return out_str

    def requestToDict(self, str_in):
        requests_dict = self.requestDatafwh(str_in)
        return requests_dict

    # ''' 一个用于指定输出的方法，一般不使用'''
    def requestDataCustom(self, str_in, str_custom='=>', space_two='\n'):
        str_dict = self.strToDict(str_in)
        str_out = self.dictToStr(str_dict, space_one=str_custom, space_two=space_two)
        return str_out

    # ''' 一个用于指定输出的postman的方法，去除空格'''
    def requestDataTostr_postman(self, str_in, space_one=':', space_two='\n'):
        str_dict = self.strToDict(str_in)
        str_out = self.dictToStr(str_dict, space_one=space_one, space_two=space_two)
        return str_out

    # '''批量生成数组格式的数据'''
    def createBatchData(self, str_in, list_in):
        str_dict = self.strToDict(str_in)
        array_str = '[0]'
        array_list = [i for i in str_dict.keys() if array_str in i]
        if array_list:
            array_key = array_list[0]
        else:
            return None
        for index, value in enumerate(list_in):
            _dict_key = '{}{}{}'.format(array_key[:-2], index, array_key[-1])
            str_dict[_dict_key] = value
        out_str = self.dictToStr(str_dict)
        return out_str.encode()

    def time_to_str(self, timeOrTimeStr=0):  # 时间戳转换为字符串
        try:
            timeStamp = timeOrTimeStr
            if not timeStamp:
                timeStamp=time.time()
            timeArray = time.localtime(timeStamp)
            otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            return otherStyleTime
        except Exception as error:
            print("数据处理失败，原因为:\n%s" % (error))

    def str_to_time(self, time_to_str='1970-01-01 00:00:00'):  # 字符串转换为时间戳
        try:
            if time_to_str=='1970-01-01 00:00:00':
                time_to_str=self.time_to_str()
            d = datetime.datetime.strptime(time_to_str, "%Y-%m-%d %H:%M:%S")
            t = d.timetuple()
            timeStamp = int(time.mktime(t))
            # print(timeStamp)
            return timeStamp
        except Exception as error:
            print("数据处理失败，原因为:\n%s" % (error))

    # '''生成md5加密字符串'''
    def md5_Encry(self, str_in,upper=None):
        str_out = hashlib.md5()  # 采用md5加密
        str_out.update(str(str_in).encode(encoding='utf-8'))
        md5=str_out.hexdigest()
        if upper==True:
            return md5.upper()
        return  md5

    # '''生成sha1加密字符串'''
    def sha1_Encry(self, str_in):  # 对字符串进行加密
        str_out = hashlib.sha1()  # 采用sha1加密
        str_out.update(str('%s%s' % (str_in, self.fwhConfig['Encay_str'])).encode(encoding='utf-8'))
        return str_out.hexdigest()


    def get_timestamp(self):  # 输出当前时间的13位时间戳
        current_milli_time = lambda: int(round(time.time() * 1000))  # 输出13位时间戳,round:对浮点数进行四舍五入
        return str(current_milli_time())

    # 对字典进行排序
    def sortedDict(self,dict_in):
        if isinstance(dict_in, dict):
            __dict = dict(sorted(dict_in.items(), key=lambda x: x[0]))  # 对字典进行排序
            return __dict
        else:
            return None

    def fwh_TimestampAndSign_dispose(self,str_in, search_time_str='timestamp', search_sign_str='sign'):
        str_dict = self.strToDict(str_in)
        str_dict=self.sortedDict(str_dict)
        _dict_key_list = [i for i in str_dict.keys()]
        if not (search_time_str in _dict_key_list and search_sign_str in _dict_key_list):
            print('timestamp或sign参数不存在')
            return None
        str_dict[search_time_str] = self.get_timestamp()  # 将时间替换为最新得时间戳
        not_sign_dict = str_dict
        not_sign_dict.pop(search_sign_str)  # 去除sign参数
        return not_sign_dict,str_dict,_dict_key_list

    # '''使用非通用sign完成加密字符串计算'''
    def fwh_sign_sha1(self,str_in, search_sign_str='sign'):  # 服务号请求签名处理封装
        '''主要过程：
            1.替换输入字符串中的时间戳为最新的时间戳
            2.将字符串中的sign字段过滤掉并通过ascii对其进行排序，因为加密时不需要此字段
            3.将排序且处理后的字符串通过sha1算法，得到加密字符串
            4.将得到的加密字符串替换至原字符串'''
        not_sign_dict,str_dict,_dict_key_list=self.fwh_TimestampAndSign_dispose(str_in)#接受去掉sign的dict，原始dict,原始dictkeys
        if not not_sign_dict:
            return None
        input_sign_str = self.dictToStr(not_sign_dict, space_one='', space_two='')  # sign加密前得字符串
        out_sign_str = self.sha1_Encry(input_sign_str)  # 得到加密后的加密字符串
        str_dict[search_sign_str] = out_sign_str  # 得到最终加密完成得参数
        out_str = self.dictToStr(str_dict)
        # print(out_str)
        return out_str

    # '''封装服务号请求数据格式为数组得加密字符串处理'''
    def fwh_sign_sha1_Array(self,str_in, search_sign_str='sign'):  # 服务请求签名处理封装（请求格式为数组时的封装）
        not_sign_dict, str_dict, _dict_key_list = self.fwh_TimestampAndSign_dispose(str_in)
        if not not_sign_dict:
            return None
        out_list_join_course = [a for a in _dict_key_list if ('[' in a) and (']' in a)]  # 去除数组外的其他参数
        other_dict = {}#存放数组以及sign以外的参数
        out_list_other = [a for a in _dict_key_list if not ( '[' in a or ']' in a or search_sign_str==a)]  # 获取数组外的其他参数
        for i in out_list_other:
            other_dict[i] = str_dict[i]
        other_str = self.dictToStr(other_dict, space_one='', space_two='')#数组以及sign以外的参数转换为字符串
        join_course_index = out_list_join_course[0].find('[')
        join_course_array_index = out_list_join_course[0].find(']')
        join_course = out_list_join_course[0][:join_course_index]  # 匹配join_course固定字符串
        join_course_array = out_list_join_course[0][:join_course_array_index + 1]#匹配数组参数前缀：join_course[0]
        join_course_array_list = len([i for i in out_list_join_course if join_course_array in i])  # 确定每组参数得个数
        join_course_dict,join_course_list = {},[]
        for i in out_list_join_course:
            join_course_dict[i] = not_sign_dict[i]
            if len(join_course_dict) == join_course_array_list:
                join_course_list.append(join_course_dict)
                join_course_dict = {}
        # ensure_ascii:防止中文被转义,separators:去除字符串中多余的空格
        join_course_list = json.dumps(join_course_list, ensure_ascii=False, separators=(',', ':'))
        input_sign_str = '{}{}{}'.format(join_course, join_course_list, other_str)
        out_sign_str = self.sha1_Encry(input_sign_str)
        str_dict[search_sign_str] = out_sign_str
        str_give = self.dictToStr(str_dict)
        return str_give

    # '''根据请求参数格式返回对应得加密字符串处理方法'''
    def fwh_request_sha1(self, str_in):
        not_sign_dict, str_dict, _dict_key_list = self.fwh_TimestampAndSign_dispose(
            str_in)  # 接受去掉sign的dict，原始dict,原始dictkeys
        if not not_sign_dict:
            return None
        _dict_key_list = [i for i in _dict_key_list if ('[' in i and ']' in i)]
        if not _dict_key_list:
            return self.fwh_sign_sha1(str_in)
        else:
            return self.fwh_sign_sha1_Array(str_in)


if __name__ == "__main__":
    request_data_to_str = operationRequestData()
    tuple1 = ('file', 'C:\\Users\\Acer\\Pictures\\Screenshots\\10086.png')
    # print(request_data_to_str.out_join_files(tuple1))
    str_in = '''page: 1
limit: 10
uid: 
keywords: 
start_date: 
end_date: '''
    str_batch = '''course_finance_id[0]: 275365
course_finance_id[1]: 275364
total_price: 9800
state: 1'''
    str_in_array = '''join_name[0]: test1
    join_school[0]: cq1
    join_tel[0]: 10086
    join_card[0]: 1234
    join_name[1]: test2
    join_school[1]: cq2
    join_tel[1]: 10087
    join_card[1]: 1235
    join_name[2]: test3
    join_school[2]: cq3
    join_tel[2]: 10088
    join_card[2]: 1236
    page: 1
    limit: 10
    uid: 
    keywords: 
    start_date: 
    end_date: 
    timestamp: 12334
    sign: 122'''

    list_in = [1, 2, 3, 4, 5, 6]
    # print(request_data_to_str.createBatchData(str_batch, list_in))
    response={"result": [{"_id": "5e8edab8e5f09a0001ca7e7c", "shopIdenty": 810109299, "brandIdenty": 32900, "name": "范围1",
                 "startPrice": 11.0, "deliveryPrice": 2.0, "deliveryTime": 3, "geoType": "2", "shapeType": 1,
                 "radius": "2", "circleCenterGeo": {"latitude": "67.96367756156171", "longitude": "53.098459063846555"},
                 "status": 1, "sort": 1},
                {"_id": "5e93cc23e5f09a0001ca7e92", "shopIdenty": 810109299, "brandIdenty": 32900, "name": "范围2",
                 "startPrice": 111.0, "deliveryPrice": 22.0, "deliveryTime": 1, "geoType": "2", "shapeType": 1,
                 "radius": "2", "circleCenterGeo": {"latitude": "67.34563", "longitude": "56.34552"}, "status": 1,
                 "sort": 1}], "code": 0, "message": "成功[OK]", "message_uuid": "c223f78e-237c-4f9d-9022-640b177a8ab7"}
    jsonpath='$.result[*].name'
    print(request_data_to_str.json_path_parse_public(jsonpath, response))
    # print(request_data_to_str.json_path_parse_public(str_in_array))

