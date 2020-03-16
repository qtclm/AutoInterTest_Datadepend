import sys
import json
import os
sys.path.append("../")
from operation_data.get_data import GetData
from tool.import_common import Tool
from jsonpath_rw import jsonpath,parse
from operation_data import data_config
from tool.OperationDatas import OperationYaml,OperationExcle
from tool.import_common import Tool
import demjson
#jsonpath_rw：接口自动化测试中，存在依赖情况：test_02的某个请求参数的值，需要依赖test_01返回结果中某个字段的数据，
# 所以就先需要拿到返回数据中特定字段的值

class DependentData(GetData):
    def __init__(self,case_id):
        super().__init__()
        # 实例依赖字段yaml文件
        self.yamlField=OperationYaml('dependFieldInfo.yaml')
        # 数据依赖字段实例
        self.dependFieldYaml=''
        self.case_id=case_id
        self.data=GetData()
        self.depend_key_dict = {}#存放依赖key数据
    
    #执行依赖测试，并返回结果
    def run_dependent(self):
        row_num=self.opera_excle.get_row_num(self.case_id)
        url = self.data.get_url(row_num)
        request_data = self.data.requestData(row_num)
        header=self.data.headerData(row_num)
        method=self.data.get_request_method(row_num)
        depend_response=self.run_method.run_main(method,url,request_data,header)
        self.log.info(self.mylog.out_varname(row_num))
        self.log.info(self.mylog.out_varname(url))
        self.log.info(self.mylog.out_varname(request_data))
        self.log.info(self.mylog.out_varname(header))
        self.log.info(self.mylog.out_varname(method))
        self.log.info(self.mylog.out_varname(depend_response))
        # 对服务号后台得请求做特殊判断
        if method!='get' and self.yaml.readDataForKey('config')['fwh_admin_test_api'] in url:
            response = self.run_method.run_main(method=method, url=url, data=request_data,headers=header, res_format='text')
        else:
            response = self.run_method.run_main(method=method, url=url, data=request_data,headers=header, res_format='json')
        self.log.info(self.mylog.out_varname(response))
        return response

    
    #根据依赖key去获取执行依赖测试case的响应，然后返回
    def get_data_for_key(self,row):
        self.depend_data_dict={}#执行前清空dict
        yamlDepentKey=self.data.get_depent_key(row)
        depend_Field_dict={}#数据依赖字段
        depend_key_dict=self.depend_key_dict
        # response_data为依赖测试的执行结果
        response_data = self.run_dependent()
        try:
            # ''' 判断depend_data使用eval是否发生异常，如果异常当做单字符处理，
            # 如果没异常判断是否是list且是否为空，满足条件循环处理，否则不处理'''
            if isinstance(response_data,str):
                response_data=eval(response_data)
            if isinstance(yamlDepentKey, list) and yamlDepentKey:
                for i in yamlDepentKey:
                    self.depend_data_parse(i,response_data)
                    # print(self.depend_key_dict)
            else:
                return None
        except SyntaxError as syntaxerror:
            self.log.error(self.mylog.out_varname(syntaxerror))
            self.depend_data_parse(yamlDepentKey,response_data)
            print(self.mylog.out_varname(syntaxerror))
        excleDepentKey=self.dependFiel_kw(row)
        depend_Field_dict[excleDepentKey]=depend_key_dict
        return depend_Field_dict
        
    def depend_data_parse(self,depent_key,response_data):
        '''处理依赖'''
        if depent_key:
            # 定义要获取的key
            json_exe = parse(depent_key)
            # 定义响应数据,key从响应数据里获取
            madle = json_exe.find(response_data)
            depend_data_index = depent_key.rfind('.')
            depend_data_str = depent_key[depend_data_index + 1:]
            # math.value返回的是一个list，可以使用索引访问特定的值jsonpath_rw的作用就相当于从json里面提取响应的字段值
            try:
                math_value = [i.value for i in madle]
                if math_value:
                    math_value=math_value[0]
                    self.depend_key_dict[depend_data_str] = math_value
                # print(self.depend_key_dict)
            except IndexError as indexerror:
                self.log.error(self.mylog.out_varname(indexerror))
                return None
        else:
            return None
        
        
    # 返回数据依赖字段
    def dependFiel_kw(self, row):
        col = int(data_config.get_field_depend())
        depend_field = self.opera_excle.get_cell_value(row, col)
        self.dependFieldYaml = '{}{}'.format(self.yaml.readDataForKey('dependField'),row)
        # print('self.data.writelist',self.data.writelist)
        if not depend_field:
            # 判断field关键字是否存在存实例中
            if self.dependFieldYaml in self.data.writelist:
                return self.dependFieldYaml
            else:
                return False
        else:
            return depend_field

    # 获取数据依赖字段
    def get_depend_field(self, row):
        self.write_dependField(row)
        depend_field = self.dependFiel_kw(row)
        depend_field_data = self.yamlField.readforKey_onetier(key=depend_field)
        # print(depend_field)
        # print(depend_field_data)
        if depend_field_data:
            return depend_field_data
        else:
            return False

    # 写入数据依赖字段信息至yaml
    def write_dependField(self,row):
        try:
            falg=None
            dependFieldYaml=self.get_data_for_key(row)
            if dependFieldYaml:
                # '''这句代码用于处理yaml写入失败（浮点对象异常的问题）
                value = eval(demjson.encode(dependFieldYaml))
                self.yamlField.write_yaml(value)
                return True
            else:
                return False
        except BaseException as error:
            self.log.error(self.mylog.out_varname(error))
            return False
        
    # 将依赖处理完毕的请求数据写入excle
    def writeDependRequestDataToExcle(self,row):
        source_data=self.get_depend_field(row)
        # print(self.mylog.out_varname(source_data))
        falg=None
        if source_data:
            falg=self.data.writeDependFiledToRequestData(row,source_data=source_data)
            if falg:
                return True
            else:
                return False
        else:
            return False
    
    
if __name__=='__main__':
    dd=DependentData(1)
    # key=dd.get_data_for_key(2)
    # print(dd.write_dependField(3))
    # print(key)
    # value=dd.write_dependData_to_dependField(5)
    # print(value)