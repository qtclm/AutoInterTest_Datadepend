import sys
sys.path.append('../')
from tool.OperationDatas import OperationYaml,OperationExcle
from operation_data import data_config
import demjson
from tool.import_common import ToolALL
from tool.decorator_token import args_None
import re

#args_None:检测参数是否为空的装饰器，只适用于行参没有默认值且只有一个行参的函数


class GetData(ToolALL):
    def __init__(self):
        super().__init__()
        # dependyaml文件与sql执行结果yaml文件
        self.yamlKey=OperationYaml('dependKeyInfo.yaml')
        self.yamlsqlExecute=OperationYaml('sqlExecuteInfo.yaml')
        self.opera_excle = OperationExcle()
        # 创建实例对象dependkey与dependFiled与yaml配置里面的key
        self.dependKey=''
        self.dependField=''
        self.dependKeyYaml=''
        self.sqlExecuteResult=''
        # '''定义header类型'''
        self.No_auth_headerFlag=self.yaml['No_auth_headerFlag'] #无需token认证
        self.crm_headerFlag = self.yaml['crm_headerFlag']# crm
        self.fwh_headerFlag = self.yaml['fwh_headerFlag'] # 服务号微信端
        self.fwh_admin_headerFlag = self.yaml['fwh_admin_headerFlag'] # 服务号后台
        # 定义content_type
        self.content_type_json=self.yaml['content_type_json']
        self.content_type_form_urlencoded=self.yaml['content_type_form_urlencoded']
        self.content_type_text=self.yaml['content_type_text']
        self.content_type_form_data=self.yaml['content_type_form_data']
        self.content_type_xml=self.yaml['content_type_xml']
        #存放sql
        self.sql=None
        self.writelist=[]

    # 获取caseID
    def get_caseId(self,row):
        col=int(data_config.get_case_id())
        caseId=self.opera_excle.get_cell_value(row,col)
        if caseId=='ID':
            return None
        else:
            return caseId
    
    # 获取excle行数，就是用例数
    def get_case_line(self):
        line_num = self.opera_excle.get_lines()
        return line_num

    # 获取是否执行
    @args_None
    def get_is_run(self, row: object) -> object:
        flag = None
        col = int(data_config.get_run())
        run_model = self.opera_excle.get_cell_value(row, col)
        if run_model == 'yes':
            flag = True
        elif run_model == '是否执行':
            pass
        else:
            flag = False
        return flag
    
    
    @args_None
    # 获取header
    def getHeader(self,row):
        col = int(data_config.get_header())
        header = self.opera_excle.get_cell_value(row, col)
        return header
    
   
    @args_None
    # 确定header类型
    def getHeaderType(self,row):
        header=self.getHeader(row)
        header_OutputCase = self.requestDataDispose.strOutputCase(header)
        flag = None
        if self.No_auth_headerFlag in header_OutputCase :
            flag=self.No_auth_headerFlag
            return flag
        elif self.crm_headerFlag in header_OutputCase:
            flag = self.crm_headerFlag
            return flag
        elif self.fwh_headerFlag in header_OutputCase:
            flag = self.fwh_headerFlag
            return flag
        elif self.fwh_admin_headerFlag in header_OutputCase:
            flag = self.fwh_admin_headerFlag
            return flag
        else:
            flag = None
            return flag

    # 获取content_type的值
    def getContentType(self,row):
        col = int(data_config.get_content_type())
        content_type = self.opera_excle.get_cell_value(row, col)
        return content_type

    def ContentTypeData(self,row):
        content_type=self.getContentType(row)
        content_type_OutputCase=self.requestDataDispose.strOutputCase(content_type)
        header_content_type=None
        # 请求数据格式为json时使用
        if [i for i in self.content_type_json if i in content_type_OutputCase] :
            header_content_type= self.yaml['headers_json']
        # 请求数据格式为浏览器原生时使用
        elif [i for i in self.content_type_form_urlencoded if i in content_type_OutputCase]:
            header_content_type= self.yaml['headers_form_urlencoded']
        # 请求数据格式为text时使用，响应一般返回html
        elif [i for i in self.content_type_text if i in content_type_OutputCase]:
            header_content_type= self.yaml['headers_text']
        # 一般用于文件上传时使用
        elif [i for i in self.content_type_form_data if i in content_type_OutputCase]:
            header_content_type= self.yaml['headers_form_data']
        # 请求数据格式为xml时使用
        elif [i for i in self.content_type_xml if i in content_type_OutputCase]:
            header_content_type= self.yaml['headers_xml']
        else:
            print("暂不支持的content_type")
            header_content_type= None
        self.log.info(self.mylog.out_varname(header_content_type))
        return header_content_type

    @args_None
    # 输出header
    def headerData(self, row):
        header_flag=self.getHeaderType(row)
        header_content_type=self.ContentTypeData(row)
        if header_content_type and isinstance(header_content_type,dict):
            if header_flag==self.No_auth_headerFlag:  # 不需要token时得header
                notoken_headers = data_config.get_header_no_auth()
                header_content_type.update(notoken_headers)
                return header_content_type
            elif header_flag==self.crm_headerFlag:  # CRM header
                crm_headers = data_config.get_crm_token()
                header_content_type.update(crm_headers)
                return header_content_type
            elif header_flag==self.fwh_headerFlag:  # 服务号header
                fwhc_headers = data_config.get_fwh_token()
                header_content_type.update(fwhc_headers)
                return header_content_type
            elif header_flag==self.fwh_admin_headerFlag:  # 服务号后台header
                fwh_admin_header = data_config.get_fwhadmin_cookie()
                header_content_type.update(fwh_admin_header)
                return header_content_type
            else:
                self.log.error('error:header填写错误')
                return None
        return None

    # 获取请求url名称
    @args_None
    def get_request_name(self, row):
        col = int(data_config.get_request_name())
        request_name = self.opera_excle.get_cell_value(row, col)
        if request_name:
            # print('请求url:' + request_name)
            return request_name
        else:
            return None
        
    
    # 获取请求方式
    @args_None
    def get_request_method(self, row):
        col = int(data_config.get_request_method())
        request_method = self.opera_excle.get_cell_value(row, col)
        return request_method

    # 获取URL
    @args_None
    def get_url(self, row):
        col = int(data_config.get_url())
        url = self.opera_excle.get_cell_value(row, col)
        headerFlag=self.getHeaderType(row)
        if headerFlag==self.crm_headerFlag:
            url=self.yaml['crm_test_api']+url
            # print(1,url)
        elif headerFlag==self.fwh_headerFlag:
            url = self.yaml['fwh_test_api'] + url
            # print(2, url)
        elif headerFlag==self.fwh_admin_headerFlag:
            url = self.yaml['fwh_admin_test_api'] + url
            # print(3, url)
        else:
            url=url
            # print(4, url)
        return url

    # 获取请求数据
    @args_None
    def get_request_data(self, row):
        col = int(data_config.get_data())
        request_data = self.opera_excle.get_cell_value(row, col)
        return request_data
    
    # 更改请求数据类型
    @args_None
    def requestData(self, row):
        '''根据每一行的内容中的header值来判断是哪个系统的接口并使用特定的方法完成对请求数据的处理'''
        header_flag=self.getHeaderType(row)
        request_data = self.get_request_data(row)
        try:
            if header_flag==self.crm_headerFlag or \
                    header_flag==self.fwh_admin_headerFlag:  # 处理crm接口处理
                if request_data:  # 请求参数不为空
                    crm_request_data = self.requestDataDispose.requestDataGeneral(request_data)
                    return crm_request_data
                else:
                    return request_data
            elif header_flag==self.fwh_headerFlag:  # 处理服务号微信端请求数据
                if request_data:  # 请求参数不为空
                    fwh_request_data = self.requestDataDispose.requestDatafwh(request_data)
                    return fwh_request_data
                else:
                    return request_data
            else:  # 其余情况当做json格式处理
                json_data = demjson.encode(request_data)
                return json_data
        except IndexError as indexError:
            self.log.error(self.mylog.out_varname(indexError))
            # print(indexError)
            return None
    
    # #通过获取关键字拿到data数据
    # def get_data_for_json(self,row):
    #     opear_json=OperationJson()
    #     request_data=opear_json.get_data(self.get_request_data(row))
    #     return request_data
    
    # 获取预期结果
    @args_None
    def get_expect_data(self, row):
        col = int(data_config.get_expect())
        expect = self.opera_excle.get_cell_value(row, col)
        # ''' 替换双引号为单引号，避免由于引号问题出现断言失败'''
        return expect

    # # 根据sql获取预期结果
    @args_None
    def get_sql_expect_data(self, row,col=None):
        # '''根据header确认数据库配置'''
        #''' 根据传入的列以确定数据读取、写入的位置'''
        if col is None:
            col = int(data_config.get_expect())
        else:
            col=col
        sql=self.opera_excle.get_cell_value(row,col)
        self.sql=sql
        if sql:
            header_flag=self.getHeaderType(row)
            if header_flag==self.crm_headerFlag:  # CRM header
                try:
                    sql_except = self.tencent_cloud.sql_operation_limit(sql)
                except TypeError as error:
                    sql_except = None
                    self.log.error(self.mylog.out_varname(error))
            elif header_flag==self.fwh_headerFlag or \
                    header_flag==self.fwh_admin_headerFlag:  # 服务号 、服务号后台sql配置
                try:
                    sql_except = self.tencent_cloud.sql_operation_limit(sql)
                except TypeError as error:
                    sql_except = None
                    self.log.error(self.mylog.out_varname(error))
            else:
                try:
                    sql_except = self.tencent_cloud.sql_operation_limit(sql)
                except TypeError as error:
                    sql_except = None
                    self.log.error(self.mylog.out_varname(error))
            return sql_except
        else:
            return False
    
    # '''根据传入的sql_data确定是否需要执行sql操作'''
    def get_sqlFlag(self,row,sql_data):
        select_str = 'select'
        insert_str = 'INSERT'
        update_str = 'UPDATE'
        delete_str = 'DELETE'
        # '''大写sql'''
        sql_falg_upper=[i.upper() for i in [select_str, insert_str, update_str, delete_str]]
        # '''小写sql'''
        sql_falg_lower=[i.lower() for i in sql_falg_upper]
        if sql_data:
            if (sql_data[:len(select_str)].upper() in sql_falg_upper) or \
                    (sql_data[:len(select_str)].lower() in sql_falg_lower):
                return True
            else:
                return False
        else:
            return False
    
    #确定最终获取预期结果的方式
    @args_None
    def expectData(self,row):
        expect=self.get_expect_data(row)
        expect_falg=self.get_sqlFlag(row,expect)
        # print(self.mylog.out_varname(expect_falg))
        if expect_falg:
            expect = self.get_sql_expect_data(row)
        # print(self.mylog.out_varname(expect))
        return expect

    # 写入实际结果
    def write_result(self, row, value):
        col = int(data_config.get_result())
        write_row_col_value = '{}:{}:{}'.format(row, col, value)
        self.log.info(self.mylog.out_varname(write_row_col_value))
        self.opera_excle.write_value(row, col, value)
        # # #保存
        # self.opera_excle.save_workbook('DataCase_ALL_result.xlsx')
        self.opera_excle.save_workbook()

    # 获取实际结果
    @args_None
    def get_result(self, row):
        col = int(data_config.get_result())
        result = self.opera_excle.get_cell_value(row, col)
        self.log.info(self.mylog.out_varname(result))
        return result

    # 判断是否有case的依赖
    @args_None
    def is_depend(self, row):
        col = int(data_config.get_case_dapend())
        max_line=self.get_case_line()
        depend_case_id = self.opera_excle.get_cell_value(row, col)
        if depend_case_id:
            try:
                depend_case_id=int(depend_case_id)
                if depend_case_id >= max_line:
                    return None
                else:
                    return depend_case_id
            except TypeError as typeerror:
                # print(typeerror)
                self.log.error(self.mylog.out_varname(typeerror))
                return None
        else:
            return None
        
    # 获取依赖数据的key关键字
    @args_None
    def depentKey_kw(self, row):
        # '''写入数据后重新获取的值未更新：
        # 原因：self.data在实例化的时候就已经生成，所以要使写入的值立马生效有两个方式：
        # 1.读取之前在实例化对象
        # 2.读取数据的方式改成不用实例，直接用实例方法
        col = int(data_config.get_key_depend())
        excleDepentKey = self.opera_excle.get_cell_value(row, col)
        self.dependKeyYaml = '{}{}'.format(self.yaml['dependKey'], row)
        if not excleDepentKey:
            # '''通过yaml文件获取depend'''
            if self.dependKeyYaml in self.opera_excle.write_list:
                return self.dependKeyYaml
            else:
                return False
        else:
            return excleDepentKey
          
    # 根据依赖key关键字返回依赖key数据
    def get_depent_key(self,row):
        dependCaseFlag=self.is_depend(row)
        if dependCaseFlag:
            self.write_dependKey(row)
            depend_key = self.depentKey_kw(row)
            depend_key_data = self.yamlKey.readforKey_onetier(key=depend_key)
            if depend_key_data:
                return depend_key_data
            else:
                return False
        else:
            return False
        
    # 写入数据依赖key：可能不准确,按特定规则生成的，需手动确认
    def write_dependKey(self,row):
        str_in=self.get_request_data(row)
        # 获取配置中的dependKey完成dependKey字符拼接
        self.dependKey = '{}{}'.format(self.yaml['dependKey'], row)
        self.dependField = '{}{}'.format(self.yaml['dependField'], row)
        headerFlag=self.getHeaderType(row)
        join_str=''#依赖key生成固定拼接字符串
        if headerFlag==self.fwh_admin_headerFlag:
            join_str=self.yaml['fwhadmin_dependKey_joinstr']
        # 特殊处理服务号获取用户信息接口
        elif (self.yaml['fwh_test_api']+'/index/user/info' in self.get_url(self.get_caseId(row)) ):
            join_str=self.yaml['fwh_user_dependKey_joinstr']
        else:
            join_str=self.yaml['rule_dependKey_joinstr']
        if str_in:
            dependKeyInfo=self.requestDataDispose.denpendKeyGenerate(str_in,join_str=join_str)
            if dependKeyInfo:
                dependKey_dict = {}  # 临时存放dependKey
                dependKey_dict[self.dependKey]=dependKeyInfo
                # '''这句代码用于处理yaml写入失败（浮点对象异常的问题）
                value = eval(demjson.encode(dependKey_dict))
                # '''写入数据至yaml'''
                # 将数据写进实例
                self.opera_excle.writeDatasObject(self.dependKey)
                self.opera_excle.writeDatasObject(self.dependField)
                self.writelist=self.opera_excle.write_list
                # print(self.opera_excle.write_list)
                # print(self.writelist)
                self.yamlKey.write_yaml(value)
                return True
            else:
                return False
        else:
            return False
        
    #通过数据依赖字段将所需字段的值写入请求参数
    def writeDependFiledToRequestData(self,row,source_data=None):
        try:
            questdata_col=int(data_config.get_data())
            dependKey_col=int(data_config.get_key_depend())
            dependField_col=int(data_config.get_field_depend())
            str_in=self.get_request_data(row)
            requestDataDepend=self.requestDataDispose.requestDataDepend(source_data,str_in)
            # print(self.mylog.out_varname(requestDataDepend))
            self.log.info(self.mylog.out_varname(requestDataDepend))
            if requestDataDepend:
                requestDataDepend=str(requestDataDepend)
                # print('requestDataDepend',requestDataDepend)
                self.opera_excle.writeDatasObject(requestDataDepend)
                self.opera_excle.write_value(row,dependKey_col,self.dependKey)
                self.opera_excle.write_value(row, dependField_col, self.dependField)
                self.opera_excle.write_value(row,questdata_col,requestDataDepend)
                # 写完数据保存操作
                # self.opera_excle.save_workbook('DataCase_ALL1.xlsx')
                return True
            else:
                return False
        except BaseException as error:
            self.log.error(self.mylog.out_varname(error))
            print(error)
            return False
    
    # 获取sql语句
    def get_sqlStatementData(self,row):
        col=int(data_config.get_sql_statement())
        # '''调用sql_expect_data赋值self.sql,并返回sql执行结果'''
        data=self.get_sql_expect_data(row, col)
        if data:
            sql_flag=self.get_sqlFlag(row,self.sql)
            if sql_flag:
                return data
            else:
                return False
        else:
            return False
    
    # 获取sql执行结果
    def get_sqlExecuteResult(self,row):
        sql_value=self.get_sqlStatementData(row)
        # print(sql_value)
        if sql_value:
            self.write_sqlExecuteResult(row,sql_value)
            col=int(data_config.get_sql_execute_result())
            sql_value=self.opera_excle.get_cell_value(row,col)
            self.sqlExecuteResult = self.yamlsqlExecute.readforKey_onetier(sql_value)
            if self.sqlExecuteResult:
                return self.sqlExecuteResult
            else:
                return False
        else:
            return False
    
    # 将sql执行结果写入yaml与excle
    def write_sqlExecuteResult(self,row,sql_value):
        col=int(data_config.get_sql_execute_result())
        self.log.info(self.mylog.out_varname(sql_value))
        if sql_value:
            kw_str='FROM'
            re_str='%s\s+(\w+)\s+'%(kw_str.lower())
            if self.sql:
                table_str=re.search(re_str,self.sql)
                if not table_str:
                    re_str = '%s\s?(\w+)\s' %(kw_str.upper())
                    table_str = re.search(re_str, self.sql)
                table_str=table_str.group()
                # 匹配出表名，并作为依赖key的一部分
                table_name=table_str[len(kw_str):].strip()
                # 获取sql执行关键字并组装
                self.sqlExecuteResult='{}{}_{}'.format(self.yaml['sqlExecuteResult'],row,table_name)
                self.log.info(self.mylog.out_varname(self.sqlExecuteResult))
                SqlExecute_dict={}
                # '''这句代码用于处理yaml写入失败（浮点对象异常的问题）
                value = eval(demjson.encode(sql_value))
                SqlExecute_dict[self.sqlExecuteResult]=value
                # '''写入数据至excle与yaml'''
                # self.opera_excle.writeDatasObject(self.sqlExecuteResult)
                self.yamlsqlExecute.write_yaml(SqlExecute_dict)
                self.opera_excle.write_value(row,col,self.sqlExecuteResult)
                # 保存
                self.opera_excle.save_workbook()
                return True
            else:
                return False
        else:
            return False
    
    def write_sqlExecuteResultToRequestData(self,row):
        source_data=self.get_sqlExecuteResult(row)
        # print('source_data',source_data)
        self.log.info(self.mylog.out_varname(source_data))
        if source_data:
            # 将获取出来的sql执行结果写入请求数据
            result=self.writeDependFiledToRequestData(row,source_data=source_data)
            # print(self.mylog.out_varname(result))
            if result:
                return True
            else:
                return False
        else:
            return False
        

            
        
if __name__ == '__main__':
    Gd = GetData()
    # for i in range(2,Gd.get_case_line()):
    for i in range(2,3):
        print(Gd.headerData(i))